import pandas as pd
from raceresults.models import Race
from raceresults.models import Result
from datetime import timedelta

from scoreware.race import utils

dates = pd.read_csv('/home/bnorthan/runnin/raceresults/data/All Stockade results/dates_.csv')

for index, date in dates.iterrows():
    print(date.day, date.month, date.year)

    year=date.year
    day=date.day 

    race_date=str(year)+'-11-'+str(day)
    race=Race(race_name="Stockade-athon",city='Schenectady',race_date=race_date)
    race.save()
    file = '/home/bnorthan/runnin/raceresults/data/All Stockade results/'+str(year)+'.csv'
    df=pd.read_csv(file)

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

        #print(r)
        
        result.save()