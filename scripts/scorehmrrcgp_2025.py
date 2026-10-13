import pandas as pd
import sys

from importlib import reload

from scoreware.match import matchmember 
from scoreware.race import readers

import imp
from scoreware.race import header
from scoreware.race import utils
from scoreware.race import hmrrc_gp_util 

# Race 2 Marathon 
members_name='../data/2025/Membership/2025-10-24 Members Hudson Mohawk Road Runners Club.csv'
race_name='../data/2025/Marathon/marathonf.csv'
race_out_base_dir='../data/2025/Marathon/'
race_out_base = 'Marathon'
fixed_width=False

# Race 2 Stockade 
members_name='../data/2025/Membership/2025-11-24 Members Hudson Mohawk Road Runners Club.csv'
race_name='../data/2025/Stockade/stockade_2025.csv'
race_out_base_dir='../data/2025/Stockade/'
race_out_base = 'Stockade'
fixed_width=False

# Race 3 Hangover 
members_name='./data/2025/Membership/2026-01-29 Members Hudson Mohawk Road Runners Club.csv'
race_name='./data/2025/Hangover/hangover.csv'
race_out_base_dir='./data/2025/Hangover/'
race_out_base = 'Hangover'

# Race 4 10 Miler
members_name='./data/2025/Membership/2026-04-05 Members Hudson Mohawk Road Runners Club.csv'
race_name='./data/2025/10 Miler/10_miler.csv'
race_out_base_dir='./data/2025/10 Miler/'
race_out_base = '10 Miler'
fixed_width=False

# Race 4 ROTG 
members_name='./data/2025/Membership/2026-04-05 Members Hudson Mohawk Road Runners Club.csv'
race_name='/home/bnorthan/runnin/raceresults/data/2025/ROTG/rotg_2026.txt'
race_out_base_dir='./data/2025/ROTG/'
race_out_base = 'ROTG'
fixed_width=True

# Race 5 Delmar 
members_name='./data/2025/Membership/2026-06-26 Members Hudson Mohawk Road Runners Club.csv'
race_name='/home/bnorthan/runnin/raceresults/data/2025/Delmar/delmar.csv'
race_out_base_dir='./data/2025/Delmar/'
race_out_base = 'Delmar'
fixed_width=False

# Race 6 Masters
members_name='./data/2025/Membership/2026-06-26 Members Hudson Mohawk Road Runners Club.csv'
race_name='/home/bnorthan/runnin/raceresults/data/2025/Masters/masters.csv'
race_out_base_dir='./data/2025/Masters/'
race_out_base = 'Masters'
fixed_width=False

# Race 7 Valleycats
members_name='./data/2025/Membership/2026-08-12 Members Hudson Mohawk Road Runners Club.csv'
race_name='/home/bnorthan/runnin/raceresults/data/2025/Valleycats/valleycats.txt'
race_out_base_dir='./data/2025/Valleycats/'
race_out_base = 'Valleycats'
fixed_width=True

# Race 8 Colonie 
members_name='./data/2025/Membership/2026-08-12 Members Hudson Mohawk Road Runners Club.csv'
race_name='/home/bnorthan/runnin/raceresults/data/2025/Colonie/colonie.csv'
race_out_base_dir='./data/2025/Colonie/'
race_out_base = 'Colonie'
fixed_width=False

# Race 8 Colonie 
members_name='./data/2025/Membership/2026-08-12 Members Hudson Mohawk Road Runners Club.csv'
race_name='/home/bnorthan/runnin/raceresults/data/2025/Colonie/colonie.csv'
race_out_base_dir='./data/2025/Colonie/'
race_out_base = 'Colonie'
fixed_width=False


# Race 8 Colonie 
members_name='./data/2025/Membership/2026-09-01 Members Hudson Mohawk Road Runners Club.csv'
race_name='/home/bnorthan/runnin/raceresults/data/2025/Tawasentha/tawasentha.csv'
race_out_base_dir='./data/2025/Tawasentha/'
race_out_base = 'Tawasentha'
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
    
    print(racers.head())
    
    racers.gender=racers.gender.str.strip()
    print (racers.head())

    racers=racers.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    print(racers.head())

    racers.age = racers.age.astype(int)
    
    bad = members[members['First name'].isna() | members['Last name'].isna()]
    if len(bad) > 0:
        print("\n*** Bad rows detected (missing First/Last name): ***")
        print(bad[['First name','Last name']].to_string())
        ans = input("Press Enter to continue or q to quit: ")
        if ans.strip().lower() == 'q':
            sys.exit()

    matchmember.match(members, racers, 4.5, 5.5)

    print (racers.head())

    racers = racers.drop(racers.index[-1])
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
