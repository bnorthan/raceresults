"""Stockade-athon leaders: most finishes, streaks and course records.

Links every result 1976-2025 to a person (scoreware.runner.cluster), prints the
top N with the years each person ran and how any less-certain year was linked
(so a wrong link is easy to spot), and writes two csvs next to the year files:
  persons.csv     every result with its person_id
  most_races.csv      top 100 by races run      } read by the website's
  active_streaks.csv  top 100 current streaks   } Stockade leaders pages
  longest_streaks.csv top 100 streaks ever      }
  records.csv         fastest times: overall, age groups, age graded

Run from the repo root:  python scripts/events/stockade_leaders.py [N]
"""
import os
import sys

import pandas as pd

from scoreware.race import readers, utils
from scoreware.race.agegrade import age_grade, age_standard
from scoreware.runner.cluster import cluster_runners

repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
base_dir  = os.path.join(repo_root, 'data', 'Stockade-athon all time')
TOP_N     = int(sys.argv[1]) if len(sys.argv) > 1 else 20
NO_RACE   = {2020}      # virtual race, no results: doesn't break a streak

# links worth a second look, in the order they are listed
REVIEW = ['fuzzy', 'swapped', 'name part', 'age outlier', 'initial', 'no age', 'ambiguous']


def display_name(rows):
    """Most common full name, preferring rows not written in ALL CAPS."""
    names = rows[rows.given.str.len() > 1]
    names = names if len(names) else rows
    mixed = names[~names.last_name.str.isupper()]
    names = mixed if len(mixed) else names
    first, last = (names.first_name + '|' + names.last_name).mode()[0].split('|')
    return f'{first} {last}'.title() if last.isupper() else f'{first} {last}'


def year_ranges(years):
    """[1976, 1977, 1978, 1981] -> '1976-1978, 1981'"""
    years, out, start = sorted(years), [], None
    for i, y in enumerate(years):
        start = y if start is None else start
        nxt = years[i + 1] if i + 1 < len(years) else None
        if nxt != y + 1 and not (nxt == y + 2 and y + 1 in NO_RACE):
            out.append(str(y) if y == start else f'{start}-{y}')
            start = None
    return ', '.join(out)


def longest_streak(years):
    """(length, first year, last year) of the longest unbroken run; 2020 doesn't break one."""
    runs = []
    for y in sorted(years):
        if runs and (y == runs[-1][2] + 1 or (y == runs[-1][2] + 2 and y - 1 in NO_RACE)):
            runs[-1] = (runs[-1][0] + 1, runs[-1][1], y)
        else:
            runs.append((1, y, y))
    return max(runs, key=lambda r: r[0]) if runs else (0, None, None)


def born(rows):
    b = (rows.year - rows.age).dropna()
    return f'~{int(b.median())}' if len(b) else '?'


def review_note(rows):
    parts = []
    for link in REVIEW:
        ys = rows[rows.link == link].year
        if len(ys):
            parts.append(f'{year_ranges(ys)} {link}')
    return '; '.join(parts)


def active_streak(years, latest):
    """(length, first year) of the unbroken run ending at the latest race, or (0, None)."""
    n, y, since = 0, latest, None
    while y in years or y in NO_RACE:
        if y in years:
            n, since = n + 1, y
        y -= 1
    return n, since


def summary(rows, latest):
    active, since = active_streak(set(rows.year), latest)
    streak, first, last = longest_streak(rows.year)
    return {'runner': display_name(rows), 'races': rows.year.nunique(),
            'streak': streak, 'streak_years': f'{first}-{last}' if streak > 1 else str(first),
            'active': active, 'since': since,
            'born': born(rows), 'years': year_ranges(rows.year), 'check': review_note(rows)}


def ranked(scores, n, linked, latest):
    """Top n of a person_id -> score series, ties at the cutoff included."""
    scores = scores[scores > 0].sort_values(ascending=False, kind='stable')
    top = scores[scores >= scores.iloc[min(n, len(scores)) - 1]]
    out, rank = [], 0
    for i, (pid, score) in enumerate(top.items()):
        rank = i + 1 if i == 0 or score != top.iloc[i - 1] else rank
        out.append({'rank': rank, **summary(linked[linked.person_id == pid], latest), 'person_id': pid})
    return pd.DataFrame(out)


# 5-year groups; no one 90 or older has ever finished
AGE_GROUPS = ['14 & under'] + [f'{a}-{a + 4}' for a in range(15, 90, 5)]


def age_group(age):
    if pd.isna(age):
        return None
    return AGE_GROUPS[0] if age < 15 else f'{min(int(age) // 5 * 5, 85)}-{min(int(age) // 5 * 5, 85) + 4}'


def clock(seconds):
    m, s = divmod(int(round(seconds)), 60)
    h, m = divmod(m, 60)
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'


def timed_results(people):
    """Linked results with a usable time, gender filled from the runner's other
    years, age estimated from them when missing, and an age grade."""
    r = people[(people.person_id >= 0) & people.time.notna()].copy()
    r['seconds'] = r.time.astype(str).map(utils.time_to_seconds)
    r = r[r.seconds > 0]
    known = people[people.gender != 'u'].groupby('person_id').gender.agg(lambda g: g.mode()[0])
    r['gender'] = r.gender.where(r.gender != 'u', r.person_id.map(known)).fillna('u')
    birth = (people.year - people.age).groupby(people.person_id).median()
    estimate = r.year - r.person_id.map(birth).round()
    r['age_est'] = r.age.isna() & estimate.notna()
    r['age'] = r.age.fillna(estimate)
    r['grade'] = [age_grade(s, a, g) for s, a, g in zip(r.seconds, r.age, r.gender)]
    # beats the world-level standard for the runner's age, or with no age known,
    # the 15K open standard for men (40:15): a typo, not a record
    impossible = (r.grade > 100) | (r.seconds < age_standard(25, 'M'))
    for x in r[impossible].itertuples():
        print(f'  excluded, faster than the age standard: {x.year} {x.first_name} {x.last_name} '
              f'{x.gender} {x.age:.0f} {x.time}')
    return r[~impossible]


def best(rows, n, by='seconds', ascending=True):
    """Each runner's best result, top n, ties at the cutoff included."""
    rows = rows.sort_values(by, ascending=ascending, kind='stable').drop_duplicates('person_id')
    if len(rows) > n:
        cut = rows[by].iloc[n - 1]
        rows = rows[rows[by] <= cut] if ascending else rows[rows[by] >= cut]
    return rows


def records(people, linked):
    r = timed_results(people)
    lists = [('Men', best(r[r.gender == 'M'], 10)), ('Women', best(r[r.gender == 'F'], 10))]
    r['group'] = r.age.map(age_group)
    for gender, label in (('M', 'Men'), ('F', 'Women')):
        for group in AGE_GROUPS:
            lists.append((f'{label} {group}', best(r[(r.gender == gender) & (r.group == group)], 5)))
    # recorded ages only: a year off moves a child's or an 80-year-old's grade by points
    lists.append(('Age graded', best(r[r.grade.notna() & ~r.age_est], 10, by='grade', ascending=False)))

    out = []
    for name, rows in lists:
        rank = 0
        for i, x in enumerate(rows.itertuples()):
            value = x.grade if name == 'Age graded' else x.seconds
            rank = i + 1 if i == 0 or value != prev else rank
            prev = value
            out.append({'list': name, 'rank': rank,
                        'runner': display_name(linked[linked.person_id == x.person_id]),
                        'gender': x.gender, 'age': f"{'~' if x.age_est else ''}{x.age:.0f}" if pd.notna(x.age) else '',
                        'year': x.year, 'time': clock(x.seconds),
                        'grade': f'{x.grade:.1f}%' if x.grade else '', 'person_id': x.person_id})
    return pd.DataFrame(out)


results = readers.read_alltime(os.path.join(base_dir, 'csv'))
# names a runner has told us are both theirs (married names etc.)
aliases = [((a.first_name, a.last_name), (a.same_as_first_name, a.same_as_last_name))
           for a in pd.read_csv(os.path.join(base_dir, 'aliases.csv')).itertuples()]
people  = cluster_runners(results, aliases=aliases)
people.drop(columns=['given', 'last']).to_csv(os.path.join(base_dir, 'persons.csv'), index=False)

linked = people[people.person_id >= 0]
latest = linked.year.max()
SITE_N = 100            # rows written for the website
MOST_MIN = 10           # most-races page lists everyone with at least this many

races  = linked.groupby('person_id').year.nunique()
most   = ranked(races[races >= MOST_MIN], len(races), linked, latest)
most.to_csv(os.path.join(base_dir, 'most_races.csv'), index=False)

current = linked[linked.person_id.isin(linked[linked.year == latest].person_id)]
active  = current.groupby('person_id').year.apply(lambda ys: active_streak(set(ys), latest)[0])
streaks = ranked(active[active >= 2], SITE_N, linked, latest)
streaks.to_csv(os.path.join(base_dir, 'active_streaks.csv'), index=False)

longest = linked.groupby('person_id').year.apply(lambda ys: longest_streak(ys)[0])
longest = ranked(longest[longest >= 2], SITE_N, linked, latest)
longest.to_csv(os.path.join(base_dir, 'longest_streaks.csv'), index=False)

recs = records(people, linked)
recs.to_csv(os.path.join(base_dir, 'records.csv'), index=False)

print(f'{len(results)} results, {results.year.nunique()} races, {people.person_id.max() + 1} people\n')
print(f"{'#':>3}  {'Runner':<24} {'Races':>5}  {'Streak':>6}  {'Born':>5}  Years")
for r in most[most['rank'] <= TOP_N].itertuples():
    print(f'{r.rank:>3}  {r.runner:<24} {r.races:>5}  {r.streak:>6}  {r.born:>5}  {r.years}')
    if r.check:
        print(f"{'':>48}check: {r.check}")

print(f'\nActive streaks (unbroken through {latest}, 2020 skipped)')
print(f"{'#':>3}  {'Runner':<24} {'Streak':>6}  {'Since':>5}  {'Races':>5}")
for r in streaks[streaks['rank'] <= TOP_N].itertuples():
    print(f'{r.rank:>3}  {r.runner:<24} {r.active:>6}  {r.since:>5}  {r.races:>5}')

print(f'\nLongest streaks ever (2020 skipped)')
print(f"{'#':>3}  {'Runner':<24} {'Streak':>6}  {'Years':<10}  {'Races':>5}")
for r in longest[longest['rank'] <= TOP_N].itertuples():
    print(f'{r.rank:>3}  {r.runner:<24} {r.streak:>6}  {r.streak_years:<10}  {r.races:>5}')

print('\nRecords')
for name, rows in recs.groupby('list', sort=False):
    print(f'  {name}')
    for x in rows.itertuples():
        print(f'    {x.rank:>2}  {x.runner:<24} {x.time:>8}  {x.year}  {x.gender} {x.age:>3}  {x.grade}')
