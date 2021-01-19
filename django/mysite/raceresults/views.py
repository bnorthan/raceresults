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

def race(request, race_id):
    race=[]

    results=Race.objects.get(pk=race_id).result_set.all()

    return render(request, 'race/index.html', {'l_race':results})
