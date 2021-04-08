# Hints

## Deleting the database and starting over

In development you may want to totally delete the database, see [this script](https://github.com/bnorthan/raceresults/blob/main/django/mysite/clean.sh).

## Environments on pythonanywhere

Pythonanywhere is a great way to test pulbically.  However after following the initial tutorial (which leads you through creating a Django environment), the next time you login, you need to re-activate the environment.  

Use: ```lsvirtualenv``` to get a list of virtual environments

then ```workon myvirtualenv``` to switch to the environment