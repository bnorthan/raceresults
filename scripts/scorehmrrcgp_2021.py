import pandas as pd
import sys

from importlib import reload

from scoreware.match import matchmember 
from scoreware.race import readers

import imp
from scoreware.race import header
from scoreware.race import utils
from scoreware.race import hmrrc_gp_util 


# race 1 Labor Day

members_name='../data/2021/Membership/2021-10-2 Members Hudson Mohawk Road Runners Club.csv'
race_name='../data/2021//LaborDay/LaborDay5k.txt'
race_out_base_dir='../data/2021/LaborDay/'
race_out_base = 'LaborDay5k'
fixed_width=True

# race 2 Anniversary
'''
members_name='../data/2021/Membership/2021-10-02 Members Hudson Mohawk Road Runners Club.csv'
race_name='../data/2021//Anniversary/Anniversary.csv'
race_out_base_dir='../data/2021/Anniversary/'
race_out_base = 'Anniversary'
fixed_width=False
'''

# race 3 marathon

members_name='../data/2021/Membership/2021-10-16 Members Hudson Mohawk Road Runners Club.csv'
race_name='../data/2021//Marathon/marathon.csv'
race_out_base_dir='../data/2021/Marathon/'
race_out_base = 'Marathon'
fixed_width=False

# race 4 Stockade-athon

members_name='../data/2021/Membership/2021-11-21 Members Hudson Mohawk Road Runners Club.csv'
race_name='../data/2021//Stockade/stockade.csv'
race_out_base_dir='../data/2021/Stockade/'
race_out_base = 'Stockade'
fixed_width=False

race_out_name=race_out_base_dir+race_out_base+'.csv'
race_out_males=race_out_base_dir+race_out_base+'_males.csv'
race_out_females=race_out_base_dir+race_out_base+'_females.csv'
race_parsed_name=race_out_base_dir+race_out_base+'_parsed.csv'

read_race_results=True

if read_race_results:
    members=pd.read_csv(members_name)
    members["age"]=members['Birthdate (e.g., 01 Jun 1954)'].apply(lambda x:utils.datestring_to_age(x))
    members["gender"]=members['Gender'].apply(lambda x:utils.parse_gender(x))

    print (members.head())

    if fixed_width:
        racers=readers.parse_general(pd.read_fwf(race_name), header.RaceHeader.headers, 1)
    else:
        racers=readers.parse_general(pd.read_csv(race_name), header.RaceHeader.headers, 1)
    racers.gender=racers.gender.str.strip()
    print (racers.head())
    matchmember.match(members, racers, 4.5, 5.5)

    print (racers.head())

    racers["category_10"]=racers.age.apply(lambda x:hmrrc_gp_util.age_to_cat_hmrrc_10(x))

    racers["div_place"]=racers.groupby(["gender","category_10"])["place"].rank("dense", ascending=True)

hmrrc=racers[racers['member']=='yes']
hmrrc=hmrrc[['place', 'mfname','mlname','gender','age', 'category_10']]
hmrrc.head()

racers.to_csv(race_parsed_name)

hmrrc=hmrrc.sort_values(['gender','category_10','place'])
hmrrc['name']=hmrrc.mfname+" "+hmrrc.mlname
hmrrc.gender=hmrrc.gender.str.upper()

females=hmrrc[hmrrc.gender=='F']
males=hmrrc[hmrrc.gender=='M']

# move this to general function
def getCategoryNames(hmrrc, gender, category):
    temp=hmrrc[hmrrc.gender==gender]
    temp=temp[temp.category_10==category]
    temp=temp.reset_index(drop=True)
    temp=temp.name
    scored=pd.DataFrame()
    scored['score']=[12,10,8,7,6,5,4,3,2,1]
    scored['name']=temp
    return scored

a_open_F=getCategoryNames(hmrrc, 'F', 'a_open')
a_30_39_F=getCategoryNames(hmrrc, 'F', 'b_30_39')
a_40_49_F=getCategoryNames(hmrrc, 'F', 'c_40_49')
a_50_59_F=getCategoryNames(hmrrc, 'F', 'd_50_59')
a_60_69_F=getCategoryNames(hmrrc, 'F', 'e_60_69')
a_70_99_F=getCategoryNames(hmrrc, 'F', 'f_70+')

females=pd.concat([a_open_F, a_30_39_F, a_40_49_F, a_50_59_F, a_60_69_F, a_70_99_F], axis=1)

females.to_csv(race_out_females)

a_open_M=getCategoryNames(hmrrc, 'M', 'a_open')
a_30_39_M=getCategoryNames(hmrrc, 'M', 'b_30_39')
a_40_49_M=getCategoryNames(hmrrc, 'M', 'c_40_49')
a_50_59_M=getCategoryNames(hmrrc, 'M', 'd_50_59')
a_60_69_M=getCategoryNames(hmrrc, 'M', 'e_60_69')
a_70_99_M=getCategoryNames(hmrrc, 'M', 'f_70+')

males=pd.concat([a_open_M, a_30_39_M, a_40_49_M, a_50_59_M, a_60_69_M, a_70_99_M], axis=1)

males.to_csv(race_out_males)

#a_open_F=females[females.category_10=='a_open']
#a_30_39_F=females[females.category_10=='a_30_39']
#a_40_49_F=females[females.category_10=='a_40_49']
#a_50_59_F=females[females.age_cat=='a_50_59']
#a_60_69_F=females[females.age_cat=='a_60_69']
#a_70_99_F=females[females.age_cat=='a_70_99']
