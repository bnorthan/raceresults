#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 24 06:11:03 2021

@author: bnorthan
"""

def timeToSeconds(time):
    temp=time.split('.') 
    temp=temp[0].split(':')
    try:
        if (len(temp)==3):
            return 3600*int(temp[0])+60*int(temp[1])+int(temp[2])
        elif (len(temp)==2):
            return 60*int(temp[0])+int(temp[1])
        elif (len(temp)==1):
            return 60*int(temp[0])
    except:
        return -1
    
def stripLeadingZeros(time):
    return time.strip('0').strip(':')
    
