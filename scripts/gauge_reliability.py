"""Grade the occupancy percentage Quebec publishes for each ER against the
headcount published beside it, on the same rows, hour by hour.

The Console des urgences shows two numbers per emergency room: a stretcher
occupancy percentage and a count of people currently in the department. Only
the percentage is quoted in coverage and only the percentage is what most
people read. This asks a narrow question of the archive: when the crowd in the
room really is bigger in hour A than in hour B, does the published percentage
say so?

Every pair of hours at one ER where the headcount differs is scored once.

  agree     the percentage is higher in the hour that really is busier
  disagree  the percentage is higher in the hour that is less busy
  blind     the percentage is identical in both hours, so it cannot separate
            them at all

Blind pairs are a consequence of resolution. An ER whose percentage is computed
over a handful of stretchers can only report a few distinct values, so a wide
range of real crowds collapses onto one number. The step column measures that
directly: the smallest gap between two distinct published values.

Writes data/gauge-reliability.csv.
"""
import csv, os
from itertools import combinations

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOURLY = os.path.join(HERE, "data", "er-hourly.csv")
OUT = os.path.join(HERE, "data", "gauge-reliability.csv")


def num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main():
    by_facility = {}
    meta = {}
    with open(HOURLY) as fh:
        for row in csv.DictReader(fh):
            occ, present = num(row["stretcher_occupancy_pct"]), num(row["present"])
            if occ is None or present is None:
                continue
            fid = row["facility_id"]
            meta[fid] = (row["facility_name"], row["region_name"])
            by_facility.setdefault(fid, []).append((occ, present))

    out = []
    for fid, points in by_facility.items():
        name, region = meta[fid]
        values = sorted({occ for occ, _ in points})
        gaps = [b - a for a, b in zip(values, values[1:]) if b - a > 1e-9]
        step = min(gaps) if gaps else None

        agree = disagree = blind = 0
        for (occ_a, present_a), (occ_b, present_b) in combinations(points, 2):
            if present_a == present_b:
                continue
            if occ_a == occ_b:
                blind += 1
            elif (occ_a > occ_b) == (present_a > present_b):
                agree += 1
            else:
                disagree += 1

        pairs = agree + disagree + blind
        if not pairs:
            continue
        crowds = [present for _, present in points]
        out.append({
            "facility_id": fid,
            "facility_name": name,
            "region_name": region,
            "hours": len(points),
            "distinct_published_values": len(values),
            "smallest_step_pct": round(step, 2) if step else "",
            "implied_stretchers": round(100 / step) if step else "",
            "people_min": int(min(crowds)),
            "people_max": int(max(crowds)),
            "hour_pairs_scored": pairs,
            "agree_pct": round(100 * agree / pairs, 1),
            "disagree_pct": round(100 * disagree / pairs, 1),
            "blind_pct": round(100 * blind / pairs, 1),
        })

    out.sort(key=lambda r: (-r["blind_pct"], -r["disagree_pct"]))
    with open(OUT, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        writer.writeheader()
        writer.writerows(out)
    print("%d emergency rooms scored -> %s" % (len(out), OUT))


if __name__ == "__main__":
    main()
