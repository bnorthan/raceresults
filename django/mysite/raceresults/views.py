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
    category_10=tables.Column()
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
    
    results1=results.filter(category_10='c_40_49').filter(gender='F')
    results2=results.filter(category_10='c_40_49').filter(gender='M')
    results3=results.filter(category_10='d_50_59').filter(gender='M')
    results4=results.filter(category_10='d_50_59').filter(gender='F')

    # convert to simple race format
    results1=SimpleRace(results1)
    results2=SimpleRace(results2)
    results3=SimpleRace(results3)
    results4=SimpleRace(results4)
    
    # RequestConfig sets up the table
    RequestConfig(request).configure(results1)
    RequestConfig(request).configure(results2)
    RequestConfig(request).configure(results3)
    RequestConfig(request).configure(results4)

    # render the table
    return render(request, 'gp/index.html', {'l_race1':results1, 'l_race2':results2,'l_race3':results3, 'l_race4':results4})


# view all results for a runner in a table
def runner(request, runner_id):
    
    results=Runner.objects.get(pk=runner_id).result_set.all()
    
    results=SimpleRace(results)

    RequestConfig(request).configure(results)

    return render(request, 'runner/index.html', {'l_runner':results})
