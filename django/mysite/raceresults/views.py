from scoreware.race import utils
from scoreware.strava import stravautil
from django.shortcuts import render, redirect
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
        return redirect('race', race_id=l_races.first().id)
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

# view all results for a race in a table
def race(request, race_id):

    # get all results for this race
    results=Race.objects.get(pk=race_id).result_set.all()
    
    race=Race.objects.filter(pk=race_id)

    race_name=race[0].race_name + ' '+str(race[0].race_date)
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