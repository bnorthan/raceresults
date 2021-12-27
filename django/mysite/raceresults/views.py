from scoreware.race import utils
from django.shortcuts import render
from django.http import HttpResponse
from .models import Race
from .models import Runner

import django_tables2 as tables
from django_tables2 import RequestConfig

# Create your views here.
def index(request):
    #return HttpResponse("Hello, world. You're at the race results index.")
    races=Race.objects.all()
    return render(request, 'raceresults/index.html', {'l_races':races})

def runners(request):
    runners=Runner.objects.all()
    return render(request, 'runners/index.html', {'l_runners':runners})

class SimpleRace(tables.Table):
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
    
    # convert to simple race format
    results=SimpleRace(results)
    
    # RequestConfig sets up the table
    RequestConfig(request).configure(results)

    # render the table
    return render(request, 'race/index.html', {'l_race':results})

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

from django.views.generic import TemplateView

class AboutView(TemplateView):
    template_name="about.html"