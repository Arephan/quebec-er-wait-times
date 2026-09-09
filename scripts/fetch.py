#!/usr/bin/env python3
"""Append the last 7 days of hourly ER occupancy to data/er-hourly.csv.

Reads the public JSON mirror at sante.handled.tools, which republishes the
MSSS "Console des urgences" open-data feed. No key, no account.
Existing (timestamp, facility) pairs are kept, so re-running is safe.
"""
import csv, json, os, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = "https://sante.handled.tools"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOURLY = os.path.join(HERE, "data", "er-hourly.csv")
FACILITIES = os.path.join(HERE, "data", "facilities.csv")
COLUMNS = ["ts_local", "facility_id", "facility_name", "region_code", "region_name",
           "slug", "stretcher_occupancy_pct", "waiting", "present"]


def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "quebec-er-wait-times/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=40).read().decode())


def main():
    facilities = get("/api/facilities")["rows"]

    with open(FACILITIES, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "name", "establishment", "region_code", "region_name",
                         "address", "lat", "lng", "slug"])
        for f in facilities:
            writer.writerow([f["id"], f["name"], f["establishment"], f["region_code"],
                             f["region_name"], f["address"], f["lat"], f["lng"], f["slug"]])

    rows = {}
    if os.path.exists(HOURLY):
        with open(HOURLY) as fh:
            for row in csv.DictReader(fh):
                rows[(row["ts_local"], row["facility_id"])] = [row[c] for c in COLUMNS]

    def history(f):
        try:
            return f, get("/api/facility/%s/history" % f["id"])["rows"]
        except Exception:
            return f, []

    with ThreadPoolExecutor(8) as pool:
        for f, points in pool.map(history, facilities):
            for p in points:
                ts = p.get("ts") or ""
                if len(ts) != 16:  # the upstream feed emits a truncated timestamp now and then
                    continue
                rows[(ts, f["id"])] = [ts, f["id"], f["name"], f["region_code"],
                                       f["region_name"], f["slug"],
                                       p.get("occ_pct"), p.get("waiting"), p.get("present")]

    with open(HOURLY, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(COLUMNS)
        writer.writerows(sorted(rows.values(), key=lambda r: (r[0], r[1])))
    print("%d hourly rows, %d facilities" % (len(rows), len(facilities)))


if __name__ == "__main__":
    main()
