# Hints

## Deleting the database and starting over

In development you may want to totally delete the database, see [this script](https://github.com/bnorthan/raceresults/blob/main/django/mysite/clean.sh).

## Environments on pythonanywhere

Pythonanywhere is a great way to test publically.  However after following the initial tutorial (which leads you through creating a Django environment), the next time you login, you need to re-activate the environment.  

Use: ```lsvirtualenv``` to get a list of virtual environments

then ```workon myvirtualenv``` to switch to the environment

## Static (css, images, etc) Files on Pythonanywhere

On your own PC static files will be served by the django dev server. In a production setting like PythonAnywhere, you need to

set the STATIC_ROOT in your settings.py, to, eg, /home/yourusername/myproject/static
run manage.py collectstatic which will collect static files from your app folders and put them in there
set up a static files mapping on the web tab, from /static/ to /home/yourusername/myproject/static

## Some useful regex to scan for times and gender

There are some examples in the [Stockadeathonalltime.py script](https://github.com/bnorthan/raceresults/blob/main/scripts/events/Stockadeathonalltime.py).  If converting another large set of historical data may want to refactor that script into some utilities. 
