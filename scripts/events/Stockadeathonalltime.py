#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 12:09:12 2021

@author: bnorthan

- this script needs to be run in the Django python shell
- to start Django python shell from the mysite project 
- (or other project that imports the raceresults plugin) 
- run python manageserver shell

The script loads a csv file of race results, then adds a race, and the results 
of the race to the database of the Django raceresults plugin

"""

import os
import re
import sys
import pandas as pd
from datetime import timedelta

from importlib import reload

from scoreware.race import utils
from scoreware.race import header
from scoreware.race import readers

from django.db.transaction import atomic

# function to read and clean csv format
def stockade_csv(file, out_file):
    race_=pd.read_csv(file)
    results=readers.parse_general(race_, header.RaceHeader.headers, 1)
    results.head()
    results.to_csv(out_file)

# function to read clean fixed width format
def fwf_colspecs(file):
    """Column boundaries for a fixed-width results file.  Columns are found in
    the first 100 lines, as pandas does, but pandas then clips anything wider
    that turns up later (a long name, a '100/107' division place, a 100+ minute
    time).  Here each gap between two columns is cut where the fewest lines of
    the whole file have a word running across the cut, so spill-over stays with
    its own column."""
    with open(file, encoding=(encoding or 'latin-1')) as f:
        lines = f.read().splitlines()
    width = max(map(len, lines))
    used = [any(i < len(l) and not l[i].isspace() for l in lines[:101]) for i in range(width)] + [False]
    cores, start = [], None
    for i, u in enumerate(used):
        if u and start is None:
            start = i
        elif not u and start is not None:
            cores.append((start, i))
            start = None

    def cuts(p):        # lines with a word running across the boundary before position p
        return sum(1 for l in lines if p < len(l) and not l[p - 1].isspace() and not l[p].isspace())

    bounds = [0]
    for (_, a_end), (b_start, _) in zip(cores, cores[1:]):
        middle = (a_end + b_start) / 2
        bounds.append(min(range(a_end, b_start + 1), key=lambda p: (cuts(p), abs(p - middle))))
    return list(zip(bounds, bounds[1:] + [width]))

def stockade_fwf(file,out_file,rename=None):
    # latin-1 keeps one byte == one character, which is what the fixed-width
    # column positions were laid out against; utf-8 would shift any line
    # containing a curly apostrophe.  Mojibake is undone after parsing.
    race_=pd.read_fwf(file, encoding=(encoding or 'latin-1'), colspecs=fwf_colspecs(file))
    if rename:
        race_=race_.rename(columns=rename)
    results=readers.parse_general(race_, header.RaceHeader.headers, 1)
    if 'time' in results.columns:
        results['time']=results['time'].map(clean_time)
    for col in ('first_name', 'last_name', 'city', 'full_name'):
        if col in results.columns:
            results[col]=results[col].apply(utils.fix_mojibake)
    results.to_csv(out_file)

def get_lines(file):
    with open(file,encoding=encoding) as f:
        lines = f.readlines()
    return lines


AGE_PATTERN  = '([1-9]?[1-9][0-9])'
FIRST_LETTER = '[^\\W\\d]'
# a place or division-place number, including scanned ones like 'I6', '9S4',
# '3!', '[16', 'ii' and 'III' (1 read as I/i/l, 5 as S)
NUMBER_LIKE  = re.compile(r'[\dIiLl!|S?t().\[\]]+')

def strip_places(text, places):
    """Drop up to `places` leading place / division-place tokens.  Lines without a
    division place ('place RICHARD ...') and names glued to one ('30Jeff')
    keep their name, since those tokens aren't all digit look-alikes."""
    tokens = text.split()
    for _ in range(places):
        t = tokens[0] if tokens else ''
        if NUMBER_LIKE.fullmatch(t) and (any(c.isdigit() for c in t) or len(t) <= 3):
            tokens.pop(0)
    return ' '.join(tokens)

SCANNED_TIME = str.maketrans('lIiOoSB', '1110058')

def clean_time(t):
    """A fixed-width time cell -> 'mm:ss[.d]' / 'h:mm:ss', or '' if unreadable.
    Scanned letters become digits ('5l:53.O', 'S7:39.9') and stray marks go
    ('.63:24.7', '79:42 .'), dots become colons ('63.49.7'); anything still
    odd ('?6:55.5') is left blank."""
    t = str(t).translate(SCANNED_TIME).strip(" .'\"`,")
    t = re.sub(r'^(\d{2,3})\.(\d\d)(?=\.|$)', r'\1:\2', t)      # '63.49.7' -> '63:49.7'
    return t if re.fullmatch(r'(\d{1,2}:)?\d{1,3}:\d\d(\.[\d?]*)?', t) else ''

def close_up_time(line):
    """A stray space before the seconds: '1:01 :39' (1994)."""
    return re.sub(r'(\d) :(\d\d)', r'\1:\2', line)

def repair_time(line):
    """Second try when no time was found: a space inside the minutes
    ('29 5 1:22.7', 1988-89) or an age glued to the time ('3872:17.3')."""
    line = re.sub(r'(\d\d) (\d) (\d:\d\d)', r'\1 \2\3', line)
    return re.sub(r'(?<![0-9:])(\d\d)(\d\d:\d\d)', r'\1 \2', line)

def looks_like_result(line):
    """Place number (and maybe a division place), a name, then more digits (age
    or a mangled time).  Title lines like '1990 Stockade-athon' have no digits
    after the name."""
    return re.match(r'\s*\d[\d\s]*[A-Za-z]{2,}.*\d', line) is not None

def parse_result_line(line, time_pattern, last_first=False, places=1):
    """'place [div_place] name [,] [(]age[)] time' -> dict, or None for a
    non-result line.  A finisher whose time can't be read is kept, with time
    None and a note, rather than silently dropped."""
    line = close_up_time(line)
    time = re.findall(time_pattern, line)
    if not time and re.findall(time_pattern, repair_time(line)):
        line = repair_time(line)
        time = re.findall(time_pattern, line)
    note = None
    if time:
        before = re.split(time_pattern, line)[0]
        time   = time[0].replace('.', ':')
    elif looks_like_result(line):
        before, time, note = line, None, 'time unreadable: ' + line.strip()
    else:
        return None
    before = strip_places(before, places)
    match  = re.search(FIRST_LETTER, before)
    if not match:
        return None
    before = before[match.start():]
    age    = re.findall(AGE_PATTERN, before)
    age    = age[0] if len(age) > 0 else 0
    name   = re.split(r'[({\[<>]|[\s,]\d', before, maxsplit=1)[0]   # name ends at '(age)' or the age
    fname, lname = split_name(name, last_first)
    return {'first_name': fname, 'last_name': lname, 'time': time, 'age': age, 'note': note}

def _is_initial(token):
    return len(token.rstrip('.')) == 1

TITLES_BEFORE = {'dr', 'mr', 'mrs', 'ms', 'rev'}
TITLES_AFTER  = {'md', 'phd', 'dds'}

def _is_trailing_junk(token):
    """Scanner debris where the age was ('COLE R', 'DOWER I3'), or a title ('MD')."""
    return _is_initial(token) or re.search(r'\d', token) or token.lower().rstrip('.') in TITLES_AFTER

def split_name(name, last_first=False):
    """Name text -> (first, last), keeping every word of the last name:
    'MARK MIN DEL' -> ('MARK', 'MIN DEL'), 'Joseph F. Schmoe' -> ('Joseph F.', 'Schmoe'),
    'Mary Ellen Cusano' -> ('Mary Ellen', 'Cusano'), 'DR. DON SYMANOWICZ' -> ('DON', 'SYMANOWICZ'),
    'St. Onge, Paul' -> ('Paul', 'St. Onge'), 'Powers, Jr., Joseph' -> ('Joseph', 'Powers Jr.')."""
    if last_first and ',' in name:
        parts = [p.strip(' .:;') for p in name.split(',') if p.strip(' .:;')]
        last  = parts[0] if parts else 'No-one'
        rest  = parts[1:]
        if rest and rest[0].lower() in utils.NAME_SUFFIXES:
            last += ' ' + rest.pop(0)
        return (rest[0] if rest else 'Nobody'), last
    tokens = [t.strip(',:;') for t in name.split()]
    tokens = [t for t in tokens if t]
    while len(tokens) > 1 and tokens[0].lower().rstrip('.') in TITLES_BEFORE:
        tokens.pop(0)
    while len(tokens) > 2 and _is_trailing_junk(tokens[-1]):
        tokens.pop()
    if not tokens:
        return 'Nobody', 'No-one'
    if last_first:                      # no comma: 'Last First'
        tokens = tokens[1:] + tokens[:1]
    tokens[-1] = tokens[-1].rstrip('.')
    # initials and second given names stay with the first name:
    # 'R Jeffrey Cole', 'Don F Miller', 'Mary Ellen Cusano'
    n_first = 1
    while n_first < len(tokens) - 1 and (_is_initial(tokens[n_first - 1]) or _is_initial(tokens[n_first])
                                         or tokens[n_first].lower() in utils.GIVEN_NAMES):
        n_first += 1
    first = ' '.join(tokens[:n_first])
    last  = ' '.join(tokens[n_first:]) or 'No-one'
    return first, last

def write_rows(rows, out_file):
    unreadable = sum(r['note'] is not None for r in rows)
    print(f'{year}: {len(rows)} rows, {unreadable} kept with an unreadable time')
    apply_corrections(pd.DataFrame(rows)).to_csv(out_file)


def apply_corrections(df):
    """Fix known misreads (scanning errors, typos) in this year's derived csv from
    corrections.csv (year, place, field, wrong, right, why).  The txt source is
    never edited.  A correction whose 'wrong' value no longer matches is reported,
    not applied, so a parser change can't silently misapply it."""
    path = os.path.join(base_dir, 'corrections.csv')
    if not os.path.exists(path) or 'place' not in df.columns:
        return df
    fixes = pd.read_csv(path, dtype=str)
    for _, c in fixes[fixes.year == str(year)].iterrows():
        hit = (df.place.astype(str) == c.place) & (df[c.field].astype(str) == c.wrong)
        if hit.sum() == 1:
            df.loc[hit, c.field] = c.right
        else:
            print(f'{year}: correction not applied (place {c.place} {c.field} != {c.wrong!r})')
    return df


SCANNED_1982 = re.compile(r'^\s*(\S+)\s+(?:(\d\S*)\s+)?(.+?)\s+([A-Za-z])\s+((?=\S?[\d?i])\S{1,2})\s+(\S.*?)\s*$')
# digits the scan put inside names: WE6LERZ, 6AIGE
SCANNED_DIGITS = str.maketrans('01568', 'OISGB')

def parse_1982_line(line):
    """'10  2 MINBEL, H   M 30 48:39' -> dict, or None for a non-result line.
    Names are ALL CAPS, so any lowercase letter is a scanned comma
    ('EBBETSf R', 'STEADMANt H'), and a digit is a scanned letter ('WE6LERZ');
    sex scanned as H/N/K is M.  The division place is sometimes missing."""
    m = SCANNED_1982.match(line)
    if not m or not re.search('[A-Z]{2}', m.group(3)):
        return None
    place, div_place, name, sex, age, time = m.groups()
    name = re.sub(r'[a-z,:;»Â]+', ',', name).translate(SCANNED_DIGITS)
    if ',' in name:
        last, initial = name.rsplit(',', 1)
    else:
        last, _, initial = name.rpartition(' ')
    last    = re.sub(r'^[^A-Z]+|[^A-Z]+$', '', last.replace(',', ''))
    initial = re.sub(r'[^A-Z0-9]', '', initial)
    note = None
    if not re.fullmatch(r'[01]?[0-9][0-9]:[0-5][0-9]', time):
        time, note = None, 'time unreadable: ' + line.strip()
    return {'place': place, 'first_name': initial, 'last_name': last,
            'gender': {'M': 'M', 'H': 'M', 'N': 'M', 'K': 'M', 'F': 'F'}.get(sex, 'u'),
            'age': age if age.isdigit() else None, 'div_place': div_place,
            'time': time, 'note': note}


repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_dir  = os.path.join(repo_root, 'data')
base_dir  = os.path.join(data_dir, 'Stockade-athon all time')
txt_dir   = os.path.join(base_dir, 'txt')
csv_dir   = os.path.join(base_dir, 'csv')

# ============================================================
# Set years to process. Examples:
#   Single year:  years = [1986]
#   Range:        years = list(range(1976, 2026))
# ============================================================
years = list(range(1976, 2026))

for year in years:

    file     = txt_dir + '/' + str(year) + '.txt'
    file_m   = txt_dir + '/' + str(year) + '_m.txt'
    file_f   = txt_dir + '/' + str(year) + '_f.txt'
    out_file = csv_dir + '/' + str(year) + '.csv'

    # skip years with no source data at all (2020)
    if year in (1983, 1984, 1985):
        needed = [file_m, file_f]
    elif year == 2019:
        needed = [os.path.join(data_dir, '2019', 'Stockade2019.csv')]
    else:
        needed = [file]
    if not all(os.path.exists(f) for f in needed):
        print(f'{year}: no source data -- skipping')
        continue

    # -- Per-year configuration --
    # defaults
    method       = 0
    encoding     = None
    last_first   = False
    time_pattern = '(?:[1-2]:)?[0-5][0-9]:[0-5][0-9]'
    rename       = None

    if year == 1976:
        # format: "N. First Last (age)   mm:ss"
        encoding = 'utf-8'

    elif year == 1978:
        # pdftotext -layout of a spreadsheet-exported pdf, utf-8
        encoding = 'utf-8'

    elif year in (1979, 1980):
        # fixed-width like 1977-1981, but 'AG' is age-group (division) place,
        # not age -- header.py would otherwise map 'ag' onto age
        encoding = None
        method   = 0
        rename   = {'AG': 'div'}

    elif year in range(1977, 1982):
        # 1977-1981: fixed-width with column headers, utf-8
        encoding = None
        method   = 0

    elif year == 1982:
        # scanned: "place  div_place  LAST, I  sex age time", cp1252
        encoding = 'cp1252'

    elif year in (1983, 1984, 1985):
        # split male/female files (_m.txt / _f.txt), cp1252
        encoding = 'cp1252'

    elif year in range(1986, 1990):
        # format: "N N FIRST LAST (age) mm:ss.d"  Men's/Women's section headers, cp1252
        # time is mm:ss.d -- match just mm:ss, ignore decimal tenths; 100+ minutes
        # is 1mm:ss, and a typo like '611:29' is left unreadable, not cut to 11:29
        encoding     = 'cp1252'
        method       = 1
        time_pattern = '(?<![0-9])1?[0-9]{2}:[0-5][0-9]'
        last_first   = False

    elif year in range(1990, 1993):
        # format: "N Last, First, age mm.ss"  Male/Female section headers, cp1252
        # (1991 alone is "N First Last, age mm.ss")
        # time uses dot separator (46.51 means 46:51)
        encoding     = 'cp1252'
        method       = 1
        time_pattern = '(?<![0-9])[01]?[0-9][0-9]\\.[0-9][0-9]'
        last_first   = year != 1991

    elif year in range(1993, 1997):
        # colon times, no gender section headers (gender stored as u), cp1252
        # 1993 writes an hour-plus time as minutes (64:41), 1994 as 1:04:41
        encoding     = 'cp1252'
        method       = 2
        time_pattern = '(?<![0-9])(?:[0-9]:)?[0-9]{1,3}:[0-5][0-9]'

    elif year >= 1997:
        # 1997+: fixed-width with column headers, utf-8
        encoding = None
        method   = 0

    # -- Parsing --

    if year == 1976:
        # format: "N. First Last (age)   mm:ss"
        rows = []
        for line in get_lines(file):
            pattern = '[0-9][0-9]:[0-5][0-9]'
            time = re.findall(pattern, line)
            if len(time) > 0:
                name  = line.split('.')[1].split('(')[0].strip()
                fname = name.split()[0]
                lname = name.split()[1] if len(name.split()) > 1 else ' '
                rows.append({'first_name': fname, 'last_name': lname, 'time': time[0]})
        pd.DataFrame(rows).to_csv(out_file)

    elif year == 2019:
        # 2019 was never added to txt/; the raw csv lives under data/2019/
        # columns: Place,Name,Age,S,City,St,Guntime,Pace  (full name, no div place)
        stockade_csv(os.path.join(data_dir, '2019', 'Stockade2019.csv'), out_file)

    elif year == 1978:
        # format: "place gender_place [div_place] First   Last   [age] sex div h:mm:ss"
        # div_place and age are sometimes blank, sex is sometimes '?'.
        # First and last are separate layout columns, so split on 2+ spaces
        # (handles "St John", "Reilly Jr", "R Jeffrey").
        pattern = re.compile(r'^\s*(\d+)\s+\d+\s+(?:(\d+)\s+)?(.+?)\s+(?:(\d+)\s+)?([MF?])\s+(\S+)\s+((?:[0-9]:)?[0-5][0-9]:[0-5][0-9])\s*$')
        rows    = []
        skipped = 0
        for line in get_lines(file):
            m = pattern.match(line)
            if not m:
                if re.match(r'^\s*\d+\s', line):
                    skipped += 1
                    print('error', line)
                continue
            place, div_place, name, age, sex, div, time = m.groups()
            fname, lname = re.split(r'\s{2,}', name, maxsplit=1)
            # source sex disagrees with the gender-place sequence
            sex = {'307': 'F',   # Lisa Miller: 'M' in source, div HSF, women's place 8
                   '501': 'M',   # Inger Giaever: '?' in source, men's place 444
                   }.get(place, sex)
            rows.append({'place': place, 'first_name': fname, 'last_name': lname,
                         'gender': sex if sex in ('M', 'F') else 'u', 'age': age,
                         'division': div, 'div_place': div_place, 'time': time})
        print(f'{year}: {len(rows)} rows, {skipped} numbered lines skipped')
        pd.DataFrame(rows).to_csv(out_file)

    elif year == 1982:
        # scanned: parse by position (place, div place, name, sex, age, time)
        # rather than by commas, which the scan often misreads
        rows = [r for r in map(parse_1982_line, get_lines(file)) if r]
        write_rows(rows, out_file)

    elif year in (1983, 1984, 1985):
        # split male/female files; 1985 has a few dot times (61.57); a typo like
        # '643:01' is left unreadable, not cut to 43:01
        pattern = '(?<![0-9])[01]?[0-9][0-9][:.][0-5][0-9]'
        rows = []
        for lines, gender in [(get_lines(file_m), 'M'), (get_lines(file_f), 'F')]:
            for line in lines:
                row = parse_result_line(line, pattern, places=2)
                if row:
                    rows.append({**row, 'gender': gender})
        write_rows(rows, out_file)

    elif method == 1:
        # regex parser - detects gender from "Wom" / "Men" section header lines
        # used for 1986-1992: decimal times like 46:06 (dot converted to colon)
        gender = 'M'
        rows   = []
        for line in get_lines(file):
            if line[0:3] == 'Wom':
                gender = 'F'
            row = parse_result_line(line, time_pattern, last_first, places=2 if year < 1990 else 1)
            if row:
                rows.append({**row, 'gender': gender})
        write_rows(rows, out_file)

    elif method == 2:
        # regex parser - no gender section headers (1993-1996), gender stored as 'u'
        rows = []
        for line in get_lines(file):
            row = parse_result_line(line, time_pattern)
            if row:
                rows.append({**row, 'gender': 'u'})
        write_rows(rows, out_file)

    elif method == 0:
        # fixed-width format with column headers (1977-1981, 1997+)
        stockade_fwf(file, out_file, rename)

    print(f'{year}: done -> {out_file}')


