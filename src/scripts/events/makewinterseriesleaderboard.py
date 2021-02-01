#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 24 05:54:14 2021

@author: bnorthan
"""

import sys
import numpy as np
import pandas as pd

sys.path.append('../../util/')
import raceutil


data=pd.read_csv('../../../data/2021/2021-02-01 2021 HMRRC VIRUAL WINTER SERIES Hudson Mohawk Road Runners Club.csv')

data.head()

data['time']=data['TIME (HH:MM:SS):'].apply(lambda x: raceutil.stripLeadingZeros(x))
data=data.drop('TIME (HH:MM:SS):',axis=1)
data['seconds']=data['time'].apply(lambda x: raceutil.timeToSeconds(x))

distances=data['DISTANCE COMPLETED:'].unique();

markdown='## HMRRC Virtual Winter Series'

events={}
for distance in distances:
    print(distance)
    event=data[data['DISTANCE COMPLETED:']==distance]
    event=event.sort_values(by='seconds')
    event=event.drop('seconds',axis=1)
    event=event.rename({'DISTANCE COMPLETED:': 'distance'},axis=1)
    markdown+='  \n  \n  \n'+distance+' results  \n  \n'+event.to_markdown()+  '  \n  \n';
    print(event)
    
out_file=open('../../../events/VirtualWinter/leaderboard.md', "w")
out_file.write(markdown)
out_file.close()