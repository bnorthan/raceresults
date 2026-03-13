import pandas as pd
from raceresults.models import Race
from raceresults.models import Result
from datetime import timedelta
from django.utils.text import slugify
from scoreware.race import utils

def add_race(df,race_name, city, date):
    print(date.day, date.month, date.year)

    year=date.year
    day=date.day 
    month = date.month

    race_date=str(year)+'-'+str(month)+'-'+str(day)
    race=Race(race_name=race_name,city=city,race_date=race_date, slugified_race_name=slugify(race_name))
    race.save()

    for index, r in df.iterrows():
        result=Result()
        result.race=race    

        if 'first_name' in df:
            result.first_name=r.first_name
        if 'last_name' in df:
            result.last_name=r.last_name
        if 'time' in df:
            seconds=utils.time_to_seconds(str(r.time));
            duration=timedelta(seconds=seconds)
            result.time=duration
        if 'age' in df:
            result.age=r.age
        if 'gender' in df:
            result.gender=r.gender

        print(r)
        
        result.save()
