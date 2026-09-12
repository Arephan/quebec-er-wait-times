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

## `data/best-hour-by-er.csv` — the quietest hour at each emergency room

Québec publishes each ER's waiting count every hour and overwrites the previous reading,
so the hour-of-day profile of an emergency room is not published anywhere. This file is
that profile, computed from `data/er-hourly.csv`.

One row per facility with at least 12 distinct hours of the day observed (108 of them),
covering 2026-09-02 06:00 to 2026-09-11 17:00 local time:

| Column | Meaning |
|---|---|
| `days_observed` | distinct calendar days the facility reported |
| `hours_covered` | distinct hours of the day with at least one reading |
| `best_hour` / `best_hour_mean_waiting` | the hour of day with the lowest mean waiting count |
| `worst_hour` / `worst_hour_mean_waiting` | the hour of day with the highest mean waiting count |
| `swing` | worst mean minus best mean, in people |
| `usable` | `yes` when the swing is 5 people or more |

91 of the 108 have a swing of 5 people or more. The other 17 do not have a clock worth
planning around, and that is a finding too — it can only be established by keeping the
hours, which is what this archive does.

`waiting` is the ministry's own count of people in the waiting room. Means are taken over
every reading at that hour of the day in the window; a facility that reports irregularly
will have fewer readings behind each hour, which `hours_covered` and `days_observed` expose.

## `data/weekday-by-er.csv` — which day of the week each emergency room is busiest

The ministry's feed carries no day-of-week view, and because it overwrites every hour there
is no way to build one from the published page. This file is that view, computed from
`data/er-hourly.csv` over the eight **complete** days in the archive, 2026-09-03 00:00 to
2026-09-10 23:00 local time. The two partial edge days are excluded on purpose: 2026-09-02
starts at 06:00 and 2026-09-11 ends at 17:00, and including them would bias Wednesday upward
and Friday downward by the hours each one is missing.

One row per facility, all 120, each with at least 20 hourly readings on every weekday:

| Column | Meaning |
|---|---|
| `quietest_day` / `quietest_day_mean_present` | the weekday with the lowest mean count of people present |
| `busiest_day` / `busiest_day_mean_present` | the weekday with the highest |
| `swing_people` | busiest mean minus quietest mean, in people |
| `mean_sunday` … `mean_saturday` | the mean for each weekday, so you can check the two above |

There is no province-wide bad day. The **quietest** day clusters on the weekend — Saturday
for 37 emergency rooms and Sunday for 35, 72 of 120 between them. The **busiest** day does
not cluster at all: Tuesday at 26 facilities, Wednesday at 24, Sunday at 22, Monday 14,
Thursday 13, Friday 12, Saturday 9. A rule of thumb picked up in one city is wrong in the
next one.

46 of the 120 swing 10 people or more between their quietest and busiest weekday; 21 swing
under 3, which means the weekday is not worth planning around there. The largest swing in
the province belongs to the Montreal Children's Hospital, and it runs backwards from the
adult pattern: 83.5 people present on an average Sunday against 37.8 on an average Thursday.

Eight days is one observation per weekday, two for Thursday. Treat this as a first cut whose
method is reproducible rather than a settled seasonal profile — the window widens every hour
the archive runs, and `mean_sunday` … `mean_saturday` are published so the ranking can be
checked rather than taken on trust.
