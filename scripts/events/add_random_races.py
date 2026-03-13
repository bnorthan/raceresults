import pandas as pd
from importlib import reload
from scoreware.race import django_util
reload(django_util)
from datetime import datetime

name = "/home/bnorthan/runnin/raceresults/data/2022/Marathon/marathon.csv"


# make date March 18th 2023
date = datetime(2022, 10, 13)

from scoreware.race import readers
from scoreware.race import header

race = pd.read_csv(name);
final = readers.parse_general(race, header.RaceHeader.headers, 1)

django_util.add_race(final, 'Mohawk Hudson Marathon', 'Schenectady to Albany', date)


