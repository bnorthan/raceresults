import Levenshtein
import pandas as pd

from scoreware.runner.matcher import matchRunner

SAME_TOWN = 0.85    # city similarity that counts as the same town


def _blank(value):
    return str(value).strip().lower() in ('', 'nan', 'none')


def _age(value):
    """An age, or None when it is missing or nonsense -- a birthdate Wild Apricot
    can't parse comes out of datestring_to_age as 0."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if 5 <= value <= 100 else None


def decide(runner, member, score, accept_score, ask_score):
    """('y' | 'n' | 'ask', reason) for a runner and their best-scoring member.

    An exact first + last name with no M/F conflict goes by age and town:
      age within 1 year                              -> y
      no birthdate, or 2 years apart, same town      -> y
      no birthdate, or 2 years apart, other town     -> ask
    Everything else (3+ years apart, a name that isn't exact) goes by score:
      ask_score and up -> y, above accept_score -> ask, otherwise n.
    """
    first1, last1, gender1, age1, city1 = runner
    first2, last2, gender2, age2, city2 = member
    sexes = {str(g).strip().lower()[:1] for g in (gender1, gender2)}
    sex_conflict = sexes == {'m', 'f'}
    if first1 == first2 and last1 == last2 and not sex_conflict:
        gap = None if age2 is None else abs(age1 - age2)
        if gap is not None and gap <= 1:
            return 'y', 'exact name, same age'
        if gap is None or gap <= 2:
            what = 'no birthdate' if gap is None else f'{gap:.0f} years apart'
            same_town = not _blank(city1) and not _blank(city2) \
                and Levenshtein.ratio(city1, city2) >= SAME_TOWN
            if same_town:
                return 'y', f'exact name, {what}, same town'
            return 'ask', f"exact name, {what}, {'no town on file' if _blank(city2) else 'different town'}"
    if score >= ask_score:
        return 'y', f'score {score:.2f}'
    if score > accept_score:
        return 'ask', f'score {score:.2f}'
    return 'n', f'score {score:.2f}'


def match(members, runners, accept_score, ask_score):
    """Mark each runner member yes/no (columns member, mfname, mlname), asking on stdin
    when decide() can't tell."""
    people = [(str(m['First name']).lower(), str(m['Last name']).lower(), m.gender, _age(m.age),
               str(m.City).lower())
              for _, m in members.iterrows()
              if not (pd.isna(m['First name']) or pd.isna(m['Last name']))]

    counts = {'y': 0, 'n': 0, 'asked': 0}
    for index, r in runners.iterrows():
        runner = (r.first_name.lower(), r.last_name.lower(), r.gender.strip(), r.age, str(r.city).lower())
        score, member = max(((matchRunner(*runner, *m), m) for m in people), key=lambda sm: sm[0])
        answer, why = decide(runner, member, score, accept_score, ask_score)

        if answer == 'ask':
            counts['asked'] += 1
            m_age = 'no birthdate' if member[3] is None else f'{member[3]:.0f}'
            print(f"\nplace {r.place}: {r.first_name} {r.last_name}, {r.age}, {r.city}")
            m_city = '(no town)' if _blank(member[4]) else member[4].title()
            print(f"  member:  {member[0].title()} {member[1].title()}, {m_age}, {m_city}   ({why})")
            answer = 'y' if input('Is this a match? ').strip().lower() == 'y' else 'n'
        elif answer == 'y':
            print(f"match: {r.first_name} {r.last_name} = member {member[0].title()} {member[1].title()}  ({why})")
        counts[answer] += 1

        if answer == 'y':
            runners.at[index, 'member'] = 'yes'
            runners.at[index, 'mfname'] = member[0].capitalize()
            runners.at[index, 'mlname'] = member[1].capitalize()
        else:
            runners.at[index, 'member'] = 'no'
            runners.at[index, 'mfname'] = 'nomatch'
            runners.at[index, 'mlname'] = 'nomatch'

    print(f"\n{counts['y']} members, {counts['n']} not members, {counts['asked']} asked")
