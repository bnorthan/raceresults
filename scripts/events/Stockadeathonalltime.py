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
def stockade_fwf(file,out_file):
    # latin-1 keeps one byte == one character, which is what the fixed-width
    # column positions were laid out against; utf-8 would shift any line
    # containing a curly apostrophe.  Mojibake is undone after parsing.
    race_=pd.read_fwf(file, encoding=(encoding or 'latin-1'))
    results=readers.parse_general(race_, header.RaceHeader.headers, 1)
    for col in ('first_name', 'last_name', 'city', 'full_name'):
        if col in results.columns:
            results[col]=results[col].apply(utils.fix_mojibake)
    results.to_csv(out_file)

def get_lines(file):
    with open(file,encoding=encoding) as f:
        lines = f.readlines()
    return lines


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

    # skip years with no source data at all (1978, 2020)
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

    if year == 1976:
        # format: "N. First Last (age)   mm:ss"
        encoding = 'utf-8'

    elif year in range(1977, 1982):
        # 1977-1981: fixed-width with column headers, utf-8
        encoding = None
        method   = 0

    elif year == 1982:
        # unique column format: "N  time  Last, First sex age"
        encoding = 'cp1252'

    elif year in (1983, 1984, 1985):
        # split male/female files (_m.txt / _f.txt), cp1252
        encoding = 'cp1252'

    elif year in range(1986, 1990):
        # format: "N N FIRST LAST (age) mm:ss.d"  Men's/Women's section headers, cp1252
        # time is mm:ss.d -- match just mm:ss, ignore decimal tenths
        encoding     = 'cp1252'
        method       = 1
        time_pattern = '[0-9][0-9]:[0-5][0-9]'
        last_first   = False

    elif year in range(1990, 1993):
        # format: "N Last, First, age mm.ss"  Male/Female section headers, cp1252
        # time uses dot separator (46.51 means 46:51)
        encoding     = 'cp1252'
        method       = 1
        time_pattern = '[01]?[0-9][0-9]\\.[0-9][0-9]'
        last_first   = True

    elif year in range(1993, 1997):
        # colon times, no gender section headers (gender stored as u), cp1252
        encoding     = 'cp1252'
        method       = 2
        time_pattern = '(?:[1-2]:)?[0-5][0-9]:[0-5][0-9]'

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

    elif year == 1982:
        # format: "N  time  Last, First sex age"
        errors  = 0
        pattern = '[01]?[0-9][0-9]:[0-5][0-9]'
        rows    = []
        for line in get_lines(file):
            time = re.findall(pattern, line)
            if len(time) > 0:
                try:
                    line_ = line.split(maxsplit=2)[2].split(',')
                    if len(line_) == 1:
                        line_ = line_[0].split('.')
                    lname = line_[0].strip()
                    line_ = line_[1].split()
                    fname = line_[0].strip()
                    sex   = line_[1].strip()
                    age   = line_[2].strip()
                    rows.append({'first_name': fname, 'last_name': lname, 'time': time[0], 'age': age, 'gender': sex})
                except:
                    errors += 1
                    print('error', line)
        print(f'{year}: errors {errors}')
        pd.DataFrame(rows).to_csv(out_file)

    elif year in (1983, 1984, 1985):
        # split male/female files
        pattern      = '[01]?[0-9][0-9]:[0-5][0-9]'
        age_pattern  = '([1-9]?[1-9][0-9])'
        first_letter = '[^\\W\\d]'
        rows = []
        for lines, gender in [(get_lines(file_m), 'M'), (get_lines(file_f), 'F')]:
            for line in lines:
                line = line[2:]
                time = re.findall(pattern, line)
                if len(time) > 0:
                    line_ = re.split(pattern, line)[0].strip()
                    match = re.search(first_letter, line_)
                    if not match:
                        continue
                    line_ = line_[match.start():]
                    age   = re.findall(age_pattern, line_)
                    age   = age[0] if len(age) > 0 else 0
                    line_ = line_.split(maxsplit=2)
                    fname = line_[0] if len(line_) > 0 else 'Nobody'
                    lname = line_[1] if len(line_) > 1 else 'No-one'
                    rows.append({'first_name': fname, 'last_name': lname, 'time': time[0], 'age': age, 'gender': gender})
        pd.DataFrame(rows).to_csv(out_file)

    elif method == 1:
        # regex parser - detects gender from "Wom" / "Men" section header lines
        # used for 1986-1992: decimal times like 46:06 (dot converted to colon)
        age_pattern  = '([1-9]?[1-9][0-9])'
        first_letter = '[^\\W\\d]'
        gender = 'M'
        rows   = []
        for line in get_lines(file):
            if line[0:3] == 'Wom':
                gender = 'F'
            line = line[2:]
            time = re.findall(time_pattern, line)
            if len(time) > 0:
                time[0] = time[0].replace('.', ':')
                line_   = re.split(time_pattern, line)[0].strip()
                match   = re.search(first_letter, line_)
                if not match:
                    continue
                line_   = line_[match.start():]
                age     = re.findall(age_pattern, line_)
                age     = age[0] if len(age) > 0 else 0
                line_   = line_.split(maxsplit=2)
                fname   = line_[0].strip(',') if len(line_) > 0 else 'Nobody'
                lname   = line_[1].strip(',') if len(line_) > 1 else 'No-one'
                if last_first:
                    fname, lname = lname, fname
                rows.append({'first_name': fname, 'last_name': lname, 'time': time[0], 'age': age, 'gender': gender})
        pd.DataFrame(rows).to_csv(out_file)

    elif method == 2:
        # regex parser - no gender section headers (1993-1996), gender stored as 'u'
        age_pattern  = '([1-9]?[1-9][0-9])'
        first_letter = '[^\\W\\d]'
        rows = []
        for line in get_lines(file):
            line = line[2:]
            time = re.findall(time_pattern, line)
            if len(time) > 0:
                time[0] = time[0].replace('.', ':')
                line_   = re.split(time_pattern, line)[0].strip()
                match   = re.search(first_letter, line_)
                if not match:
                    continue
                line_   = line_[match.start():]
                age     = re.findall(age_pattern, line_)
                age     = age[0] if len(age) > 0 else 0
                line_   = line_.split(maxsplit=2)
                fname   = line_[0].strip(',') if len(line_) > 0 else 'Nobody'
                lname   = line_[1].strip(',') if len(line_) > 1 else 'No-one'
                rows.append({'first_name': fname, 'last_name': lname, 'time': time[0], 'age': age, 'gender': 'u'})
        pd.DataFrame(rows).to_csv(out_file)

    elif method == 0:
        # fixed-width format with column headers (1977-1981, 1997+)
        stockade_fwf(file, out_file)

    print(f'{year}: done -> {out_file}')


