"""Group race results into people: the same runner across many years, even
when the name is spelled differently or the age is missing.

Results are linked in passes, strongest evidence first:
  a. exact name (after normalize_name) and compatible age
  b. similar names, scored with matcher.matchRunner; also a first and last
     name swapped in one year ('Whitlock Ed'), a two-part married name
     against one of its parts ('Bertasso-Hughes' / 'Bertasso'), and known
     aliases a runner has told us about ('Paola' / 'Chauhan')
  c. results too thin to stand on their own -- an age that disagrees with
     every other year, an initial instead of a first name, or no age at all --
     join a person only when exactly one person could own them

Hard rules no pass breaks: one result per person per year, birth windows that
overlap (within slack_years), no M/F conflict, no Jr/Sr conflict.
"""
import collections
import datetime

import Levenshtein
import pandas as pd

from scoreware.race.utils import normalize_name, last_name_parts, birth_window, windows_overlap
from scoreware.runner.matcher import matchRunner

PLACEHOLDERS = {('none', 'none'), ('no', 'number')}

# a result with no age only joins someone who was plausibly this old that day
MIN_AGE, MAX_AGE = 8, 90


class Person:
    def __init__(self, i, r):
        self.rows = [i]
        self.years = {r.year}
        self.given = r.given
        self.givens = {r.given}
        self.lasts = {r.last}
        self.parts = set(last_name_parts(r.last_name))
        self.swapped = normalize_name(r.last_name, r.first_name)[:2]
        self.suffix = r.suffix
        self.gender = r.gender
        self.window = r.window
        self.n_aged = int(r.window is not None)
        self.cities = collections.Counter([r.city] if isinstance(r.city, str) else [])

    def add(self, other):
        """Absorb another person (or a one-row person) into this one."""
        self.rows += other.rows
        self.years |= other.years
        self.givens |= other.givens
        self.lasts |= other.lasts
        self.parts |= other.parts
        self.suffix = self.suffix or other.suffix
        if self.gender == 'u':
            self.gender = other.gender
        self.window = _narrow(self.window, other.window)
        self.n_aged += other.n_aged
        self.cities.update(other.cities)

    def birth_year(self):
        if self.window is None:
            return None
        lo, hi = self.window
        return (lo.toordinal() + hi.toordinal()) / 2 / 365.25

    def city(self):
        return self.cities.most_common(1)[0][0].lower() if self.cities else None


def _narrow(w1, w2):
    """Combined birth window.  Only a window that truly overlaps narrows it; one
    that is merely within slack (a typo) leaves the established window alone."""
    if w1 is None or w2 is None:
        return w1 or w2
    if windows_overlap(w1, w2, slack_years=0):
        return max(w1[0], w2[0]), min(w1[1], w2[1])
    return w1


def _compatible(p, q, slack):
    return (not (p.years & q.years)
            and (p.gender == q.gender or 'u' in (p.gender, q.gender))
            and (p.suffix == q.suffix or not p.suffix or not q.suffix)
            and windows_overlap(p.window, q.window, slack))


def _plausible_age(p, race_date):
    """Could p have been MIN_AGE..MAX_AGE on race_date?  (unknown window: yes)"""
    if p.window is None:
        return True
    lo, hi = p.window
    return (race_date - hi).days >= 365.25 * MIN_AGE and (race_date - lo).days <= 365.25 * MAX_AGE


def cluster_runners(results, slack_years=1, fuzzy_accept=5.0, last_name_ratio=0.85, given_name_ratio=0.75,
                    aliases=()):
    """results: one row per finish, as from readers.read_alltime.
    aliases: ((first, last), (first, last)) pairs known to be the same runner.

    Returns a copy with columns given, last, person_id and link, where link says
    how the row joined its person: 'exact', 'fuzzy', 'swapped', 'known alias', 'name part',
    'age outlier', 'initial',
    'no age', 'ambiguous' (could belong to more than one person, so left on its
    own) or 'placeholder' (person_id -1).
    """
    df = results.reset_index(drop=True).copy()
    keys = [normalize_name(f, l) for f, l in zip(df.first_name, df.last_name)]
    df['given'], df['last'], df['suffix'] = zip(*keys)
    df['window'] = [birth_window(a, d) for a, d in zip(df.age, df.race_date)]
    df['link'] = 'exact'

    placeholder = [(g, l) in PLACEHOLDERS or not g or not l for g, l in zip(df.given, df['last'])]
    df.loc[placeholder, 'link'] = 'placeholder'
    thin = (df.window.isna() | (df.given.str.len() == 1)) & (df.link != 'placeholder')
    rows = list(df.itertuples())

    # -- a. exact name, compatible age ---------------------------------------
    people = []
    groups = collections.defaultdict(list)
    for r in sorted((r for r in rows if r.link == 'exact' and not thin[r.Index]), key=lambda r: r.year):
        new = Person(r.Index, r)
        group = groups[(r.given, r.last, r.suffix)]
        fits = [p for p in group if _compatible(p, new, slack_years)]
        if fits:
            min(fits, key=lambda p: abs(p.birth_year() - new.birth_year())).add(new)
        else:
            group.append(new)
            people.append(new)

    # -- b. similar names ------------------------------------------------------
    by_last = collections.defaultdict(list)
    for p in people:
        by_last[next(iter(p.lasts))].append(p)
    by_letter = collections.defaultdict(list)
    for last in by_last:
        by_letter[last[0]].append(last)

    candidates = []
    for lasts in by_letter.values():
        for i, l1 in enumerate(lasts):
            for l2 in lasts[i:]:
                if l1 != l2 and (abs(len(l1) - len(l2)) > 2 or Levenshtein.ratio(l1, l2) < last_name_ratio):
                    continue
                for j, p in enumerate(by_last[l1]):
                    for q in (by_last[l2][j + 1:] if l1 == l2 else by_last[l2]):
                        # misspellings, not siblings: Mark/Marc yes, Daniel/David no
                        if Levenshtein.ratio(p.given, q.given) < given_name_ratio \
                                or not _compatible(p, q, slack_years):
                            continue
                        score = matchRunner(p.given, l1, p.gender, p.birth_year(), p.city(),
                                            q.given, l2, q.gender, q.birth_year(), q.city())
                        if score >= fuzzy_accept:
                            candidates.append((score, p, q, 'fuzzy'))

    # first and last name swapped in one year's results ('Whitlock Ed')
    by_key = collections.defaultdict(list)
    for p in people:
        by_key[(p.given, next(iter(p.lasts)))].append(p)
    for p in people:
        if p.swapped == (p.given, next(iter(p.lasts))):
            continue
        for q in by_key.get(p.swapped, []):
            if _compatible(p, q, slack_years):
                candidates.append((6.0, p, q, 'swapped'))

    # names a runner told us are both theirs ('Elizabeth Paola' / 'Elizabeth Chauhan');
    # the hard rules still apply, so a wrong entry can't merge two different people
    for name1, name2 in aliases:
        k1, k2 = normalize_name(*name1)[:2], normalize_name(*name2)[:2]
        for p in by_key.get(k1, []):
            for q in by_key.get(k2, []):
                if _compatible(p, q, slack_years):
                    candidates.append((7.0, p, q, 'known alias'))

    # a two-part (married) last name against one of its parts ('Bertasso-Hughes' / 'Bertasso')
    for p in people:
        for part in p.parts:
            for q in by_last.get(part, []):
                if q is p or Levenshtein.ratio(p.given, q.given) < given_name_ratio \
                        or not _compatible(p, q, slack_years):
                    continue
                score = matchRunner(p.given, part, p.gender, p.birth_year(), p.city(),
                                    q.given, part, q.gender, q.birth_year(), q.city())
                if score >= fuzzy_accept:
                    candidates.append((score, p, q, 'name part'))

    owner = {}
    def find(p):
        while p in owner:
            p = owner[p]
        return p
    for score, p, q, why in sorted(candidates, key=lambda c: -c[0]):
        p, q = find(p), find(q)
        if p is q or not _compatible(p, q, slack_years):
            continue
        big, small = (p, q) if len(p.rows) >= len(q.rows) else (q, p)
        df.loc[small.rows, 'link'] = why
        big.add(small)
        owner[small] = big
    people = [p for p in people if p not in owner]

    # -- c. thin results -------------------------------------------------------
    def by_name():
        index = collections.defaultdict(list)
        for p in people:
            for last in p.lasts:
                index[last].append(p)
        return index

    # an age that disagrees with every other year: a one-result person whose
    # name matches exactly one established person
    index = by_name()
    for p in [p for p in people if len(p.rows) == 1]:
        owners = [q for q in index[next(iter(p.lasts))]
                  if q is not p and q.n_aged >= 2 and p.given in q.givens
                  and not (p.years & q.years)
                  and (p.gender == q.gender or 'u' in (p.gender, q.gender))
                  and (p.suffix == q.suffix or not p.suffix or not q.suffix)]
        if len(owners) == 1:
            owners[0].rows += p.rows
            owners[0].years |= p.years
            df.loc[p.rows, 'link'] = 'age outlier'
            people.remove(p)

    # initials and missing ages, oldest first
    index = by_name()
    for r in sorted((rows[i] for i in df.index[thin]), key=lambda r: r.year):
        new = Person(r.Index, r)
        initial = len(r.given) == 1
        owners = [p for p in index[r.last]
                  if (any(g.startswith(r.given) for g in p.givens) if initial else r.given in p.givens)
                  and _compatible(p, new, slack_years)
                  and _plausible_age(p, r.race_date)]
        if len(owners) == 1:
            owners[0].add(new)
            df.loc[r.Index, 'link'] = 'initial' if initial else 'no age'
        else:
            people.append(new)
            index[r.last].append(new)
            df.loc[r.Index, 'link'] = 'ambiguous' if owners else ('initial' if initial else 'no age')

    person_id = [-1] * len(df)
    for pid, p in enumerate(people):
        for i in p.rows:
            person_id[i] = pid
    df['person_id'] = person_id
    return df.drop(columns=['suffix', 'window'])
