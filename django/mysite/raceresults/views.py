from scoreware.race import utils
from scoreware.strava import stravautil
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Race
from .models import Runner
from .models import Result

import django_tables2 as tables
from django_tables2 import RequestConfig
from django.utils.text import slugify
from django.db.models.functions import Lower

'''
# Create your views here.
def index(request):
    #return HttpResponse("Hello, world. You're at the race results index.")
    races=Race.objects.all()
    return render(request, 'raceresults/index.html', {'l_races':races})
'''
def index(request):
    race_names = Race.objects.order_by('race_name').values('race_name').distinct()
    return render(request, 'raceresults/new_index.html', {'race_names': race_names})

def races(request, race_name):
    l_races = Race.objects.filter(slugified_race_name=race_name)
    # skip the list page if there's only one match — go straight to results
    if l_races.count() == 1:
        return redirect('race', race_slug=l_races.first().slugified_race_name)
    context = {'l_races': l_races, 'race_name': race_name}
    return render(request, 'raceresults/races.html', context)
   
def runners(request):
    runners=Runner.objects.all()
    return render(request, 'runners/index.html', {'l_runners':runners})

class SimpleRace(tables.Table):
    class Meta:    
        #model=Result
        attrs={"class":"paleblue", "orderable":"True", "width":"100%"}
  
    first_name=tables.Column()
    last_name=tables.Column()
    #gender=tables.Column()
    #city=tables.Column()
    time=tables.Column()

class SimpleRaceWithYear(tables.Table):
    class Meta:    
        #model=Result
        attrs={"class":"paleblue", "orderable":"True", "width":"100%"}
  
    first_name=tables.Column()
    last_name=tables.Column()
    #gender=tables.Column()
    #city=tables.Column()
    time=tables.Column()
    race=tables.Column()

class DetailedRace(tables.Table):
    class Meta:    
        #model=Result
        attrs={"class":"paleblue", "orderable":"True", "width":"100%"}
  
    first_name=tables.Column()
    last_name=tables.Column()
    gender=tables.Column()
    city=tables.Column()
    time=tables.Column()
    member=tables.Column()
    member_first_name=tables.Column()
    member_last_name=tables.Column()
    category_10=tables.Column()
    points=tables.Column()
    race=tables.Column()

# old /race/<id>/ links -- ids aren't stable across db rebuilds, so a temporary
# (not permanent) redirect to the slug url
def race_by_id(request, race_id):
    race = get_object_or_404(Race, pk=race_id)
    return redirect('race', race_slug=race.slugified_race_name)

# view all results for a race in a table
def race(request, race_slug):

    race = get_object_or_404(Race, slugified_race_name=race_slug)

    # get all results for this race
    results = race.result_set.all()

    race_name=race.race_name + ' '+str(race.race_date)
    # convert to simple race format
    results=SimpleRace(results)
    
    # RequestConfig sets up the table
    RequestConfig(request).configure(results)

    # render the table
    return render(request, 'race/index.html', {'l_race':results,'l_name':race_name})

# view all results for a race in a table
def gp(request, race_id):

    # get all results for this race
    results=Race.objects.get(pk=race_id).result_set.all()

    age_cat=utils.get_cat_hmrrc_10();
    gender = ['F','M']

    results_list=[]

    for g in gender:
        for ac in age_cat:
            results_list.append(results.filter(category_10=ac).filter(gender=g))
    
    # convert to simple race format
    simple_list=[]
    for result in results_list:
        simple_list.append(SimpleRace(result))
    for result in simple_list:
        RequestConfig(request).configure(result)
    
    # render the table
    return render(request, 'gp/index.html', {'l_race':simple_list});

# view all results for a runner in a table
def runner(request, runner_id):
    
    results=Runner.objects.get(pk=runner_id).result_set.all()
    
    results=SimpleRace(results)

    RequestConfig(request).configure(results)

    return render(request, 'runner/index.html', {'l_runner':results})

def search(request):
    last=request.GET.get('last')
    print('LAST',last)
    results=Result.objects.filter(last_name__iexact=last)

    print(results)

    for r in results:
        race=Race.objects.filter(id=r.race_id)
        print(r.first_name, r.last_name, r.time, race[0].race_date)
 
    results=SimpleRaceWithYear(results)

    RequestConfig(request).configure(results)

    return render(request, 'runner/index.html', {'l_runner':results})

from django.views.generic import TemplateView

def strava(request):
    print()
    print('get code from url')
    code=request.GET.get('code')
    print('CODE',code)
    
    if code != None:
        try:
            token = stravautil.get_athlete_token('77193', '0809ff532abda7541d9b324d122c04003b449001', code)
            athlete = stravautil.get_athlete(token)
            f_name=athlete['firstname']
            l_name=athlete['lastname']
        except:
            f_name=None
            l_name=None
    else:
        f_name=None
        l_name=None
    print('hello',f_name,l_name)
    
    return render(request, 'strava/index.html', {'f_name':f_name, 'l_name':l_name})
    
class AboutView(TemplateView):
    template_name="about.html"

# -- Stockade-athon leaders: most finishes, active streaks ----------------------
import csv
from pathlib import Path
from django.conf import settings

# these csvs are written by scripts/events/stockade_leaders.py
LEADERS_DIR = Path(settings.BASE_DIR).parent.parent / 'data' / 'Stockade-athon all time'

def read_leaders(name):
    with open(LEADERS_DIR / name, newline='') as f:
        rows=list(csv.DictReader(f))
    for r in rows:
        for key in ('rank', 'races', 'streak', 'active'):
            r[key]=int(r[key]) if r.get(key) else None
    return rows

class MostRacesTable(tables.Table):
    class Meta:
        attrs={"class":"paleblue", "width":"100%"}

    rank=tables.Column(verbose_name='#')
    runner=tables.Column()
    races=tables.Column()
    streak=tables.Column(verbose_name='Longest streak')
    years=tables.Column(orderable=False)

class ActiveStreaksTable(tables.Table):
    class Meta:
        attrs={"class":"paleblue", "width":"100%"}

    rank=tables.Column(verbose_name='#')
    runner=tables.Column()
    active=tables.Column(verbose_name='Active streak')
    since=tables.Column()
    races=tables.Column(verbose_name='Total races')

class LongestStreaksTable(tables.Table):
    class Meta:
        attrs={"class":"paleblue", "width":"100%"}

    rank=tables.Column(verbose_name='#')
    runner=tables.Column()
    streak=tables.Column(verbose_name='Longest streak')
    streak_years=tables.Column(verbose_name='Years')
    races=tables.Column(verbose_name='Total races')

def stockade_leaders(request, tab, table, heading, intro):
    RequestConfig(request, paginate=False).configure(table)
    return render(request, 'raceresults/stockade_leaders.html',
                  {'tab':tab, 'table':table, 'heading':heading, 'intro':intro})

def most_races(request):
    return stockade_leaders(request, 'most', MostRacesTable(read_leaders('most_races.csv')),
        'Most finishes, 1976\u20132025',
        'Everyone with 10 or more Stockade-athon finishes since 1976, matched across the '
        'years by name and age. Streaks skip 2020, which was a virtual race with no results.')

def longest_streaks(request):
    return stockade_leaders(request, 'longest', LongestStreaksTable(read_leaders('longest_streaks.csv')),
        'Longest streaks',
        'The longest run of consecutive Stockade-athons each runner has finished, '
        'whenever it happened. 2020 was a virtual race with no results, so it doesn\'t break a streak.')

def records(request):
    lists = {}
    for r in read_leaders('records.csv'):
        lists.setdefault(r['list'], []).append(r)
    groups = [name[len('Men '):] for name in lists if name.startswith('Men ')]
    return render(request, 'raceresults/stockade_leaders.html', {
        'tab': 'records',
        'heading': 'Course records',
        'intro': 'The fastest Stockade-athon 15K times since 1976, one line per runner at their best. '
                 'An age marked ~ is estimated from the runner\'s other years. Age grades use the 2025 '
                 'road standards (Alan Jones, USATF Masters Long Distance Running); the age-graded list '
                 'uses recorded ages only.',
        'overall': [('Men', lists.get('Men', [])), ('Women', lists.get('Women', []))],
        'age_groups': [(g, lists.get('Men ' + g, []), lists.get('Women ' + g, [])) for g in groups],
        'graded': lists.get('Age graded', []),
    })

def active_streaks(request):
    return stockade_leaders(request, 'active', ActiveStreaksTable(read_leaders('active_streaks.csv')),
        'Active streaks',
        'Runners who have finished every Stockade-athon since the year shown, up to the most '
        'recent race. 2020 was a virtual race with no results, so it doesn\'t break a streak.')
