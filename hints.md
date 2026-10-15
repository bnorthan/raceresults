# Hints

## Deleting the database and starting over

In development you may want to totally delete the database, see [this script](https://github.com/bnorthan/raceresults/blob/main/django/mysite/clean.sh).

## Deploying to PythonAnywhere from scratch

Checklist, done 2026-08-14 for `bnorthan.pythonanywhere.com`.  Substitute your own
username for `bnorthan` throughout.

1. **Push everything first.**  PythonAnywhere pulls from GitHub, so anything sitting
   uncommitted locally will not be there.

2. **Bash console** (Consoles tab -> Bash):

   ```bash
   git clone https://github.com/bnorthan/raceresults.git
   mkvirtualenv --python=/usr/bin/python3 raceresults
   cd ~/raceresults
   pip install -r requirements.txt
   pip install -e .                 # installs scoreware; see the sys.path note below
   python django/mysite/manage.py collectstatic --noinput
   ```

   Every new console needs `workon raceresults` again — without it `pip` installs into
   the system site-packages, which the web app never looks at.

3. **Web tab -> Add a new web app** -> accept the domain -> pick **Manual configuration**
   (*not* "Django"; the Django option scaffolds a fresh project and ignores the repo)
   -> Python 3.10.

4. Fill in the fields on that page:

   | Field | Value |
   |---|---|
   | Source code | `/home/bnorthan/raceresults/django/mysite` |
   | Working directory | `/home/bnorthan/raceresults/django/mysite` |
   | Virtualenv | `/home/bnorthan/.virtualenvs/raceresults` |
   | Static files: URL | `/static/` |
   | Static files: Directory | `/home/bnorthan/raceresults/django/mysite/static` |

5. Click the **WSGI configuration file** link in the Code section and replace the whole
   file (it ships as a wall of commented-out framework templates) with:

   ```python
   import os
   import sys

   for p in ['/home/bnorthan/raceresults/django/mysite', '/home/bnorthan/raceresults']:
       if p not in sys.path:
           sys.path.insert(0, p)

   os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

   The repo root is on the path as well as `django/mysite`, because `views.py` does
   `from scoreware.race import utils`.  If `pip install -e .` succeeded that second entry
   is redundant, but it costs nothing and it is what fixes
   `ModuleNotFoundError: No module named 'scoreware'` when the editable install did not
   take (`python-Levenshtein` in `setup.py` needs a compiler and can fail).

6. **Upload the database.**  `db.sqlite3` is gitignored, so the clone does not include it
   and the site comes up with zero races.  Files tab ->
   `https://www.pythonanywhere.com/user/bnorthan/files/home/bnorthan/raceresults/django/mysite`
   -> Upload a file -> pick the local `django/mysite/db.sqlite3` (~3.6 MB).  There is no
   terminal-to-terminal copy on a free account; the browser upload is the way (paid
   accounts get ssh/scp).

7. Hit the green **Reload** button at the top of the Web tab.  Nothing on disk takes
   effect until you do — the app is held in memory.  Then load
   `https://bnorthan.pythonanywhere.com/raceresults/`.

**When it breaks**: Web tab -> Log files -> error log, read the bottom.  `DEBUG = True`
and `ALLOWED_HOSTS = ['*']` are already set in `settings.py`, which is fine for a test
deploy but should change before this is anything but a test deploy.

**Pasting into the PA console**: if pasted text arrives with a leading `200~`, that is
bracketed paste.  Run `bind 'set enable-bracketed-paste on'` in the console (and put it
in `~/.bashrc`), or paste one line at a time.

## Updating the live site (no database upload)

Step 6 of the checklist above -- uploading `db.sqlite3` through the Files tab -- is only
needed the *first* time, and strictly speaking not even then.  The database is derived
data: every race on the site is rebuilt from `data/Stockade-athon all time/csv/` by
`scripts/makedjangotable.py`, which deletes and reloads each race by name.  So to publish
new or corrected results, commit the csv and rebuild on the server:

```bash
# locally
python scripts/events/Stockadeathonalltime.py     # txt -> csv  (years list at the top)
git add "data/Stockade-athon all time" && git commit && git push

# in a PythonAnywhere bash console
workon raceresults
~/raceresults/deploy.sh
```

`deploy.sh` pulls, migrates, rebuilds the race tables from csv, runs collectstatic, and
reloads the web app if `PA_API_TOKEN` is set (Account -> API token); without the token it
tells you to click Reload on the Web tab.

Race pages live at slug URLs (`/raceresults/race/2025-stockade-athon/`). The slug is set
once from the race name and never recomputed, and the rebuild reuses each `Race` row, so
both the slug and the id survive a rebuild. Old `/raceresults/race/<id>/` links redirect
to the slug URL.

Keeping the db out of git is deliberate: it is a 4.5 MB binary that would grow the repo
on every results update, and it would become a second source of truth alongside the csv.

## Production settings (one-time, on PythonAnywhere)

The `SECRET_KEY` in `settings.py` is public (it is in git history) and `DEBUG` is on, which
is fine locally only. On the server, a gitignored `mysite/local_settings.py` overrides
both; `deploy.sh` refuses to run without it. Create it once, in a PA bash console, so the
key is generated there and never leaves the server:

```bash
workon raceresults
cd ~/raceresults/django/mysite/mysite
python -c "from django.core.management.utils import get_random_secret_key as k; print(f'SECRET_KEY = {k()!r}\nDEBUG = False\nALLOWED_HOSTS = [\"bnorthan.pythonanywhere.com\"]')" > local_settings.py
```

Then Reload on the Web tab. With `DEBUG = False`, Django stops serving css itself, so the
`/static/` mapping on the Web tab (below) must be in place. Errors now go to the error log
instead of the browser. Changing the key logs you out of `/admin`; nothing else is affected.

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
