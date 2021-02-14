from django.shortcuts import render
from django.http import HttpResponse
from .models import Race

import django_tables2 as tables
from django_tables2 import RequestConfig

# Create your views here.
def index(request):
    #return HttpResponse("Hello, world. You're at the race results index.")
    races=Race.objects.all()
    return render(request, 'raceresults/index.html', {'l_races':races})

class SimpleRace(tables.Table):
    class Meta:    
        #model=Result
        attrs={"class":"paleblue", "orderable":"True", "width":"100%"}
  
    first_name=tables.Column()
    last_name=tables.Column()
    city=tables.Column()
    time=tables.Column()
    race=tables.Column()

def race(request, race_id):
    
    results=Race.objects.get(pk=race_id).result_set.all()
    
    results=SimpleRace(results)
    
    RequestConfig(request).configure(results)

    return render(request, 'race/index.html', {'l_race':results})
