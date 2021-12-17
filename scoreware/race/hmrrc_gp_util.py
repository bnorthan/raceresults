# utilities specific to hmrrc grand prix
import pandas as pd

def get_hmrrc_scores():
    return [12,10,8,7,6,5,4,3,2,1] 

def get_cat_hmrrc_10():
    return ['a_open','b_30_39','c_40_49','d_50_59','e_60_69','f_70+']

def age_to_cat_hmrrc_10(age):
    if (0<age<30):
        return "a_open"
    if (30<=age<40):
        return "b_30_39"
    if (40<=age<50):
        return "c_40_49"
    if (50<=age<60):
        return "d_50_59"
    if (60<=age<70):
        return "e_60_69"
    if (age>=70):
        return "f_70+"

def score_by_category(race, gender, category, scores):
    temp=race[race.gender==gender]
    temp=temp[temp.category_10==category]
    temp=temp.reset_index(drop=True)
    scored=pd.DataFrame()
    scored['score']=scores
    scored['name']=temp.member_first_name+' '+temp.member_last_name
    return scored

def totals_by_category(race, gender, category):
    temp=race[race.gender==gender]
    temp=temp[temp.category_10==category]
    temp=temp.reset_index(drop=True)
    temp=temp[['gp_score','full_name']]
    temp=temp.groupby('full_name').sum()
    return temp.sort_values('gp_score',ascending=False).reset_index()

def place_to_gp_score(place):
    if place==1:
        return 12
    elif place==2:
        return 10
    elif place==3:
        return 8 
    elif place==4:
        return 7
    elif place==5:
        return 6
    elif place==6:
        return 5
    elif place==7:
        return 4
    elif place==8:
        return 3
    elif place==9:
        return 2
    elif place==10:
        return 1,
    else:
        return 0

def score_hmrrc_gp_race(racers, gender):
    categories = get_cat_hmrrc_10()
    scores = get_hmrrc_scores()

    gp = pd.DataFrame()

    for category in categories:
        print(category)
        temp=score_by_category(racers, gender, category, scores)
        gp=pd.concat([gp, temp], axis=1)

    return gp

def score_hmrrc_gp_totals(racers_totals, gender):
    categories = get_cat_hmrrc_10()
    scores = get_hmrrc_scores()

    gp = pd.DataFrame()

    for category in categories:
 
        temp=totals_by_category(racers_totals,gender,category).sort_values('gp_score',ascending=False)
        gp = pd.concat([gp, temp], axis=1)

    return gp