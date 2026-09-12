"""Write data/nearest-alternatives.csv: the 5 nearest other emergency rooms
to each of the 120 departments, by great-circle distance from the addresses
in facilities.csv, with how often each one actually publishes a number.

MSSS publishes no geography with the occupancy feed, so "where else can I go"
cannot be answered from the ministry's own files.
"""
import csv, math, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(HERE, "data", "facilities.csv")
C = os.path.join(HERE, "data", "coverage-by-er.csv")
OUT = os.path.join(HERE, "data", "nearest-alternatives.csv")

def km(a, b):
    R = 6371.0088
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(h))

fac = [r for r in csv.DictReader(open(F, encoding="utf-8")) if r["lat"] and r["lng"]]
for r in fac:
    r["pt"] = (float(r["lat"]), float(r["lng"]))
cov = {r["facility_id"]: r for r in csv.DictReader(open(C, encoding="utf-8"))}

rows = []
for a in fac:
    others = sorted(((km(a["pt"], b["pt"]), b) for b in fac if b["id"] != a["id"]),
                    key=lambda t: t[0])[:5]
    for rank, (d, b) in enumerate(others, 1):
        cb = cov.get(b["id"], {})
        rows.append({
            "facility_id": a["id"], "facility_name": a["name"], "region_name": a["region_name"],
            "rank": rank, "alt_facility_id": b["id"], "alt_facility_name": b["name"],
            "alt_region_name": b["region_name"], "distance_km": round(d, 1),
            "crosses_region": "yes" if b["region_code"] != a["region_code"] else "no",
            "alt_coverage_pct": cb.get("coverage_pct", ""),
            "alt_hours_with_occupancy_pct": cb.get("hours_with_occupancy_pct", ""),
        })

with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(len(rows), "rows,", len(fac), "departments with coordinates")

dark = [r for r in rows if r["alt_hours_with_occupancy_pct"] in ("0", "")]
print("neighbour entries that never publish an occupancy number:", len(dark))
allfive = {}
for r in rows:
    allfive.setdefault(r["facility_name"], []).append(r["alt_hours_with_occupancy_pct"])
print("departments whose 5 nearest alternatives ALL never publish:",
      sum(1 for k, v in allfive.items() if all(x in ("0", "") for x in v)))
