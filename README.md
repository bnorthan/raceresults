# raceresults
This repo contains some utilities to read running race results and render on a github.io site or Django

For the last few years I've scored the HMRRC Grand Prix and (since Covid started) compiled results for HMRRC virtual races.  I've hacked together a lot of scripts for parsing running data (parsing times, age grading, matching club members with runners in races, reading race results in different formats, etc.).  In 2021 I plan to move those utilities to this repository.  

To start with (January 2021) I've added a simple CSV reader and code to render the csv to a github.io page and a Django table.   More to come over the next few weeks and months. 

[See the hints page](https://github.com/bnorthan/raceresults/blob/main/hints.md) for a list of tricks and hints that may be helpful if you are not a seasoned Django and/or web developer.

# Github.io

[The makemarkdown script](https://github.com/bnorthan/raceresults/blob/main/src/scripts/makemarkdown.py) reads a csv and outputs it as markdown.  The markdown is then [rendered here](https://bnorthan.github.io/raceresults/results/2020/VirtualStockade).

# Django

[The makedjangotable Python script](https://github.com/bnorthan/raceresults/blob/main/src/scripts/makedjangotable.py) reads a csv and converts each line of results to a Django model and saves it to a database.  It can then be rendered as a Django table.  

[This Django site](https://github.com/bnorthan/raceresults/tree/main/django/mysite) was created by following [this tutorial](https://docs.djangoproject.com/en/3.1/intro/tutorial01/) 

[The raceresults plugin](https://github.com/bnorthan/raceresults/tree/main/django/mysite/raceresults) has a simple model and view for races and results. 

To create the Django site locally 

Go to the 'mysite' [directory](https://github.com/bnorthan/raceresults/tree/main/django/mysite).  
Run 'python manage.py migrate' (this should create the sqlite database)  
Run 'python manage.py shell' This will open a python shell where you can interact with the database  
Run [the makedjangotable script](https://github.com/bnorthan/raceresults/blob/main/src/scripts/makedjangotable.py) this will add a race and results for the race to the database.  
Run 'python manage.py runserver' and you should be able to see the results at http://localhost:8000/raceresults/race/1/.  

## How the Django plugin works  

If you are not familiar with Django take a look at a [Django tutorial](https://docs.djangoproject.com/en/3.1/intro/tutorial01/)

The Django plugin raceresults is made of models, views, urls and html templates.  See...

[Models](https://github.com/bnorthan/raceresults/blob/main/django/mysite/raceresults/models.py)  
[Views](https://github.com/bnorthan/raceresults/blob/main/django/mysite/raceresults/views.py)  
[urls](https://github.com/bnorthan/raceresults/blob/main/django/mysite/raceresults/urls.py)  
[html templates](https://github.com/bnorthan/raceresults/tree/main/django/mysite/raceresults/templates)

