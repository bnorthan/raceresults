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
    race_=pd.read_fwf(file)    
    results=readers.parse_general(race_, header.RaceHeader.headers, 1)
    results.head()
    results.to_csv(out_file)

def get_lines(file):
    with open(file,encoding=encoding) as f:
        lines = f.readlines()
    return lines


# regex to detect time in mm:ss format (ie 55:22, 65:34, 88:23, etc)
time_pattern='[01]?[0-9][0-9]:[0-9][0-9]' 

# regex to detect time in hh:mm:ss format (ie 55:22, 1:05:34, 1:28:32, 2:05:11, etc)
time_pattern='(?:[1-2]:)?[0-5][0-9]:[0-5][0-9]' 

last_first=False
method=1

year=1997
method=0

'''
year=2005
method=0

year=2004
method=0

year=2003
method=0

year=2002
method=0

year=2001
method=0

year=2000
method=0

year=1999
method=0

year=1998
method=0

year=1997
method=0

year=1996 #1994, 1995, 1996
method=2
encoding='cp1252'
time_pattern='(?:[1-2]:)?[0-5][0-9]:[0-5][0-9]' 

year=1994
method=2
encoding='cp1252'

year=1993
method=2
encoding='cp1252'

year=1992
time_pattern='[01]?[0-9][0-9]\.[0-9][0-9]' 
last_first=True
method=1

year=1991
time_pattern='[01]?[0-9][0-9]\.[0-9][0-9]' 
method=1

year=1990
time_pattern='[01]?[0-9][0-9]\.[0-9][0-9]' 
last_first=True
method=1
'''

'''
year=1988
file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.txt'
out_file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.csv'
encoding='cp1252'

year=1987
file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.txt'
out_file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.csv'
encoding='cp1252'

year=1986
file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.txt'
out_file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.csv'
encoding='cp1252'

year=1985
file_m = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'_m.txt'
file_f = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'_f.txt'
out_file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.csv'
encoding='cp1252'

year=1984
file_m = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'_m.txt'
file_f = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'_f.txt'
out_file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.csv'

year=1983
file_m = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'_m.txt'
file_f = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'_f.txt'
out_file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.csv'

year=1983
file_m = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'_m.txt'
file_f = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'_f.txt'
out_file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.csv'

year=1982
file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.txt'
out_file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.csv'

year=1981
file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.txt'
out_file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.csv'
stockade_fwf(file,out_file)

year=1980
file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.txt'
out_file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.csv'
stockade_fwf(file,out_file)

year=1979
file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.txt'
out_file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.csv'
stockade_fwf(file,out_file)

year=1977
file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.txt'
out_file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.csv'
stockade_fwf(file,out_file)

year=1976
file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.txt'
out_file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.csv'
'''

years=[2003,2004,2005,2006,2007,2008,2009,2010,2011]
years=[2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021]

years=[2019,2020,2021]
method=3
for year in years:
    
    if (method==3):
        file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'_.csv'
        out_file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.csv'
    else:
        file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.txt'
        out_file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.csv'

    if (method==3):
        stockade_csv(file, out_file)
    
    if (method==0):
        stockade_fwf(file, out_file)

    if method==2:
        df=pd.DataFrame(columns=['first_name','last_name','time','age','gender'])
        lines=get_lines(file)
        
        age_pattern='([1-9]?[1-9][0-9])'
        first_letter='[^\W\d]'

        gender='u'
        for line in lines:
            line=line[2:]
            time=re.findall(time_pattern,line)
            if (len(time)>0):
                time[0]=time[0].replace('.',':')
                print(line,time[0])
                seconds=utils.time_to_seconds(time[0]);
                duration=timedelta(seconds=seconds)
                line_=re.split(time_pattern,line)[0].strip()
                pos=re.search(first_letter,line_).start()
                line_=line_[pos:]

                # age
                age=re.findall(age_pattern, line_)
                if(len(age)>0):
                    age=age[0]
                else:
                    age=0

                line_=line_.split(maxsplit=2)

                if (len(line_)>0):
                    fname=line_[0]
                    fname=fname.strip(',')
                else:
                    fname='Nobody'

                if (len(line_)>1):
                    lname=line_[1]
                    lname=lname.strip(',')
                else:
                    lname='No=one'

                if last_first==True:
                    temp=fname
                    fname=lname
                    lname=temp

                print(fname,lname,gender,age,time[0])
                df=df.append({'first_name':fname,'last_name':lname,'time':time[0],'age':age,'gender':gender}, ignore_index=True)
                #print(fname,lname,line_[1])
        df.to_csv(out_file)
    
    if method==1:
        df=pd.DataFrame(columns=['first_name','last_name','time','age','gender'])
        lines=get_lines(file)
        
        age_pattern='([1-9]?[1-9][0-9])'
        first_letter='[^\W\d]'

        gender='M'
        for line in lines:
            if line[0:3]=='Wom':
                gender='F'
            line=line[2:]
            time=re.findall(time_pattern,line)
            if (len(time)>0):
                time[0]=time[0].replace('.',':')
                print(line,time[0])
                seconds=utils.time_to_seconds(time[0]);
                duration=timedelta(seconds=seconds)
                line_=re.split(time_pattern,line)[0].strip()
                pos=re.search(first_letter,line_).start()
                line_=line_[pos:]

                # age
                age=re.findall(age_pattern, line_)
                if(len(age)>0):
                    age=age[0]
                else:
                    age=0

                line_=line_.split(maxsplit=2)

                if (len(line_)>0):
                    fname=line_[0]
                    fname=fname.strip(',')
                else:
                    fname='Nobody'

                if (len(line_)>1):
                    lname=line_[1]
                    lname=lname.strip(',')
                else:
                    lname='No=one'

                if last_first==True:
                    temp=fname
                    fname=lname
                    lname=temp

                print(fname,lname,gender,age,time[0])
                df=df.append({'first_name':fname,'last_name':lname,'time':time[0],'age':age,'gender':gender}, ignore_index=True)
                #print(fname,lname,line_[1])
        df.to_csv(out_file)
            #lines=lines_m.append(lines_f)

    if (year==1983)  or (year==1984) or (year==1985):
        df=pd.DataFrame(columns=['first_name','last_name','time','age','gender'])
        lines_m=get_lines(file_m)
        lines_f=get_lines(file_f)
        
        pattern='[01]?[0-9][0-9]:[0-5][0-9]'
        age_pattern='([1-9]?[1-9][0-9])'
        first_letter='[^\W\d]'

        lines_t=[lines_m, lines_f]
        genders=['M','F']
        for i in range(2):
            lines=lines_t[i]
            gender=genders[i]
            for line in lines:
                line=line[2:]
                time=re.findall(pattern,line)
                if (len(time)>0):
                    #print(line)
                    seconds=utils.time_to_seconds(time[0]);
                    duration=timedelta(seconds=seconds)
                    line_=re.split(pattern,line)[0].strip()
                    pos=re.search(first_letter,line_).start()
                    line_=line_[pos:]

                    # age
                    age=re.findall(age_pattern, line_)
                    if(len(age)>0):
                        age=age[0]
                    else:
                        age=0

                    line_=line_.split(maxsplit=2)

                    if (len(line_)>0):
                        fname=line_[0]
                    else:
                        fname='Nobody'

                    if (len(line_)>1):
                        lname=line_[1]
                    else:
                        lname='No=one'

                    print(fname,lname,gender,age,time[0])
                    df=df.append({'first_name':fname,'last_name':lname,'time':time[0],'age':age,'gender':gender}, ignore_index=True)
                #print(fname,lname,line_[1])
        df.to_csv(out_file)
            #lines=lines_m.append(lines_f)
    errors=0
    if (year==1982):
        df=pd.DataFrame(columns=['first_name','last_name','time','age','gender'])
        lines=get_lines(file)
        pattern='[01]?[0-9][0-9]:[0-5][0-9]'
        for line in lines:
            time=re.findall(pattern,line)
            if (len(time)>0):
                #print(line)
                seconds=utils.time_to_seconds(time[0]);
                duration=timedelta(seconds=seconds)
    
                try:
                    print(time[0])
                    line_=re.split(pattern,line)[0].strip()
                    line_=line.split(maxsplit=2)
                    line_=line_[2].split(',')
                    if (len(line_)==1):
                        line_=line+[0].split('.')
                    lname=line_[0].strip()
                    line_=line_[1]
                    line_=line_.split()
                    fname=line_[0].strip()
                    sex=line_[1].strip()
                    age=line_[2].strip()
                    
                    print('lname',lname,'fname',fname,'sex',sex,'age',age)
                    print()

                    df=df.append({'first_name':fname,'last_name':lname,'time':time[0],'age':age,'gender':sex}, ignore_index=True)
                except:
                    errors=errors+1
                    print('error',line_)
        print('errors',errors)
        df.to_csv(out_file)

    if (year==1976):
        df=pd.DataFrame(columns=['first_name','last_name','time'])
        lines=get_lines(file)
        for line in lines:
            pattern='[0-9][0-9]:[0-5][0-9]'
            time=re.findall(pattern,line)
            if (len(time)>0):
                print('time',time[0])
                name=line.split('.')[1]
                name=name.split('(')[0]
                print('name',name)

                seconds=utils.time_to_seconds(time[0]);
                duration=timedelta(seconds=seconds)
                name=name.strip()

                fname=name.split()[0]

                if len(name.split())>1:
                    lname=name.split()[1]
                else:
                    lname=' '
            
                df=df.append({'first_name':fname,'last_name':lname,'time':time[0]}, ignore_index=True)

        df.to_csv(out_file)


