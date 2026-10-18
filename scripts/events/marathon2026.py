"""Mohawk Hudson River Marathon 2026 (ARE Event Productions text) -> csv for GP scoring.

    python scripts/events/marathon2026.py

The text repeats its title and column header every ~52 finishers, and the header
labels sit a couple of characters off the data, so columns come from the data
itself: a position that is blank on every finisher line is a gap between columns.
Positions are counted in bytes, not characters -- the timing software padded by
bytes, so a 3-byte character ('O’Reilly') would otherwise shift the rest of its line.
City and state share one column, and the timer cuts a long city to fit, right up
against the state ('Hanscom Air Force BaMA'), so the state is the column's last two
characters rather than its last word.  'time' and 'pace' are net -- the file's places are in net order.
"""
import os
import re

import pandas as pd

repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
race_dir = os.path.join(repo_root, 'data', '2026', 'Marathon')

COLUMNS = ['place', 'time', 'pace', 'bib', 'first_name', 'last_name', 'age', 'sex', 'city_st',
           'division', 'division_place', 'division_total', 'gender_place',
           'first_13_1m', 'second_13_1m', '5m', '18_1m', '20m', '24m', 'last_2_2m', 'last_10k',
           'gun_clock', 'gun_pace']


def gap_columns(lines):
    """(start, end) of each column: runs of positions not blank on every line."""
    width = max(len(l) for l in lines)
    blank = [all(i >= len(l) or l[i] == 32 for l in lines) for i in range(width)]
    spans, i = [], 0
    while i < width:
        if blank[i]:
            i += 1
            continue
        j = i
        while j < width and not blank[j]:
            j += 1
        spans.append((i, j))
        i = j
    return spans


def split_state(city_st):
    """city_st unstripped: the state, when there is one, fills its last two characters."""
    st = city_st[-2:]
    return (city_st[:-2].strip(), st) if re.fullmatch('[A-Z]{2}', st) else (city_st.strip(), '')


with open(os.path.join(race_dir, 'draft.txt'), 'rb') as f:
    lines = f.read().splitlines()
data = [l for l in lines if re.match(rb'\s*\d+\s', l)]
spans = gap_columns(data)
assert len(spans) == len(COLUMNS), f'{len(spans)} columns found, expected {len(COLUMNS)}'

fields = [[l[a:b].decode('utf-8') for a, b in spans] for l in data]
df = pd.DataFrame(fields, columns=COLUMNS).apply(lambda c: c.str.strip())
df['city'], df['st'] = zip(*(split_state(f[COLUMNS.index('city_st')].ljust(2)) for f in fields))

# nothing dropped or garbled: places run 1..N, every age is a number
places = df.place.astype(int)
assert list(places) == list(range(1, len(df) + 1)), 'places are not 1..N'
assert df.age.str.fullmatch(r'\d+').all(), df[~df.age.str.fullmatch(r'\d+')]
other = len([l for l in lines if l.strip()]) - len(data)
print(f'{len(df)} finishers; {other} non-blank header/title lines dropped')
print('sex:', df.sex.value_counts().to_dict())

out = df[['place', 'bib', 'first_name', 'last_name', 'age', 'sex', 'city', 'st', 'time', 'pace']]
out.to_csv(os.path.join(race_dir, 'marathon.csv'), index=False)
print('wrote', os.path.join(race_dir, 'marathon.csv'))
