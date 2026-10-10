# raceresults

Utilities + a Django site for parsing, storing and displaying running race results
(HMRRC / Capital Region races, and ~50 years of Stockade-athon results).

## The pipeline

```
raw results (txt, fwf, csv, pdf-scrape)   data/<year>/... , data/Stockade-athon all time/txt/
        │  per-year parsing script (regex / fixed-width)
        ▼
normalized csv                            data/Stockade-athon all time/csv/<year>.csv
        │  makedjangotable.py  (Race + Result rows)
        ▼
sqlite db                                 django/mysite/db.sqlite3
        │  django views + django_tables2
        ▼
website                                   /raceresults/... (index, race, runner, search)
```

## Layout

| Path | What |
|---|---|
| `scoreware/` | installable package (`pip install -e .`) — the reusable library |
| `scoreware/race/header.py` | `RaceHeader.headers`: canonical column name → list of aliases |
| `scoreware/race/readers.py` | `parse_general(df, headers, id)` — maps a raw dataframe onto canonical columns |
| `scoreware/race/utils.py` | `time_to_seconds`, age categories, name helpers |
| `scoreware/match/`, `runner/` | fuzzy matching of race entrants to club members |
| `scripts/` | one-off / per-year driver scripts (not a package) |
| `scripts/events/Stockadeathonalltime.py` | txt → csv for every Stockade-athon year, one branch per format era |
| `scripts/makedjangotable.py` | csv → Django `Race`/`Result` rows |
| `django/mysite/` | the Django project; app is `raceresults` |
| `data/` | raw + parsed results, by year; `Stockade-athon all time/` holds the historical set |
| `_layouts/ _posts/ results/` | the older Jekyll github.io output (mostly superseded by Django) |

## Models (`django/mysite/raceresults/models.py`)

- `Race` — `race_name`, `slugified_race_name` (auto on save), city, `race_date`
- `Result` — first/last name, gender, city, `time` (DurationField), member flag,
  matched member name, `category_10` age category, points, FK → `Race`, nullable FK → `Runner`
- `Runner` — first/last name only; currently barely used (no results are linked to one)

## Design direction (decided 2026-08, not yet built)

The current schema fuses "a race" with "a set of results", and `Runner` is dead. Both
are expensive to change once more data lands on them, so fix them before building
features on top. Everything else (page layout, hosting, which forms exist) is cheap to
change later and should not be agonized over.

**Event vs Race.** A preview run, a group run, a real race and a virtual race are all
*events* — date, location, description, optional registration, optional results. Model
`Event` as the thing on the calendar, and treat a results set as one possible *outcome*
of an event. Registrations, volunteers and waivers then attach to `Event` naturally.
Give `Event` a `registration_url` from the start so linking out to Wild Apricot is a
first-class mode; internal registration later becomes a second mode on the same model
rather than a rewrite.

**Person identity.** A `Person` with one or more email addresses, that `Result` rows
link to. This is the hook every personal feature hangs off — runner history across 50
years, PRs, claiming a result, magic-link login, matching a signup to a club member.
Email is the join key because it is exact and it is what Wild Apricot exports; allow
several per person, since people sign up with a different address than the club has on
file.

**Boundary with Wild Apricot.** Wild Apricot stays the system of record for membership
and dues. This site *imports* from it (currently the periodic CSV export in
`data/<year>/Membership/`, which includes e-Mail; possibly the REST API later) and never
hand-edits member data, so there is exactly one truth. Signups live in Wild Apricot for
now — two signup places would split the headcount. This site's job is the part Wild
Apricot is not designed for: a preview page with course info alongside past winners,
course records and runner history drawn from the archive.

**Constraints to hold to.**
- Resist generality — no plugin system, no multi-tenancy, no configurable form builder.
  Being narrowly opinionated about *running* is where this site can add something that
  Wild Apricot's generality makes hard.
- No payments for now. That is well-covered ground and the least interesting part.
- Everything stays exportable to CSV. The database must never be the only copy.
- URLs are forever; keep existing race URLs working through any migration.

**On the long term.** Replacement is not the aim and not something to push for. Wild
Apricot handles membership, dues and official records well, and many people in the club
already know how to use it — that familiarity is real value, not an obstacle to work
around. The near-term posture is to complement it.

At the same time, don't design the door shut. If this site grows into something the club
wants to lean on more heavily, that should be a conclusion the club reaches on its own
because the running-specific parts turned out to be genuinely useful — pulled by demand
rather than pushed by a proposal. The gates on any such shift are organizational rather
than technical (dues, financial records, continuity if a volunteer steps away), and they
deserve respect. The choices above — Event as a first-class model, Person identity,
`registration_url`, CSV export — keep the option open at no extra cost today. That is the
point: none of this is a bet on replacement, it just isn't a bet against it.

## Running things

Locally, use the conda env `rundataenv` (`conda activate rundataenv`); the base
mambaforge `python` has no pandas/Django.

```bash
# library, editable
pip install -e .

# db + server
cd django/mysite
python manage.py migrate
python manage.py runserver          # http://localhost:8000/raceresults/

# txt -> csv for the historical Stockade set (edit the `years` range at the top)
python scripts/events/Stockadeathonalltime.py

# csv -> database (edit `alltime_years` near the bottom; deletes+reloads each race)
cd django/mysite && python ../../scripts/makedjangotable.py
```

`clean.sh` in `django/mysite` wipes the db to start over. See `hints.md` for
PythonAnywhere deployment notes (static files, virtualenvs).

## Current state (2026-10)

- DB holds 49 races / ~49k results: every Stockade-athon 1976–2025 except 2020
  (virtual race, no source data).
- csv exists for every year except 2020, all built by `Stockadeathonalltime.py` from
  `txt/` (2019 reads `data/2019/Stockade2019.csv` directly). Real race dates come from
  `csv/dates.csv`; 2022–2025 are inferred (2nd Sunday of November), not official.
- 1978 came from a spreadsheet-exported pdf (`pdf/`), converted with `pdftotext -layout`.
  Two gender typos are overridden by place in its branch of the script.
- `data/All Stockade results/` is an older duplicate of `data/Stockade-athon all time/`.

## Known rough edges

- **1993 is truncated** (123 of ~830 finishers). The method-2 time regex
  `(?:[1-2]:)?[0-5][0-9]:[0-5][0-9]` rejects times written as `64:41`. 1994–96 row
  counts are within ~10 of their source line counts, so they look unaffected.
- **Reloading a race changes its id**: `makedjangotable.py` deletes and re-creates the
  `Race`, so `/raceresults/race/<id>/` URLs break on every reload. This conflicts with
  "URLs are forever" and needs a stable key (`slugified_race_name` or year) before the site is linked to.
- Parsers fail silently — a line that doesn't match the time regex is skipped with no
  count. Always compare parsed row count against `wc -l` of the source.
- csv schemas differ by era (1976 has only name+time; 1982–96 add age/gender;
  1997+ add city/state/pace/div_place). Anything consuming them must tolerate missing columns.
- `readers.parse_general` prints heavily and has an `if/else` bug: the `full_name` branch
  falls through to the `else` for the `lf_name` case.
- Encodings vary (`utf-8` vs `cp1252`); some names contain mojibake (`O?Brien`).
- Strava client id/secret are hardcoded in `views.py`.

## Conventions

- Times are stored as `timedelta`; parse with `utils.time_to_seconds`.
- Gender is `'M'`, `'F'`, or `'u'` (unknown) — 1993–96 are all `u`.
- Canonical result columns: `place, first_name, last_name, gender, age, city, state,
  div_place, time, pace`. Add new source aliases to `RaceHeader.headers` rather than
  renaming columns in a script.
- Scripts hardcode absolute paths under `/home/bnorthan/runnin/raceresults/` — prefer
  paths relative to the repo root for anything new.
