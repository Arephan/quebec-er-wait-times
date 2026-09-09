"""How far apart are two emergency departments in the same region, in the same hours?

Reads data/er-hourly.csv and, for every health region, compares the emergency
departments inside it: the median stretcher occupancy each one recorded, the
gap between the busiest and the emptiest, and how often the busiest was over
100% while the emptiest was under it in the very same hour.

Only facilities with at least 100 hourly readings in the window are counted, so
a hospital that reported twice cannot look like a region-wide pattern. Regions
with fewer than two such facilities are skipped.

    python3 analysis/within_region_gap.py

Standard library only.
"""

import csv
import os
import statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(os.path.dirname(HERE), "data", "er-hourly.csv")
MIN_READINGS = 100


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main():
    by_facility = defaultdict(list)
    by_hour = defaultdict(dict)
    region_of = {}
    name_of = {}

    with open(CSV, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            occupancy = number(row["stretcher_occupancy_pct"])
            if occupancy is None:
                continue
            fid = row["facility_id"]
            by_facility[fid].append(occupancy)
            by_hour[row["ts_local"]][fid] = occupancy
            region_of[fid] = (row["region_code"], row["region_name"])
            name_of[fid] = row["facility_name"]

    counted = {f: v for f, v in by_facility.items() if len(v) >= MIN_READINGS}

    regions = defaultdict(list)
    for fid, values in counted.items():
        regions[region_of[fid]].append(fid)

    rows = []
    for region, fids in regions.items():
        if len(fids) < 2:
            continue
        medians = {f: statistics.median(counted[f]) for f in fids}
        busiest = max(medians, key=medians.get)
        emptiest = min(medians, key=medians.get)
        split = 0
        shared = 0
        for hour, readings in by_hour.items():
            if busiest in readings and emptiest in readings:
                shared += 1
                if readings[busiest] >= 100 > readings[emptiest]:
                    split += 1
        rows.append(
            {
                "region": region[1],
                "facilities": len(fids),
                "busiest": name_of[busiest],
                "busiest_median": medians[busiest],
                "emptiest": name_of[emptiest],
                "emptiest_median": medians[emptiest],
                "gap": medians[busiest] - medians[emptiest],
                "shared_hours": shared,
                "split_hours": split,
            }
        )

    rows.sort(key=lambda r: r["gap"], reverse=True)

    print(f"{len(rows)} regions with at least two continuously reporting emergency departments")
    print(f"readings per facility: at least {MIN_READINGS}\n")
    header = f"{'region':34} {'EDs':>3} {'gap':>7}  {'busiest (median)':44} {'emptiest (median)':44} {'split hours':>11}"
    print(header)
    print("-" * len(header))
    for r in rows:
        busy = f"{r['busiest'][:34]} ({r['busiest_median']:.0f}%)"
        empty = f"{r['emptiest'][:34]} ({r['emptiest_median']:.0f}%)"
        share = f"{r['split_hours']}/{r['shared_hours']}"
        print(f"{r['region'][:34]:34} {r['facilities']:>3} {r['gap']:>6.0f}p  {busy:44} {empty:44} {share:>11}")


if __name__ == "__main__":
    main()
