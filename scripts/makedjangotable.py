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

import sys
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
        
        result=Result(first_name=r['first_name'],last_name=r['last_name'],gender=r.gender,city=r.city, time=duration,race=race,member=r.hmrrc, category_10=r['category_10'])
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
'''

race=pd.read_csv('../data/2021/LaborDay/LaborDay5k_parsed.csv')
add_race(race, race_name='Labor Day 5k', race_city='Schenectedy', race_date='2021-09-06')
