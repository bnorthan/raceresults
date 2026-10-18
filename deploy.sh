#!/usr/bin/env bash
# Update the live site on PythonAnywhere from GitHub.
#
# The sqlite db is gitignored on purpose -- it is derived data.  Everything the
# site shows is rebuilt here from data/Stockade-athon all time/csv/, so there is
# never a database to upload by hand.
#
# Normally started by scripts/updatepa on your own machine, which runs this as a
# PA scheduled task.  By hand, in a PythonAnywhere bash console:
#     workon raceresults
#     ~/raceresults/deploy.sh            # only what changed since the last deploy
#     FULL=1 ~/raceresults/deploy.sh     # rebuild the db no matter what
#
# The web app is reloaded with PA_API_TOKEN (Account -> API token), from the
# environment or ~/.pa_api_token; without it, click Reload on the Web tab.
# The last line is '== deployed <commit> ==' -- updatepa waits for it.
set -euo pipefail

REPO="${REPO:-$HOME/raceresults}"
PA_USER="${PA_USER:-bnorthan}"
PA_DOMAIN="${PA_DOMAIN:-${PA_USER}.pythonanywhere.com}"
PA_API_TOKEN="${PA_API_TOKEN:-$(cat "$HOME/.pa_api_token" 2>/dev/null || true)}"
STAMP="$HOME/.raceresults_deployed"     # last commit this script deployed

cd "$REPO"
echo "== $(date -u '+%Y-%m-%d %H:%M:%S') UTC =="

# without this file the site runs on the public dev key with DEBUG on
if [ ! -f django/mysite/mysite/local_settings.py ]; then
    echo "missing django/mysite/mysite/local_settings.py (production SECRET_KEY, DEBUG = False)"
    echo "see 'Production settings' in hints.md"
    exit 1
fi

echo "== pulling =="
git pull --ff-only
head=$(git rev-parse HEAD)
last=$(cat "$STAMP" 2>/dev/null || true)

if [ "$last" = "$head" ] && [ -z "${FULL:-}" ]; then
    echo "already deployed"
    echo "== deployed ${head:0:7} =="
    exit 0
fi

# the db is rebuilt only when something that feeds it changed; a first run, an
# unknown last commit or FULL=1 rebuilds everything
rebuild=
if [ -n "${FULL:-}" ] || [ -z "$last" ] || ! changed=$(git diff --name-only "$last" "$head" 2>/dev/null); then
    rebuild=1
elif grep -qE '^(data/Stockade-athon all time/csv/|scripts/makedjangotable\.py|scoreware/race/|django/mysite/raceresults/models\.py)' <<< "$changed"; then
    rebuild=1
fi

python -c "import scoreware" 2>/dev/null || { echo "== installing scoreware =="; pip install -e .; }

cd django/mysite
echo "== migrate =="
python manage.py migrate --noinput
if [ -n "$rebuild" ]; then
    echo "== rebuilding race tables from csv =="
    python ../../scripts/makedjangotable.py
else
    echo "== race tables unchanged, no rebuild =="
fi
echo "== collectstatic =="
python manage.py collectstatic --noinput

if [ -n "$PA_API_TOKEN" ]; then
    echo "== reloading ${PA_DOMAIN} =="
    curl -sSf -X POST -H "Authorization: Token ${PA_API_TOKEN}" \
        "https://www.pythonanywhere.com/api/v0/user/${PA_USER}/webapps/${PA_DOMAIN}/reload/" > /dev/null
else
    echo "no PA_API_TOKEN -- click Reload on the Web tab"
fi

echo "$head" > "$STAMP"
echo "== deployed ${head:0:7} =="
