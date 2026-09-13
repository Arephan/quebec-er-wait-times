# Quebec ER wait times — hourly archive

Hourly emergency-room occupancy for all 120 acute-care emergency departments in Quebec, going back to 2026-09-02, plus a derived stretcher count for 98 of them and average length of stay for 108 of them.

Quebec's Ministère de la Santé et des Services sociaux (MSSS) publishes ER occupancy as open data, refreshed once an hour. That feed only carries the current hour — once it refreshes, the previous reading is not available from it anymore. This repo stores the readings as they come in.

## Files

| File | Rows | Contents |
|---|---|---|
| [`data/er-hourly.csv`](data/er-hourly.csv) | 30,115 | one row per facility per hour |
| [`data/facilities.csv`](data/facilities.csv) | 120 | name, establishment, region, street address, lat/lng |
| [`data/stretcher-capacity.csv`](data/stretcher-capacity.csv) | 98 | stretcher count behind each department's published percentage, derived |
| [`data/same-day-hour-choice.csv`](data/same-day-hour-choice.csv) | 108 | whether waiting for a quieter hour helps, per facility, derived |
| [`data/length-of-stay.csv`](data/length-of-stay.csv) | 120 | average length of stay per department, stretcher and non-stretcher, hours |
| [`data/gauge-reliability.csv`](data/gauge-reliability.csv) | 107 | how often each department's published percentage agrees with the headcount beside it |
| [`data/coverage-by-er.csv`](data/coverage-by-er.csv) | 120 | how many of the 232 archived hours each department actually filled, and what it filled them with |
| [`data/overflow-episodes.csv`](data/overflow-episodes.csv) | 107 | how long a department stays above 100% stretcher occupancy once it gets there: episode count, median/longest spell, recovery time |
| [`data/nearest-alternatives.csv`](data/nearest-alternatives.csv) | 600 | the five nearest other emergency rooms to each department, in kilometres, and whether each one publishes a number |
| [`data/weekday-by-er.csv`](data/weekday-by-er.csv) | 120 | each department's occupancy and headcount averaged by day of the week |
| [`data/best-hour-by-er.csv`](data/best-hour-by-er.csv) | 108 | the quietest hour of the day at each department, and how much quieter it is |
| [`data/hour-by-weekday-by-er.csv`](data/hour-by-weekday-by-er.csv) | 18,133 | the full hour-of-week cross-tab: one row per department, weekday and hour |

`er-hourly.csv` covers 2026-09-02 06:00 to 2026-09-12 16:00, local Quebec time (America/Montreal).

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

## `data/gauge-reliability.csv` — does the published percentage track the crowd?

Quebec publishes two numbers for every emergency room: a stretcher occupancy percentage and a count of people currently in the department. The percentage is the one that gets quoted, and for most people it is the only one they read. This table asks whether it earns that.

Every pair of hours at one department where the headcount differs is scored once, over 2026-09-02 06:00 to 2026-09-11 21:00:

- **agree** — the percentage is higher in the hour that really had more people in the room
- **disagree** — the percentage is higher in the hour that had fewer
- **blind** — the percentage is identical in both hours, so it cannot separate them

```
facility_id, facility_name, region_name, hours, distinct_published_values,
smallest_step_pct, implied_stretchers, people_min, people_max,
hour_pairs_scored, agree_pct, disagree_pct, blind_pct
```

Across the 107 departments that publish a percentage at all:

- **97 of 107** point the wrong way on at least one hour pair in ten.
- **16** agree less than half the time, which is worse than a coin toss on the question "which of these two hours was busier here".
- **18** are blind on a quarter or more of their pairs.
- **Two** — Radisson and Murdochville — published one single value for all 232 hours while the room went from 0 people to 3 and from 0 to 14.

The clearest single case is **Hôpital Pierre-Le Gardeur** in Lanaudière, a fifty-stretcher department with a one-percent step, so resolution is not the problem. It disagrees on 48.6% of pairs and agrees on 46.8%. On 2 September at 07:00 it published **117% with 75 people in the department**. On 5 September at 18:00 it published **81% with 123 people**. The number read 36 points higher on the hour with 48 fewer people.

The reason is in the denominator. The percentage counts occupied stretchers against funded stretchers; it says nothing about the people waiting in chairs, who are the larger half of most departments. The two numbers answer different questions and only one of them is on the front of the page.

`smallest_step_pct` is the smallest gap between two distinct values the department has ever published, and `implied_stretchers` is 100 divided by it. Departments with a large step are coarse by construction: Isle-Dieu and René-Ricard can only publish 0% or 100%, so they are blind on 86% and 80% of their pairs respectively.

Rebuild it with `python3 scripts/gauge_reliability.py`.

## `data/coverage-by-er.csv` — which departments are actually in this file

Every table in this repository is built from `er-hourly.csv`, and `er-hourly.csv` has a row for all 120 emergency departments every hour whether or not Quebec put anything in it. That makes "120 departments" the wrong number to quote for almost any question. This table is the metadata to read before the data: for each department, how many of the 232 archived hours carry an occupancy percentage, how many carry a waiting count, how many carry a headcount, and the longest unbroken run of hours with nothing.

```
facility_id, facility_name, region, archive_hours,
hours_with_occupancy_pct, hours_with_waiting, hours_with_present,
coverage_pct, longest_gap_hours, first_reading, last_reading
```

Over 2026-09-02 06:00 to 2026-09-11 21:00, 232 hours:

- **107 departments publish an occupancy percentage.** 90 of them filled all 232 hours. 17 missed exactly one hour, never more.
- **108 publish a waiting count and a headcount** — one more than publish a percentage.
- **13 never published a percentage at all**, not once in 232 hours.

Those 13 are not one failure but two. **Twelve are silent on all three columns**: Sacré-Coeur, Fleury, Jean-Talon and Albert-Prévost in Montreal, and eight departments across Mauricie–Centre-du-Québec including Sainte-Croix, Hôtel-Dieu d'Arthabaska and Hôpital du Centre-de-la-Mauricie. Four Montreal emergency rooms and an entire region's worth publish no hourly number of any kind.

The thirteenth is different. **CHSLD et Hôpital Paul-Gilbert** in Chaudière-Appalaches published a waiting count and a headcount in all 232 hours and a percentage in none of them — at 21:00 on 11 September, 12 people waiting and 17 in the department, and an empty gauge. It is the one department where the data exists to compute the number and the number is withheld. Calling it "dark" is wrong; it is dark on one column.

The practical use is as a denominator check. A claim about "Quebec's emergency rooms" built on the percentage column is a claim about 107 departments, not 120, and it is missing four hospitals on the island of Montreal.

Rebuild it from `er-hourly.csv`; it needs no other input.

## `data/nearest-alternatives.csv` — what else is within reach, and whether it reports

The occupancy feed has no geography in it. It says how full a department is; it does not say
what the next department is or how far away. So the question a person actually has — the room
I was sent to is full, where else can I go — cannot be answered from the ministry's files alone.

This table joins the street addresses in `facilities.csv` to the occupancy record and lists,
for each of the 120 departments, the five nearest other emergency rooms: great-circle distance
in kilometres, whether the alternative sits in a different health region, and how many of the
archived hours that alternative has actually published an occupancy number for.

```
facility_id, facility_name, region_name, rank, alt_facility_id, alt_facility_name,
alt_region_name, distance_km, crosses_region, alt_coverage_pct, alt_hours_with_occupancy_pct
```

Three things fall out of it.

**65 of the 600 neighbour entries never publish an occupancy number at all.** They are in the
feed as facilities and they are the nearest alternative to somebody, but the column that would
tell you whether to drive there is empty in every archived hour.

**One department's five nearest alternatives are all dark.** Pavillon Sainte-Marie's closest
five — at 14.5, 23.5, 30.2, 43.4 and 53.2 km — have published nothing in the window. Anyone
leaving that waiting room is choosing blind for the next 53 kilometres.

**For 26 of the 120 departments, the nearest alternative is in a different health region.**
Regional dashboards are the usual way this data is presented, which means for roughly one
department in five the closest option is on a page the person is not looking at.

Distances are straight-line, not driving distance, and they are computed from the published
street address of each installation. Treat them as a sort order, not as a travel estimate.

## Embedding the current hour on your own page

These files hold past hours. The current hour for a single department is available as a
standalone card sized for an iframe:

```html
<iframe src="https://sante.handled.tools/embed/hopital-de-matane"
        width="100%" height="160" style="border:0" loading="lazy"
        title="Hôpital de Matane — occupation des civières"></iframe>
```

The path segment is the `slug` column of `er-hourly.csv` and `facilities.csv`, so no lookup
table is needed to go from a row here to its widget.

- `/embed/<slug>` is French, `/en/embed/<slug>` is English.
- `?theme=light`, `?theme=dark`, or leave it off, in which case it follows the reader's OS
  setting.
- The card shows stretcher occupancy, people present, people waiting, and the time of the
  reading, off the same MSSS hourly feed this archive stores.
- There is no API key and no script tag. The iframe does not read the page it sits in.

[sante.handled.tools/embed](https://sante.handled.tools/embed) builds the snippet for any of
the 120 departments from a dropdown.

### `data/hour-by-weekday-by-er.csv`

Median stretcher occupancy and median waiting count for every **hour of the week** — 7 weekdays x 24 hours — at each of the 108 departments that publish a number. 18,133 rows. Columns: `facility_id, facility_name, region_name, slug, weekday, hour_local, n_readings, median_occupancy_pct, median_waiting`.

`best-hour-by-er.csv` collapses the week into one 24-hour profile and `weekday-by-er.csv` collapses the day into seven numbers. This file is the cross-tab neither of them can show: a department whose Monday evening and Saturday evening look nothing alike is invisible in both.

**Read `n_readings` before you use a cell.** The archive is roughly eleven days deep, so most cells rest on one or two observations and a few rest on none. Cells with `n_readings` of 1 are a single hour that happened, not a typical hour. The file gets steadier every hour the archive grows; it is published now because the shape is already usable at the region and day-part level, not because every cell is.

Timestamps are America/Toronto local, matching the rest of the archive.

## Does the hour you leave change what you walk into?

The live ministry page answers one question: how full is this emergency room right
now. A reasonable objection to keeping an hourly history is that nobody plans an ER
visit in advance — the trip is decided the same day — so a weekly pattern is of no
practical use.

That objection can be tested against the archive, and `data/same-day-hour-choice.csv`
is the test. For every facility, day and hour in the window, take the hour in the
following six with the lowest historical median queue for that facility, and compare
the queue actually observed then against the queue at the moment of the decision. The
historical median leaves the day being tested out, so the choice never sees its own
answer. Nothing here looks further ahead than the same afternoon.

Over 22,547 decision points at 108 emergency rooms:

| | |
|---|---|
| the hour made no difference at all | 23.8% of decisions |
| waiting for the quieter hour left a shorter queue | 55.0% of the decisions where it made any difference |
| how much shorter, typically | 1 person |

So the effect is real and it is small. At 75 of the 97 facilities where the hour
changes anything, the quieter hour is the better bet more often than not; at the
remaining 22 it is not, and going immediately is as good a choice as any. Where it is
worth something it is worth a lot: the median at Hôpital général juif is 5 people
fewer in the queue, and at the Coaticook MRC service centre 6.

A caveat the numbers do not carry on their own: this is ten days of one September, and
a queue that is one person shorter is not a reason to delay care for anyone who needs
it now.

`scripts/same-day-hour-choice.py` reproduces the file from `data/er-hourly.csv` with
no dependencies beyond the standard library.
## `data/overflow-episodes.csv` — how long an over-100% spell actually lasts, per department

The ministry publishes a stretcher-occupancy percentage for right now. It does not publish how long
a department stays above 100% once it gets there, because that needs a history and the ministry's
page keeps none. This file cuts the archive into **episodes**: a run of consecutive hourly readings
in which `stretcher_occupancy_pct` is strictly above 100, for each of the 107 departments that
publish an occupancy figure at all.

One row per department. Columns:

| Column | Meaning |
|---|---|
| `hours_observed` | hourly readings with a non-blank occupancy value (248–252 across the file) |
| `hours_over_100` / `share_hours_over_100_pct` | how much of that time the department was over 100% |
| `episodes_over_100` | number of distinct spells above 100% |
| `median_episode_hours` / `mean_episode_hours` / `longest_episode_hours` | the length of those spells |
| `episodes_ending_within_archive` | spells that actually came back down before the archive ended |
| `median_hours_to_recover` | median length of *those* spells — the ones we watched end |

### What is in it

- **90 of the 107 departments went over 100% at least once.** 17 never did.
- **Eight departments were above 100% in every single hour of the archive** — 248 to 252
  consecutive readings each, no gap: Hôpital de la Cité-de-la-Santé (Laval), Hôpital de Saint-Eustache (Laurentides), Hôpital du Suroît (Montérégie), Hôpital et CLSC de Sept-Îles (Côte-Nord), Hôpital général de Montréal, Hôpital général du Lakeshore, Hôpital général juif et Hôpital Royal Victoria (all four Montréal).
  For these, `median_hours_to_recover` is blank on purpose: nothing recovered, so
  there is no recovery to take a median of. A snapshot of any one of those hours tells a reader the
  department is full; only the history tells them it has not been anything else for ten days.
- At the other end, some departments cross 100% often and clear fast: CHUS – Hôpital Fleurimont has
  11 separate spells with a median length of **1 hour**, and Hôpital de Saint-Georges 10 spells with
  a median of **1.5 hours**. Two departments can show the same number at the same moment and mean
  completely different things about the next few hours.
- Across all departments with at least one spell, the median of the per-department median spell
  length is **4 hours**.

### Caveat

The archive is 252 hours long. A spell running at the first or last reading is counted at the
length we can see, which is a floor, not the true length — that is what
`episodes_ending_within_archive` is for.
