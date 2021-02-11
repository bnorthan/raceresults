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

sys.path.append('../util/')
import raceutil

results = pd.read_csv('../../data/2020/VirtualStockadeFinal.csv')

race=Race(race_name="Virtual Stockade-athon",city="Capitol Region")
race.save()

for index, r in results.iterrows():
    seconds=raceutil.timeToSeconds(r.Time);
    duration=timedelta(seconds=seconds)
    
    result=Result(first_name=r['First name'],last_name=r['Last name'],city=r.City, time=duration,race=race)
    result.save()