from dateutil.parser import parse
import datetime
import pandas as pd

def time_to_hh_mm_ss_str(time):
    ts=time.split(':')
    if int(ts[0])>10:
        strtime='00:'+ts[0]+':'+ts[1]
    else:
        strtime=ts[0]+':'+ts[1]+':'+ts[2]
    return strtime

def parse_gender(gender_string):
    if str(gender_string).lower()[0]=='f':
        return 'F'
    else:
        return 'M'

def calculate_age(birthDate): 
    today = datetime.datetime.today() 
    age = today.year - birthDate.year - \
         ((today.month, today.day) < \
         (birthDate.month, birthDate.day)) 
  
    return age

def datestring_to_age(datestring):
    today=datetime.datetime.today()
    
    try: 
        dob=parse(datestring)
    except:
        dob=today
    
    return calculate_age(dob)

def date_to_age(dates):
    num_total=0
    num_errors=0
    
    for dateString in dates:
        print(dateString)
        num_total=num_total+1
        try: 
            date=parse(dateString)
        except:
            date=datetime.datetime.today
            num_errors=num_errors+1

    print("Num Total: "+str(num_total))
    print("Num Erros: "+str(num_errors))
 
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
    if len(split)>1:
        last_name=split[1];
    
        for i in range(2,len(split)):
            last_name=last_name+' '+split[i]
    else:
        last_name=''    
    return last_name
