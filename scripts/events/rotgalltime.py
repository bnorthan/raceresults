import pandas as pd
from scoreware.race.django_util import add_race
from datetime import datetime

name = "/home/bnorthan/runnin/raceresults/data/All ROTG results/rotg_with_numbers.txt"
entries_name = "/home/bnorthan/runnin/raceresults/data/All ROTG results/rotg2023final.csv"

race = pd.read_fwf(name);
entries = pd.read_csv(entries_name);

# join race and entries on number
joined = pd.merge(race[['No.','S','Age', 'City', 'St', 'Time','Pace']], entries[['No.','First Name','Last Name', 'USATF']], on='No.', how='left')

joined.to_csv("/home/bnorthan/runnin/raceresults/data/All ROTG results/rotg_with_usatf.csv")

# make date March 18th 2023
date = datetime(2023, 3, 18)

from scoreware.race import readers
from scoreware.race import header

final = readers.parse_general(joined, header.RaceHeader.headers, 1)

add_race(final, 'Runnin\' of the Green', 'Rotterdam', date)




