"""Which Quebec emergency departments never dropped below 100% stretcher occupancy?

Reads data/er-hourly.csv and prints, for every facility with at least 100 hourly
readings in the file, the minimum, median and maximum occupancy it recorded.
A facility whose minimum is at or above 100 was never once below capacity in the
window - including overnight and on the weekend.

    python3 analysis/never_below_100.py

Standard library only.
"""
import csv
import os
import statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, os.pardir, "data", "er-hourly.csv")
MIN_READINGS = 100


def number(value):
    try:
        return float(value)
    except ValueError:
        return None


def main():
    with open(CSV, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    hours = sorted({row["ts_local"] for row in rows})
    readings = defaultdict(list)
    for row in rows:
        occupancy = number(row["stretcher_occupancy_pct"])
        if occupancy is not None:
            readings[(row["facility_name"], row["region_name"])].append(occupancy)

    kept = {k: v for k, v in readings.items() if len(v) >= MIN_READINGS}
    never_below = sorted(
        (k + (len(v), min(v), statistics.median(v), max(v)) for k, v in kept.items() if min(v) >= 100),
        key=lambda r: -r[4],
    )
    never_above = sorted(
        (k + (len(v), min(v), statistics.median(v), max(v)) for k, v in kept.items() if max(v) < 100),
        key=lambda r: r[4],
    )

    print(f"{len(hours)} hourly readings, {hours[0]} to {hours[-1]} (America/Montreal)")
    print(f"{len(kept)} facilities reported at least {MIN_READINGS} times\n")

    print(f"Never below 100% ({len(never_below)}):")
    for name, region, n, lo, mid, hi in never_below:
        print(f"  {mid:6.1f} median  {lo:5.0f} lowest  {hi:5.0f} highest  n={n:3d}  {name} ({region})")

    print(f"\nNever above 100% ({len(never_above)}):")
    for name, region, n, lo, mid, hi in never_above:
        print(f"  {mid:6.1f} median  {hi:5.0f} highest  n={n:3d}  {name} ({region})")


if __name__ == "__main__":
    main()
