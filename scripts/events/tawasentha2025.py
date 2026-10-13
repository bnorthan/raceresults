"""Tawasentha 2025 txt -> csv, matching the Colonie/Delmar 2025 csv schema.

Source lines (copied out of a pdf) look like:

    1 Noah Valvo 18:16:00 M 27 Delanson

i.e. <place> <name...> <time> <sex> <age> <city..., ST?>, where the time is
really mm:ss with a spurious ":00" appended.

The pdf copy comes apart from place ~51 on: the places arrive first as a run of
bare numbers, then the rows they belong to arrive with no place at all.  Bare
numbers are queued and handed to the placeless rows in order.
"""

import csv
import re
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "2025" / "Tawasentha" / "tawasentha.txt"
DST = ROOT / "data" / "2025" / "Tawasentha" / "tawasentha.csv"

COLUMNS = ["place", "age_place", "name", "age", "sex", "city", "state", "time", "pace"]

PLACE_ONLY = re.compile(r"^(\d{1,4})$")
LINE = re.compile(
    r"^(?:(?P<place>\d{1,4})\s+)?(?P<name>\D.*?)\s+"
    r"(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\s+"
    r"(?P<sex>[MF])\s+(?P<age>\d{1,3})\s+(?P<city>.+)$"
)


def clean_time(t):
    """18:16:00 -> 18:16 (the pdf appends a :00 to every mm:ss time)."""
    parts = t.split(":")
    if len(parts) == 3 and parts[2] == "00" and int(parts[0]) < 60:
        return ":".join(parts[:2])
    return t


def parse(path):
    rows, skipped, orphan_places = [], [], deque()
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.lower().startswith("place "):
                continue
            bare = PLACE_ONLY.match(line)
            if bare:
                orphan_places.append(bare.group(1))
                continue
            m = LINE.match(line)
            if not m:
                skipped.append((n, line))
                continue
            place = m.group("place")
            if place is None:
                place = orphan_places.popleft() if orphan_places else ""
            city, state = m.group("city"), ""
            if "," in city:
                city, state = (p.strip() for p in city.rsplit(",", 1))
            rows.append(
                {
                    "place": place,
                    "age_place": "",
                    "name": m.group("name"),
                    "age": m.group("age"),
                    "sex": m.group("sex"),
                    "city": city,
                    "state": state,
                    "time": clean_time(m.group("time")),
                    "pace": "",
                }
            )
    return rows, skipped, list(orphan_places)


if __name__ == "__main__":
    rows, skipped, leftover = parse(SRC)
    rows.sort(key=lambda r: int(r["place"]) if r["place"] else 10**6)
    with open(DST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} results -> {DST}")
    places = [int(r["place"]) for r in rows if r["place"]]
    if places and places != list(range(1, len(rows) + 1)):
        print(f"  WARNING: places are not 1..{len(rows)}: {sorted(set(range(1, max(places) + 1)) - set(places))} missing")
    if leftover:
        print(f"  WARNING: {len(leftover)} unused place numbers: {leftover}")
    for n, line in skipped:
        print(f"  skipped line {n}: {line!r}")
