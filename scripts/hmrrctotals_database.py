import pandas as pd
from scoreware.race import utils
from scoreware.race import hmrrc_gp_util

# import importlib so we can reload during development
from importlib import reload
# reload hmrrc_gp_util
reload(hmrrc_gp_util)

from raceresults.models import Race
from raceresults.models import Result

out_dir='../data/2021/Totals/'

race_ids = [14,15]
race_out_base = 'LaborDay5k'

racers_total = pd.DataFrame()

for race_id in race_ids:
    race =Race.objects.get(pk=race_id)
    results=race.result_set.all()

    racers=pd.DataFrame(list(results.values()))
    racers=racers[racers.member=='yes']
    racers["place"]=racers.index
    racers["div_place"]=racers.groupby(["gender","category_10"])["place"].rank("dense", ascending=True)
    racers['gp_score']  = racers.div_place.apply(lambda x: hmrrc_gp_util.place_to_gp_score(x))

    females = hmrrc_gp_util.score_hmrrc_gp(racers, 'F')
    males = hmrrc_gp_util.score_hmrrc_gp(racers, 'M')
    
    females.to_csv(out_dir+race.race_name+'_females.csv')
    males.to_csv(out_dir+race.race_name+'_males.csv')

    racers_total=racers_total.append(racers)

racers_total['full_name']=racers_total.member_first_name+' '+racers_total.member_last_name
racers_total=racers_total[['full_name','gender','category_10','gp_score']]

females_totals = hmrrc_gp_util.score_hmrrc_gp_totals(racers_total, 'F')
females_totals.to_csv(out_dir+'gp_females_totals.csv')

males_totals = hmrrc_gp_util.score_hmrrc_gp_totals(racers_total, 'M')
males_totals.to_csv(out_dir+'gp_males_totals.csv')

