# Quebec ER wait times — hourly archive

Hourly emergency-room occupancy for all 120 acute-care emergency departments in Quebec, going back to 2026-09-02, plus a derived stretcher count for 98 of them and average length of stay for 108 of them.

Quebec's Ministère de la Santé et des Services sociaux (MSSS) publishes ER occupancy as open data, refreshed once an hour. That feed only carries the current hour — once it refreshes, the previous reading is not available from it anymore. This repo stores the readings as they come in.

## Files

| File | Rows | Contents |
|---|---|---|
| [`data/er-hourly.csv`](data/er-hourly.csv) | 27,355 | one row per facility per hour |
| [`data/facilities.csv`](data/facilities.csv) | 120 | name, establishment, region, street address, lat/lng |
| [`data/stretcher-capacity.csv`](data/stretcher-capacity.csv) | 98 | stretcher count behind each department's published percentage, derived |
| [`data/length-of-stay.csv`](data/length-of-stay.csv) | 120 | average length of stay per department, stretcher and non-stretcher, hours |

`er-hourly.csv` covers 2026-09-02 06:00 to 2026-09-11 08:00, local Quebec time (America/Montreal).

```
ts_local, facility_id, facility_name, region_code, region_name, slug,
stretcher_occupancy_pct, waiting, present
```

`stretcher_occupancy_pct` is occupied stretchers over the department's funded stretcher count. Values above 100 are normal and are what Quebec ER reporting tracks. `waiting` is people waiting to be seen; `present` is people in the department.

About 11% of rows have an empty `stretcher_occupancy_pct`. The MSSS feed does not report every facility every hour, and I did not fill anything in.

## Two things visible in the current window

Median occupancy province-wide by hour of day:

| Hour | 00 | 03 | 06 | 09 | 12 | 13 | 15 | 18 | 21 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|
| Median | 80 | 82 | 88 | 89 | 90 | 92 | 89 | 83 | 83 | 79 |

Pooled across the week that is a 13-point spread, highest at 1 p.m. and lowest at 11 p.m. Individual days don't repeat it — the daily peak hour comes out at 12, 05, 15, 12, 09, 19 and 04 over the seven days in the file, so treat the curve as a weekly average.

36.7% of readings are above 100% occupancy. Highest medians in the window: Royal Victoria 206, Jewish General 200, Lakeshore General 188.5, Sept-Îles 180, Montreal General 168.

Seven days is not enough to say anything seasonal. The numbers above are here mainly so you can verify the file parses and matches.

## The stretcher count behind the percentage

MSSS publishes the occupancy percentage and not the denominator, so the same number means
a different thing at each department. `stretcher-capacity.csv` recovers the denominator from
the published values themselves.

The percentage can only land on multiples of 100/N, where N is the funded stretcher count.
La Sarre's readings are 20, 40, 60, 80, 100, 120, 140 and nothing in between — a step of 20
points, so N = 5. Amos steps by 14.29 points, so N = 7. Over 163 hours of readings the
step size is stable enough to read off 98 of the 120 departments; the other 22 either never
publish or never move enough to show a step.

This matters when you compare two departments. A one-person change moves La Sarre's published
number by 20 points and Amos's by 14. If you sort a list of departments by the percentage, a
five-stretcher room with six people in it outranks a fifty-stretcher room with fifty-five.

The method was put to Santé Québec's Laurentides region in September 2026 and its
communications office confirmed in writing that the published rate is occupied stretchers over
funded stretchers, and that a single arrival moves a small department's rate much further than
a large one's. `hours_observed` and `distinct_values_published` are in the file so the read is
checkable per department: few distinct values means a coarse gauge and a weak inference.

## Updating it

```
python3 scripts/fetch.py
```

Standard library only. It pulls the last ten days and merges on `(ts_local, facility_id)`, so re-running extends the archive rather than duplicating rows. Run it weekly or more often and there is no gap.

The JSON mirror it reads is public, with no key or account:

```
GET https://sante.handled.tools/api/facilities
GET https://sante.handled.tools/api/facility/<id>/history
GET https://sante.handled.tools/api/now
```

## Source and licence

The data comes from the MSSS Console des urgences open-data release and is republished here under the licence of the original dataset. Cite the MSSS as the source. The mirror and this archive are maintained alongside [sante.handled.tools](https://sante.handled.tools/donnees), which publishes the same numbers as pages per hospital, city and region. Code in `scripts/` is MIT.

Not a ministry project, and not endorsed by one. Not medical advice. In an emergency, call 911.
