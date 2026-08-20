#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
How to run:
  cd django/mysite
  python manage.py shell < ../../scripts/makedjangotable.py
  OR standalone (Django auto-configured):
  cd django/mysite && python ../../scripts/makedjangotable.py
"""

import os, sys
import django
from django.conf import settings

# Allow running standalone (not just inside Django shell)
if not settings.configured:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'django', 'mysite'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    django.setup()

import pandas as pd
from datetime import timedelta
from raceresults.models import Race
from raceresults.models import Result

from importlib import reload

from scoreware.race import utils
from scoreware.race import header
from scoreware.race import readers

from django.db.transaction import atomic

@atomic
def add_race(race_data, race_name, race_city,race_date):
    
    results=readers.parse_general(race_data, header.RaceHeader.headers, 1)
    results.head()
    
    race=Race(race_name=race_name,city=race_city,race_date=race_date)
    race.save()
    
    for index, r in results.iterrows():
        seconds=utils.time_to_seconds(r.time);
        duration=timedelta(seconds=seconds)
        
        result=Result(first_name=r['first_name'],last_name=r['last_name'],gender=r.gender,city=r.city, time=duration,race=race,member=r.hmrrc, category_10=r['category_10'],member_first_name=r['member_first_name'], member_last_name=r['member_last_name'])
        print(r.last_name)
        result.save()

'''
race=pd.read_csv('../data/2020/VirtualStockadeFinal.csv')
add_race(race,race_name='2020 Stockade-athon (Virtual)',race_city='Capitol Region', race_date='2020-11-15')
race=pd.read_csv('../data/2019/Stockade2019.csv')
add_race(race, race_name='2019 Stockade-athon', race_city='Schenectedy', race_date='2019-11-10')
race=pd.read_fwf('../data/2018/stockade.txt')
add_race(race, race_name='2018 Stockade-athon', race_city='Schenectedy', race_date='2018-11-11')
race=pd.read_fwf('../data/2017/2017stockade.txt')
add_race(race, race_name='2017 Stockade-athon', race_city='Schenectedy', race_date='2017-11-12')

race=pd.read_csv('../data/2016/stockade.csv')
add_race(race, race_name='2016 Stockade-athon', race_city='Schenectedy', race_date='2016-11-13')

race=pd.read_csv('../data/2021/LaborDay/LaborDay5k_parsed.csv')
add_race(race, race_name='Labor Day 5k', race_city='Schenectedy', race_date='2021-09-06')

race=pd.read_csv('../data/2021/Anniversary/Anniversary_parsed.csv')
add_race(race, race_name='Anniversary 5.6 Miler', race_city='Albany', race_date='2021-09-26')
race=pd.read_csv('/home/bnorthan/runnin/raceresults/data/2021/Marathon/Marathon_parsed.csv')
add_race(race,race_name='2021 HMRRC Marathon',race_city='Capitol Region', race_date='2021-10-11')

'''
'''
race=pd.read_csv('/home/bnorthan/runnin/raceresults/data/2021/Stockade/Stockade_parsed.csv')
add_race(race,race_name='2021 Stockade-athon',race_city='Schenectady', race_date='2021-11-14')
'''

# ==============================================================================
# All-time Stockade: load minimal CSVs (first_name, last_name, time) to database
# Prereq: run Stockadeathonalltime.py first to generate the CSVs from txt files
#
# To run:  cd django/mysite && python ../../scripts/makedjangotable.py
# Change alltime_years to control which years get loaded:
#   single year:  alltime_years = [1978]
#   all years:    alltime_years = list(range(1976, 2026))
# ==============================================================================

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_dir   = os.path.join(repo_root, 'data', 'Stockade-athon all time', 'csv')

from scoreware.race import hmrrc_gp_util


def load_stockade_dates():
    """Real race dates from csv/dates.csv (day, month, year).  2022-2025 are
    inferred from the 2nd-Sunday-of-November pattern, not from an official source."""
    path = os.path.join(csv_dir, 'dates.csv')
    dates = {}
    d = pd.read_csv(path)
    for _, r in d.iterrows():
        stamp = f"{int(r['year'])}-{str(r['month']).strip()}-{int(r['day'])}"
        dates[int(r['year'])] = pd.to_datetime(stamp).date()
    return dates


stockade_dates = load_stockade_dates()


def add_alltime_stockade(year):
    csv_file = os.path.join(csv_dir, str(year) + '.csv')
    if not os.path.exists(csv_file):
        print(f'{year}: CSV not found at {csv_file} -- skipping')
        return

    # delete all existing copies of this race (and their results via CASCADE)
    race_name = str(year) + ' Stockade-athon'
    existing = Race.objects.filter(race_name=race_name)
    count = existing.count()
    if count > 0:
        existing.delete()

    df = pd.read_csv(csv_file)
    race_date = stockade_dates.get(year)
    if race_date is None:
        race_date = str(year) + '-11-01'
        print(f'{year}: no date in dates.csv, defaulting to {race_date}')

    race = Race(race_name=race_name, city='Schenectady', race_date=race_date)
    race.save()

    # csv schemas differ by era - use whatever columns this year happens to have
    has = lambda c: c in df.columns

    results, skipped = [], 0
    for _, r in df.iterrows():
        seconds = utils.time_to_seconds(str(r.time))
        if seconds < 0:
            skipped += 1
            continue

        gender = 'u'
        if has('gender') and pd.notna(r.gender):
            g = str(r.gender).strip().upper()[:1]
            gender = g if g in ('M', 'F') else 'u'

        city = None
        if has('city') and pd.notna(r.city):
            city = str(r.city).strip()

        category = 'unknown'
        if has('age') and pd.notna(r.age):
            try:
                category = hmrrc_gp_util.age_to_cat_hmrrc_10(int(float(r.age)))
            except (ValueError, TypeError):
                pass

        results.append(Result(
            first_name=str(r.first_name), last_name=str(r.last_name),
            gender=gender, city=city, category_10=category,
            time=timedelta(seconds=seconds), race=race))

    Result.objects.bulk_create(results, batch_size=1000)
    note = f' ({skipped} skipped, no time)' if skipped else ''
    print(f'{year}: {race_date}  loaded {len(results)} results{note}')


# Change this list to control which years get loaded:
#   single year:  alltime_years = [1979]
#   all years:    alltime_years = list(range(1976, 2026))
alltime_years = list(range(1976, 2026))

for year in alltime_years:
    add_alltime_stockade(year)
