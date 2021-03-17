#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 24 06:11:03 2021

@author: bnorthan
"""

def time_to_seconds(time):
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
    
def strip_leading_zeros(time):
    return time.lstrip('0').lstrip(':')

def get_last_name(full_name):
    split=full_name.split()
    last_name=split[1];
    for i in range(2,len(split)):
        last_name=last_name+' '+split[i]
        
    return last_name

    
