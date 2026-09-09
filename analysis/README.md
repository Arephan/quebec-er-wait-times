# Eleven emergency departments that never went below capacity

Window: 163 consecutive hourly readings, 2026-09-02 06:00 to 2026-09-09 00:00,
America/Montreal. 107 of Quebec's 120 emergency departments reported occupancy at
least 100 times in that window; the rest report too rarely to say anything about.

Eleven of those 107 never once recorded a stretcher occupancy below 100%. Not at
4 a.m., not on the Saturday. The Royal Victoria's *lowest* reading of the week was
176%.

| Median | Lowest | Highest | Facility | Region |
|---|---|---|---|---|
| 206.0 | 176 | 258 | Hôpital Royal Victoria | Montréal |
| 200.0 | 142 | 274 | Hôpital général juif | Montréal |
| 188.5 | 145 | 219 | Hôpital général du Lakeshore | Montréal |
| 180.0 | 120 | 240 | Hôpital et CLSC de Sept-Îles | Côte-Nord |
| 168.0 | 142 | 200 | Hôpital général de Montréal | Montréal |
| 156.0 | 125 | 178 | Hôpital du Suroît | Montérégie |
| 154.0 | 118 | 196 | Hôpital de Gatineau | Outaouais |
| 153.0 | 110 | 188 | Hôpital de la Cité-de-la-Santé | Laval |
| 149.0 | 103 | 183 | Hôpital de Saint-Eustache | Laurentides |
| 136.0 | 100 | 188 | Hôpital de Hull | Outaouais |
| 131.0 | 100 | 166 | Hôpital Anna-Laberge | Montérégie |

Four are on the island of Montreal, but seven are not: Laval, the Laurentides, two
in the Outaouais, two in the Montérégie, and Sept-Îles, 900 km up the north shore.

Twelve other departments never went **above** 100% in the same window, most of them
small northern and rural sites reporting a median of zero occupied stretchers.
The script prints that list too.

## Reproduce it

```
python3 analysis/never_below_100.py
```

Standard library, reads `data/er-hourly.csv`, prints both lists.

## What to be careful about

"Never below 100%" is a statement about the readings in this file, not about the
department. About 11% of rows across the archive have no occupancy figure, so a
facility can look continuously full partly because it did not report during a
quiet hour. The 100-reading floor above is there to limit that; the per-facility
`n` column tells you how much of the window each one actually covered.

The number is also not computable from the official source. The MSSS feed carries
the current hour only — once it refreshes, the previous reading is gone from it.
A minimum across a week exists only if somebody kept the hours, which is what this
repo is for.

---

Second script: `within_region_gap.py` compares each ED with the other EDs in its own region. Output is checked in at `within-region-gap.txt`.
