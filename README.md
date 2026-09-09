# Quebec ER wait times — hourly archive

Hourly emergency-room occupancy for all 120 acute-care emergency departments in Quebec, going back to 2026-09-02.

Quebec's Ministère de la Santé et des Services sociaux (MSSS) publishes ER occupancy as open data, refreshed once an hour. That feed only carries the current hour — once it refreshes, the previous reading is not available from it anymore. This repo stores the readings as they come in.

## Files

| File | Rows | Contents |
|---|---|---|
| [`data/er-hourly.csv`](data/er-hourly.csv) | 19,555 | one row per facility per hour |
| [`data/facilities.csv`](data/facilities.csv) | 120 | name, establishment, region, street address, lat/lng |

`er-hourly.csv` covers 2026-09-02 06:00 to 2026-09-09 00:00, local Quebec time (America/Montreal).

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

## Updating it

```
python3 scripts/fetch.py
```

Standard library only. It pulls the last seven days and merges on `(ts_local, facility_id)`, so re-running extends the archive rather than duplicating rows. Run it weekly or more often and there is no gap.

The JSON mirror it reads is public, with no key or account:

```
GET https://sante.handled.tools/api/facilities
GET https://sante.handled.tools/api/facility/<id>/history
GET https://sante.handled.tools/api/now
```

## Source and licence

The data comes from the MSSS Console des urgences open-data release and is republished here under the licence of the original dataset. Cite the MSSS as the source. The mirror and this archive are maintained alongside [sante.handled.tools](https://sante.handled.tools/donnees), which publishes the same numbers as pages per hospital, city and region. Code in `scripts/` is MIT.

Not a ministry project, and not endorsed by one. Not medical advice. In an emergency, call 911.
