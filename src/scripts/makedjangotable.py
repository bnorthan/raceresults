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

sys.path.append('../util/')
import raceutil
import header
import readers
reload(readers)

def add_race(race_data, race_name, race_city,race_date):
    
    results=readers.parse_general(race_data, header.RaceHeader.headers, 1)
    results.head()
    
    #results = pd.read_csv('../../data/2020/VirtualStockadeFinal.csv')
    
    race=Race(race_name=race_name,city=race_city,race_date=race_date)
    race.save()
    
    for index, r in results.iterrows():
        seconds=raceutil.timeToSeconds(r.time);
        duration=timedelta(seconds=seconds)
        
        result=Result(first_name=r['first_name'],last_name=r['last_name'],city=r.city, time=duration,race=race)
        result.save()
    
#add_race(pd.read_csv('../../data/2020/VirtualStockadeFinal.csv'),race_name='Virtual Stockade-athon',race_city='Capitol Region', race_date='2020-11-15');
#add_race(pd.read_csv('../../data/2019/Stockade2019.csv'), race_name='2019 Stockade-athon', race_city='Schenectedy', race_date='2019-11-10');
add_race(pd.read_fwf('../../data/2018/stockade.txt'), race_name='2018 Stockade-athon', race_city='Schenectedy', race_date='2018-11-11');
