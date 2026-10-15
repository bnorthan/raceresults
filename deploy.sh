#!/usr/bin/env bash
# Rebuild the live site on PythonAnywhere from the committed csv files.
#
# The sqlite db is gitignored on purpose -- it is derived data.  Everything the
# site shows is rebuilt here from data/Stockade-athon all time/csv/, so there is
# never a database to upload by hand.
#
# In a PythonAnywhere bash console:
#     workon raceresults
#     ~/raceresults/deploy.sh
#
# Set PA_API_TOKEN (Account -> API token) to have the web app reloaded for you;
# otherwise click Reload on the Web tab afterwards.
set -euo pipefail

REPO="${REPO:-$HOME/raceresults}"
PA_USER="${PA_USER:-bnorthan}"
PA_DOMAIN="${PA_DOMAIN:-${PA_USER}.pythonanywhere.com}"

cd "$REPO"
echo "== pulling =="
git pull --ff-only

# without this file the site runs on the public dev key with DEBUG on
if [ ! -f django/mysite/mysite/local_settings.py ]; then
    echo "missing django/mysite/mysite/local_settings.py (production SECRET_KEY, DEBUG = False)"
    echo "see 'Production settings' in hints.md"
    exit 1
fi

python -c "import scoreware" 2>/dev/null || { echo "== installing scoreware =="; pip install -e .; }

cd django/mysite
echo "== migrate =="
python manage.py migrate --noinput
echo "== rebuilding race tables from csv =="
python ../../scripts/makedjangotable.py
echo "== collectstatic =="
python manage.py collectstatic --noinput

if [ -n "${PA_API_TOKEN:-}" ]; then
    echo "== reloading ${PA_DOMAIN} =="
    curl -sS -X POST -H "Authorization: Token ${PA_API_TOKEN}" \
        "https://www.pythonanywhere.com/api/v0/user/${PA_USER}/webapps/${PA_DOMAIN}/reload/" \
        > /dev/null && echo "reloaded"
else
    echo
    echo "Done.  Click Reload on the Web tab to pick it up."
    echo "(export PA_API_TOKEN=... to have this script do the reload too)"
fi
