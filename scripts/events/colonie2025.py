"""Colonie 2025 txt -> csv, matching the Delmar 2025 csv schema.

Source lines look like:

    Devin Finn M 20 Albany 4:29.84
    Mary Ellen Moslander F 14 Rotterdam 6:59.33
    Jayden Thomas M 20 Bennington, VT 4:49.3

i.e. <name...> <sex> <age> <city..., ST?> <time>, already sorted by time and
with no place column.
"""

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "2025" / "Colonie" / "colonie.txt"
DST = ROOT / "data" / "2025" / "Colonie" / "colonie.csv"

COLUMNS = ["place", "age_place", "name", "age", "sex", "city", "state", "time", "pace"]

LINE = re.compile(
    r"^(?P<name>.+?)\s+(?P<sex>[MF])\s+(?P<age>\d{1,3})\s+"
    r"(?P<city>.+?)\s+(?P<time>\d{1,2}:\d{2}(?:\.\d+)?)$"
)


def parse(path):
    rows, skipped = [], []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            m = LINE.match(line)
            if not m:
                skipped.append((n, line))
                continue
            city = m.group("city")
            state = ""
            if "," in city:
                city, state = (p.strip() for p in city.rsplit(",", 1))
            rows.append(
                {
                    "place": len(rows) + 1,
                    "age_place": "",
                    "name": m.group("name"),
                    "age": m.group("age"),
                    "sex": m.group("sex"),
                    "city": city,
                    "state": state,
                    "time": m.group("time"),
                    "pace": "",
                }
            )
    return rows, skipped


if __name__ == "__main__":
    rows, skipped = parse(SRC)
    with open(DST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} results -> {DST}")
    for n, line in skipped:
        print(f"  skipped line {n}: {line!r}")
