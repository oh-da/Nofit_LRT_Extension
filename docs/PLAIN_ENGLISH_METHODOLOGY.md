# Nofit LRT Extension — Full Project Documentation, in Plain English

> **Status note, 23 September 2026.** The numbers in Parts 1–4 are the state of 22 September
> 2026. Three things changed on 23 September: the trips file's mode codes 4 (group taxi) and 5
> (Matronit) were found swapped and the chain rerun with the corrected codes; step 33 estimated
> the cost sensitivity λ at the person level; and, after new smart-card data for 2025 and a
> rerun of the matrix tests, step 15's ticketing reference was moved from the on-board survey's
> destination pattern to RavKav's own inferred alightings and the whole chain rebuilt. **Part 5
> at the end of this document explains all of this in plain language and carries the current
> headline numbers**; `METHODOLOGY.md` §0 ("Rerun" and "Rebuild") and §6m–§6ag are the
> technical record.

*Written 23 September 2026, based on `METHODOLOGY.md` and the supporting `docs/` files as
they stood on that date.*

## What this document is

This document explains the whole Nofit LRT project, from the raw data it starts with to
the ridership number it ends on, in plain language. It covers, for every one of the
project's 32 processing steps:

- **what data goes in**
- **what is done to that data, step by step** (including the math, explained in words —
  not just named)
- **what comes out**
- **what tests or checks were run, what the actual results were, and what those results
  mean** — is it a good match, a real problem, something to keep in mind, or nothing to
  worry about

The goal is that you should be able to read this end to end and understand the whole
project — what it's built on, how solid each piece is, and where today's headline
ridership number actually comes from — without needing to open the notebooks or decode
statistics jargon.

**This document is a plain-language companion to `METHODOLOGY.md`, not a replacement for
it.** `METHODOLOGY.md` is the precise technical record — the exact formulas, file names,
and numbers, kept up to date step by step as the work happens. This document restates
that same content in simpler words, with more explanation of *why* each method works the
way it does. Every number, formula, and test result here is taken directly from
`METHODOLOGY.md` and its supporting `docs/` files — nothing here is a new calculation. If
the wording here and `METHODOLOGY.md` ever seem to disagree on a number, treat
`METHODOLOGY.md` as correct, since it is the file kept in sync with the actual notebooks
and outputs.

## How this document is organized

The document is split into four parts, roughly following the order the work was actually
done in:

- **Part 1 (Steps 1 – 1e).** Where the project stands today and what should (and should
  not) be trusted; the raw input files; the one rule used everywhere to turn survey diary
  entries into "trips"; and the earliest attempt at building a demand matrix.
- **Part 2 (Steps 2 – 15).** Blending the household survey with mobile-phone (cellular)
  data; a second, independent extraction of trips from a different survey file; the bus
  matrix built from real ticket-tap data; the train matrix; lining everything up to a
  common year (2022); and three rounds of statistical testing that eventually convinced
  the project to stop leaning on the cellular data and switch to a survey-only base.
- **Part 3 (Steps 16 – 25).** The current 2022 base matrices (car / bus / taxi-type /
  rail); how demand flows along the future LRT corridor; growing the matrices forward to
  2040 and 2050 under two different growth scenarios; and the planned LRT line's own
  stations and station-to-station travel times.
- **Part 4 (Steps 26 – 32).** Putting a single "cost" number (combining time, and other
  factors) on every way of getting around the corridor — car, bus, the existing Metronit
  bus-rapid-transit line, and the new LRT under different scenarios; checking that cost
  model against how people actually travel today; and using it to estimate how many
  riders would switch to the new LRT, both today and in the future. It closes with a
  plain guide to the output files, a list of things to watch out for, and instructions
  for reproducing the whole pipeline.

Each step follows the same layout: **What it's for**, **Inputs**, **How it works**,
**Formulas**, **Outputs**, **Tests / checks and what they showed**, and **Caveats**.
Every step also carries a **status tag** — current, historical, or diagnostic — copied
from `METHODOLOGY.md`'s own tracking table:

- **Current** — this is a building block behind today's trusted answer.
- **Historical** — this was tried, and has since been replaced or set aside; kept only as
  a record of what was tested and why it didn't become the final approach.
- **Diagnostic** — this doesn't produce a usable demand matrix on its own; it's a test or
  check that was used to decide between other approaches.

One phrase you will see over and over: **"potential movements."** This is the project's
own term for a demand number that comes out of an origin-destination matrix and is loaded
onto a route on paper. It is **not** a measured count of people actually on a bus or
train — it assumes no capacity limits and no route-choice behaviour. Keep that
distinction in mind throughout, especially in Parts 3 and 4.

## Glossary — plain-English meanings of terms used throughout

- **TAZ (Traffic Analysis Zone)** — one of the small areas the whole study region is cut
  into (778 of them here). The basic building block of the whole model: every trip starts
  in one TAZ and ends in another.
- **Superzone / GS zone / V2 area** — three different, unrelated ways of grouping the 778
  TAZs into bigger, coarser areas (36 superzones; 25 GS zones; 25 "V2" corridor-study
  areas). They are used at different points for different purposes. Having the same
  zone-count (e.g. both GS and V2 happen to have 25 zones) does **not** mean they cover
  the same areas — they must never be mixed up.
- **OD matrix (origin–destination matrix)** — a big table where each row is a starting
  zone, each column is an ending zone, and each cell is the number of trips made from
  that row's zone to that column's zone.
- **AM peak** — the morning rush-hour window this whole study focuses on: 06:00 to 09:00.
- **Expansion weight** — since only a sample of households were surveyed, each surveyed
  household is given a multiplier (its "weight") so that adding up sampled trips ×
  weights gives an estimate for the whole real population, not just the people who
  happened to be surveyed.
- **RavKav** — Israel's national smart-card ticketing system for public transport. Every
  tap-on/tap-off leaves a record, so it gives a near-complete count of actual bus
  journeys, unlike the household survey (which only covers a small sample of people).
- **OnBoard survey** — a separate, smaller survey where bus passengers were asked, in
  person, where they actually got off. Used because RavKav's own guess at where a
  passenger got off is calculated by the ticketing system, not reported by the rider.
- **GTFS** — a standard data format used worldwide for public transport timetables
  (stops, routes, trip times). Here it's the national government's official bus and BRT
  timetable data.
- **Metronit** — the existing bus-rapid-transit (BRT) line(s) in the Haifa area — buses
  that run on their own lane with fewer stops, faster than a regular bus route.
- **Furness balancing / IPF (iterative proportional fitting)** — a standard way to adjust
  a whole matrix so its row totals and column totals match new target numbers, while
  disturbing its internal pattern as little as possible. Works by repeatedly rescaling
  rows to hit their targets, then columns to hit theirs, back and forth, until both sides
  are close enough. Explained with a worked example inside Step 23.
- **Empirical-Bayes shrinkage** — a way of blending a small, possibly-unreliable sample
  (the survey) with a much bigger, more stable reference (cellular data), where the
  blend leans more on the sample when there's a lot of it, and leans more on the
  reference when there's very little sample to go on. Explained in detail, with a worked
  example, inside Step 2.
- **Cosine similarity** — a score from 0 to 1 that says how similar the *pattern* of two
  matrices is (which cells are relatively bigger or smaller than others), ignoring their
  overall size. 1 means identical pattern.
- **GEH** — a standard measure from traffic modelling for comparing a modelled number
  against a real, observed number on the same link; a value under 5 is generally taken
  as an acceptable match. Unlike cosine similarity, it does care about overall scale.
- **PCA (principal component analysis)** — a statistical method for finding the main,
  shared *pattern* hiding inside a set of data (here: where trips tend to go), so that
  two different groups (e.g. car trips vs transit trips) can be compared on whether they
  share that same main pattern or not. Explained with a worked example inside Step 21.
- **Generalized cost** — a single number that combines several real factors of a trip
  (in-vehicle time, waiting time, walking/access time, and — where included — cost) into
  one comparable "how attractive is this way of travelling" score, so that car, bus, and
  LRT can be compared on equal footing.
- **Skim (or skim matrix)** — a matrix where each cell holds a travel time or cost (not a
  number of trips) between two zones, for one particular mode of travel — e.g. "the
  driving time skim" or "the LRT in-vehicle-time skim."
- **Logit model / incremental logit** — a standard mathematical way of estimating how
  likely someone is to choose one travel option over another, based on how much better
  or worse each option is (usually on generalized cost). "Incremental" here means the
  model is used to estimate how many of *today's* travellers would switch to a new option
  (the LRT), rather than rebuilding everyone's travel choice from scratch. Explained in
  detail, with the model's actual limitations, inside Step 31.
- **λ (lambda), cost-sensitivity parameter** — inside the logit model, this number
  controls how strongly a difference in generalized cost between two options actually
  changes people's choices. A bigger λ means people react more strongly to time/cost
  differences.
- **Peak-hour factor (PHF)** — the fraction of a three-hour window's total trips that
  falls inside just the single busiest hour within it. Used to convert a three-hour
  potential-movement number into a more realistic single-hour figure.

---

## Part 1 — Where the project stands, the raw inputs, and the first survey-only build attempts (Steps 1 – 1e)


This is a plain-English walkthrough of the first part of `METHODOLOGY.md`. It covers
where the project stands today, what data feeds it, the one rule that is applied every
time the raw survey is read, and the first five processing steps.

---

### 0. What this project is, and what to trust today

### What the project is

This is a travel-demand study for a **planned light rail (LRT) line extension near
Haifa, in northern Israel**. The area studied is cut up into **778 small zones** called
TAZs (Traffic Analysis Zones) — the standard building block in transport modelling. The
goal is to build a table (an "origin–destination", or OD, matrix) that says, for the
morning rush hour (**06:00–09:00**), how many trips go from each zone to each other zone,
broken down by how people travel (car, bus, taxi-type, rail).

Two very different data sources feed this:

- **The 2018 Travel Habits Survey (THS)** — people were asked to keep a detailed diary of
  every trip they made. This gives rich detail on *why* and *how* people travel, but only
  **5,108 households** were surveyed, so the sample is small and thin in many zones.
- **A cellular-derived OD matrix** — built from mobile phone movements between cell
  tower areas. This covers almost the whole population, so it doesn't suffer from small
  sample problems, but its zones are coarser than the 778 TAZs, and it misses any trip
  short enough that a phone doesn't visibly move between cell areas.

The project's first phase tried to get the best of both: treat the cellular data as a
baseline pattern and use the survey to correct it, blending the two wherever the survey
had enough evidence to be trusted. **That approach has since been abandoned as the base
method.** Testing done in later steps (steps 12–14) and an outside review carried out on
21 September 2026 (written up in `docs/Nofit_Demand_Methodology_Review.md`) led the team
to switch to a **survey-only base**, with the bus numbers separately checked and
corrected ("calibrated") against real ticketing data. The cellular-blended ("hybrid")
matrices are now kept only as historical record, not as something to build on.

### What "authoritative baseline" means in practice

In a project with this many steps and this many output files, not every file is equally
trustworthy today. "Authoritative baseline" means: **these are the specific files you
should use if you need today's best answer.** Everything else is either an intermediate
building block that feeds those files, a diagnostic test that doesn't produce a usable
matrix, or a historical product that has been superseded and should not be relied on for
new work.

**The current authoritative product** is a **survey-only** set of matrices, built for the
year **2022**, split into four layers — **car, bus, taxi-type and rail** — located at:

```
Output/ths2017/three_mode_2022/{car,bus,taxi,rail}_2022_*.csv
```

These four layers are then summed into the actual deliverable matrices — **car / transit
/ total** — at the 778-TAZ level, in:

```
Output/final_2022/
```

What this product actually represents, in plain terms:

- It counts **trips made by residents**, where **both the start and the end of the trip
  are inside the study area** ("person-journeys", not vehicle counts or boardings).
- It only covers the **AM peak, 06:00–09:00**, on a **representative weekday**.
- It is priced at **2022**: the bus numbers use real ticketing (RavKav) volumes from May
  2022; everything else is the 2018 survey grown forward to 2022 using population/
  demographic growth factors; the rail numbers are grown using the national rail
  ridership trend.
- It is good enough for **early, exploratory comparison of corridor options** — e.g.
  "is more demand near Nazareth or near the Krayot suburbs" — but it is **not** yet
  checked against any external, independent count (like a traffic count or a fare-gate
  count), so it should not be treated as a validated, final demand forecast. Its
  corridor numbers are **potential movements over a three-hour window**, or **at the
  single busiest hour of departures**, not actual passenger loads on a specific
  vehicle or line.

The plain-language, non-technical write-up of this current base, including its tests and
corridor results, is `reports/Survey_Matrices_Car_Bus_Rail_Report.docx` (revision 2.1,
21 September 2026). Older reports have been moved to `reports/historical/` and each one
now carries a note at the front saying which of its conclusions are now out of date.

### The headline numbers, as of 21 September 2026

These are the key results the current base supports (all for the 06:00–09:00 window
unless stated otherwise; see `METHODOLOGY.md §6n`, `§6o`, `§6r`, etc. for the underlying
detail):

- **Trips between the corridor's own zones**, by mode: **72,331 car / 9,366 bus / 3,812
  taxi-type / 0 rail**. Bus's share of corridor-to-corridor trips (bus plus rail, against
  all modes) is **11%**.
- The **2018 bus baseline**, before growing to 2022, depends on which of three ways you
  measure "coverage" of the ticketing data: **126,117** trips under the main rule used
  (made up of 116,083 survey-based + 92,713 ticketing-based + 110,654 from a simple
  binary yes/no rule) — a sensitivity check sweeping the coverage threshold gives a range
  of **117,500 to 131,700**.
- **Busiest transit link (bus + rail), over the full three hours**: **1,661** trips
  towards Nazareth (between the Ein Hayam and Bat Galim stops), and **1,650** towards
  Tirat Carmel (between Neot Peres and Neve David).
- **Peak hour** (the single busiest clock-hour for people *departing*) is **07:00–08:00**
  for every mode. The share of the three-hour total that falls in that one peak hour
  (called "PHF₃ₕ" — peak-hour factor over three hours) is **0.62 for car, 0.59 for bus,
  0.58 for taxi-type** — i.e. the peak hour alone carries roughly **1.8 times** what an
  average hour of the three would carry.
- **Busiest transit link in just the peak hour**: **981** trips towards Nazareth, **974**
  towards Tirat Carmel (against an average-hour figure of about 550) — this has a
  roughly **±15%** uncertainty band depending on how the bus scaling factor is chosen.
- A statistical comparison (principal component analysis, or PCA — a way of finding the
  dominant travel patterns in the data) of where car trips go versus where transit trips
  go shows they share the same *dominant* destination pattern (**overlap score 0.75**,
  rising to **0.83** for well-sampled origin zones, against a benchmark "repeatability"
  score for transit itself of **0.81–0.86** — meaning the overlap is about as high as
  transit data agrees with itself). But transit trips are **less local** (a
  "self-containment" score — the share of trips that stay inside the same zone/area — of
  **0.45** for transit vs **0.62** for car) and are **more weighted towards central Haifa**
  (a **2–3 percentage point** shift, a pattern too consistent to be chance: **p = 0.04**
  at the coarser "superzone" level, **p = 0.002** at the finer TAZ level — "p" here is a
  statistical significance value; smaller means less likely to be a random fluke).
  **Practical takeaway: you cannot just take the car travel pattern and rescale it to
  estimate the transit pattern — transit needs its own, separately estimated,
  destination pattern.**
- Looking ahead: under the growth scenarios, the corridor's internal transit market
  (2022 → future years) is projected to grow by a factor of **1.27 to 1.57**, depending
  on the scenario and target year.

**What this base can and cannot be used for.** It supports *relative* comparisons: which
alignment or segment carries more demand, roughly how big the market is between two
areas, where demand is concentrated, and how a three-hour flow scales up to a single peak
hour (about 1.8×). It does **not** support: turning these numbers into actual passenger
loads, capacity planning, service-frequency decisions, formal ridership forecasts, or
economic appraisal. Reasons: the numbers have not been checked against an outside,
independent count; the bus total depends on an assumed coverage threshold; the two ways
of measuring transit (survey-based vs ticketing-based) disagree by a factor of **2–3×**
in one direction near the Nazareth end; the fine TAZ-level detail comes from a rough,
"purpose-blind" allocation (it doesn't know if a trip was for work, shopping, etc.); and
the peak-hour numbers are "potential movements" — they assume no capacity limits, no
route-choice behaviour and no trips beyond the study area.

### Lineage — what's current, what's historical, at a glance

The table below (condensed and put in plain words from `METHODOLOGY.md §0`) tells you,
for each output folder, what built it, what it covers, and its current status:

| Output | Built by | What it is | Geography | Vintage | Status |
|---|---|---|---|---|---|
| `final_2022/{car,transit,total}_2022_taz.csv` and friends | step 22 | The deliverable car / transit / total matrices | 778 TAZ | 2022 | **Current — the actual deliverable** |
| `ths2017/three_mode_2022/{car,bus,taxi,rail}_2022_*.csv` | step 16 | The four mode layers behind the deliverable | 778 TAZ / 36 superzones / 28 areas | 2022 | **Current** |
| `ths2017/three_mode_2022/rail_station_smartcard_2022_taz.csv` | step 16 | Rail, station to station, all riders | 19 station zones | 2022 | Current (kept separate) |
| Corridor link-flow / profile files | steps 17–18 | Three-hour "potential movement" totals along the line | 18 line areas | 2022 | Current |
| Peak-hour factor and link-flow files | step 20 | Same, but scaled to the single peak hour | 18 line areas | 2022 | Current |
| `ths2017/two_mode/*` | step 15 | Car and bus matrices before the 2022 uplift | 778 / 36 / 28 | 2018 (bus ticketing cells: 2022) | Current intermediate |
| `bus/bus_od_taz_avg.csv` etc. | step 8 | Raw ticketing (RavKav) journeys | 722–730 TAZ | 2022 | Current input |
| `bus/bus_od_taz_new.csv` etc. | step 9 | Ticketing volumes spread using the OnBoard survey pattern | 722 TAZ / 28 areas | 2022 | Current input, **but with an open question**: it's not confirmed whether the OnBoard survey rows represent one bus leg or a whole journey |
| `train/train_od_taz_6_9.csv` | step 10 | Rail, station to station | 19 stations | 2019 | Current input |
| `ths2017/study_taz/hybrid_taz_trips_balanced.csv` | step 19 | A corrected version of the old hybrid | 778 | 2018 | Historical, but corrected |
| `ths2017/study_taz/hybrid_*`, `submatrices/*` | step 6 | Old survey-plus-cellular hybrid | 778 / 36 / 25 / 28 | 2018 | **Historical** — doesn't reproduce its own superzone totals correctly |
| `ths2017/study_taz/matrix_avg_*` | step 5 | Survey matrix (cellular only used to split one coarse zone into TAZs) | 778 / native | 2018 | Current survey source |
| `historical/ths2018/*` | steps 1–4 | Earliest hybrid attempt, from the activities file | 778 / 36 / 25 | 2018 | **Historical** |
| `ths2017/tests/*` | various | Diagnostic tests, not usable matrices | various | — | Diagnostics only |
| `transit/*` | steps 10–11 | Mixed-frame composite (residents' car/other + all-rider bus/rail) | 25 areas | mixed → 2022 | **Historical composite** |
| `forecast_taz/{BU,HS}_{2040,2050}/*` | step 23 | The 2040/2050 growth scenarios, built on the *current* 2022 base | 778 TAZ / 36 / 28 | 2040/2050 | **Current — the four scenario sets** |
| `forecast/*` (older) | older forecast notebooks | 2040/2050 growth built on the *old, historical* composite | 25 areas | 2040/2050 | **Historical** — replaced by step 23 |
| `corridor_v2/*` | step 24 | Corridor flows on a newer 25-area grouping (the "V2 aggregation") | 25 V2 areas | 2022 | Current |
| `lrt_v2/*` | step 25 | The planned LRT line's station-to-station travel times | 24 stations | planned line | Current — main trunk only |
| `gc/*`, `skims/*` | steps 26, 31 | "Generalized cost" components (travel time/cost combined across modes) and full skims | 25 V2 areas | mixed | Current — but still missing money-cost components; some parameters are assumed, not fitted |

**One important note on geography**: there are two different 25-zone groupings in this
project — the "GS zones" (`Input/TAZ_GSnew.csv`) and the "V2 areas"/forecast research
areas. They happen to have the same number of zones (25) but are **not the same
zones**, and files for one must never be matched up with files for the other just
because they're both 25 rows long.

**What the outside review flagged, and what was done about it:** the review found that
the 2040/2050 forecast branch wasn't actually built on the current (survey-only) base —
this is fixed by rebuilding it (tracked as an open task); that the old TAZ-level hybrid
didn't add back up to its own superzone totals — this has been tested and a corrected,
rebalanced version produced; that the bus "coverage rule" needed to vary by trip type —
this is now done ("segmented"); that taxi trips were previously mixed into the bus
layer — they are now split out; and that corridor numbers needed to be clearly labelled
as three-hour "potential movements", not real loads — this labelling has been added,
along with peak-hour figures with uncertainty ranges. Still open: whether the OnBoard
survey rows are single bus legs or full journeys; some double counting risk between bus
and rail; a rough zone-splitting step inside the old hybrids; a smoothing parameter
(**k = 50**) that barely affects results because it's applied to already-large,
already-expanded volumes; the rough, purpose-blind way trips are allocated to fine
zones; how areas just outside the study boundary and three dropped zones are handled;
keeping track of which "vintage" (survey year vs adjustment year) each number is in; and
checking everything against an outside, independent count.

---

### 1. Input data

All of the raw inputs live under `Input/Matrices/` (or `Input/` directly, as noted). Here
is what each file is, plain and simple:

| File | What's in it | Where it's from / how big |
|---|---|---|
| `ACTIVITIES_DEC18_corrected.csv` | The 2018 survey's activity diary: one row for every single activity (trip stop) that every surveyed person recorded, for each day they were surveyed | **172,529 rows**, covering **5,108 households**. Each household was surveyed for **two days** (`ACT_DAY` = 10 and 20: 86,978 and 85,465 rows respectively; a small leftover of 86 rows tagged day 11/22 is ignored). Columns include the household ID, person ID, day, activity ID, start/end time, the type of activity, the zone it happened in, and a "tour" grouping ID |
| `households_with_weights.csv` | The "expansion weight" for each surveyed household — the multiplier used to scale a small sample up to represent the whole real population | **5,108 rows**, exactly one per household, matching the activities file with no gaps or duplicates. Has an original weight (`wf`) and a revised one (`wf_new`) — averaging about **159**, ranging **5 to 350** across households. **`wf_new` is the one actually used everywhere in this project.** |
| `AvgDayHourlyTrips201819_1270_weekday_v1.csv` | The cellular (mobile-phone-derived) OD matrix, for an average 2018–19 weekday, broken down hour by hour, using a national zoning system of 1,270 zones | Only the three morning columns (`h6`, `h7`, `h8`, i.e. 6am–9am) are used here |
| `1270_02_09_2021_TAZ_North_keys.csv` | A lookup table that translates the national 1,270-zone system into the project's own 778 study zones, and also into 36 "superzones" (groups of TAZs) | **400** national zones overlap the study area; one national zone can contain up to **8** study TAZs (on average about 2) |
| `TAZ_GSnew.csv` | A lookup from TAZ to a coarser 25-zone grouping ("GS zones") | Covers **781** TAZs down to **25** GS zones, including zone 105 |
| `taz_keys_from_shapefile.csv` | A stand-in for the main keys table, used automatically when the main one isn't available (e.g. before pulling from Git LFS) | Built directly from the map shapefile. Covers the same 778 TAZs; matches the main keys table exactly except for one zone (TAZ 3602), which the real keys table places differently — that difference is applied as a manual override. This substitute has been checked and matches the main table cell-for-cell where it should |
| `sz_localities.csv` | For each superzone, the two main towns/localities in it | Pulled from the keys table, weighted by population — used only for labelling charts and tables, not for any calculation |
| `trips_ths_2017.xlsx` | The survey's *trips* file (a different, more processed view of the same 2018 survey than the activities file): one row per activity per person per survey day | **146,394 rows**, covering **16,401 people** (the same survey panel as the activities file). Includes an activity-order number, the zone of each activity, the hour the person left, a pre-grouped travel-mode field (car / transit / rail / other), the person's weight, and the reported door-to-door travel time and distance |
| `Corridor_TAZ_Agg_V2.xlsx` (added 22 Sep 2026) | The newer "V2" corridor grouping used for the LRT-specific analysis | Has **25 areas** grouped into three route orderings (a trunk shared by all three, plus a Nazareth branch, a Krayot branch, and a Kiryat Yam branch) and a table matching **174 TAZs** to those 25 areas — all 174 of those TAZs exist in the main 778-zone matrices, and none appear twice. One TAZ (1509, where an LRT station is planned) is not included in this table |
| `hf_lrt_3.shp`, `station_hf_lrt_3.geojson` (added 22 Sep 2026) | The planned LRT route line and its candidate station points | One route line, **18.94 km** long, from Hamifrats to Tirat Carmel; **46** candidate platform points which group into **24** actual stations. Coordinates are converted to the Israel TM Grid for accurate distance measurement |
| `israel-public-transportation.zip` (GTFS feed, added 22 Sep 2026) | The Ministry of Transport's official national public-transport timetable data (stops, routes, trip schedules, etc.) | A standard public-transport data format ("GTFS"); the specific bus-rapid-transit ("Metronit") lines are tagged with codes 83001–83005. Captures the timetable as it stood on **22 May 2026** |
| `Streets.shp`, `std_202605.csv` (added 22 Sep 2026) | Measured road-link driving speeds for buses, from May 2026 | **161,534** street links nationally; **157,618** of them have a matched speed record (a **99.9%** match rate). Speeds are broken out by weekday and hour. Within the study area: **54,507** links (**5,632 km**), of which **48,092** have an actual measured speed |

**A data-quality note worth knowing:** the activities file currently in the project has
*more* records in it than the version used in the very first (original) analysis. Running
the identical processing on both gives **14,912** unweighted AM-peak trips on the current
file versus **11,303** in the old analysis's saved output. Spot checks show the actual
processing logic hasn't changed — the extra records are additional survey entries,
concentrated in a couple of specific zones (0 and 103–106). Practical effect: **none of
the numbers in this document should be directly compared against numbers recorded inside
the very first notebook (`THS_2018_MTX.ipynb`)** — they come from a different underlying
dataset.

---

### 2. The trip-extraction rule used everywhere

Every step that reads the raw survey diary applies the exact same rule to turn diary
entries into "trips". This rule was inherited from the original analysis and has been
kept fixed on purpose, so that results from different steps stay comparable. Here it is,
step by step:

1. Split the diary by which of the two survey days it's from (day 10 or day 20).
2. Within each survey day, sort each person's activities in the order they actually
   happened (by person, by "tour", by activity number).
3. For each person, turn consecutive activities into a trip: the **origin** zone is
   where the *previous* activity happened, and the **destination** zone is where the
   *current* activity happened.
4. Work out the **time the person left** for that trip: if the previous activity was
   "Home", use its recorded *end* time; otherwise use the current activity's *start*
   time.
5. **Keep only trips where the departure hour falls between 6am and 9am** (6 inclusive,
   9 excluded — i.e. the three hours 06:00–08:59).
6. Apply a **"model-area" filter**, added later after auditing the trip definitions:
   - Keep the trip only if **both** its origin and destination are a real, known zone
     (not blank, and not zone "0", which is used for unlocatable/unknown places).
   - Drop the trip if the destination activity's travel mode is recorded as `Default`
     (an internal code, 99), which means no travel mode was actually reported.

**Why rule 6 matters, and why it's safe to apply.** The `Default`/code-99 entries turn
out to almost always be the very *first* activity recorded on a person's survey day
(20,511 out of 20,585 such records) — and a person's first activity of the day can never
be the destination of a real trip, because there's nothing before it to travel *from*.
Checking this directly: of roughly 29,600 trips extracted in the AM peak, only 3 had a
"Default" arrival, so dropping them barely removes anything and prevents a small number
of false ("phantom") trips. Separately, people who never left home all day (10.9% of
person-days, i.e. their whole day is one single "Home" activity) already correctly
produce zero trips, simply because there's nothing to connect them to.

**The filter that actually matters is dropping "zone 0" trips**: **998** sampled trips
(representing **204,000** trips once expanded to the full population — **3.4%** of all
trips) touched an unlocatable zone and, before this filter existed, were sitting in the
raw matrices (often lumped into a meaningless "zone 0 to zone 0" cell). After removing
all of the above, the share of trips that stay inside the same superzone (rather than
crossing into another one) is unchanged at **75%** — which is reassuring: it shows the
survey's tendency to record a lot of short, local trips is real behaviour in the data,
not an artefact created by how trips were extracted.

Note: the original analysis also had a second ("v2") way of deciding departure time
(always using the previous activity's end time, even if it wasn't "Home"). This project
uses the *original* ("v1") rule — as described in step 4 above — throughout.

**How the cellular data is processed** (this had to be reconstructed, since the original
code that built certain columns wasn't preserved): add together the three morning hourly
columns (h6+h7+h8); translate the origin/destination zones from the 1,270-zone national
system into the project's 778 TAZs using the keys table; add everything up into a full
778×778 matrix; then scale each row so it sums to 1 (turning raw volumes into a
"probability" — the share of trips from that zone going to each destination). This
reconstruction was checked cell-by-cell (to six decimal places) against the version saved
in the original analysis, and matched. **One caveat to keep in mind**: this method
assigns the *full* value of one coarse national-zone flow to *every* possible pairing of
the smaller TAZs inside it (up to 8×8 = 64 replicated pairings for the most subdivided
zones). Scaling each row back down to sum to 1 removes most of this distortion, but when
results are added back up to the superzone level, zones that happen to be finely
subdivided can still end up slightly over-represented.

---

### 3. Step 1 — Household-weighted matrices (`THS_2018_MTX_weighted.ipynb`) — [STATUS: historical]

**What it's for.** A raw trip count from the survey only describes the small group of
people who were actually surveyed. Multiplying each of their trips by their household's
expansion weight turns that sample into an estimate for the *whole real population*.
Since every diary activity record is tagged with a household ID, joining in the
expansion weight is a clean, exact match — all 5,108 households match up one-to-one.

**Inputs.** The activity diary (`ACTIVITIES_DEC18_corrected.csv`) and the household
weights (`households_with_weights.csv`).

**How it works.**
1. Apply the standard trip-extraction rule from section 2 above.
2. Build the origin-by-destination table as usual, but instead of *counting* trips in
   each cell, **add up each trip's household weight (`wf_new`)**. So instead of "3 trips
   from zone A to zone B", the cell becomes "3 sampled trips, representing roughly 3 ×
   152 ≈ 456 real trips" (152 being the rough average multiplier — see below).

**Formulas.** No explicit formula is given beyond "sum `wf_new` per origin-destination
pair" — in plain words: for every real trip in the population that a sampled trip
represents, count it once, using the household's own personalised multiplier rather than
one fixed number for everyone.

**Outputs.**
- `Output/matrix_10_weighted.csv`, `matrix_20_weighted.csv` — the actual weighted
  (population-scale) trip counts, one file per survey day.
- `Output/prob_matrix_10_weighted.csv`, `prob_matrix_20_weighted.csv` — the same
  matrices, but with each row rescaled to sum to 1 (a "share of trips from this zone"
  view).

**Tests / checks and what they showed.**

| | Day 10 | Day 20 |
|---|---|---|
| Sampled trips (raw count) | 14,420 | 14,197 |
| Expanded trips (after weighting) | 2,193,422 | 2,163,320 |
| Matrix shape (zones that actually appear) | 656 × 706 | 650 × 695 |

The average expansion factor works out to about **152** real trips per sampled trip, and
this is consistent between the two survey days — a good sign that the weighting isn't
behaving erratically. (For reference: under the *old*, pre-filter trip definition, the
totals were slightly higher — 14,912 / 14,705 sampled and 2,296,819 / 2,264,158 expanded
— since that version hadn't yet dropped the "zone 0" trips described in section 2.)

**Caveats.** None specific to this step beyond the general ones already noted (small
sample, "zone 0" cleanup already applied here).

---

### 4. Step 1b — Validation against cellular (`THS_2018_MTX_weighted_vs_cellular.ipynb`) — [STATUS: diagnostic]

**What it's for.** Before blending the survey and cellular data together (a later step),
this step measures *how well they actually agree* — at two different levels of zoom —
and separately checks whether the household weighting from Step 1 changed that
agreement.

**Inputs.** The weighted survey matrices from Step 1, plus the cellular OD matrix,
processed as described in section 2.

**How it works.**
1. Convert both the survey and the cellular matrices into "probability" matrices — each
   row rescaled to sum to 1, so you're comparing *patterns* of where trips go, not raw
   volumes (which differ hugely in scale between a small survey and population-wide
   cellular data).
2. Compare them at two zoom levels: the fine **778-TAZ** level, and the coarser
   **36-superzone** level. For the superzone comparison, raw weighted counts are added up
   *first*, and only *then* rescaled to sum to 1 — this was found to work best in the
   original analysis.
3. Also build the *unweighted* survey matrices (i.e. before applying household weights
   at all) as a point of reference, to see what effect weighting itself has.
4. Score the agreement using several measures (explained below), both across the whole
   matrix and restricted to just the "dense" part of the range (cells with a probability
   between 0 and 0.25, where most of the real signal lives).

**Formulas / measures used, explained in plain words.**
- **Pearson correlation (r)**: a single number between −1 and +1 that says how closely
  two sets of paired numbers move together in a straight-line way. **+1** means they move
  in perfect lockstep; **0** means no relationship at all. Here, it's applied to every
  matching cell of the survey matrix and the cellular matrix, laid out side by side, to
  ask: "when the cellular matrix says a cell is bigger, does the survey matrix usually
  agree it's bigger too?"
- **RMSE (root-mean-squared error)**: take the difference between the survey and
  cellular value in every matching cell, square each difference (which makes big misses
  count much more than small ones), average all those squared differences, then take the
  square root to bring the units back to normal. A lower RMSE means the two matrices are,
  on average, closer to each other cell by cell.
- **MAE (mean absolute error)**: like RMSE, but just averages the plain (unsquared) size
  of the differences — a simpler, less big-miss-sensitive version of the same idea.

**Outputs.** `Output/prob_matrix_cellular.csv` (the 778×778 cellular probability
matrix), `prob_sz_cellular.csv`, `prob_sz_10_weighted.csv`, `prob_sz_20_weighted.csv`
(the 36×36 superzone versions), plus scatter-plot figures under `Output/figures/`.

**Tests / checks and what they showed.**
1. **Weighting rescales the numbers, it does not change the shape of the pattern.**
   The weighted and unweighted superzone probability matrices correlate at
   **r ≈ 0.998** on both days — near-perfect agreement. Meaning: applying household
   weights barely changes *where* trips appear to go relative to each other; it mainly
   changes the *size* of the numbers (turning sample counts into population estimates).
2. **How well the survey agrees with cellular is basically unaffected by weighting**:
   at the superzone level, r = **0.855** (Day 10) / **0.856** (Day 20) weighted, versus
   **0.854** / **0.855** unweighted — essentially identical. At the fine TAZ level,
   weighting actually **slightly lowers** the correlation (0.283–0.288 weighted versus
   0.294–0.300 unweighted). The likely reason: at TAZ level many cells only have one or
   two sampled trips, and multiplying a single, possibly unusual, trip by a large
   household weight can amplify noise rather than signal.
3. **The zoom level matters far more than the weighting does.** Correlation is only
   about **r ≈ 0.29** at the fine TAZ level but jumps to about **r ≈ 0.86** at the
   coarser superzone level, on the very same underlying data. This tells you that most of
   the TAZ-level "disagreement" between survey and cellular data is just statistical
   sparseness (too few sampled trips per cell to be reliable), not a real, systematic
   difference in behaviour — once you zoom out enough to average that sparseness away,
   the two sources actually agree well.
4. **The one real, systematic disagreement is short, local (intra-zone) travel.** Every
   single one of the 36 diagonal cells (i.e. trips that start and end inside the *same*
   superzone) shows the survey reporting a *higher* share of intra-zone trips than
   cellular does. On average, the survey says **72%** of an average superzone's AM-peak
   departures stay inside that same superzone, while cellular data says only **34%** do
   (for comparison, outside the diagonal — trips leaving the superzone — the two sources
   are far closer: 0.008 vs 0.019 on average). The likely explanation: very short,
   local trips (e.g. walking or a short drive within the same neighbourhood) often don't
   move a phone from one cell-tower area to another, so cellular tracking simply misses
   them, while the survey diary catches them because the person reported them directly.
5. Day 10 and Day 20 behave almost identically on every single one of these measures —
   a good internal consistency check.

**Caveats.** None additional beyond what's captured in the findings above — but note
that this comparison only tells you the *pattern* (row-normalized) agreement; it says
nothing about whether the overall *volume* of trips in either source is correct.

---

### 4b. Step 1c — Weighted matrices by mode (`THS_2018_MTX_weighted_by_mode.ipynb`) — [STATUS: historical]

**What it's for.** Split the already weighted (population-scale) Day 10 / Day 20
matrices apart by travel mode, so each mode can be analysed on its own.

**Inputs.** Same activity diary and household weights as Step 1, plus the survey's
`MODE_NAME` field.

**How it works.**
1. Run the identical trip extraction and household weighting as Step 1.
2. Group the survey's 14 detailed mode categories (which have full coverage — no blanks)
   into four simpler groups:
   - **CAR** — driving or being a passenger in a vehicle, or riding a motorcycle/moped.
   - **TRANSIT** — public bus, the Metronit BRT ("Matronit"), or a special/group taxi.
   - **RAIL** — train.
   - **OTHER** — walking, "Default"/no mode reported, chartered bus, bicycle, other, or
     truck.
3. A trip's mode is decided by the mode recorded on its *destination* activity — i.e.
   the mode used to *arrive*.
4. By construction, the four mode-specific matrices for a given day always add up
   exactly to that day's full all-mode weighted matrix from Step 1 — nothing is lost or
   double-counted.

**Outputs.** `Output/matrix_{10,20}_weighted_{CAR,TRANSIT,RAIL,OTHER}.csv` — eight
matrices in total (four modes × two survey days), each showing weighted OD trip totals
for that mode.

**Tests / checks and what they showed.**

| | CAR | TRANSIT | RAIL | OTHER |
|---|---|---|---|---|
| Day 10 | 1,234,371 (56.3%) | 143,215 (6.5%) | 3,990 (0.2%) | 811,847 (37.0%) |
| Day 20 | 1,202,092 (55.6%) | 143,776 (6.6%) | 4,669 (0.2%) | 812,783 (37.6%) |

The mode shares are stable across the two survey days, which is reassuring. One specific
finding: the "model-area filter" (from section 2 — dropping trips that touch an
unlocatable zone) hits **RAIL** the hardest, cutting expanded rail trips from roughly
**14.7 thousand down to about 4 thousand** per day. The reason is that most surveyed rail
trips have at least one end *outside* the study area, so once the filter is applied, only
a small handful of zones remain with any rail trips at all (11×14 zones on Day 10, 17×15
on Day 20). **Practical takeaway: the RAIL matrix from this step should be treated as
indicative only, not reliable** — the sample left after filtering is too thin.

**Caveats.** The RAIL breakdown is weak and indicative only, for the reason above.

---

### 4c. Step 1d — Sub-area matrices (`THS_2018_MTX_submatrix.ipynb`) — [STATUS: historical]

**What it's for.** Cut the weighted matrices (both the all-mode ones from Step 1 and
the four mode-specific ones from Step 1c) down to a smaller list of **119** specific
study TAZs — useful when analysis only needs to focus on a sub-area rather than the
whole 778-zone study region.

**Inputs.** The weighted matrices from Steps 1 and 1c, and a fixed list of 119 TAZs.

**How it works.**
1. Keep only trips where **both** the origin and the destination are on the list of 119
   zones.
2. Reindex every resulting sub-matrix to the *same* 119×119 layout, in the same zone
   order — so any zone on the list that never actually appears as an origin or
   destination just becomes an all-zero row/column, rather than being dropped from the
   table entirely.
3. As a result, all ten output files (5 matrices per day × 2 days) share exactly the
   same 119×119 shape, and — just like in Step 1c — the four mode-specific files for a
   given day still add up to that day's all-mode file.

**Outputs.** `Output/submatrices/` — ten files, using the same names as their parent
matrices, each 119×119.

**Tests / checks and what they showed.** About **6.5%** of all expanded AM-peak trips
have both ends inside this 119-zone sub-area: **142,532** on Day 10 and **139,007** on
Day 20 — and this share is unchanged by the model-area filter from section 2, because
none of the 119 listed zones include the problematic "zone 0". By mode, the share of
each mode's trips that stay inside the sub-area is roughly: **CAR ≈ 5%, TRANSIT ≈ 9.5%,
OTHER ≈ 7.5%**. RAIL is empty on Day 10 and nearly empty on Day 20 (just 169 expanded
trips) — consistent with the rail weakness already flagged in Step 1c. Separately, **16**
of the 119 zones never once show up as an AM-peak survey origin across the two days
combined (and **15** never show up as a destination) — meaning the survey simply has no
recorded trips touching those particular zones in this window.

**Caveats.** Same rail weakness as Step 1c; several of the 119 zones have effectively no
survey data at all for this window.

---

### 4d. Step 1e — AM-peak trip generation rates per person (`THS_2018_MTX_trip_generation.ipynb`) — [STATUS: historical]

**What it's for.** Work out a **trip production rate**: on average, how many AM-peak
trips does a person living in a given zone make, per survey day? This is a classic
transport-modelling building block ("trip generation").

**Inputs.** The activity diary, the household weights, and the keys table (for mapping
zones to superzones).

**How it works.**
1. Define each person's **home zone** as the zone recorded for their `mainActivity` at
   **3:00 AM** — the survey day is defined as starting at 03:00, and every person's very
   first diary activity of the day begins exactly at that moment. So: if that very first
   activity is tagged "Home", its zone is used as the home zone. This works for **96.4%**
   of person-days; the remaining cases (e.g. night-shift workers, people away from home
   that night) are excluded from *both* the top and bottom of the rate calculation for
   that day, so they don't distort the result either way. As a further sanity check,
   individuals who are recorded as "Home" on *both* of their two survey days sit in the
   *same* home zone **99.99%** of the time — i.e. this home-zone definition is very
   stable.
2. Build the rate as a simple ratio for each zone:
   - **Numerator**: total expanded (weighted) AM-peak trips made that day by people whose
     home zone is this zone — counted using the exact same trip-extraction rule as
     everywhere else, and attributed to the home zone **no matter where in the study
     area the trip itself actually happens**.
   - **Denominator**: total expanded (weighted) number of people whose home zone is this
     zone, counted at 3:00 AM.
3. Also aggregate the same ratio up to the 36 superzones, using the keys table.

**Formulas.** The rate is simply: (expanded AM-peak trips made by residents of the zone)
÷ (expanded number of residents of the zone at 3:00 AM) — in plain words, "trips per
person," specific to the AM peak window.

**Outputs.**
- `Output/trip_generation_taz.csv`, `trip_generation_sz.csv` — per zone, per survey day:
  the sampled and weighted person counts, the weighted trip counts, the rate itself, and
  the two-day average.
- `Output/trip_generation_summary.csv` — a compact, one-row-per-TAZ table with the TAZ
  number, its superzone, the two-day-average trips-per-person rate, and an estimated
  population figure (household weight × observed residents at 3:00 AM, averaged over the
  two days).
- A rate figure (chart) under `Output/figures/`.

**Tests / checks and what they showed.** The **overall** rate comes out to **0.837**
trips per person on Day 10 and **0.833** on Day 20, averaging to **0.835 AM-peak trips
per person**, based on roughly **2.60 million** expanded residents (using the
model-area-filtered trip definition; under the older, pre-filter definition the rate was
slightly higher at 0.872). At the superzone level, rates vary quite a bit — from a low of
**0.63** in superzone 4 up to **1.25** in superzone 25 — showing real differences in how
much different parts of the study area travel in the morning peak. **35** superzones and
**520** home TAZs have at least some data; however, **93** of those TAZs have fewer than
**20** sampled person-days behind their rate, so those specific rates are flagged as
indicative only — too few observations to be fully reliable.

As a cross-check, this diary-based way of identifying someone's home zone was compared
against the *separate* household register (the `TAZ` field in
`households_with_weights.csv`, which comes from where the household said it lived, not
from the 3 AM diary entry). The two agree for about **95%** of households, and where they
disagree it is almost always by one zone into an adjacent zone — a reassuringly small and
explainable mismatch, not a sign of a data problem.

**Caveats.** Rates for TAZs with fewer than 20 sampled person-days (93 of them) are
indicative only. A small number of person-days (3.6%) are excluded from the calculation
entirely because a stable 3 AM home zone couldn't be identified for them.

---

## Part 2 — Blending survey and cellular data, a second independent extraction, bus and rail, and the tests that moved the project to a survey-only base (Steps 2 – 15)


This part covers Steps 2 through 15 of the demand-matrix build: the empirical-Bayes
blend of survey and cellular data at superzone level, its push down to TAZ level and to
a second zoning system (GS), a second independent extraction of trips from a different
survey file, the same blend re-run on that file, trip-generation rates from it, the bus
matrix built from RavKav ticketing data, its combination with an on-board survey, the
train matrix and the combined "adjusted all-mode" matrix, the leveling of everything to
a common 2022 year, and three statistical test notebooks (cosine/GEH, Kolmogorov–
Smirnov, MSSIM) that ultimately led the project to stop trusting the cellular-based
hybrid and switch to a survey-only base with ticketing-calibrated bus (Step 15).

Status tags below are taken from the product/status table in METHODOLOGY.md §0. Where a
step's outputs are not tagged individually there, this is noted rather than guessed.

---

### Step 2 — Superzone hybrid via empirical-Bayes shrinkage (`THS_2018_MTX_hybrid.ipynb`) — [STATUS: historical]

**What it's for.** Combine the household travel survey (THS 2018) with the cellular-
phone-based OD matrix into one blended ("hybrid") matrix, at the coarse 36-superzone
level, so the result uses the survey wherever it has enough evidence and leans on
cellular data (which covers the whole population but is blind to some short trips)
everywhere else.

**Inputs.** The weighted survey OD matrices for Day 10 and Day 20 (Step 1's output), the
cellular row-normalized probability matrix from Step 1b, and the survey's unweighted trip
counts per superzone (needed as the "how much evidence do we have" measure).

**How it works.**
1. For every origin superzone A, and every destination superzone B, look at two
   candidate probabilities of going from A to B: the survey's own probability
   `P_survey(B|A)` and the cellular data's probability `P_cell(B|A)`.
2. Blend them into one number, weighted by how much survey evidence exists for that
   origin. This weighting technique is called empirical-Bayes shrinkage: think of
   `P_cell` as a "prior" (a sensible starting guess based on population-scale data) and
   `P_survey` as new evidence from a sample. If the sample for a given origin is large,
   trust it almost fully; if the sample is small (or zero), pull the estimate back
   ("shrink" it) toward the prior, because a raw estimate from very few observations is
   unreliable.
3. The shrinkage weight is controlled by a single number, `k` (chosen in the next step).
   `k` acts like a pretend sample size for the prior: the prior counts as if it were `k`
   observations. Concretely, if `k = 20` and an origin has only `n_A = 5` real survey
   trips, only 5/(5+20) = 20% of the answer comes from the survey and 80% from cellular.
   If the same origin instead had `n_A = 500` survey trips, it would get 500/(500+20) ≈
   96% weight — almost entirely survey. So a small `k` means "trust the survey quickly,
   even with few observations"; a large `k` means "demand a lot of survey evidence before
   trusting it over cellular."
4. To pick `k`, the notebook runs a cross-day validation test: blend Day 10 with
   cellular and see how well the blend predicts the actual Day 20 pattern (and vice
   versa), for several candidate values of `k` (0, 1, 2, 5, 10, 20, 50, 100, 200, 500,
   1000, ∞). The error measure is the mean Jensen–Shannon divergence (JSD) between the
   predicted and actual destination-probability rows, averaged over origins. JSD is a
   standard way to compare two probability distributions (here, two rows of "share of
   trips going to each destination superzone"): it is 0 when the two rows are identical
   and grows toward 1 as they become completely different. Lower JSD means a better
   prediction.
5. Two deliberate design choices in the formula: `P_survey` is the population-weighted
   row (so it represents the real population's behavior, not just the raw sample), while
   `n_A` — the count that drives the shrinkage weight — is the *unweighted* number of
   sampled trips (because statistical reliability depends on how many independent
   observations you actually collected, not on how big the expansion weights make them
   look).

**Formulas.**
```
P*(B|A) = λ_A · P_survey(B|A) + (1 − λ_A) · P_cell(B|A),    λ_A = n_A / (n_A + k)
```
- `P*(B|A)`: the blended ("hybrid") probability of a trip from origin superzone A going
  to destination superzone B.
- `P_survey(B|A)`: the survey's own (weighted) probability of that same move.
- `P_cell(B|A)`: the cellular data's probability of that move — the prior.
- `λ_A` (lambda): the shrinkage weight for origin A, between 0 and 1 — how much of the
  blend comes from the survey. It depends only on the origin, not the destination.
- `n_A`: number of unweighted (raw, sampled) survey trips observed leaving origin A.
- `k`: the shrinkage constant described above — the "pretend sample size" given to the
  cellular prior. Larger `k` shrinks harder toward cellular.

**Outputs.** `Output/hybrid_sz_prob.csv` (36×36 blended probabilities at the chosen
`k* = 2`), `hybrid_sz_prob_k100.csv` (a more cellular-leaning sensitivity variant at
`k = 100`), `hybrid_sz_trips.csv` (same pattern scaled up to actual average-weekday
AM-peak trip counts, ≈ 2.15M total), `hybrid_lambda.csv` (the `n_A` and `λ` used for each
origin), `hybrid_cv_results.csv` plus CV-curve and lambda-curve figures.

**Tests / checks and what they showed.** The cross-day validation itself is the check.
Result table:

| k | 0 | **2** | 20 | 100 | 500 | ∞ (pure cellular) |
|---|---|---|---|---|---|---|
| mean JSD | 0.0157 | **0.0156** | 0.0177 | 0.0350 | 0.0904 | 0.1964 |

The curve is essentially flat for `k` between 0 and 5, then rises steadily as `k` grows
(more cellular weight makes predictions worse). So the data ask for almost no shrinkage
at this coarse (superzone) scale — i.e., trust the survey almost completely. A version
that excludes the diagonal (trips that stay inside the same superzone) agrees, picking
`k = 5`, about 1% better than `k = 0`. The reason this works is that every origin
superzone already has plenty of survey observations (at least 91 per day, pooled at
least 194, median around 700) — the sample is big enough at this scale to be reliable on
its own, and the gap between survey and cellular (see Step 1b) is a *systematic*
difference (mostly the diagonal / intra-zone trips), not random sampling noise that
shrinkage could fix.

**Caveats.** The two survey days come from the *same households* repeating their routines
twice, so this cross-day check really measures how self-consistent the survey is, not
whether it is objectively correct. It cannot catch a bias shared by both days, and it will
always favor the survey whenever survey and cellular disagree — a structural limitation
of using day-to-day agreement as the tuning criterion.

---

### Step 3 — TAZ-level matrix via superzone correction factors (`THS_2018_MTX_hybrid_taz.ipynb`) — [STATUS: historical]

**What it's for.** Push the superzone-level hybrid (Step 2) down to the fine, 778-zone
(TAZ) level, so the demand matrix can be used at the resolution the LRT corridor study
actually needs.

**Inputs.** The pooled superzone hybrid probabilities from Step 2, the cellular TAZ-level
matrix, and (for the rejected alternative route) the raw TAZ-level survey rows.

**How it works.** Two approaches were tried; only the second was adopted.

1. **Route A (tested, rejected): blend survey and cellular directly at TAZ level**, using
   the same shrinkage formula as Step 2 but computed row-by-row for each of the 778 TAZs
   (with two different priors tried). The cross-day validation again always picked
   `k = 0` (trust the survey completely) — but at this fine resolution a TAZ's row is
   really just a handful of specific households (median 11 sampled trips, and 125 TAZs
   had *zero* trips on Day 10). Because the same people repeat the same TAZ-to-TAZ
   commute on both survey days, "Day 10 predicts Day 20 well" at this scale mostly just
   means "the same few households did the same thing twice" — habit persistence, not
   evidence that the estimate is correct for the wider population. So this cross-day test
   is not a valid way to tune `k` at TAZ resolution, and the route was dropped.

2. **Route B (adopted): correct the cellular TAZ pattern using superzone-level correction
   factors.** Instead of blending noisy TAZ rows directly, the idea is: keep each TAZ's
   own cellular destination pattern (which captures fine, within-superzone detail well),
   but rescale it so that, once you add TAZs back up into superzones, the totals follow
   the trusted superzone hybrid from Step 2. For every pair of superzones A and B, compute
   a single correction factor `R_AB` = (what the survey-informed hybrid says the A→B
   flow should be) ÷ (what raw cellular data says it is). Then multiply every individual
   TAZ-to-TAZ cell that sits inside that A→B superzone block by `R_AB`, and finally
   re-normalize each TAZ row so it still sums to 1 (a valid probability row). The result:
   each TAZ keeps its own fine-grained cellular destination shape, but the overall
   superzone-to-superzone pattern is pulled to match the calibrated (mostly survey-based)
   hybrid.

3. **Converting to trip counts (the "trips version").** The blended probabilities are
   turned into actual trip volumes using the same "survey sets the scale, cellular sets
   the structure" principle: each superzone's total average-weekday departures (from the
   expanded survey) is split among its member TAZs using cellular outflow shares (i.e.,
   cellular data decides how much of a superzone's traffic comes from which of its TAZs),
   and then spread to destinations using the hybrid probabilities from step 2 above.

**Formulas.**
```
R_AB = P*(B|A) / P_cell(B|A)          (from the pooled superzone hybrid)
C̃_ij = C_ij · R_AB                    (scale the individual cellular OD cells)
P̃(j|i) = C̃_ij / Σ_j C̃_ij            (row-normalize)
```
- `R_AB`: the correction factor for the superzone block from A to B — how many times
  bigger (or smaller) the survey-calibrated flow is compared to the raw cellular flow,
  for that whole block of superzone pairs.
- `P*(B|A)`: the Step-2 hybrid probability for that superzone pair (the "truth" the
  correction is aiming at).
- `P_cell(B|A)`: the raw cellular probability for the same superzone pair (what's being
  corrected).
- `C_ij`: the raw cellular trip value for one specific fine TAZ pair `i` (in superzone A)
  to `j` (in superzone B).
- `C̃_ij` ("C tilde"): that same cell after being multiplied by the correction factor for
  its superzone block.
- `P̃(j|i)` ("P tilde"): the final TAZ-level probability of going from TAZ `i` to TAZ `j`,
  obtained by dividing each corrected cell by the sum across its whole row (so the row
  adds up to 1 again).

**Outputs.** `Output/hybrid_taz_prob.csv` (778×778 probabilities, `k_SZ = 2`, follows the
survey wherever it has something to say), `hybrid_taz_prob_k100.csv` (a safer variant
where rare OD pairs matter more), `hybrid_taz_trips.csv` (778×778 trip counts),
`submatrices/hybrid_taz_trips.csv` (a 119×119 sub-area cut, 121,179 trips, 5.6% of the
total), `sz_correction_factors.csv` / `sz_correction_factors_k100.csv` (the 36×36 `R`
tables), `hybrid_taz_cv_results.csv`, CV-curve and R-heatmap figures.

**Tests / checks and what they showed.** Held-out validation (predicting a survey day
with *no* TAZ-level survey input at all): the corrected matrix scores a mean row JSD of
0.671, versus 0.775 for raw cellular alone (about 13% better) — and is about on par with
a much simpler "proportional downscale" approach (0.667). So the correction genuinely
helps, but only modestly, over just scaling cellular data down. Diagnostics on the
correction factors themselves (pooled hybrid, `k_SZ = 2`): the diagonal (intra-superzone)
`R` has a median of 2.21 (up to 13.7) — i.e., the survey wants substantially more
intra-superzone travel than cellular shows, confirming the Step 1b finding. But 45% of
off-diagonal superzone pairs had *zero* pooled survey observations, so their correction
factor falls to a "shrinkage floor" (median ≈ 0.10) — meaning the correction is carrying
over not just the survey's pattern, but also its sparsity (gaps where the survey simply
saw nothing). This motivated the `k_SZ = 100` variant, where the off-diagonal median
correction is a less aggressive ≈ 0.26, keeping more of a cellular floor for OD pairs the
survey never observed. Superzone-level origin totals of the trips version match the
survey's expanded departures exactly (checked in the notebook).

**Caveats.** The block-level correction is followed by re-normalizing each TAZ row on its
own mix of corrected cells — so rows with a large intra-superzone share partly "give back"
some of the correction, meaning the corrected matrix does **not** exactly reproduce the
superzone-level totals it was built from. Step 19 (a later notebook, outside this part's
scope) measured this: for the primary trips-file version of this hybrid, 55 of 627
superzone blocks with over 100 trips deviate by more than 10% from target, the worst by
49%, and a rebalanced matrix was published to fix it. Also, within a superzone, splitting
the origin volume by cellular outflow shares gives each national (cellular) zone a weight
proportional to how many child TAZs it has — the same replicated-zone artifact flagged in
earlier steps — which this rebalancing does not repair.

---

### Step 4 — GS zoning pipeline (`THS_2018_MTX_GS.ipynb`) — [STATUS: historical]

**What it's for.** Recreate everything Steps 2–3 did, but using a second, alternative
zoning system called **GS** (25 zones) instead of the 36 superzones — because a second
geography is needed for some downstream reporting/comparison.

**Inputs.** `Input/TAZ_GSnew.csv` (the TAZ → GS mapping, covering every one of the 778
study TAZs, including TAZ 105, which is missing from the `SZ_NEW`/superzone table used
in Steps 2–3).

**How it works.**
1. Repeat the exact same two methods as Steps 2 and 3 — the empirical-Bayes shrinkage
   blend, then the TAZ-level correction-factor step — but replace the TAZ→superzone
   mapping with the TAZ→GS mapping everywhere. No new method is introduced; this is the
   same math (see Step 2's formula and Step 3's correction-factor formula) applied on a
   different set of zone groupings.
2. Run the same cross-day validation to choose the GS-level shrinkage constant `k`.

**Formulas.** Same as Steps 2 and 3 (`P*(B|A) = λ_A·P_survey + (1−λ_A)·P_cell`,
`λ_A = n_A/(n_A+k)`; and the `R_AB` correction-factor formulas), computed on GS zones
instead of superzones.

**Results.** GS-level expanded trips total 2,193,422 (Day 10) / 2,163,320 (Day 20) — the
same as the full-matrix totals, since the GS mapping covers every model-area TAZ (unlike
the superzone mapping, which was missing TAZ 105). Weighted survey-vs-cellular
correlation at GS level: r = 0.840 (Day 10) / 0.838 (Day 20). Cross-day validation of the
shrinkage constant finds a genuine, if tiny, interior optimum this time: **k\* = 1** (JSD
0.0248 vs 0.0252 at `k = 0`, rising beyond that) — so, like the superzone hybrid, the GS
hybrid is still overwhelmingly survey-dominant (λ ranges 0.909–0.9999; even the smallest
GS origin has 10 pooled observations, enough to be trusted almost fully). Hybrid GS trips
total ≈ 2.18M average-weekday AM-peak trips, slightly above the superzone-based 2.15M
because the GS mapping also covers TAZ 105. GS-level correction factors applied to
cellular TAZ cells: diagonal `R` median 1.89 (max 5.7), off-diagonal median 0.09, with
48% of off-diagonal GS pairs having zero pooled survey observations (the same
sparsity-inheritance issue as Step 3). TAZ-level trip totals built through GS match the
GS survey departure totals exactly (checked in the notebook).

**Outputs.** `Output/prob_gs_{10,20}_weighted.csv`, `prob_gs_cellular.csv` (25×25);
`hybrid_gs_prob.csv` (at `k* = 1`), `hybrid_gs_prob_k100.csv`, `hybrid_gs_trips.csv`,
`hybrid_gs_lambda.csv`, `hybrid_gs_cv_results.csv`; `gs_correction_factors.csv` (25×25);
`hybrid_taz_prob_gs.csv`, `hybrid_taz_trips_gs.csv` (778×778 TAZ matrices, this time
calibrated through GS zones instead of superzones).

**Tests / checks and what they showed.** The cross-day validation curve is the check —
see the `k* = 1` result above. It shows the same broad conclusion as Step 2: the survey
carries almost all the useful information at this coarse a scale, cellular data
contributes only a thin correction.

**Caveats.** None beyond those already noted for Steps 2–3 (this step reuses their
method and inherits their limitations, e.g. sparsity of survey-observed OD pairs feeding
into low correction factors, and the replicated cellular-zone weighting issue).

---

### Step 5 — Matrices from the THS 2017 trips file (`THS_2017_trips_matrices.ipynb`) — [STATUS: current — the survey source used from here on (cellular is used only to split coarse zones into TAZs)]

**What it's for.** Build a second, *independent* extraction of trip matrices, this time
from a different survey data file (the "trips file," `trips_ths_2017.xlsx`) rather than
the activity-diary file used in Steps 1–4. This gives a cross-check of the whole
approach and, from Step 6 onward, becomes the primary survey source.

**Inputs.** `Input/THS_2017-2018/trips_ths_2017.xlsx` — one row per activity per person per survey day,
with a person identifier (`PerID3`), an ordering field (`placeno`), the activity's zone
(`actTaz`), departure hour (`Dep_h`), a pre-aggregated travel mode (CAR / TRANSIT / RAIL /
OTHER, plus `IRR` marking the very first activity of the day), and the expansion weight
`new_wf`. Also `Input/TAZ_2636_Keys.xlsx`, the bridge table between this file's zone
system and the study zone system.

**How it works.**
1. Within each person and survey day, order activities by `placeno`; each trip runs from
   the *previous* activity's zone (`actTaz`) to the *current* one's.
2. The trip's departure hour is taken from the *origin* activity's `Dep_h` field, kept
   only if it falls in {6, 7, 8} (the AM peak).
3. The trip's mode is taken from the *destination* activity's pre-aggregated mode field.
   `IRR` (marking only the very first activity of a person's day) never becomes a trip
   mode — checked and confirmed in the notebook.
4. Every trip's weight is `new_wf`. No `actTaz` value is 0, and zones outside the 778-zone
   study system keep their real (national) zone number, so trips with one end outside the
   region are retained rather than discarded.
5. **Zone conversion.** `actTaz` uses the *national* 2636-zone system, not the study
   system (roughly 310 zone numbers happen to be shared between the two systems, but this
   is coincidence, not a real match). `Input/TAZ_2636_Keys.xlsx` bridges: `actTaz` (2636)
   → `TAZ_1250` (same ids as the study keys' `TAZ_1270`) → study TAZ number. The keys
   cover 100% of trip ends. Because the last link (1250-zone → study TAZ) is one-to-many
   (one 1250-zone can hold up to 8 study TAZs), each trip's weight has to be split among
   the possible child TAZ pairs. This is done proportionally, using cellular data's
   outflow shares on the origin side and inflow shares on the destination side — i.e., if
   cellular data says 70% of a coarse zone's outbound traffic comes from one particular
   TAZ inside it, that TAZ gets 70% of any trip's weight that starts in that coarse zone.
6. Two survey days are averaged cell-by-cell to build a representative weekday matrix,
   since the two survey days are different by activity content.

**Formulas.**
```
M_taz = Sₒᵀ M₁₂₅₀ S_d
```
- `M₁₂₅₀`: the trip matrix at the coarse 1250-zone resolution.
- `Sₒ`, `S_d`: allocation matrices that spread each coarse origin (`Sₒ`) and destination
  (`S_d`) zone's volume across its child study TAZs, in proportion to cellular
  outflow/inflow shares.
- `M_taz`: the resulting fine, study-TAZ-level matrix. In plain words: take a matrix at
  the coarse zone level, and use the (transposed) origin-splitting shares on one side and
  the destination-splitting shares on the other side to "spray" each coarse cell's trips
  out into all the fine TAZ pairs it could represent, weighted by how much of that coarse
  zone's real traffic cellular data says belongs to each fine TAZ.

**Results (expanded AM-peak trips, by mode):**

| | CAR | TRANSIT | RAIL | OTHER | All |
|---|---|---|---|---|---|
| Day 1 | 1,380,188 (62.8%) | 142,924 (6.5%) | 17,219 (0.8%) | 656,482 (29.9%) | 2,196,813 |
| Day 2 | 1,343,321 (61.8%) | 140,585 (6.5%) | 19,210 (0.9%) | 669,334 (30.8%) | 2,172,451 |

Day-averaged matrix: 2,184,632 average-weekday AM-peak trips (CAR 1,361,754 / OTHER
662,908 / TRANSIT 141,755 / RAIL 18,214), with the four mode matrices summing exactly to
the all-mode matrix.

Restricted to trips with both ends inside the study area (excluding 116,473 weighted
trips with an end outside): 2,068,158 average-weekday trips (CAR 1,283,589 / OTHER
645,111 / TRANSIT 134,349 / RAIL 5,109).

**Outputs.** `Output/ths2017/matrix_day{1,2}_{CAR,TRANSIT,RAIL,OTHER,ALL}.csv`,
`matrix_avg_{CAR,TRANSIT,RAIL,OTHER,ALL}.csv` (in the trips-file's own zonation);
`Output/ths2017/study_taz/matrix_avg_{CAR,TRANSIT,RAIL,OTHER,ALL}_taz.csv` (778×778,
allocation-based) and `matrix_avg_ALL_sznew.csv` / `matrix_avg_ALL_gs.csv` (36×36 /
25×25).

**Tests / checks and what they showed.** This is itself a cross-validation of Steps 1–4's
activities-based extraction, using a completely separate survey file. All-mode totals
agree within 0.2–0.4% (2,196,813 here vs 2,193,422 on the activities file, Day 1 vs Day
10) — a strong sign the two independent extractions are measuring the same thing at the
aggregate level. Mode composition differs somewhat (this file assigns more trips to CAR,
≈62% vs ≈56%, and fewer to OTHER; RAIL is much bigger here, 17–19k vs ≈4k, because this
file keeps out-of-region rail destinations that the activities extraction's model-area
filter drops). At the study-system level, the superzone destination-probability pattern
correlates at **r = 0.994** with the activities-based pipeline — meaning the two
independent survey extractions agree not just on totals, but on the *shape* of demand
across the region.

**Caveats.** None specific to this step are flagged beyond the mode-composition
differences already explained by the different filtering rules of the two source files.

---

### Step 6 — Hybrid pipeline on the THS 2017 trips file (`THS_2017_hybrid_pipeline.ipynb`) — [STATUS: historical — superzone OD blocks are not exactly reproduced, per Step 19]

**What it's for.** Rebuild the entire empirical-Bayes shrinkage + correction-factor chain
(Steps 2–4's method) using the trips file (Step 5) as the survey source instead of the
activities file, becoming — at the time — the primary fusion product, while the older
activities-based hybrid set is kept as a historical record.

**Inputs.** The trips-file survey matrices from Step 5 (study-area trips only: 13,476
sampled trips Day 1 / 13,387 Day 2; 2,068,158 average-weekday expanded), the cellular
matrices, and `Input/Submatrix_tazs.xlsx` for the sub-area aggregation.

**How it works.** Identical methodology to Steps 2–3: empirical-Bayes shrinkage with
cross-day validation to pick `k`, then correction factors applied to the cellular
structure, done at both superzone and GS levels. The counts used to drive the shrinkage
weight (`n_A`) come from the *dominant* superzone/GS of each 1250-zone. The final
matrices are day-averaged; the pooled (both-day) counts are used to pick `k`.

**Formulas.** Same as Step 2 (shrinkage blend, `λ_A = n_A/(n_A+k)`) and Step 3
(correction factors `R_AB`), now computed on the trips-file survey data.

**Results.** Cross-day validation now finds a *genuine* interior optimum (unlike the
earlier, nearly-flat curve of Step 2): **k\* = 5** at both superzone and GS levels
(superzone JSD 0.0191 at `k = 5` vs 0.0195 at `k = 0`, then rising). Resulting weights:
λ = 0.962–0.997 at superzone level, 0.706–0.999 at GS level — still very survey-dominant,
but with a slightly bigger role for the cellular prior than in the activities-based run.
Correction factors: superzone diagonal median 2.04 / off-diagonal median 0.18; GS 1.79 /
0.17. The off-diagonal correction factors sit noticeably higher here than in the
activities-based run, because — thanks to the allocation step in Step 5 — the survey side
here already carries some fine (sub-superzone) structure inherited from cellular data,
so it is less "flat" than the activities-based survey rows were. All trip totals are
preserved exactly through the pipeline (checked in the notebook).

Sub-area matrices were also built here: `Input/Submatrix_tazs.xlsx` defines a 205-TAZ
sub-area, grouped into 28 named areas, with 119 of those TAZs forming the LRT corridor
(matching the earlier 119-TAZ sub-matrix list exactly) plus 86 more non-corridor TAZs.
Average-weekday trips in the sub-area: 276,977 all-mode (110,641 within the corridor);
hybrid trips 273,320 (94,610 within corridor); RAIL only 131.

**Outputs.** `hybrid_sz_prob/trips/lambda.csv`, `hybrid_gs_prob/trips/lambda.csv`,
`hybrid_cv_results.csv`, `sz_correction_factors.csv`, `gs_correction_factors.csv`,
`hybrid_taz_prob.csv` / `hybrid_taz_trips.csv` (superzone-calibrated, 778×778),
`hybrid_taz_prob_gs.csv` / `hybrid_taz_trips_gs.csv` (GS-calibrated), and
`submatrices/` (28×28 area matrices, plus `area_legend.csv`).

**Tests / checks and what they showed.** The cross-day validation curve (above) is the
check for this step's own `k` choice; unlike Step 2's essentially-flat curve it shows a
real, if modest, benefit to a small amount of cellular shrinkage. Beyond that, the deeper
statistical testing of how well this hybrid matches reality is done later, in Steps 12–14.

**Caveats.** As later established by Step 19 (outside this part's scope), the corrected
matrix does **not** exactly reproduce the superzone-level OD block totals it was built
from, for the same reason as in Step 3 — the per-row re-normalization after applying
block corrections lets rows with a strong intra-superzone share "give back" part of the
correction.

---

### Step 7 — Trip generation rates on the trips file (`THS_2017_trip_generation.ipynb`) — [STATUS: not individually tagged in the product/status table; parallels Step 1e using the current trips-file survey source]

**What it's for.** Compute how many AM-peak trips an average person makes, per home
zone, using the trips file instead of the activities file — mirroring Step 1e (§4d) on
the newer source, as a check and an updated rate table.

**Inputs.** The trips file (`trips_ths_2017.xlsx`), the validated AM-peak trip extraction
from Step 5, and the zone-keys tables (for aggregating to superzone/GS).

**How it works.**
1. Home zone = the location recorded at 3:00 AM (the `placeno = 1` row, which always
   starts at 03:00), used only where `mainActivity = 1` (Home) — 96.9% of person-days;
   the remaining 3.1% are excluded from both sides of the rate calculation.
2. Numerator: each person-day's validated AM-peak trip count (from Step 5's extraction),
   weighted by `new_wf`.
3. Denominator: expanded number of persons who were home at 3:00 AM.
4. Rates are computed at the native 2636-zone resolution, and then — via each home
   1250-zone's dominant study zone — rolled up to superzone (`SZ_NEW`) and GS levels.
5. Unlike the activities-based rates (Step 1e), **every** AM-peak trip counts here,
   including ones that leave the study area entirely (because every trip in this file
   carries a real zone). So this rate is the *total* generation rate, not restricted to
   model-area trips.

**Results.** Overall rate: **0.831 (Day 1) / 0.827 (Day 2) → 0.829 AM-peak trips per
person**, over about 2.60M expanded persons — close to, but not identical to, the
activities-based rate of 0.835 (Step 1e). The superzone ranking is almost identical to
the activities-based one: superzones 25 and 39 highest (≈1.18 / 1.12 trips per person),
superzones 19 and 4 lowest (≈0.60 / 0.63). 478 home 2636-zones are covered (89 of them
with fewer than 20 sampled person-days, flagged as thin). 209 person-days have homes
outside the northern study area (only visible in the 2636-zone table).

**Outputs.** `Output/ths2017/trip_generation_taz2636.csv`, `trip_generation_sz.csv`,
`trip_generation_gs.csv`, `trip_generation_summary.csv` (with zone codes, rate and
population — total population 2,601,228), and figure `ths2017_trip_generation.png`.

**Tests / checks and what they showed.** The main check is the cross-comparison against
the activities-based rate from Step 1e: 0.829 vs 0.835 trips per person, and an "almost
identical" superzone ranking — a reassuring agreement between two independent
extractions on both the overall rate and its spatial pattern.

**Caveats.** 89 of the 478 covered home zones have fewer than 20 sampled person-days and
are flagged as indicative only (same caveat pattern as Step 1e). Because this file
counts trips leaving the study area, the rate here is not directly comparable cell-for-
cell to the activities-based, model-area-only rate without keeping that distinction in
mind.

---

### Step 8 — Bus RavKav AM-peak matrix by TAZ (`BusRavKav_matrix.ipynb`) — [STATUS: current input]

**Background (why this step exists).** Per `docs/TRANSIT_DEMAND_PLAN.md`, the project
needed a better handle on *corridor transit demand* than the household survey alone could
give: the THS TRANSIT matrix rests on roughly 1,000 sampled transit trips per day,
expanded by a factor of about 150, so individual area-to-area cells are statistically
thin and unstable. RavKav — the national smart-card ticketing system — offered a
near-census of actual bus journeys (around 550,000/day nationally), far more reliable at
fine geography. The decision (documented in that plan) was to bring in RavKav ticketing
data as a second, independent transit-volume source and ultimately prefer it over the
survey for corridor transit demand, while keeping the survey as the base for car/other
modes. This step is the first piece of that: building the RavKav-based bus OD matrix.

**What it's for.** Build an AM-peak bus origin-destination matrix, by TAZ, directly from
smart-card ticketing records — a near-complete count of actual bus journeys, not a
sample.

**Inputs.** `Input/TAZ_North/TAZ_North.shp` (781 TAZ polygons) and four RavKav bus-trip
files for Tuesdays 2022-05-03/17/24/31 (roughly 2.5–2.9 million records each,
nationwide). Each record is one **boarding (leg)**, carrying its own boarding/alighting
stop plus journey-level fields that stay constant across all legs of one journey: the
overall origin/destination stop (first boarding to final alighting), the journey's start
hour, and an expansion weight (`total_boardings`). A `passanger_trip_id` uniquely
identifies each boarding leg; `bus_trip_id` identifies the whole linked journey (which
may include transfers, i.e. several legs).

**How it works.**
1. Spatially join all 27,186 unique stops to the TAZ polygons — 9,924 stops (36.5%) fall
   inside the northern study area.
2. Drop exact duplicate records first (about 7% of rows).
3. Define a **journey** as one `bus_trip_id`, and a **leg** as one deduplicated record.
4. Filter to weekday = 3 (Tuesday) and journey start hour in {6, 7, 8} (AM peak).
5. Weight by `total_boardings`, and average over the four sampled Tuesdays.
6. Build the OD matrix from each journey's overall origin stop to its overall
   destination stop (counting each journey exactly once, so a journey with transfers is
   not double-counted as multiple trips), keeping only journeys with both ends inside
   `TAZ_North`.
7. Separately, build per-TAZ boarding and alighting totals from each individual leg's
   physical boarding/alighting stop (so a transfer journey does contribute at each of its
   boarding points here, unlike in the OD matrix).

**A correction worth flagging explicitly:** an earlier version of this notebook
deduplicated journeys by `passanger_trip_id` instead of `bus_trip_id`. Since
`passanger_trip_id` is unique *per boarding leg*, that earlier version counted every
transfer leg of a multi-leg journey as if it were a separate full journey, which inflated
the area-wide OD matrix by a factor of ×1.52. This was identified and fixed on
2026-09-08.

**Results.** Roughly 510,000–560,000 AM-peak bus journeys nationally per Tuesday, of
which about 17% (94,203 on the average day) have both ends inside the northern study
area — about 70% of the household survey's TRANSIT estimate of 134,349 in-study AM-peak
trips (the ticketing count is lower partly because it requires both ends to be geocoded
inside `TAZ_North`, and it excludes taxi-type modes that the survey's TRANSIT category
includes). Per-TAZ totals: 157,264 average boardings and 147,632 alightings across 730
TAZs; the largest single generator is TAZ 1219 (about 6,500 boardings, 8,900 alightings —
a major terminal). A fifth date file sitting outside the designated `BusRavKav` directory
was intentionally excluded, per the four-file instruction.

**Outputs.** `Output/bus/bus_stops_taz.csv` (stop-to-TAZ lookup), `bus_od_taz_avg.csv`
(722×711 average-Tuesday OD journeys), `bus_boardings_alightings_taz.csv` (per-TAZ
averages).

**Tests / checks and what they showed.** The main validation of this step's numbers is
the discovery and correction of the ×1.52 inflation bug described above — after the fix,
the in-study journey total (94,203) sits at a plausible ≈70% of the survey's transit
estimate, whereas the pre-fix, leg-inflated version would have overstated it. Deeper
comparison against the survey happens in Step 9's "Comparison with THS TRANSIT" and in
the vintage-alignment step.

**Caveats.** RavKav journey origins are **boarding locations**, not doorsteps — right for
loading a corridor with boardings, but not a perfect stand-in for a traveler's true
origin (see Step 9's outlier discussion). Only 36.5% of stops fall inside the study area,
and ridership figures reflect all riders (not residents only), unlike the household
survey.

---

### Step 9 — Bus OD combined with OnBoard survey probabilities (`BusOnBoard_matrix.ipynb`) — [STATUS: current input, open question]

**Background (why this step exists).** RavKav ticketing (Step 8) gives reliable *volumes*
— how many people boarded where — but its destinations (final alighting stops) are
algorithmically inferred by the ticketing system, not directly reported by passengers.
An alternative, on-board passenger survey records where riders say they actually got off,
which should be a more trustworthy *pattern* of destinations, even though it is a smaller
sample. `docs/TRANSIT_DEMAND_PLAN.md` frames this as using "each source for what it
measures well": RavKav for scale (near-census), the on-board survey for destination
accuracy (passenger-reported, not inferred).

**Input.** `Input/6_9_BusProbability_ByTAZ.xlsx` (the OnBoard survey): for 599 origin
TAZs, the probability of alighting at each destination TAZ given boarding at that origin,
for the 6:00–9:00 window. Rows sum exactly to 1, including a `toTAZ = NaN` category for
unknown alighting locations (median share where present: 7.4%).

**How it works.**
1. Build a clean probability matrix: drop the `NaN` (unknown) destination category and
   renormalize each row back to summing to 1 — implicitly assuming unknown alightings
   are distributed the same way as known ones.
2. Build the "new" combined matrix: for each origin, take its total RavKav-measured
   volume (Step 8's row total) and spread it across destinations using the OnBoard
   probabilities instead of RavKav's own inferred destinations. In short: RavKav decides
   *how many* people leave each origin, OnBoard decides *where they go*. Origins that the
   OnBoard survey does not cover (6.4% of total volume) simply keep their original RavKav
   row.

**Results.** Total volume is preserved at 94,203 average-Tuesday journeys (only the
destination pattern changes); 93.6% of that volume gets redistributed using OnBoard
probabilities. The two sources genuinely disagree at fine geography — TAZ-level
correlation between RavKav's own inferred destinations and OnBoard's reported ones is
only r ≈ 0.09, even for high-volume origins — while agreeing much better at the regional
(superzone) scale, r ≈ 0.70. This gap is exactly the rationale for doing the
substitution: RavKav's destinations are algorithmically inferred, OnBoard's are
passenger-reported, so swap in the more trustworthy source at the level of detail where
it matters (fine destination pattern) while trusting RavKav for the coarser volumes.

**Outputs.** `Output/bus/bus_probability_matrix.csv` (594×548, row-stochastic —
each row sums to 1), `bus_od_taz_new.csv` (722×728, the combined matrix), `bus_od_area_new.csv`
(28×28, the combined matrix restricted to the 205 sub-area TAZs and aggregated to the
named areas), `bus_od_area_new_filtered.csv` (25×25 after a noise cut), `bus_growth_2018_2022.csv`.

**Tests / checks and what they showed — comparison with THS TRANSIT at area level.**
This is the key validation cited by `docs/TRANSIT_DEMAND_PLAN.md` as the evidence behind
the decision to prefer RavKav×OnBoard over the household survey for corridor transit
demand:
- **Scale**: sub-area totals — RavKav×OnBoard 23,995 vs THS TRANSIT 26,247
  average-weekday passengers (ratio 0.91). With each journey counted once, the two
  independent sources corroborate each other's overall scale — this is a modest,
  reasonable gap, not a wild mismatch.
- **Cell-level agreement**: correlation r = 0.76 on area-to-area counts. Large
  residential areas sit near parity (Kiryat Yam 0.96, Kiryat Motzkin-Bialik 0.89, Tirat
  Carmel 0.99), while hub/boundary areas are the clear outliers — Hamifrats 9.0× (i.e.
  ticketing shows about 9 times the survey's count there), Kiryat Ata Center 1.9×, Neve
  Yosef 1.8×. The explanation given: ticketing attributes a journey to the area where the
  passenger *boarded* (often a transfer hub), while the household survey attributes it to
  the traveler's *true home origin* — a genuine frame difference, not measurement error.
- **Growth context**: read purely as a 2018→2022 change, the sub-area ratio implies an
  8.6% total decline (−2.2%/year) — described as a real, modest decline (the study team
  separately verified that May 2022 bus ridership was not still COVID-suppressed), though
  confounded by the frame differences above. This is smaller than the −30% decline seen
  in the full, unfiltered study-area comparison, which additionally reflects the
  ticketing frame (both ends must be geocoded, no taxi-type modes counted).

Figure: `Output/figures/bus_vs_ths_transit_area.png`.

**Caveats.** The OnBoard survey's row unit (is each row a boarding leg or a full journey?)
is explicitly flagged as unconfirmed and left as an open question. RavKav's journey
origins remain boarding locations, not doorsteps, so hub areas' apparent "transit share"
partly reflects transfer/non-resident traffic passing through, not local trip generation
by that area's land use — this caveat carries forward into all later steps that use this
combined matrix.

---

### Step 10 — Train matrix, complete transit, adjusted all-mode (`Transit_complete_matrix.ipynb`) — [STATUS: mixed — the train input itself is "current input"; the combined transit/all-mode products (`transit_od_area.csv`, `all_adjusted_area*.csv`, `mode_share_area*.csv`, `car_other_area_2022.csv`) are tagged "historical composite" in the product table]

**What it's for.** Executes the plan set out in `docs/TRANSIT_DEMAND_PLAN.md`: add a
train matrix (built the same way as the bus matrix), combine it with the calibrated bus
matrix into a single "complete transit" matrix, and then substitute this measured
transit layer into the survey's all-mode matrix in place of the survey's own (thin)
transit and rail entries.

**Inputs.** `Input/Matrices/Train_mtx_table.csv` (2019 smart-card data, station-to-
station, with hourly columns), the calibrated bus matrix from Step 9
(`bus_od_area_new_filtered.csv`), and the survey's all-mode / TRANSIT / RAIL sub-area
matrices from Step 6.

**How it works.**
1. Process the train data the same way the bus data was processed (station-to-TAZ
   tagging, sum hours 6+7+8): the `TAZ 9999` "rest of stations" rows (representing
   13,624 out-of-area trips) are ignored, leaving 5,535 average-day trips between the 19
   named stations, of which 962 have both ends in the sub-area.
2. Build the **complete transit** matrix by simply adding the filtered bus matrix
   (23,909 passengers) and the train matrix (962), giving 24,871 passengers at the
   25-area level.
3. Build the **adjusted all-mode** matrix by substitution rather than averaging: take
   the survey's all-mode matrix, remove its own TRANSIT and RAIL components, and add back
   the measured (ticketing-based) transit matrix in their place. Car and other modes,
   where the survey is the only source, are left untouched.

**Formulas.**
```
ALL_adjusted = (survey ALL − TRANSIT − RAIL) + measured transit
```
- `survey ALL`: the survey's own all-mode trip matrix (all modes summed).
- `TRANSIT`, `RAIL`: the survey's own bus/taxi-type and train components, which are being
  removed because they rest on a small, noisy sample.
- `measured transit`: the ticketing-based complete transit matrix from step 2 above (bus
  + train).
- `ALL_adjusted`: the final all-mode matrix — car and "other" travel exactly as reported
  by the survey, but with the transit layer replaced by the better-measured ticketing
  data. In plain words: swap out the weakest ingredient of the survey's all-mode total
  for a more reliable one, without touching the parts the survey does well.

**Results.** `ALL_adjusted` = 260,770 trips; transit share is **9.5%** overall (10.7% in
the corridor areas specifically) against the survey's own reported share of 10.1%. Since
each journey is counted once on both sides of the substitution, this swap is close to
scale-neutral — it mainly changes the *pattern and frame* of the transit layer, not its
overall size. The vintage mix is documented explicitly: base (car/other) is 2018, bus is
2022, train is 2019 — these get leveled to a common year in Step 11.

**Outputs.** `Output/train/train_od_taz_6_9.csv`, `train_od_area.csv`;
`Output/transit/transit_od_area.csv`, `all_adjusted_area.csv`, `mode_share_area.csv`.

**Tests / checks and what they showed.** The mode-share table produced per area shows hub
areas with very high apparent transit shares — Neve Yosef 75%, Hamifrats 50% — but the
text is explicit that these reflect boarding-location and non-resident-frame effects (see
Step 9's caveats), not genuine residential mode choice at those locations; they should
not be read as "75% of Neve Yosef residents take transit."

**Caveats.** The measured transit layer includes non-residents (anyone who boarded a bus
or train there), while the car/other base counts residents only — a frame mismatch that
should be documented rather than read as a behavioral signal. This mismatched-vintage,
mismatched-frame combination is exactly what Step 11 (vintage alignment) and later steps
work to address; the product table in METHODOLOGY.md §0 tags this whole family of
products (`transit_od_area.csv`, `all_adjusted_area*.csv`, `mode_share_area*.csv`,
`car_other_area_2022.csv`) as **historical composite** — i.e., it has since been
superseded as the project's authoritative base, even though within it the raw train input
itself is still marked "current."

---

### Step 11 — Vintage alignment to 2022 (`Vintage_alignment_2022.ipynb`) — [STATUS: historical composite, per the same product-table row as Step 10's combined outputs]

**What it's for.** The adjusted all-mode matrix from Step 10 mixes data from different
years (car/other from the 2018 survey, bus from 2022, train from 2019). This step levels
everything to a single common year, **2022** — the year the RavKav bus data comes from —
by scaling totals ("margins") up or down, while leaving the internal travel *pattern*
untouched.

**Inputs.** `Input/Zonal_2020.csv` (observed 2020 population and total employment by
study TAZ) and `Input/Zonal_BU_2025.csv` (a 2025 forecast of the same variables).

**How it works.**
1. Compute a per-area annual growth factor from the 2020→2025 forecast, then apply it
   only over the 4 years from 2018 to 2022 (see formula below).
2. Population drives the growth factor on the *origin* side of the matrix, since
   AM-peak trip origins are predominantly people's homes. Employment drives it on the
   *destination* side. A handful of pure-employment districts with very low 2020
   population (under 500) — Namal, Hutzot, Kiryat Nahum, Haifa Airport, Hamifrats, Matam
   — fall back to using the employment factor even on the origin side, since population
   there is not a meaningful measure.
3. The 2018 CAR/OTHER area matrix is then rebalanced ("Furnessed") so that its row and
   column totals match these new, grown targets, while keeping the *relative pattern*
   of the matrix as close as possible to the original. This is the standard Furness /
   iterative proportional fitting (IPF) technique: alternately rescale every row so row
   totals hit their targets, then rescale every column so column totals hit theirs,
   repeating back and forth until both sets of targets are satisfied (or close enough) —
   the matrix's internal shape shifts as little as the new margins allow, rather than
   being redrawn from scratch. (Column targets are themselves rescaled to match the
   origin-side grand total, so the two margins are made internally consistent before
   balancing.)
4. Train volumes are scaled by a single national factor: the ratio of national
   heavy-rail ridership in 2022 versus 2019 (54.7 million ÷ 69 million ≈ 0.793) — i.e.
   rail ridership had not recovered from the pandemic by 2022, so this applies a
   "recovery lag" correction.
5. Bus is left untouched — it is treated as the 2022 anchor, since it already comes from
   May 2022 RavKav data, and the study team separately verified that May 2022 bus
   ridership was not still COVID-suppressed. No pandemic correction is therefore applied
   to any component besides rail.

**Formulas.**
```
g = (X_2025 / X_2020)^(4/5)
```
- `X_2020`, `X_2025`: the observed 2020 value and forecast 2025 value of a variable
  (population on the origin side, employment on the destination side) for a given area.
- `g`: the resulting growth factor used to scale that area's 2018 trip totals up to 2022.
  In plain words: the ratio `X_2025/X_2020` is the *total* growth expected over the full
  5-year span 2020→2025. Taking that ratio to the power `1/5` converts it into an
  *annual* growth rate (the constant yearly multiplier that, applied 5 times, gives that
  same total growth). Raising that annual rate to the power `4` instead compounds it over
  only 4 years — matching the 2018→2022 span this step actually needs. Combining both
  steps gives the shortcut exponent `4/5` directly on the 5-year ratio. Example: if a
  zone's population is forecast to grow 10% in total from 2020 to 2025 (`X_2025/X_2020 =
  1.10`), the implied annual rate is `1.10^(1/5) ≈ 1.92%`/year; compounded over 4 years
  that's `1.0192^4 ≈ 1.079`, i.e. roughly the same as `1.10^(4/5)` — about 7.9% growth
  applied from 2018 to 2022.

**Results.** CAR/OTHER area totals rise from 235,899 to 251,684 trips (+6.7%); the
origin-side growth factors range from 0.948 (Nesher, i.e. a slight decline) to 1.256
(Tirat Carmel), with a trip-weighted average of 1.067. Train drops from 962 to 763
trips (the ×0.793 rail-recovery factor). The final `ALL_adjusted_2022` totals 276,355
trips; transit share is **8.9%** overall and **9.9%** in the corridor — close to, but
slightly different from, the mixed-vintage figures of Step 10 (9.5% / 10.7%); the largest
single per-area change from vintage-leveling is just −1.4 percentage points.

**Outputs.** `Output/transit/car_other_area_2022.csv`, `all_adjusted_area_2022.csv`,
`mode_share_area_2022.csv`, `area_growth_factors_2018_2022.csv` (the derived factor table
with population/employment levels per area).

**Tests / checks and what they showed.** The comparison against Step 10's mixed-vintage
figures (8.9%/9.9% here vs 9.5%/10.7% before) is itself the check on this step — it shows
that vintage-leveling shifts the transit-share picture only modestly (at most 1.4
percentage points in any one area), confirming that the substitution done in Step 10 was
close to scale-neutral and that most of the remaining gap between "survey transit share"
(10.1%) and "measured transit share" (8.9%) reflects a genuine, if modest, decline in
2022 ridership relative to 2018 (see Step 9's growth-context discussion) rather than an
artifact of mixing vintages.

**Caveats.** This step's outputs are tagged "historical composite" in the master product
table (§0), meaning this whole line of vintage-aligned, substitution-based products has
since been superseded by the survey-only base built in later steps (15–16), even though
the vintage-alignment method itself (growth factors + Furness rebalancing) remains
sound and is not specifically criticized in the source. As with Step 10, the frame
mismatch (measured transit includes non-residents; car/other counts residents only)
carries forward unresolved here.

---

### Step 12 — Cosine similarity and GEH tests (`THS_2017_cosine_GEH_tests.ipynb`) — [STATUS: diagnostic (regression record)]

**What it's for.** Apply two standard similarity/error measures to compare three AM-peak
matrices — the trips-file survey (Days 1/2), the allocated cellular matrix, and the
primary (Step 6) hybrid — against each other, at four levels of geography: superzone
(36), GS (25), the 28 sub-areas, and full TAZ (778). This is one of the three test
notebooks (Steps 12–14) whose results ultimately drove the project away from the
cellular-hybrid approach toward a survey-only base.

**Inputs.** The trips-file survey matrices (rebuilt with the Step 5 extraction, and
checked to equal `matrix_avg_ALL_taz.csv` exactly — note the older activities file is
*not* used here), the cellular matrix allocated down to TAZ level (using the same
`Sₒᵀ · C₁₂₅₀ · S_d` allocation formula as in Step 5, preserving the study-area total: 580,506
AM trips over 396 native zones — the pipeline's other, "replicated" cellular variant sums
to 6.4× that and is used only as a secondary sensitivity check, not for volume
comparisons), and the primary hybrid from Step 6.

**How it works.**
1. **Cosine similarity** treats a matrix (or a row of it) as one long list of numbers —
   one number per origin-destination cell — and measures the angle between two such
   lists. It ranges roughly from 0 (patterns pointing in unrelated directions) to 1
   (identical pattern). Crucially, it is *scale-free*: if you multiplied every cell of
   one matrix by 10, its cosine similarity to the other matrix would not change at all,
   because cosine similarity only cares about *where* the relative demand sits — which
   cells are big and which are small relative to each other — not the overall size of the
   numbers. It answers: "do the two matrices put trips in the same cells, in the same
   relative proportions?"
2. **GEH** is a standard traffic-modeling tolerance measure for comparing a modeled
   traffic flow against a reference (observed) count on the same link; it is computed
   with a specific formula (below) and, unlike cosine similarity, needs both matrices to
   be on the same real-world scale (it is not scale-free). Widely, GEH under 5 is
   considered "an acceptable match" in traffic-modeling practice for a given link/cell —
   though this step notes how demanding that bar becomes once cells are large (see
   results below).
3. Every statistic is benchmarked against two reference points: survey Day 1 vs Day 2
   (how different two supposedly-identical repeats of the same survey naturally look —
   a "sampling-noise ceiling"), and a **permuted-geography null** (randomly reshuffle
   which zone is which, then compute the same statistic — this shows the score you'd get
   by pure chance, with no real geographic correspondence at all).

**Formulas.**
```
GEH = √(2·(m−c)² / (m+c))
```
- `m`: the modeled/estimated flow value in a given cell (e.g. hybrid or cellular).
- `c`: the comparison/reference flow value in the same cell (e.g. survey).
- `GEH`: a single number combining absolute and relative error, designed so it behaves
  sensibly across a wide range of traffic volumes (a fixed percentage difference matters
  less at very large volumes and more at very small ones). Note in this step, hourly
  flows for GEH are the 3-hour matrix values divided by 3 (since GEH is conventionally an
  hourly-flow statistic).

**Results.**

| | SZ | GS | 28 areas | TAZ |
|---|---|---|---|---|
| Cosine (raw) day 1 vs day 2 / survey vs cellular / hybrid vs cellular | 0.996 / 0.915 / 0.917 | 0.999 / 0.953 / 0.963 | 0.997 / 0.897 / 0.902 | 0.972 / 0.442 / 0.734 |
| Cosine (row-normalized) same pairs | 0.998 / 0.870 / 0.874 | 0.986 / 0.852 / 0.891 | 0.885 / 0.681 / 0.805 | 0.675 / 0.437 / 0.825 |
| Permuted-geography null, mean (raw) | 0.58 | 0.28 | 0.20 | 0.14 |
| GEH < 5, flow-weighted share of cells: day 1 vs day 2 / survey vs cellular (row-matched) / hybrid vs cellular (row-matched) / hybrid vs survey | 46% / 6% / 5% / 94% | 39% / 1% / 2% / 52% | 63% / 9% / 13% / 15% | 79% / 46% / 67% / 39% |

**What these results mean:**
1. **Pattern agreement between survey and cellular is real, but well below the survey's
   own repeatability.** At superzone level, survey-vs-cellular cosine is 0.92, against a
   day-to-day ceiling of 0.996 (near-perfect self-agreement) and a chance level of just
   0.58 — so the agreement is statistically real (confirmed at p < 0.0005 across 2,000
   random reshufflings, at every geography level) but clearly weaker than the survey
   agrees with itself. Per origin, the flow-weighted cosine of destination profiles
   averages 0.89 at superzone level; the worst rows are the two corridor superzones 10
   and 11 (0.33 / 0.46), and this weakness is mostly driven by disagreement on the
   diagonal (intra-zone trips) — off-diagonal, those same origins score much better
   (0.75 / 0.69).
2. **The hybrid, by construction, matches the survey almost perfectly at superzone
   level and looks more like cellular below it.** Hybrid-vs-survey cosine is 1.000 at
   superzone level (94% of flow within GEH 5) — expected, since the hybrid was built to
   follow the survey at that scale. But at TAZ level the hybrid ends up closer to
   cellular (0.83, row-normalized) than to the survey (0.48) — because the survey's own
   TAZ-level pattern is itself just an allocation of cellular shares (see Step 3/5), so
   at fine resolution "the survey" and "cellular" are not fully independent to begin
   with. The correction-factor step moves 33% of TAZ-level flow beyond a GEH-5 tolerance
   relative to the row-matched cellular matrix.
3. **Scale audit.** The survey's expanded volume is 3.56× the cellular volume overall
   (2,068,158 vs 580,506 trips) — a ratio of 2.19 on trips between different 1250-zones,
   and far higher on trips that stay inside one 1250-zone (47% of survey trips are
   intra-zone vs only 14% of cellular trips). Origin-total ratios (cellular ÷ survey)
   range from 0.19 to 0.78 across superzones (median 0.29); even after applying one
   single global scaling factor to correct for the overall size difference, only 11% of
   superzones have origin totals within GEH 5 of each other — meaning cellular
   systematically undercounts short trips, and its zonal totals differ from the survey
   by more than just an overall scale factor.
4. **GEH is a demanding test at these large, aggregated scales**, because the cells
   involved are huge (superzone cells run up to 6,000 trips/hour, where a GEH of 5
   corresponds to only about a ±4% difference). Even the two survey days — which should
   agree almost perfectly — pass the GEH-5 bar in only 46% of superzone flow. Read
   relative to that 46% ceiling, survey-vs-cellular and hybrid-vs-cellular reaching only
   5–13% at superzone/GS/sub-area level is a real, substantial gap, not just statistical
   pickiness.
5. **Corridor-specific pattern.** The row-matched cellular matrix routes 1.8× the
   hybrid's volume from outside the corridor into it (253k vs 138k trips) but only 0.75×
   the hybrid's volume staying inside the corridor (71k vs 95k) — i.e. cellular data sees
   the corridor as more of a magnet for inbound trips and less of a self-contained area
   than the hybrid (survey-informed) view does. Among the 148 sub-area cells with more
   than 100 trips/hour, only 14% are within GEH 5 of the row-matched cellular matrix
   (compared with 57% for day-to-day survey agreement); the biggest disagreements are the
   intra-area cells of Kiryat Motzkin–Bialik, Kiryat Ata South, Tirat Carmel and Kiryat
   Yam (where the hybrid is 2–3× cellular), and cellular's larger flows from the Krayot
   area toward Lower City / Bat Galim / Kiryat Nahum.

**Outputs.** `Output/ths2017/tests/`: `cosine_geh_summary.csv` (headline table),
`cosine_whole_matrix.csv`, `cosine_by_origin_sz.csv`, `cosine_by_origin_summary.csv`,
`cosine_permutation_null.csv`, `geh_scale_audit_{totals,sz,1250}.csv`,
`geh_margins_scaled.csv`, `geh_cells_summary.csv`, `geh_by_flow_band.csv`,
`geh_corridor_classes.csv`, `geh_area_cells.csv`; figures under `Output/figures/`.

**Caveats.** None additional are flagged in this step beyond what the results themselves
already convey — namely that the cellular data's disagreement with the survey is
systematic (a real distributional difference in short-trip detection and corridor
attraction/containment), not just statistical noise that a bigger sample would smooth
out.

---

### Step 13 — Kolmogorov–Smirnov tests (`THS_2017_KS_tests.ipynb`) — [STATUS: diagnostic (regression record)]

**What it's for.** Compare the distribution of trip lengths (and of how concentrated
trips are in a small number of high-volume cells) implied by the same three matrices as
Step 12 (survey, cellular, hybrid), using a formal two-sample statistical test.

**Inputs.** The same three matrices as Step 12; straight-line centroid-to-centroid
distances between TAZs from `Input/TAZ_North` (intra-TAZ trips are given half the
distance to the nearest neighboring centroid, as a proxy for a very short trip).

**How it works.**
1. The **Kolmogorov–Smirnov (KS) test** compares two one-dimensional distributions — so
   it is applied not to the raw OD matrix directly, but to distributions the matrix
   *implies*: the trip-length distribution (how many trips are 1 km, 2 km, 10 km, etc.,
   each trip weighted by its expanded count) and a flow-concentration curve (what share
   of all trips is carried by the busiest handful of cells, versus by many small cells).
2. For each distribution, the KS test lines up the two matrices' cumulative curves (what
   fraction of trips are shorter than X km, as X increases) and finds `D`, the single
   biggest vertical gap between the two curves anywhere along the line. A small `D` means
   the two distributions have very similar shapes; a large `D` means they diverge
   substantially somewhere.
3. The test is run on several variants: the full trip-length distribution (TLD), the TLD
   excluding intra-TAZ trips, the TLD excluding all trips that fall inside one native
   cellular zone, a per-origin-superzone breakdown, a corridor-to-corridor-only version,
   and the flow-concentration curve at both superzone and TAZ resolution.
4. No conventional statistical p-values are reported. With the survey's large expansion
   weights, almost any tiny real difference would come out as "statistically
   significant," which would not be informative here. Instead, `D` is compared against
   two reference benchmarks: the survey's own Day 1 vs Day 2 `D` (self-agreement), and a
   200-replicate bootstrap (repeatedly resampling households at random and rebuilding the
   survey distribution, to see how much `D` naturally varies just from sampling).

**Formulas.** The KS statistic itself: `D` = the maximum absolute gap between two
cumulative distribution curves (share of trips ≤ x, as a function of x). No other
explicit formula is given in the source beyond this definition; `D` is reported directly
as the result.

**Results.**

| `D` (max gap in cumulative trip share) | day 1 vs day 2 | survey vs cellular | hybrid vs cellular | hybrid vs survey |
|---|---|---|---|---|
| TLD, all cells | 0.009 | 0.423 (at 3.7 km; bootstrap 0.41–0.43) | 0.249 | 0.192 |
| TLD, excl. intra-TAZ | 0.011 | 0.374 | 0.242 | 0.153 |
| TLD, excl. intra-cellular-zone | 0.009 | 0.301 | 0.179 | 0.185 |
| per-origin TLD, flow-weighted (SZ) | 0.034 | 0.450 (range 0.28–0.72) | 0.284 | 0.236 |
| TLD, corridor → corridor | 0.017 | 0.387 | 0.276 | 0.123 |
| flow concentration, SZ / TAZ | 0.087 / 0.028 | 0.459 / 0.499 | 0.449 / 0.310 | 0.078 / 0.252 |

**What these results mean:**
1. **Trip lengths in survey vs cellular are genuinely different populations, not two
   noisy readings of the same one.** Median centroid trip length: survey 1.95 km,
   cellular 7.6 km, hybrid 3.8 km; share of trips under 3 km: 62% (survey) / 21%
   (cellular) / 43% (hybrid). `D` = 0.42 for survey vs cellular, against a day-to-day `D`
   of only 0.009 and a bootstrap spread of about ±0.01 — the gap is roughly 40× larger
   than the natural noise band, a very strong signal of a real difference.
2. **It's not just intra-zone trips causing this.** Dropping intra-TAZ cells only brings
   `D` down to 0.37, and dropping every cell that falls inside a single native cellular
   zone still leaves `D` = 0.30 (with the biggest gap now at 4.5 km) — meaning cellular
   data is short of *inter-zone* short trips too (under about 5 km), not just the
   very-local ones. This matches the scale-audit finding in Step 12 (survey/cellular
   ratio 2.19 off the diagonal).
3. **Every origin shows this pattern.** Per-superzone `D` ranges 0.28–0.72, with the two
   corridor superzones 10 and 11 showing the largest gap (0.72 / 0.63; survey median trip
   lengths of 1.5 / 0.8 km there, against cellular's 13.1 / 8.3 km) — versus a day-to-day
   `D` of only 0.01–0.12 for the same superzones.
4. **The hybrid keeps the survey's short trip lengths inside the corridor** (corridor-to-
   corridor `D` vs survey is only 0.12, medians 1.6 vs 1.0 km) but sits between survey and
   cellular elsewhere (outside-to-outside trips: hybrid `D` = 3.7 km vs survey's 1.8 and
   cellular's 7.6 km).
5. **Cellular data is much more spread out (diffuse) than either the survey or the
   hybrid.** At TAZ level, 52% of cellular trips (once scaled to match survey totals)
   sit in cells carrying fewer than 10 trips/hour, against only 11% for the survey and
   29% for the hybrid; the inequality of the distribution (Gini coefficient) is 0.84 for
   cellular vs 0.99 for survey and 0.94 for hybrid — i.e., survey trips concentrate much
   more heavily into a small number of high-volume cells, cellular trips are smeared out
   more evenly. At superzone level, the top 1% busiest cells carry only 24% of cellular
   trips but 47% of survey trips.
6. **Distance-proxy calibration (a sanity check on the distance measure itself).**
   Compared against the survey's own self-reported travel distance (`TrvlDist`), the
   straight-line centroid-to-centroid proxy used throughout this notebook overstates
   short trips somewhat (`D` = 0.23 at a gap around 0.7 km; median proxy distance 1.95 km
   vs 1.11 km reported). Because both matrices being compared use the same proxy, the
   comparisons between them remain fair, but absolute trip-length values under about 1 km
   should be read as partly an artifact of zone geometry, not a precise measurement.

**Outputs.** `Output/ths2017/tests/ks_summary.csv`, `ks0_distance_proxy.csv`,
`ks1_tld.csv`, `ks1_tld_stats.csv`, `ks3_by_origin_sz.csv`, `ks4_corridor_classes.csv`,
`ks5_concentration.csv`, `ks5_concentration_stats.csv`; figures under `Output/figures/`.

**Caveats.** No classical significance (p-value) testing is used, deliberately, because
survey expansion weights would make virtually any difference "significant" regardless of
size — the bootstrap/day-to-day benchmarking approach is used instead specifically to
avoid that pitfall. The absolute trip-length figures below about 1 km are flagged as
partly a zone-geometry artifact of the centroid-distance proxy, not a precise physical
measurement.

---

### Step 14 — MSSIM tests (`THS_2017_MSSIM_tests.ipynb`) — [STATUS: diagnostic (regression record)]

**What it's for.** Apply a third, different kind of similarity test — borrowed from
image comparison — to the same three matrices (survey, cellular, hybrid), one that
specifically rewards getting the local *neighborhood pattern* right, not just overall
totals or shapes.

**Inputs.** The same three matrices as Steps 12–13 (trips-file survey Days 1/2, the
allocated cellular matrix scaled to the survey's total, the primary hybrid).

**How it works.**
1. **MSSIM (Mean Structural Similarity Index)** was originally developed by Wang et al.
   (2004) for comparing images, and has been adapted to OD matrices (by Djukic, van Lint &
   Hoogendoorn, 2013) by treating the matrix like an image, where each cell's trip count
   is like a pixel's brightness value. The method slides a small window (a patch, e.g.
   5×5 or 25×25 cells) across the matrix and compares the two matrices' windows on three
   things:
   - **Luminance** — the *average level* in that window (is the average trip volume
     similar in the same local neighborhood of both matrices?).
   - **Contrast** — how *spread out* the values are within that window (do both matrices
     show a similar mix of busy and quiet cells locally, or is one much flatter/spikier
     than the other?).
   - **Structure** — the *correlation* of the pattern within that window (do the peaks
     and valleys line up in the same relative positions?).
   MSSIM is the average of this window-by-window comparison score across the whole
   matrix, so a good MSSIM score means the two matrices agree not just overall, but
   neighborhood by neighborhood.
2. Because MSSIM specifically cares about *neighboring* rows/columns being real
   neighbors, the TAZs are reordered along a "Hilbert curve" of their geographic
   centroids before running the test. A Hilbert curve is a way of laying a 2-D map of
   points out into a single 1-D sequence such that points that are close together on the
   map stay close together in the sequence — so that when the matrix's rows/columns are
   arranged in this order, a small window in the matrix really does correspond to a
   cluster of geographically nearby zones. (In this ordering, 77% of adjacent matrix rows
   share the same superzone; using the zones' native, arbitrary numbering instead would
   put unrelated zones next to each other and make the test meaningless — an "ordering
   sensitivity" check confirms this matters.)
3. Windows of several sizes are tried (5/9/15/25 cells at TAZ level, 3/5 at superzone
   level, 3 on the 28 sub-areas), and the test is run both on raw trip counts and on
   `log(1 + trips)` — because OD matrix cells span an enormous range (some cells hold
   tens of thousands of trips, most hold very few), and this affects the result
   dramatically (see finding 1 below).
4. Chance level is estimated with a **broken-correspondence null**: keep one matrix in
   proper Hilbert (geographic) order, but randomly shuffle the other matrix's zone
   labels, and recompute MSSIM (averaged over 20–40 random shuffles). This shows what
   score you'd get from a matrix with no real geographic correspondence to the other one.
   A *different* check — randomly reordering *both* matrices the same way — is noted as
   not a valid chance-level test: it keeps every cell pair correctly aligned to each
   other (just relabeled), which actually makes local windows more uniform and can
   artificially inflate the luminance/contrast terms, sometimes scoring *higher* than the
   real, geographically-ordered comparison.

**Formulas.** The formula for MSSIM itself is not spelled out numerically in the source
(it references Wang et al. 2004 and its OD-matrix adaptation by Djukic et al. 2013); the
source instead reports the resulting values and their three-term decomposition
(luminance / contrast / structure), described in plain words above.

**Results (MSSIM, Hilbert order; chance-level null in brackets):**

| | day 1 vs day 2 | survey vs cellular | hybrid vs cellular | hybrid vs survey |
|---|---|---|---|---|
| TAZ, window 9, raw trips | 0.999 (0.98) | 0.993 (0.99) | 0.978 (0.93) | 0.994 (0.99) |
| TAZ, window 9, log | 0.814 (0.14) | 0.128 (0.02) | 0.475 (0.03) | 0.388 (0.11) |
| TAZ, window 25, log | 0.753 (0.08) | 0.112 (0.02) | 0.498 (0.04) | 0.332 (0.09) |
| superzone, window 3, log | 0.686 (0.07) | 0.362 (0.09) | 0.441 (0.09) | 0.938 (0.06) |
| 28 sub-areas, window 3, log | 0.619 (0.07) | 0.257 (0.05) | 0.678 (0.08) | 0.370 (0.06) |
| TAZ, window 9, log — luminance / contrast / structure terms | 0.92 / 0.91 / 0.92 | 0.29 / 0.69 / 0.70 | 0.67 / 0.87 / 0.77 | 0.60 / 0.80 / 0.74 |

**What these results mean:**
1. **On raw trip counts, the test tells you essentially nothing** — every single pair of
   matrices scores 0.97–0.999, and so does the chance-level null. The reason: the formula
   sets its two smoothing constants (`C1`, `C2`) using the matrix's maximum cell value
   (here, the huge intra-zonal cells with tens of thousands of trips), which swamps and
   flattens out the differences in the small-cell windows that make up almost the entire
   matrix. **The log-scale version is the informative one** for OD matrices, since their
   cell values span roughly five orders of magnitude and the raw-scale test cannot
   register differences at that range.
2. **On the log scale, survey vs cellular is close to pure chance at TAZ level**
   (0.128 against a null of 0.02 and a day-to-day self-agreement ceiling of 0.814) — its
   weakest component is luminance (0.29): even in the same geographic neighborhoods, the
   two matrices carry very different average local trip levels — this is the same
   diagonal / short-trip gap seen in Steps 12 and 13, now confirmed window by window.
   Contrast and structure score somewhat better (0.69 / 0.70), meaning the local texture
   (the relative pattern of busy vs quiet cells) is only moderately shared, even where
   the overall levels differ.
3. **The hybrid sits between its two source matrices, and does better than either raw
   pairing, but the picture changes with resolution.** At TAZ level it scores 0.48
   against cellular and 0.39 against survey; at superzone level it is essentially the
   survey (0.94, since it was built to match survey there); at sub-area level it leans
   closer to cellular (0.68). In short, the correction-factor mechanism keeps the
   survey's pattern at the coarse (superzone) level it was calibrated on, and lets
   cellular data shape the finer cells below it.
4. **Where the weaknesses concentrate.** Per origin superzone, survey-vs-cellular local
   similarity scores just 0.05–0.28, with the corridor superzones 19, 21, 20, 11, and 4
   and 10 at the very bottom (≤0.08); the hybrid lifts every single origin up to a
   0.36–0.57 range. Corridor-to-corridor windows specifically: 0.12 (survey vs cellular)
   vs 0.53 (hybrid vs cellular) — against a day-to-day ceiling of 0.67. Blocks *inside* a
   superzone agree better than blocks *between* superzones for survey vs cellular (0.25
   vs 0.11), and much more so for the hybrid (0.76 vs 0.44).
5. **The result is robust to the technical choices made.** Switching between Hilbert and
   native zone ordering changes scores only by 0.01–0.05, and changing the window size
   moves the survey-vs-cellular result by less than 0.03 — so none of the conclusions
   above hinge on these particular methodological choices.

**Outputs.** `Output/ths2017/tests/mssim_summary.csv` (every combination of level,
window, scale, ordering and matrix pair, including the term decomposition and
off-diagonal MSSIM), `mssim_headline.csv`, `mssim_by_origin_sz.csv`,
`mssim_corridor_classes.csv`, `mssim_sz_blocks_*.csv`; figures under `Output/figures/`.

**Caveats.** The raw-trips version of this test is explicitly flagged as uninformative
(see finding 1) — only the log-scale results should be relied on. Together, Steps 12–14
are described in METHODOLOGY.md §0 as having driven the project's conclusion (alongside
external review) that the cellular-based hybrid should be treated as historical, and
that the current base should be survey-only with the bus layer calibrated to ticketing
(Step 15).

---

### Step 15 — Two-mode matrix from the trips file, transit calibrated to RavKav × OnBoard (`THS_2017_two_mode_matrix.ipynb`) — [STATUS: current intermediate]

**Background (why this step exists).** This is the direct consequence of Steps 12–14's
findings: rather than continuing to fuse survey and cellular data (which Steps 12–14
showed disagree in ways that are systematic, not just noisy), this step builds a base
matrix **entirely from the survey trips file**, with no cellular data anywhere in the
chain — but calibrates the bus portion of it against the ticketing (RavKav) and on-board
survey products from Steps 8–9, continuing the approach `docs/TRANSIT_DEMAND_PLAN.md`
set out for transit specifically (use RavKav for volumes, on-board survey for
destinations), now formalized with an explicit statistical blending rule rather than a
simple substitution.

**What it's for.** Produce a second base-year matrix, split into car and transit, where
car comes purely from the survey and transit (mainly bus) is calibrated using a
principled statistical blend of survey and ticketing data rather than either fully
replacing the other.

**Inputs.** The trips file (`trips_ths_2017.xlsx`, Days 1/2), the bus OD matrix from Step
9 (`bus_od_taz_new.csv`), `Input/Zonal_2020.csv` (2020 population and employment), and
zone keys.

**How it works.**
1. **Mode split.** Car = `mainmode` codes 10/11. Transit = bus (codes 3 Public Bus, 4
   Matronit) + taxi-type (codes 5, 8) + rail (code 7). OTHER (walk, bicycle, etc.; 645k
   trips) is set aside entirely, reported separately, and excluded from this two-mode
   base. (From the next step onward, taxi-type is further split out as its own layer,
   separate from bus.)
2. **Zone conversion without cellular data.** The chain is `actTaz` → `TAZ_1250` → study
   TAZ, same as Step 5, but the final one-to-many split is now done using 2020
   **population** shares on the origin side and **employment** shares on the destination
   side (falling back to the other variable, then to a uniform split, where needed) —
   deliberately avoiding cellular data anywhere in this pipeline. 396 zones needed
   splitting: on the origin side, 331 used population, 47 used employment, 18 used a
   uniform split; on the destination side, 378 used employment, 0 used population, 18
   used uniform.
3. **Bus calibration — three separate ideas, each aimed at what a given source measures
   best:**
   - *(a) Destination pattern, at superzone level*: an empirical-Bayes blend, exactly
     the same style of formula as Step 2, but now blending survey with the RavKav×OnBoard
     matrix (from Step 9) as the prior instead of cellular data. `k` is chosen not by
     cross-day validation (which — as in Step 3 — would again just pick `k = 0`, because
     the same households repeat the same commutes on both survey days, so it isn't a
     genuine population-level test) but by a **household-split validation**: randomly
     split households into two halves 40 times, blend on one half, and score how well it
     predicts the other half's rows (mean row Jensen-Shannon divergence, the same measure
     used in Step 2). This finds a genuine interior optimum, `k* = 5` (JSD 0.331, versus
     0.353 for pure raw survey rows and 0.433 for pure ticketing rows) — i.e. the blend
     really does beat either source alone. Resulting weights: λ ranges 0.29–0.97
     (trip-weighted average 0.86) — so on average the survey still carries most of the
     weight, but meaningfully less than in the cellular hybrids, and some origins lean
     heavily on ticketing.
   - *(b) Volumes, per origin superzone × destination segment*: each origin superzone's
     outbound bus trips are split into three destination segments: **local** (staying in
     the same superzone), **inter-superzone, corridor-bound** (going to an LRT-corridor
     superzone), and **inter-superzone, other**. For any segment with at least 5 sampled
     survey trips, its own RavKav-to-survey volume ratio decides which source to trust:
     if RavKav records *less than half* of what the survey does for that segment
     (ratio below 0.5), keep the survey's volume (treated as a coverage guard — assume
     ticketing is simply missing trips there); otherwise, use the RavKav volume. Segments
     with too few sampled trips to judge on their own simply inherit their origin's
     overall decision. Within whatever volume is chosen, the blended destination pattern
     from step (a) spreads it across destinations.
   - *(c) TAZ-level detail*: within a superzone, the split of origin trips among member
     TAZs uses a similar shrinkage blend of survey home-based departure shares and RavKav
     boarding shares (weight `λ`); the split of destination trips among member TAZs uses
     an analogous blend of survey arrival shares and OnBoard alighting shares (weight
     `μ_B`).

**Formulas.**
```
P* = λ_A · P_survey + (1 − λ_A) · P_prior,    λ_A = n_A / (n_A + k)     (destination pattern, superzone level, prior = RavKav × OnBoard)
μ_B = m_B / (m_B + k)                                                   (destination-side shrinkage weight for TAZ-level alighting shares)
```
- Same structure and meaning as Step 2's formula: `P*` is the blended destination
  pattern, `λ_A` controls how much of it comes from the survey versus the ticketing-based
  prior, driven by `n_A` (the survey's sampled trip count for that origin) against the
  shrinkage constant `k` (here, `k* = 5`, chosen by the household-split validation
  described above rather than the cross-day method).
- `μ_B`: the analogous shrinkage weight used on the *destination* side when splitting
  TAZ-level alighting shares, where `m_B` plays the role `n_A` plays on the origin side
  (a count of destination-side evidence) and the same `k` governs how much it is pulled
  toward the OnBoard-based prior.

**Results.** Bus volume moves from 116,083 (raw survey, 2018) to **126,117** under the
segmented rule (a simpler "binary" all-or-nothing version of the rule gives 110,654; an
"all-RavKav" version that always takes ticketing gives 92,713). Within this: the local
segment falls slightly, from 62,090 (survey) to 60,200 (ticketing alone would say
23,277); the inter-superzone segment rises substantially, from 53,992 (survey) to 65,917
(ticketing alone would say 69,436). Overall transit total (bus + taxi-type + rail):
149,492 trips; transit's share of the car+transit base rises from 9.8% (pure survey) to
10.4% under the calibrated rule (corridor-to-corridor: 12.7% → 16.2%). A threshold
sensitivity sweep shows how much the final bus total depends on the 0.5 coverage-guard
cutoff: 117,515 at a 0.3 threshold, 122,160 at 0.4, 126,117 at 0.5 (the adopted value),
130,639 at 0.6, 131,650 at 0.7.

The rule produces 28 origin×segment cells where the coverage guard is triggered (i.e.
survey is kept over ticketing): 17 local segments — the seven superzones originally
flagged as thin-coverage (Nazareth/Kafr Kanna, Shefa-'Amr/Tamra, Sakhnin, Ma'alot/Beit
Jann, Safed, Beit She'an, Daliyat al-Karmel/Isfiya), plus Haifa superzones 14 and 16
(ratios 0.44–0.48), Tiberias (0.05), Afula, Migdal HaEmek, Nof HaGalil, Karmiel, Zichron,
Kiryat Shmona, Pardes Hanna, Hadera — 5 corridor-bound segments, and 6 other segments.
Nazareth's own corridor-bound segment (ratio 0.74) is actually calibrated *to* ticketing,
while its local segment (0.08) and other inter-superzone segment (0.13) keep the survey.

**Tests / checks and what they showed.** Against the RavKav×OnBoard matrix (Step 9), the
final segmented bus matrix scores a cosine similarity of 0.601 at superzone level (up
from a plain survey score of 0.589; the binary-rule variant scores 0.658, the all-RavKav
variant 0.735 — as expected, "trusting ticketing more" scores closer to ticketing) and
0.872 at the 28 sub-area level (vs 0.745 for pure survey, 0.882 for the binary variant),
with 64% of sub-area flow falling within GEH 5 of ticketing (vs 30% for pure survey,
against a day-to-day ceiling of 67%) — a genuine, substantial improvement over using
survey alone, closing a good part (though not all) of the gap to ticketing's own
internal repeatability ceiling. Destination totals — which are never directly imposed by
the calibration, only indirectly shaped by it — independently reach a cosine similarity
of 0.86 against OnBoard-informed alightings, a further sign the calibrated pattern is
behaving sensibly.

**Why the rule is called "asymmetric" and what that implies for the total:** the coverage
guard only ever pulls a segment *up* toward ticketing (when ticketing records more than
half the survey's trips — sometimes much more, up to 3× at transfer hubs) or leaves it at
the survey's level (when ticketing records less than half); it never pulls a segment
*down* below whichever value it started at. As a direct result, the calibrated bus total
(126,117) sits above both pure sources (116,083 survey, 92,713 all-ticketing). A ratio
below 0.5 in a segment does not, by itself, tell you *why* ticketing records fewer trips
there — it could mean ticketing genuinely misses some trips (bus operators outside the
RavKav data extract, cash-fare riders, un-geocoded stops) or it could mean the survey's
own expansion overstates short local bus travel in that area. The 0.5 threshold is
therefore explicitly labeled a stated assumption rather than a proven cutoff, and the
alternative variants (binary-rule, all-RavKav) are published alongside the primary result
so the sensitivity is visible. As one concrete illustration: the raw RavKav extract
records only about 3,500 AM boarding legs in the Nazareth superzone against 12,400
survey-expanded bus trips there — and since the ticketing files carry route IDs but no
operator field, it is unknown (a question left for the ticketing data provider) which bus
operators the RavKav extract actually covers, and whether cash or unvalidated boardings
are included in it at all.

**Outputs (`Output/ths2017/two_mode/`).** `car_{taz,sz,area}.csv`,
`transit_{taz,sz,area}.csv` (calibrated), `transit_survey_*.csv`,
`bus_calibrated_{taz,sz,area}.csv`, `bus_survey_*`, `taxi_survey_taz.csv`,
`rail_survey_taz.csv`, variants `bus_calibrated_binary_guard_{taz,sz}.csv`,
`bus_calibrated_all_ravkav_{taz,sz}.csv`, `bus_calibrated_uniform_factor_taz.csv`;
calibration tables `bus_calibration_cv.csv`, `bus_calibration_lambda_sz.csv`,
`bus_calibration_factors_sz.csv` (origin-wide ratios, the simple binary rule),
`bus_calibration_factors_segments.csv` (the segmented rule's per-origin×segment survey
and RavKav trips, ratio, sample count, basis, guarded flag, and factor),
`bus_calibration_threshold_sensitivity.csv`, `bus_pattern_sz_prob.csv`,
`bus_calibration_validation.csv`, `bus_calibration_destinations_sz.csv`;
`mode_share_sz.csv`, `mode_share_corridor_classes.csv`; figures `two_mode_bus_cv.png`,
`two_mode_transit_share.png`.

**Caveats.** Vintages are mixed within this step: RavKav-volume-driven segments reflect
May 2022, guarded (survey-kept) segments reflect 2018, and car, taxi-type and rail are
all 2018. Frame issues carried over from `docs/TRANSIT_DEMAND_PLAN.md` still apply
(boarding-stop origins vs true doorstep origins; ticketing includes non-residents).
Below the 1250-zone level, the survey's own TAZ-level detail is not a direct observation
but a population/employment-based split (see "Zone conversion" above) — so fine TAZ
detail should be read as an allocation, not a measurement. The OnBoard survey's row unit
(a boarding leg or a full journey?) remains unconfirmed, carried over as an open question
from Step 9.

---

## Part 3 — The current 2022 base, corridor demand, growing to 2040/2050, and the planned LRT line's travel times (Steps 16 – 25)


This section explains, in plain language, what steps 16 through 25 of the study do. Each
step corresponds to one notebook. "Potential movements" is the study's own term for a
travel-demand number that comes from an origin-destination matrix and is loaded onto a
route — it is **not** a measured passenger count on an actual bus or train. Keep that
distinction in mind throughout: most of these steps produce potential movements, not
observed loads.

---


### Step 16 — 2022-base layers: car, bus, taxi-type, rail (`THS_2017_three_mode_2022.ipynb`) — [STATUS: current]

**What it's for.** The travel survey (THS) was collected around 2018. This step moves the
survey's car/transit matrix (from step 15) forward to a **2022** reference year, and splits
it into four separate layers: **car**, **bus** (only the calibrated Public Bus and Matronit
trips), **taxi-type** (survey mode codes 5 and 8 — shared or hired taxis — kept as their own
layer because nobody is sure exactly what those codes cover, and there's no reason to assume
taxis behave like a scheduled bus), and **rail**.

**Inputs.**
- The survey's 2018-based two-mode matrix from step 15.
- `Input/Zonal_2020.csv` and `Input/Zonal_BU_2025.csv` — observed 2020 and forecast 2025
  population and employment per TAZ (traffic analysis zone), used to build growth factors.
- National heavy-rail ridership totals for 2019 and 2022 (54.7 and 69.0, units not stated
  in the source, presumably millions of annual riders) and a 2019 rail smartcard
  station-to-station matrix.

**How it works.**
1. For every TAZ, calculate a growth factor `g = (X_2025 / X_2020)^(4/5)`. This is a
   compound-growth calculation, similar to compound interest: take the ratio between the
   2025 forecast and the 2020 observed value, and raise it to a fractional power (4/5) to
   land on the right point along that growth curve, rather than assuming growth happens in
   a straight line.
2. Use the TAZ's **own** growth factor (population for origins, employment for
   destinations) only where that TAZ's 2020 base value is at least 500 — 606 origin TAZs
   qualify this way on population, 506 destination TAZs on employment. Below that, a TAZ's
   own number is too small and noisy to trust as a growth rate.
3. TAZs with essentially no population (pure-employment zones, 72 of them) use the
   employment growth factor on the origin side too, since there's no population figure to
   grow.
4. All remaining, smaller TAZs (100 on the origin side, 272 on the destination side) borrow
   their **superzone's** growth factor instead of trying to compute their own.
5. Each mode is grown differently:
   - **Car**: rebalanced ("Furnessed" — see step 23 below for the full explanation of this
     balancing technique) to the grown margins, using one overall grand total taken from the
     origin side.
   - **Bus**: split into two groups of cells. "Anchored" cells are those whose origin and
     time segment already had real 2022 RavKav (smartcard) ticketing volumes feeding the
     earlier calibration (step 11) — these are treated as already correct for 2022 and left
     completely untouched. "Guarded" cells (everything else, not backed by ticketing) are
     simply multiplied by their TAZ's origin growth factor.
   - **Taxi-type**: rebalanced the same way as car.
   - **Rail**: the survey's door-to-door rail matrix is multiplied by a single national
     ratio, 54.7 / 69.0 = 0.793, reflecting how national heavy-rail ridership changed from
     2019 to 2022 (2018 values are simply treated as equal to 2019, since no 2018 figure is
     available). A parallel 2019 station-to-station smartcard matrix is scaled by the same
     ratio and saved alongside it.

**Formulas.**
- `g = (X_2025 / X_2020)^(4/5)` — X is population (origins) or employment (destinations).
  In plain words: take the five-year growth ratio between 2020 and 2025, and compress it
  down to whatever fraction of that period (here, 4/5) is needed to move the survey from its
  2018 base to the 2022 target, assuming the growth rate is steady year over year rather than
  a flat addition.
- Rail scaling: `rail_2022 = rail_survey × 54.7/69.0 = rail_survey × 0.793`.

**Outputs (`Output/ths2017/three_mode_2022/`).** `{car,bus,taxi,rail}_2022_{taz,sz,area}.csv`,
`all_modes_2022_taz.csv`, `rail_station_smartcard_2022_taz.csv`,
`growth_factors_taz_2018_2022.csv`, `summary_2018_2022.csv`, `summary_sz_2018_2022.csv`;
figure `three_mode_2022.png`. (Two earlier, duplicate file names from a first version were
removed because their content matched files already produced under other names.)

**Tests / checks and what they showed.** This step's main "check" is really its before/after
summary table, showing 2018 vs 2022 totals per layer:

| | 2018 base | 2022 base |
|---|---|---|
| Car | 1,283,589 | 1,353,798 (+5.5%) |
| Bus (calibrated, excl. taxi) | 126,117 | 129,653 (anchored cells 69,066 unchanged; guarded cells 57,051 → 60,587) |
| Taxi-type | 18,266 | 19,359 |
| Rail (survey, door-to-door) | 5,109 | 4,050 |
| Bus / taxi / rail share, all trips | 8.8% / 1.3% / 0.4% | 8.6% / 1.3% / 0.3% |
| Bus share, corridor → corridor | 11.7% | 11.0% |

Origin growth factors: median 1.050, and 1.055 once weighted by how many car trips each TAZ
carries (the largest single factor is about 1.28, in Pardes Hanna-Karkur and Tirat Carmel).
Destination factors: weighted average 1.135, before the destinations are rescaled to match
the origin-side grand total. A notable and counter-intuitive result: corridor-bound car
trips actually **fall** by 5.8% between 2018 and 2022, even while every other travel class
grows. The source is explicit that this is because the BU-2025 demographic forecast puts
corridor employment growth *below* the regional average — a real property of the scenario
being used, not an artifact of the survey or the method. Separately, a station-based rail
alternative check finds 763 trips with both ends' stations inside the sub-area, versus only
104 door-to-door survey rail trips there — a large gap between two different ways of
counting rail demand, flagged but not resolved in this step.

**Caveats.** The exact meaning of taxi-type survey codes 5/8 is unconfirmed. The bus
layer's growth for "guarded" cells still depends on the same ticketing-coverage
limitations noted elsewhere in the study. The corridor car-trip decline is a genuine
property of the 2025 demographic scenario, not a survey artifact — it should not be read
as "car demand is falling on the corridor" in general. Rail relies on a single national
scaling ratio rather than a route- or zone-specific one, and blends the 2018 level flat
onto the 2019 level for lack of a 2018 figure.

---


### Step 17 — Corridor profile of potential movements (`Corridor_flow_profile_survey_2022.ipynb`) — [STATUS: current — three-hour potential movements]

**What it's for.** Turns the step-16 area-level 2022 matrices into a link-by-link profile
along the planned LRT corridor: how much demand would load onto each stretch of the line if
every trip between two line areas travelled along the line between them.

**Inputs.** The step-16 area matrices (car, bus, taxi, rail, 2022); the 18 corridor
"AggAreaCode" areas in line-sequence order. Three areas — Adi, Alon Hagalil and Tzipori —
are left out of this sequence, as they were in earlier work, with a note that they are to be
added back later with their uncertainty flagged (an open task, B2).

**How it works.**
1. Take the 18 line areas in order along the planned route.
2. For every origin-destination pair where **both ends** sit on this 18-area line, load that
   pair's trips onto **every link** of the line between the origin and destination area, in
   the correct direction of travel. For example, a trip from area 3 to area 8 is counted on
   the links 3–4, 4–5, 5–6, 6–7 and 7–8.
3. Do this separately for three groupings: **total** (car + bus + taxi + rail), **transit**
   (bus + rail only), and **taxi-type** on its own.

**Formulas.** No numeric formula beyond the loading rule above (a demand-assignment rule,
not an equation).

**Outputs.** `Output/ths2017/three_mode_2022/corridor_link_flows_{total,transit,taxi}_2022.csv`,
`corridor_link_flows_comparison_2022.csv` (this step's profile set alongside earlier ones,
plus the link-level transit share); figures
`corridor_flow_profile_{total,transit}_survey2022.png`.

**Tests / checks and what they showed.** This step functions as a comparison against an
earlier version of the same profile. Total corridor-internal demand comes out at 71,113
trips, against an earlier matrix's 101,004 — the source explains the gap: the earlier
number included walk/other modes and used a different car data source, so the two are not
directly comparable, not evidence of an error. The busiest link, Bat Galim – Kiryat
Eliezer, carries 6,852 trips towards Nazareth and 6,847 towards Tirat Carmel (versus 7,671 /
7,576 earlier); the Haifa-side profile matches the earlier version closely, while the
Krayot-to-Nazareth segment now carries less demand in both directions. For transit
(bus+rail): 8,622 corridor-internal trips, with the busiest links at Ein Hayam – Bat Galim
(1,661 towards Nazareth) and Neot Peres – Neve David (1,650 towards Tirat Carmel). Taxi-type
adds a further 3,606 corridor-internal trips, up to 1,415 on Ein Hayam – Bat Galim. Transit
makes up 16–37% of total link flow on the Haifa segment.

**Caveats.** Every value here is a three-hour (06:00–09:00) total of potential movements —
it does not represent station access, choice between parallel routes, how demand is spread
within the three hours, or trips that only have one end on the line. Three corridor areas
(Adi, Alon Hagalil, Tzipori) are excluded from this profile pending a task to reinstate them
with flagged uncertainty.

---


### Step 18 — Corridor transit profiles: calibrated survey vs ticketing (`Corridor_profile_hybrid_vs_ticketing.ipynb`) — [STATUS: current — three-hour potential movements]

**What it's for.** Checks whether the step-17 transit profile (built from the calibrated
survey — bus plus survey rail) agrees with an independent profile built directly from
ticketing data (step 11: RavKav card taps plus on-board survey plus station-train counts),
link by link and direction by direction.

**Inputs.** The step-17 transit profile; the step-11 ticketing profile; intermediate
calibration stages (the raw, uncalibrated 2018 survey bus numbers, and an "all-RavKav"
variant); the area-pairs behind the biggest differences; the local-vs-intercity split of
ticketing coverage within the "guarded" superzones (the superzones whose calibration is
directly tied to ticketing coverage).

**How it works.**
1. Compare calibrated-survey transit (bus + rail) against ticketing-based transit, link by
   link and per direction, with taxi-type shown on its own so it doesn't distort the
   comparison.
2. Also compare the calibration's intermediate stages (raw uncalibrated survey, and an
   all-RavKav variant) to see how much each calibration step actually moved the numbers.
3. Identify which area-to-area trip pairs are responsible for the largest differences
   between the two profiles.
4. Compute transit's share of total link flow, separately in both matrix sets.
5. Split the ticketing coverage figures into local (within-superzone / between-superzone)
   trips versus intercity (into the Haifa superzones) trips, for the guarded superzones.

**Results.** Towards Nazareth (direction 1 → 23): the calibrated-survey transit runs at
0.63–1.05 times the ticketing transit along the Haifa segment (0.87 on average over the
segment); the raw, uncalibrated survey was 25–40% lower than ticketing before calibration.
An apparent 1.5× gap seen in earlier work turns out to have been the taxi-type layer, which
is now kept separate — once removed, survey and ticketing broadly agree in this direction.
Towards Tirat Carmel (23 → 1) the ticketing profile is still about 2× the survey from Bat
Galim to Kiryat Bialik South, and about 3× near the Nazareth end. This gap traces to
specific journeys ticketed as starting from the Nazareth Area (1,363 tickets vs 430 in the
survey — a 9,900-trip difference on the link), from Hamifrats (782 vs 561) and from Neve
Yosef (741 vs 296), all heading into Haifa's western districts.

The key finding: **the segmented coverage-correction rule that fixed other gaps in earlier
steps does not close this one, and could not.** At the superzone level, Nazareth's
corridor-bound segment is already correctly calibrated against ticketing (ratio 0.74) — so
the totals look fine in aggregate. The real shortfall is hiding one level down, in how that
superzone total gets spread across individual line areas and TAZs, and in a mismatch of
"destination frame": survey trips are placed into Haifa TAZs by employment share (a proxy),
while ticketed journeys are recorded at the actual trunk-route stop where the passenger got
off — plus some further issues in how trips get attributed to transport hubs.

The coverage-based approach IS the right fix for the local market: in Nazareth, ticketing
captures only 8% of the survey's intra-superzone (very local) bus trips, 34% of
inter-superzone trips, but 74% of trips specifically into the Haifa superzones; other
guarded superzones show local coverage of just 0.05–0.24 (i.e. very sparse). But it is the
wrong diagnosis for the corridor-bound market, where the actual gap lives.

Transit's share of total link flow on the Haifa segment: 16–26% (1→23) / 14–37% (23→1) in
the calibrated-survey set; 15–27% / 18–55% in the ticketing set (whose total also counts
walk/other modes, so the two "totals" are not exactly like for like).

**Outputs.** `Output/ths2017/three_mode_2022/corridor_profile_hybrid_vs_ticketing.csv`,
`corridor_profile_components.csv`, `corridor_profile_pair_contributions.csv`,
`corridor_profile_coverage_local_vs_intercity.csv`; figures
`corridor_profile_hybrid_vs_ticketing.png`, `corridor_profile_transit_share.png`.

**Tests / checks and what they showed.** The step itself is a check: two independently
built transit profiles are set side by side. Result: good agreement towards Nazareth once
taxi-type is separated out (0.63–1.05×); a real, persistent 2–3× gap towards Tirat Carmel
that a targeted fix (the segmented coverage rule) cannot close, because the gap's actual
cause — how survey trips get spatially allocated versus where ticketed trips are actually
recorded — sits below the level that rule operates on.

**Caveats.** The segmented coverage rule is confirmed correct for local-market shortfalls
but explicitly wrong for the corridor-bound (23→1) gap; the true cause (superzone-to-area
allocation and destination-frame mismatch, plus hub attribution) is diagnosed but not fixed
within this step. The ticketing set's totals include walk/other modes, so transit-share
comparisons between the two sets are not perfectly apples-to-apples.

---


### Step 19 — Superzone conservation test and rebalanced hybrid (`Hybrid_superzone_conservation_test.ipynb`) — [STATUS: diagnostic test, with a corrected historical output]

The source's own status table lists this step's diagnostic-record outputs under "diagnostics
(regression record)" and its corrected TAZ hybrid file under "historical branch, corrected" —
so this step is best read as a diagnostic test that produces one corrected historical
product.

**What it's for.** Checks whether the detailed TAZ-level "hybrid" matrix built earlier
(steps 3/6) actually reproduces the coarser superzone-level hybrid matrix it was built from,
if you add the TAZ cells back up. This is a **conservation test**: if a detailed matrix is
genuinely a breakdown of a coarser one, summing the fine pieces back together should exactly
reproduce the coarse totals. A review comment (review §5) pointed out that the original
notebooks had only ever checked this for origin totals, never for full origin-destination
blocks — this step fills that gap.

**Inputs.** `hybrid_taz_trips.csv` (the primary TAZ-level hybrid, plus an older
"activities file" version kept for history) and `hybrid_sz_trips.csv` (the superzone-level
hybrid the TAZ version was supposedly built from).

**How it works.**
1. Re-aggregate ("sum up") the TAZ-to-TAZ hybrid matrix into superzone-to-superzone
   (`SZ_NEW`) blocks, for both the primary and the historical version.
2. Compare each re-aggregated block against the true value recorded in
   `hybrid_sz_trips.csv`.
3. Having found mismatches, rebalance the primary TAZ hybrid using iterative proportional
   fitting (IPF, also called Furness balancing — explained fully under step 23 below), with
   two sets of hard constraints it must hit exactly: every superzone origin-destination
   block total (from `hybrid_sz_trips.csv`), and every TAZ's origin total (unchanged from
   before). Destination (column) totals are left free. The current, unbalanced TAZ hybrid is
   used as the starting point.
4. Check that both constraint sets are satisfied within tolerance after rebalancing.

**Formulas.** The rebalancing step uses iterative proportional fitting / Furness, the same
alternating row-then-column adjustment method described in full detail under step 23, but
applied here with a different pair of targets: superzone OD blocks (instead of simple row
totals) and TAZ origin totals (instead of column totals).

**Outputs.** `Output/ths2017/tests/hybrid_sz_conservation_summary.csv`,
`hybrid_sz_conservation_worst_blocks.csv`; `Output/ths2017/study_taz/hybrid_taz_trips_balanced.csv`,
`hybrid_taz_prob_balanced.csv`; figure `hybrid_sz_conservation.png`.

**Tests / checks and what they showed.** This is the core content of the step.

*Before rebalancing, the primary hybrid:* origin totals matched exactly — no problem there.
But of the 627 superzone-to-superzone blocks that carried more than 100 trips, 55 (about
9%) deviated by more than 10%, and 12 (about 2%) by more than 25%. The single worst case is
reported as "SZ 35 → 3, +49%" — a block where the TAZ-reaggregated value badly overshoots
what the true superzone matrix says it should be. Averaged across all blocks and weighted
by flow, the mean error is small — 2.0% — but off-diagonal (between-superzone) trip mass
came out 3.6% too high overall, and diagonal (within-superzone) cells up to 6% too low. In
plain terms: conservation mostly holds, but breaks down noticeably in a couple of dozen
specific blocks, with a systematic tendency to move slightly too much demand between
superzones and slightly too little demand within them.

*Before rebalancing, the historical (activities-file) hybrid:* did notably worse — even
origin totals were off, by up to 6.7% for one TAZ mapping (TAZ 105), and 80 blocks deviated
by more than 10%, 20 by more than 25%.

*The rebalancing itself:* converged in just 4 iterations (an internal block-error tolerance
under 10⁻⁴), and moved only about 1.0% of total trips overall. Most individual cell
adjustment factors were modest — the middle 90% of cells (5th–95th percentile) were
multiplied by between 0.86 and 1.01, with a median close to 1 (0.97), meaning most cells
barely moved while a smaller number needed larger corrections. Corridor-to-corridor demand
moved from 94,610 to 95,348 trips as a result.

**What "rebalanced well" does and doesn't mean here.** The rebalancing fixes the
superzone-block totals and keeps the TAZ origin totals unchanged, and the notebook's final
assertion (blocks within 1%, origin totals within 0.1%) passes. But the source is explicit
that this does **not** repair the fine, within-block cell structure — which cells inside
each block get how much — because that structure still comes from the earlier "replicated
cellular mapping" (§2 of the source): a method where a single coarse national cellular flow
gets applied at full value to every possible TAZ-pair inside it, sometimes up to 8×8 times
over. This step does not touch that underlying distortion.

**Caveats.** Rebalancing corrects block totals and preserves origin totals, but the
cell-level pattern inside each superzone block still carries the replicated-cellular-mapping
distortion. The older, historical (activities-file) hybrid performs worse on this test and
is not the version that gets rebalanced/corrected here — only the primary hybrid receives
the corrected, balanced output.

---


### Step 20 — Peak hour on the corridor (`Corridor_peak_hour_2022.ipynb`) — [STATUS: current — peak-departure-hour potential movements]

**What it's for.** Steps 17 and 18 report three-hour (06:00–09:00) totals. For design work
you need the single busiest hour, not a three-hour average. This step finds when that peak
hour occurs, how sharply peaked it is, and re-expresses the link-level profiles in
peak-hour terms.

**Inputs.** The survey trips file's exact departure time, to the minute (`STDep`); the
step-15 AM extraction allocated to TAZs and to the 28 corridor sub-areas.

**How it works.**
1. `Dep_h` (the survey's rounded-down departure hour) is checked against a proper reading of
   `STDep` and the two agree 99.5% of the time — a data-quality check on the survey itself.
2. The step-15 AM trips, allocated to TAZs and up to the 28 corridor sub-areas by the same
   population/employment split rule used elsewhere, are grouped into 15-minute departure
   bins across the whole 06:00–09:00 window.
3. For each layer (car, bus, taxi-type, rail/walk-other), the **peak hour** is found by
   sliding a 60-minute window across those 15-minute bins (so it can start at :00, :15, :30
   or :45) and picking whichever window contains the largest share of that layer's
   three-hour trips.
4. Two ratios describe how peaked demand is:
   - **PHF₃ₕ** = peak-hour trips ÷ three-hour trips. If demand were spread perfectly evenly
     across the three hours, an average hour would carry exactly 1/3 = 0.333 of the total —
     so PHF₃ₕ tells you how much more concentrated the real peak hour is than a flat
     average.
   - **PHF₆₀** = peak-hour trips ÷ (4 × trips in the single busiest 15-minute bin). If
     demand within the peak hour were spread evenly across its four quarter-hours, this
     would equal 1; a lower value means there's a sharper mini-spike inside the peak hour
     itself.
5. Profiles are built at three levels: (a) study-area-wide, per layer; (b) for trips between
   line areas, split by direction and layer, weighted by how many links each trip crosses;
   (c) at the individual link level.
6. A 200-replicate household bootstrap (repeatedly resampling the household sample with
   replacement and recomputing) is run to gauge how much the corridor-level estimates in (b)
   could plausibly vary just from the survey's limited sample.
7. Deciding which factor to actually apply to the step-17/18 link profiles: use the
   direction-specific corridor factor (computed just from trips on the corridor, towards
   Nazareth or towards Tirat Carmel) only where that direction has at least 100 sampled
   trips backing it up — true only for car (194 and 236 sampled trips). Every other layer
   (bus: 1,636 sampled trips overall, taxi-type: 253) falls back to the broader,
   study-area-wide factor for that layer; rail borrows the bus factor, since rail has too
   few observations of its own.
8. Note: the factor is defined on departure time, but the actual peak on a link further
   along the route lags the departure-time peak by however long it takes to travel there.

**Formulas.**
- `PHF₃ₕ = peak-hour trips / three-hour trips` (an average, unpeaked hour would be 0.333).
- `PHF₆₀ = peak-hour trips / (4 × trips in the busiest 15-minute bin)`.

**Results.**

| Layer | Peak hour (study area) | PHF₃ₕ study area | PHF₆₀ study area | PHF₃ₕ corridor 1→23 (n) | PHF₃ₕ corridor 23→1 (n) | Applied |
|---|---|---|---|---|---|---|
| Car | 07:00–08:00 | 0.621 | 0.69 | 0.661 (194; bootstrap 0.51–0.81) | 0.626 (236; 0.47–0.75) | direction-level |
| Bus | 07:00–08:00 | 0.590 | 0.75 | 0.655 (48; 0.54–0.84) | 0.435 (26; 0.43–0.79) | study area 0.590 |
| Taxi-type | 07:00–08:00 | 0.580 | 0.68 | 0.784 (35) | 0.837 (25) | study area 0.580 |
| Walk / other | 07:00–08:00 | 0.793 | 0.64 | — | — | not in the profile |

The peak hour carries roughly 1.8× an average hour. Per-link factors are identifiable only
for car (19 link-directions have at least 30 sampled trips), and those scatter from −0.12 to
+0.19 around the direction-level factor (mean +0.03); bus links have at most 25 sampled
trips, too few for a reliable per-link factor.

Peak-hour potential movements (2022 layers): transit (bus + rail) reaches 981 trips on Ein
Hayam – Bat Galim towards Nazareth (the three-hour total there is 1,661; a flat average hour
would be 554) and 974 on Neot Peres – Neve David towards Tirat Carmel (1,650 three-hour / 550
average). All layers combined: 4,609 towards Nazareth on Ein Hayam – Bat Galim, 4,205 towards
Tirat Carmel on Bat Galim – Kiryat Eliezer.

**Sensitivity check.** How much would the busiest transit link's peak estimate change
depending on which sample the bus factor is drawn from — study-area-wide / corridor
directions pooled together / corridor direction-specific? The estimate for Ein Hayam – Bat
Galim towards Nazareth moves between 981 / 835 / 1,089 trips depending on the choice; for
Neot Peres – Neve David towards Tirat Carmel it moves between 974 / 829 / 718. This is a
meaningful swing (roughly ±20–30%), showing the applied bus peak-hour figures carry real
uncertainty depending on methodological choice.

**Outputs.** `Output/ths2017/three_mode_2022/peak_hour_factors.csv` (all levels, with hourly
shares and bootstrap ranges), `peak_hour_factors_applied.csv`, `peak_hour_factors_by_link.csv`,
`corridor_link_flows_peak_hour_2022.csv` (per link and direction: three-hour, average-hour and
peak-hour flows by layer), `peak_hour_sensitivity.csv`; figure
`corridor_flow_profile_peak_hour_2022.png`.

**Tests / checks and what they showed.** Three internal checks sit inside this step: (1) the
`Dep_h`-vs-`STDep` consistency check (99.5% agreement — the timing data is trustworthy); (2)
the bootstrap ranges, which show the corridor-level PHF₃ₕ estimates have wide uncertainty
bands, especially for bus and taxi-type where sample sizes are small (n = 25–48); (3) the
sensitivity analysis of which factor basis to apply, which shows the choice can move a
peak-hour result by roughly 20–30%.

**Caveats.** These remain potential movements in the peak departure hour, not real vehicle
loads — none of the caveats from steps 17/18 (no station access, route choice, within-hour
peaking, or off-line trip ends) are resolved here. Reliable per-link peak factors exist only
for car. The bus and taxi-type applied factors depend on the study-area-wide value because
the corridor sample is too thin to support a direction-specific estimate, and the
sensitivity check shows this choice matters by a meaningful margin. The departure-time
factor and the actual peak moment on a downstream link are offset by the travel time to
reach that link.

---


### Step 21 — PCA: car vs transit destination structure (`THS_2017_PCA_car_vs_transit.ipynb`) — [STATUS: diagnostic (regression record)]

**What it's for.** Checks whether car trips and transit trips, drawn from the same survey,
go to the same kinds of places in the same proportions — do the two modes share a
destination-choice "shape"? And where do they diverge? This reuses the PCA (principal
component analysis) approach used in earlier steps (12–14 and the PCA notebooks of §8b),
but this time splits the data by travel mode instead of by data source.

**Inputs.** The trips file, using the step-15 extraction (AM trips, both ends inside the
study area, weighted by household); the population/employment zone split; groups defined as
car (mode codes 10/11), transit (codes 3, 4, 5, 7, 8), with bus alone (codes 3, 4) run as a
sensitivity check; two geographic resolutions — 36 superzones (35 usable as an origin) and
28 sub-areas (16 usable, because transit trip counts are thinner there).

**How it works — what PCA actually does, in plain terms.**
1. Build a table where each row is one origin place (a superzone or sub-area), and each
   column is a possible destination; each cell holds the **share** of that origin's trips
   going to that destination, so every row sums to 1 (a "destination profile" for that
   origin). This is built separately for car and for transit.
2. Run PCA on this table. In plain words: instead of describing every origin's destination
   profile as dozens of separate percentages, PCA finds a small handful of underlying
   "shapes" or "recipes" that, mixed in different amounts, reconstruct most of the real
   differences between origins. For example, one shape might be "a general pull towards
   Haifa versus away from it" and another might be "how self-contained (local) this origin's
   trips are." The first component ("shape 1") is whichever single pattern explains the most
   variation between origins; the second explains the next-most on top of the first; and so
   on. This is done separately for car and for transit, producing each mode's own list of
   shapes.
3. Compare car's shapes to transit's shapes: if car's leading shape and transit's leading
   shape point in nearly the same direction across all the origins, that means the same
   underlying geography drives both modes. If they point differently, car and transit riders
   are systematically choosing different kinds of destinations.
4. To judge whether a measured amount of "overlap" is meaningful, it is checked against
   three references:
   - **Repeatability** — each mode's own pattern compared against itself, using day-1 vs
     day-2 survey responses from the same households. This gives the practical ceiling: even
     a mode compared with itself is never a perfect match, because of ordinary survey noise,
     so this tells you the most agreement you could ever expect.
   - **A permuted-geography null** — the destination shares are randomly shuffled among
     origins, then the same overlap measure is computed. This gives the floor: how much
     "overlap" appears purely by chance, with no real shared structure.
   - **A 200-replicate household bootstrap**, to see how much the overlap estimate itself
     varies from one resample of the survey to the next.
   - **A restricted run** using only origins with at least 20 sampled transit trips, since
     transit's survey sample is much thinner than car's, and results built on very few trips
     are less trustworthy.
5. Tests labelled T1–T6 (carried over from the earlier PCA suites in §6j–§6l and §8b) are
   also run; the source does not restate what T1–T6 individually check in this section.

**Formulas / key quantities, explained.**
- **Subspace overlap** — a single number from 0 to 1 measuring how much car's leading shapes
  and transit's leading shapes point in the same directions, versus unrelated directions. A
  value near 1 would mean identical shape; a value near the permuted-null number would mean
  no more agreement than chance.
- **Repeatability** — the same kind of overlap measure, but comparing a mode against itself
  (day 1 vs day 2). This is the ceiling any cross-mode overlap can realistically approach,
  because no matter how similar two modes truly are, survey noise limits how cleanly any
  single mode's own pattern can be measured.
- **Self-containment** — for a given origin, the share of that origin's own trips that stay
  within the same area or superzone. PCA surfaces this as one of the leading shared shapes.
- **The sign-flip / divergence test** — after finding that car and transit broadly overlap
  overall, this checks specifically whether the *difference* between them (transit minus
  car) points the same way for many different origins (a real, consistent shift) or is just
  noise scattered in random directions (no shift).
- **% of transit variance captured by car's components** — if you try to reconstruct
  transit's destination profiles using car's shapes instead of transit's own, how much of
  transit's real pattern-to-pattern variation can you explain? Compared against how much
  transit's own components explain of themselves (its repeatability), this shows how well
  car's structure stands in for transit's.

**Results (superzone level, k = 20 components).** Car vs transit subspace overlap = 0.75
(bootstrap range 0.66–0.76; permuted-null mean 0.57, maximum 0.70, p = 0.0005) — the observed
overlap sits clearly above chance (even the null's most extreme run only reached 0.70), so
car and transit genuinely share real structure. Set against car's own repeatability (0.95,
very consistent) and transit's own repeatability (0.81, noisier, as expected from a thinner
sample), the 0.75 overlap is real but incomplete: the two modes are not identical. On the
well-sampled origins alone (more trustworthy data), the overlap rises to 0.83 against
transit's repeatability there of 0.86 — closer, suggesting some of the shortfall at the full
sample was itself survey noise. Car's components capture 86% of the variance that transit's
own components capture of transit (versus transit's own repeatability of 89%). The leading
shape-pairs match closely (0.72 and 0.79): the first shared shape is a general geographic
axis, the second a self-containment / Haifa-bound axis.

Where the modes diverge: mean self-containment is higher for car (0.62) than for transit
(0.45) — across origins, more of each origin's car trips stay local than its transit trips.
But only 44% of the total squared divergence between car and transit sits on this
self-containment (diagonal) axis — compare that to 87% for the earlier survey-vs-cellular
comparison — meaning most of the car-vs-transit difference is *not* simply a self-containment
effect; it's spread across the broader pattern. Consistent with that, removing the diagonal
from the comparison barely changes the overlap (still 0.72). The sign-flip test does find a
real, consistent direction of divergence (p = 0.04): transit systematically moves share away
from peripheral destinations (Tirat Carmel, Umm al-Fahm, Beit She'an, Ma'alot: about −2
percentage points each) and towards the Haifa core (superzones 16, 14, 13, 12: +2 to +3
points each), relative to car. This shift is about 1.5× the size of transit's own normal
day-to-day noise — real, not jitter. Among well-sampled origins, the largest specific
departures: from Rekhasim / Zevulun, 45% of transit trips go to the Haifa superzones versus
only 9% of car trips; from Shefa-'Amr / Tamra, 66% vs 14%; from Tirat Carmel, 71% vs 23%.

**By resolution.** At the 28-area corridor level (origins with ≥10 sampled transit trips,
14 of them): overlap 0.57 against transit's own repeatability of 0.65 and car's 0.91 (with
only ≥20-trip origins, 8 of them: 0.64 vs 0.70) — the two modes are about as alike as transit
is to itself, and nothing finer can be resolved at this level; self-containment car 0.42 /
transit 0.23; the direction of the mean shift matches the superzone-level finding (Lower
City, Kiryat Nahum, Matam, Neot Peres gain transit share; Nesher Lower, Tirat Carmel,
Hamifrats lose it), but with only 14 origins no statistically common direction can be
detected (p = 0.6). At TAZ origins × superzone destinations (133 TAZs with ≥5 transit trips,
k = 15): overlap 0.75 against transit's repeatability of 0.89 and car's 0.90, with a
detectable common direction (p = 0.002) — the source flags this as the resolution where the
systematic mode difference is best established. At TAZ × TAZ (same 133 origins, k = 35):
overlap collapses to 0.27, against transit's repeatability of 0.55, car's 0.71 and a chance
level of 0.05; car's components capture only 39% of transit's variance; self-containment car
0.13 / transit 0.06 — only the coarse geography is shared at this fine resolution, not the
detailed destination cells.

**Reading, in the source's own words.** Car and transit share the dominant structure, but
transit is systematically less local and more Haifa-core-bound; a transit market cannot be
read off the car pattern by simple scaling, and a transit-specific destination pattern (as
used in the step-15 calibration) is warranted. Nothing can be concluded at TAZ level or
within Haifa itself from the survey's thin transit sample.

**Addendum, 22 September 2026 — the V2 corridor areas.** The same tests, run on the 25 newer
V2 corridor areas: with the 14 origins that have ≥10 sampled transit trips, overlap is 0.55
(k=6) against transit's repeatability of 0.76 and car's 0.79; with the 7 origins of ≥20
trips, 0.76 against 0.80 / 0.97; across all 22 usable origins, 0.59 against 0.62 / 0.79.
Self-containment 0.42 (car) vs 0.25 (transit); no statistically common direction is found
(p = 0.28–0.54); using only the 12 trunk areas leaves just 4 usable origins. The source's
conclusion: which side of transit's own noise floor the overlap number lands on depends
heavily on which handful of origins happens to be included — this resolution is
sample-limited and adds no new conclusion beyond the superzone and TAZ-to-superzone results.
Per-origin patterns still repeat: Kiryon sends 35% of transit trips to the Haifa trunk areas
vs 6% of car trips, Kiryat Bialik Center 30% vs 6%, Kiryat Yam B+C 31% vs 8%; Nazareth (83
sampled) is 90% self-contained for transit and 96% for car.

**Outputs.** `Output/ths2017/tests/pca_car_vs_transit_{summary,overlap,rcev,by_origin,levels,by_area}.csv`;
figures `Output/figures/pca_cvt_{scree,subspace_overlap,component_match,divergence,levels}.png`.

**Tests / checks and what they showed.** The whole step is itself a battery of checks. The
central one: is the observed car-vs-transit overlap (0.75 at superzone level) meaningfully
different from both pure chance (permuted null 0.57 — yes, real shared structure exists) and
from perfect agreement (repeatability ceiling around 0.8–0.95 — no, they are not identical)?
It lands genuinely in between: real but incomplete overlap. A second check (the sign-flip
test) confirms the divergence has a real, consistent direction (transit favours the Haifa
core over the periphery, relative to car), not just noise. A third check (removing the
self-containment/diagonal component) shows the divergence is not simply a self-containment
effect — it survives across the broader pattern. Reliability degrades sharply with finer
geography: usable and informative at superzone and TAZ-to-superzone level, essentially
unusable at TAZ-to-TAZ resolution (0.27, barely above the 0.05 chance floor) and
sample-limited at the newer 25-area V2 geography.

**Caveats.** Transit's much smaller survey sample limits reliability, especially at finer
geographic resolutions. At the V2 25-area level, the result depends heavily on exactly which
handful of well-sampled origins are included, so it adds no firm conclusion beyond the
superzone and TAZ-to-superzone results. Nothing can be concluded at TAZ level or specifically
within Haifa. This step's findings are the stated justification for keeping car and transit's
destination patterns separate in later steps (step 15's calibration, and step 23's growth
process, which grows each mode along its own superzone pattern rather than a shared one).

---


### Step 22 — Final 2022 TAZ matrices: car, transit, total (`Final_matrices_2022.ipynb`) — [STATUS: current — the deliverable set]

**What it's for.** This is the assembled, headline 2022 deliverable — no new modelling is
done here, just definitions and summation of the step-16 layers.

**Inputs.** The step-16 layer outputs: `car_2022_taz`, the calibrated bus layer, the survey
door-to-door rail layer, and the taxi-type layer.

**How it works.**
1. **car** = `car_2022_taz` (unchanged from step 16).
2. **transit** = bus (calibrated) + rail (survey door-to-door). Taxi-type is deliberately
   left out of this headline transit total, because of the uncertainty around what its
   survey codes actually represent (noted in step 16).
3. **total** = car + transit.
4. Taxi-type is instead carried as a separate variant (`transit_incl_taxi`,
   `total_incl_taxi`) rather than being silently folded into the headline numbers.
5. A long-format version is also written — one row per non-empty origin-destination cell,
   with columns `orig_taz, dest_taz, car, bus, rail, taxi_type, transit, total` — compressed
   with gzip, intended for loading into a SQL database, along with a manifest and a summary
   file.

**Formulas.** `transit = bus + rail`; `total = car + transit`. These are direct sums, not
statistical formulas.

**Outputs.** `Output/final_2022/{car,transit,total,transit_incl_taxi,total_incl_taxi}_2022_taz.csv`,
`final_2022_long.csv.gz`, `final_2022_summary.csv`, `MANIFEST.csv`.

**Tests / checks and what they showed.**

| Layer | All | Corridor → corridor | Corridor → outside | Outside → corridor | Outside → outside |
|---|---|---|---|---|---|
| Car | 1,353,798 | 72,331 | 47,011 | 89,181 | 1,145,275 |
| Transit (bus + rail) | 133,704 | 9,366 | 10,104 | 18,799 | 95,434 |
| **Total (car + transit)** | **1,487,501** | 81,697 | 57,115 | 107,980 | 1,240,709 |
| Taxi-type (variant) | 19,359 | 3,812 | 1,359 | 5,479 | 8,709 |
| Transit share of total | 9.0% | 11.5% | 17.7% | 17.4% | 7.7% |

Three internal consistency checks are reported: (1) the four component layers add up
cell-by-cell to the previously-produced `all_modes_2022_taz.csv` — nothing was lost or
duplicated when reassembling them; (2) the long-format file's grand total matches the
matrix file's grand total — the format conversion to SQL-friendly form didn't drop or
duplicate anything; (3) a density check — of the 605,284 possible TAZ-pair cells
(778 × 778), 351,223 carry some demand. The source explains that the bus layer alone is
dense because its calibration spreads each origin's ticketed volume across a blended
destination pattern, while car is much sparser (only 24,173 non-zero cells) because it
sticks closer to the survey's actually-observed pattern.

**Caveats.** Taxi-type is kept out of the headline transit/total figures because its
behaviour is uncertain, carrying forward step 16's caveat. The bus layer's high cell density
is a byproduct of how it was calibrated (spread over a blended pattern), not necessarily a
sign that real bus travel is genuinely that dispersed — worth remembering when reading
"non-zero cells" as a coverage measure.

---


### Step 23 — Growing the 2022 TAZ matrices to 2040/2050 (`Forecast_matrices_TAZ_2040_2050.ipynb`) — [STATUS: current — the four scenario sets, produced 22 September 2026]

**What it's for.** Projects the finished 2022 TAZ matrices (step 22) forward to two future
years — 2040 and 2050 — under two demographic scenarios, labelled **BU** and **HS** in the
source (the source does not spell out what these initials stand for; that is left ambiguous
here rather than guessed). This replaces an older, cruder forecast built on 25 aggregated
areas, which is now marked historical.

A crucial framing point from the detailed methodology document: this produces a
**demographic reference**, not an LRT forecast. It moves the 2022 travel pattern to match
future population and jobs, but keeps 2022's trip rates, destination-choice behaviour and
mode split completely fixed. It contains no service change, no LRT, no change in car
ownership, fares, telework or age structure. It is the "do-nothing" baseline that a separate
service-response model (`docs/LRT_CAPTURE_PLAN.md`) would be compared against — it is not
itself a forecast of LRT demand.

**Inputs.**
- `Output/final_2022/{car,transit}_2022_taz.csv`, `Output/ths2017/three_mode_2022/taxi_2022_taz.csv`
  — the 2022 base layers from steps 22 and 16.
- `Input/Zonal_2020.csv`, `Input/Zonal_BU_2025.csv` — observed 2020 and forecast 2025
  population/employment, used to bridge to a 2022 demographic level.
- `Input/Demographic_Forecast/Zonal_{BU,HS}_{2040,2050}.csv` — scenario population
  (`POPULATION`) and employment (`EMPL_TOT`) per TAZ — the growth targets.
- `Input/taz_keys_from_shapefile.csv` — TAZ-to-superzone mapping.
- `Input/Submatrix_tazs.xlsx`, `area_legend.csv` — corridor area definitions, for reporting.

**How it works.**

*0. Bridging to a 2022 demographic level.* There is no directly observed 2022
population/employment figure, so it is interpolated between the observed 2020 value and the
forecast 2025 value: `X_2022 = X_2020 · (X_2025/X_2020)^(2/5)` — the same style of
compound-growth calculation used in step 16, here representing "2 years of the way through a
5-year (2020–2025) trend," assuming growth compounds steadily rather than in a straight
line. Both the BU and HS scenarios share this same bridge; they only start to differ from
2022 onward.

*1. Margins — deciding where the future growth in trip-making goes.* A morning trip's
destination is not purely a function of jobs: schools, shops and homes receiving return
trips all attract morning arrivals too, so a TAZ whose arrivals come mostly from a school
should not triple just because a small nearby job count triples. Rather than splitting trips
by purpose (an open task not yet done), the study builds two **composite land-use indices**
— one for how much a TAZ generates as an origin, one for how much it attracts as a
destination — each a weighted blend of population and employment. The blend weights are
fitted once (not separately per travel layer) on total 2022 demand (car + transit +
taxi-type together) across all 778 TAZs, using a technique called non-negative least
squares — a way of finding the best-fitting weights while never allowing a negative weight,
since a negative contribution from population or jobs wouldn't make physical sense.

```
production index   I_i = c_P · P_i + c_E · E_i
attraction index    J_j = a_P · P_j + a_E · E_j
```

The fitted 2022 coefficients: production `I = 0.506·P + 0.124·E` (a resident generates
roughly four times as many origin trip-ends as a job does, in this model), attraction
`J = 0.264·P + 0.814·E` (a job pulls in roughly three times as many destination trip-ends as
a resident, in this model). Fit quality is R² ≈ 0.5 at TAZ level — population and employment
together explain roughly half of the real variation in trip-end counts across TAZs, a
moderate, not perfect, fit. The same pair of indices is used for every layer (car, transit,
taxi-type), because they describe what the land use itself generates, independent of mode.
(The source notes that fitting the indices separately per layer instead makes the
transit-only attraction index come out almost entirely job-driven — plausible, but judged
too thin and noisy a layer to trust its own fit — so one shared index is kept, and any
mode-specific difference is instead carried through each layer's own destination pattern,
not through its margins.)

Origin targets per layer:

```
O_i^y = O_i + ρ_i · ΔI_i
   ρ_i = O_i / I_i     if TAZ i is "established"
   ρ_i = r_A(i)        otherwise,   r_A = (Σ over TAZs in superzone A of O_i) / (Σ over TAZs in A of I_i)
```

A TAZ is **established** when its 2022 index is worth at least 500 residents' worth, and its
index growth factor from 2022 to the scenario year is at most 3×. For an established TAZ,
the rule reduces to ordinary proportional growth: `O_i^y = O_i · I_i^y / I_i`. For a
small-base or fast-transforming TAZ — new neighbourhoods, or anything below the threshold in
2022 — the new residents and jobs generate trips at the surrounding **superzone's** typical
rate per unit of index, rather than at the noise of that TAZ's own handful of 2022 trips.
Targets are floored at zero. Destination targets follow the identical rule using the
attraction index (`D_j^y = D_j + σ_j·ΔJ_j`), then are rescaled so the destination-side total
matches the origin-side total — the same convention used in step 16, where the origin side
(productions) governs the matrix's overall size.

**Plain-English example of the small-base rule.** Under the HS scenario, the Matam TAZ's
population is projected to go from 390 to 9,700 residents — almost a 25× increase. Growing
that TAZ's own tiny, noisy 2022 trip numbers by 25× directly would produce an unreliable
result. Because this crosses the "established" threshold (base below 500-residents'-worth,
and/or growth factor above 3×), the rule instead applies the surrounding superzone's normal
trip-generation rate to the new growth — so the new neighbourhood generates trips at a
typical rate for that kind of area, not at whatever rate its old, tiny population happened to
produce.

**Why composite indices, not employment alone, for attractions.** On a dry run (2022 → BU
2025, an overall 4.7% growth in car trips), using employment-only attractions moved the
average car trip length (mean centroid-to-centroid distance) up by +8%, because TAZs whose
morning arrivals are mostly school- or home-type, but which happen to have a small,
fast-growing job count, received targets 2–3 times their real 2022 arrivals. With the
composite index instead, the drift was +4% (7.32 → 7.61 km) — still a real, reportable
drift, but notably smaller.

**Why not the earlier 25-area margins.** A review comment (§13) found that equal area
totals hide exactly where, within an area, homes and jobs sit relative to stations; TAZ-level
margins preserve that detail. **Why not apply the 2022 step's superzone fallback to every
small TAZ.** Doing so would suppress precisely the growth the HS scenario is meant to
represent — the small-base rule keeps the real growth amount and only borrows the *rate*
from the wider superzone.

*2. Seed — distributing the new demand before balancing.* Simply rebalancing the unchanged
2022 matrix to new margins cannot put demand into cells that are completely empty in 2022 —
balancing can only rescale existing nonzero cells, not invent new ones. And a TAZ with only
390 residents in 2022 has an almost-empty row of destinations to grow from. So a "seed"
matrix is built from up to four parts added together, per cell:

```
S_ij = T_ij                                            (keep the existing 2022 pattern)
     + ΔO_i⁺ · T_ij / O_i                              (established origin: grow along its own 2022 row)
     + ΔO_i⁺ · Π_{A(i)B(j)} · D_j^y / D_{B(j)}^y      (small-base origin: grow following the layer's own
                                                        superzone pattern, spread within the destination
                                                        superzone by its targets)
     + ΔD_j⁺ · T_ij / D_j                              (established destination: grow along its own 2022 column)
     + ΔD_j⁺ · Π'_{B(j)A(i)} · O_i^y / O_{A(i)}^y     (small-base destination: reverse superzone pattern,
                                                        spread within the origin superzone by its targets)
```

`ΔO_i⁺ = max(0, O_i^y − O_i)` and `ΔD_j⁺ = max(0, D_j^y − D_j)` are the positive part of each
target's growth (never negative). Each origin, and separately each destination, uses exactly
one of its two growth terms, according to the established/small-base classification from
step 1 above. Rows or columns whose 2022 seed is empty but whose target is positive receive
the superzone pattern outright, since there's nothing of their own to grow from.

In plain terms: an established TAZ's growth is assumed to follow wherever that TAZ's trips
already, mostly, go. A brand-new or small-base TAZ's growth instead follows wherever similar
trips in its superzone typically go — because its own 2022 row or column is too thin to
trust.

Confining this superzone-pattern ("synthetic") growth term to only the small-base zones
matters: applying it to every TAZ's growth increment (not just the small-base ones) pulls
demand towards the generic superzone-average pattern and away from each TAZ's own real
concentration of destinations — in the dry run this further lengthened average trip
distances by a further 3%, on top of the drift already described above. Because car and
transit riders from the same origin often go to genuinely different kinds of destinations
(exactly what step 21's PCA established), this whole process — seed and balancing — is run
separately, layer by layer: car and transit each grow along their own superzone destination
pattern, not a shared or car-derived one.

*3. Balancing.* Iterative proportional fitting (IPF), commonly called **Furness balancing**
in transport modelling, is applied to the seed matrix `S`, per layer and per scenario-year,
to bring its row totals in line with the origin targets and its column totals in line with
the destination targets simultaneously.

*4. Mode split.* Nothing is done to it, deliberately. Because each layer (car, transit,
taxi-type) is grown using its own margins and its own destination pattern, every TAZ's mix
of car versus transit trips automatically stays at its 2022 value — a mechanical consequence
of growing each layer separately, not a separate modelling choice. The transit matrix keeps
its own (more Haifa-bound, less locally-contained) destination pattern rather than
inheriting car's. The source stresses this is the correct content for a demographic
reference; an actual change in mode share (say, because of the new LRT) is a behavioural
assumption that belongs in the separate service-response step, not here.

**Formulas — Furness / IPF balancing, explained in full.** Furness balancing solves a
specific problem: you have a matrix (the seed `S`) whose spatial *pattern* looks realistic,
but whose row totals and column totals don't yet match your two independently-derived sets
of targets (the origin targets from step 1 and the destination targets from step 1). The
difficulty is that these two sets of targets can't both be hit with a single adjustment: if
you scale every row so it sums exactly to its target, you've just changed every cell's
value — so the column sums are now thrown off their own targets. If you then fix the columns
by scaling them to match, the row totals are thrown off again. A single pass in either
direction cannot satisfy both.

The fix is to **alternate**:
1. Scale every row of the current matrix so its total exactly matches its origin target
   (multiply every cell in row *i* by `O_i^y ÷ current row-i total`).
2. Scale every column of the result so its total exactly matches its destination target
   (multiply every cell in column *j* by `D_j^y ÷ current column-j total`). This step will
   usually throw the row totals slightly off again, but typically only by a little.
3. Repeat steps 1 and 2. Each round nudges both row and column totals closer to their
   targets at the same time; the errors shrink rather than grow with each repetition, so the
   process converges — after enough rounds, both rows and columns match their targets to
   whatever precision is required, while the cell-by-cell pattern of who-goes-where stays as
   close as possible to the starting seed.

A small illustration of the mechanics (not from the source, but consistent with the method):
suppose a 2×2 matrix currently has row totals 30 and 70, but the targets are row totals 40
and 90 and column totals 60 and 70. First scale row 1 by 40/30 and row 2 by 90/70 — now the
rows match exactly, but the two columns no longer sum to 60 and 70. Next scale each column by
its own target divided by its new total — now the columns match, but the rows have drifted
slightly. Repeating this back-and-forth a handful of times settles the numbers down until
both rows and columns hit their targets together.

Why this is needed here specifically: step 1 above produces separate, independently derived
targets for every TAZ's origin total and every TAZ's destination total (from the land-use
indices and rates), rescaled proportionally against each other but not jointly consistent
cell by cell. There is no way to build a single matrix that satisfies both sets of totals
exactly, while staying as close as possible to the realistic seed pattern of step 2, except
by this alternating balancing process.

Applied here: balancing runs separately per layer (car, transit, taxi-type) and per
scenario-year — 12 separate runs in total (3 layers × 4 scenario-years) — each to a relative
tolerance of 10⁻⁶ on every margin (each row and column total must land within one-millionth
of its target, proportionally), capped at 500 iterations. The result, `T_ij^y`, is that
layer's final matrix for that scenario-year. Total = car + transit; taxi-type is kept apart,
as in the 2022 deliverables.

**Status and history of the run.**

*Dry run.* The scenario zonal forecast files were initially only Git-LFS pointers (not
actually downloaded), so the notebook first ran a dry run on data that was already
available: growing 2022 forward to BU-2025 (a real, small, near-term growth step), plus an
artificial stress test — a synthetic scenario giving the Matam TAZs a sudden 10,000-resident
increase and a 1.5× employment jump — specifically designed to exercise the small-base rule
under extreme conditions. Results: margins were met to within 10⁻⁶ for car and transit;
taxi-type (a much sparser matrix) only reached 2–3% after hitting the full 500-iteration cap
— it did not fully converge in the given budget. No negative or unreachable cells were
produced. Car's mean centroid trip length moved from 7.32 to 7.61 km under a 4.7% overall
growth (the chosen method, composite index plus confined synthetic seeding); for comparison,
an employment-only-attractions version would have given 7.91 km, and an "all-synthetic" seed
(applying the superzone pattern to every increment, not just small-base ones) would have
given 7.84 km — both alternatives lengthen trips more than the chosen method. Transit's
average length was essentially unchanged. The synthetic Matam conversion added about 2,400
new origin trips at the surrounding superzone's rate. The dry run's outputs are kept
separately under `Output/forecast_taz/dry_run/` and are explicitly **not** scenario results.

*Scenario run, 22 September 2026.* Once the real scenario zonal files were pulled from
Git-LFS, the notebook ran in scenario mode and produced the four real sets: BU_2040, BU_2050,
HS_2040, HS_2050. Convergence per `checks.csv`: car and transit margins converged to 10⁻⁶
within 25–140 Furness iterations (comfortably inside the 500-iteration cap); taxi-type again
hit the 500-iteration cap without fully converging, this time with 10–15% maximum relative
error remaining on its row (origin) margins specifically, while its column (destination)
margins converged exactly — an asymmetric, partial non-convergence limited to this one
sparse layer. On the corridor-internal V2-area market (referenced forward to step 32), the
resulting growth versus the 2022 base is: transit ×1.27 (BU 2040) / ×1.40 (BU 2050) / ×1.38
(HS 2040) / ×1.57 (HS 2050); car ×1.32 / ×1.53 / ×1.38 / ×1.59 over the same four
scenario-years.

**Outputs (per scenario-year).** `{car,transit,taxi,total}_{scenario}_{taz,sz,area}.csv`,
`margins_{scenario}.csv` (the fitted indices, the targets, and which rule — established or
superzone-rate — each TAZ took); across all scenarios: `summary_by_class.csv`, `checks.csv`,
`by_area.csv`, `trip_rates_by_sz.csv`, `corridor_link_flows_scenarios.csv`,
`landuse_indices.csv`; figure `forecast_taz_profiles_{mode}.png`.

**Tests / checks and what they showed.** Six checks are run and reported for every
scenario-year:
1. **Margins and sign** — every origin and destination target met within tolerance; no
   negative cells anywhere; layer sums add correctly to the total.
2. **Superzone consistency** — the TAZ-level result is re-aggregated to superzone OD blocks
   and compared against an entirely separate, independently-run superzone-level Furness (the
   2022 superzone matrix balanced directly to the same superzone margins). Differences
   between the two show exactly where the seed's synthetic (superzone-pattern) growth terms
   moved demand across superzone boundaries — the same kind of conservation-style check used
   in step 19, applied here to the forecast output.
3. **Trip-length distribution** — mean and median centroid-to-centroid trip distance, car
   and transit, 2022 versus each scenario-year; a drift beyond a few percent is flagged,
   since a purely demographic re-forecast should not meaningfully change how far people
   travel unless growth happens to concentrate far from jobs.
4. **Implied trip rates** — trips per resident by superzone, 2022 versus scenario-year;
   should stay near-constant where growth is "ordinary" (established TAZs growing along
   their own rate); this table shows what effect the small-base rule and the job component
   of the indices actually had.
5. **Corridor classes and profiles** — totals by corridor-relationship class (as in step
   22's table) plus the full 18-line-area three-hour potential-movement profile (as in step
   17), for total and transit, per scenario-year, set beside the 2022 figures.
6. **BU versus HS comparison** — per-TAZ and per-area differences between the two
   demographic scenarios, with the Tirat Carmel / Matam / Neot Peres / Kiryat Nahum cases
   specifically called out.

**Caveats.** What these matrices support: comparing scenario-years and scenarios on a
consistent behavioural basis; locating where growth adds demand along the corridor;
providing the demographic component of an LRT market estimate. What they do **not** support:
LRT ridership, mode shift, actual peak vehicle loads (the step-20 peak-hour factors can be
applied for a departure-hour view, but all of step 20's own caveats still apply), or any
conclusion that depends on travel behaviour changing between 2022 and the scenario-year —
because behaviour is explicitly frozen at 2022 by construction. Every 2022-base caveat
carries forward unchanged: the bus layer's ticketing-coverage threshold, the purpose-blind
allocation of trips, missing trips to/from outside the study area, and the absence of
external validation against independent counts. Two caveats are specific to this
forecasting step: (a) the constant-trip-rate assumption — ageing, car ownership changes and
telework are not represented at all, trip rates per person are frozen at 2022 levels; (b)
the superzone-rate rule for small-base TAZs depends on two tunable parameters (the
500-residents'-worth threshold and the 3× growth-factor cutoff), whose exact effect is
reported but which the source explicitly says "can be varied" — implying these particular
thresholds are a judgement call rather than a fixed rule, and their sensitivity should be
checked. The source lists specific sensitivity runs worth trying alongside the base result:
varying the small-base threshold (250 / 500 / 1,000 residents' worth) and the growth cutoff
(2× / 3× / 5×); comparing employment-only versus composite attractions; turning the
synthetic seed terms off entirely (pure Furness on the unchanged 2022 matrix — with this off,
new-development TAZs would receive no trips at all); governing the destination-side total by
employment instead of population; and applying the step-20 peak-hour factors to the
scenario-year link profiles. Also note: the BU and HS scenario labels are not defined or
expanded anywhere in the material read for this section — their exact meaning is left
ambiguous here rather than guessed.

---


### Step 24 — Corridor potential movements on the V2 aggregation (`Corridor_flow_profile_V2_routes.ipynb`) — [STATUS: current — three-hour and peak-hour potential movements]

**What it's for.** Re-runs the corridor "potential movements" profile (as in steps 17 and
20), but on a new, more detailed area layout that covers a wider stretch of the network with
three alternative branches, instead of the earlier single 18-area line.

**Inputs.** `Input/Corridor_TAZ_Agg_V2.xlsx` (the new V2 aggregation: 25 areas built from
174 TAZs); the step-16 TAZ-level layers (car, bus, taxi, rail); peak-hour factors re-estimated
for the V2 route sequences by a later step (27), with the step-20 factors used as a fallback
when that file is missing.

**How it works.**
1. The V2 aggregation splits the corridor into 25 areas with three alternative "route
   orders," reflecting the real network's branching structure: **T1** runs Tirat Carmel →
   Haifa → Tsomet Kiryat Ata → Kiryat Ata → Shefaram → Hamovil → Nazareth (17 areas); **T2**
   follows the same trunk then branches to Kiryat Haim → Kiryat Bialik Center → Kiryon →
   Tsur Shalom (16 areas); **T3** follows the same trunk then branches to Kiryat Haim West →
   Kiryat Yam B+C → Kiryat Yam A → Savyoney Yam (16 areas). All three routes share the same
   12 trunk areas (numbered 201–212) up to the branch point at Tsomet Kiryat Ata.
2. The step-16 TAZ layers are re-aggregated up to these 25 V2 areas.
3. For each route separately, the same loading rule as step 17 is applied: every
   origin-destination pair with both ends on that route loads onto every link between them,
   in the right direction — **up** meaning away from Tirat Carmel (matching the old "1→23"
   direction), **down** meaning towards it.
4. Peak-hour factors, re-estimated specifically for the V2 route sequences, are applied per
   route, per network view, per layer and per direction (car 0.62–0.65 up / 0.57–0.58 down,
   with a whole-network value of 0.556/0.522; bus 0.590; taxi-type 0.580; rail uses the bus
   factor). If the newer factor file is not available, the older step-20 factors are used
   instead.
5. A fourth view, **the tree**, doesn't pick a single route — instead it loads every
   origin-destination pair among the full 25 areas onto its unique path over the whole
   branching network (trunk plus all three branches together). This means the trunk carries
   the combined inbound flow of all three branches at once, while trips travelling directly
   from one branch to another only load the branch-specific links, not the trunk.
6. Comparability note: the V2 geography shares 143 TAZs with the earlier 28-area geography,
   but drops 62 TAZs that used to be included (Hadar Carmel, Neve Yosef, Kiryat Nahum,
   Kiryat Ata East, some influence areas) and adds 31 new ones (all of Nazareth city,
   Shefaram, Neot Peres) — so total figures are not directly comparable between the two
   geographies; only the shared Haifa-segment link values are.

**Formulas.** Same assignment (loading) rule as step 17; no new numeric formula.

**Results.** Trips with both ends among the 25 areas total 184,106 (car 156,944, bus 18,788,
taxi-type 8,323, rail 51). Route-internal totals: T1 123,906 (transit 12,546), T2 73,964
(7,711), T3 55,519 (7,054). The busiest transit link on every route is on the shared Haifa
trunk: Ein Hayam – Bat Galim/Kiryat Eliezer "up" (1,379–1,437 across routes; peak hour
814–848) and Matam/Neot Peres – Hof Carmel/Neve David "down" (1,410–1,629; peak hour
833–962).

The T1 (Nazareth) branch shows strongly one-directional morning demand: Tsomet Kiryat Ata –
Kiryat Ata North carries 5,809 trips "down" versus only 785 "up"; transit "down" on this link
is 1,174, a 20% share; the Shefaram–Nazareth links carry 650–920 transit trips "down" at a
20–23% share — the highest transit share found anywhere in this data set. The Krayot (T2)
branch holds the single busiest link of any route: Kiryat Haim – Kiryat Bialik Center at
10,144 "down" (peak hour 5,812), though with only a 10% transit share — this huge flow is
overwhelmingly car. T3's branch peaks at 4,896 "down" on Tsomet Kiryat Ata – Kiryat Haim West
(936 transit, a 19% share).

On the combined tree-network view, the trunk link Bazan-Hutsot – Tsomet Kiryat Ata carries
16,231 "down" (peak hour 8,792) and 2,898 transit (peak hour 1,710) — the combined inflow of
all three branches — against just 4,958/1,075 on the same link if you look only at the T1
route by itself. The Haifa-side trunk barely changes between views (7,183 "up" on Ein Hayam
– Bat Galim in the tree view versus 6,878–7,036 per individual route), because west of the
branch point, all traffic funnels through the same links regardless of destination branch.
14,688 trips (8% of the total) are branch-to-branch, loading only branch links, not the
trunk. "Down" (towards Tirat Carmel/Haifa) dominates every link east of Bat Galim; "up"
dominates only the segment between Tirat Carmel and Ein Hayam. Transit's share of trunk link
flow: 17–33% down, 10–22% up.

Against the earlier 18-area profile (busiest transit link there: 1,661/1,650): the V2
per-route figures are 1,379–1,437/1,410–1,629, and the combined network (tree) view gives
1,518/2,898 — notably higher on the busiest link than any single route, because the tree
view correctly captures the combined effect of all three branches funnelling together.

**Outputs.** `Output/corridor_v2/area_legend_v2.csv`, `{layer}_2022_area_v2.csv`,
`corridor_v2_link_flows_long.csv` (route × link × direction × layer, three-hour and
peak-hour), `corridor_v2_link_flows_wide.csv`, `corridor_v2_route_summary.csv`,
`corridor_v2_network_link_flows.csv`, `corridor_v2_vs_earlier_profile.csv`; figure
`corridor_v2_route_profiles_2022.png`.

**Tests / checks and what they showed.** The step's built-in check is the explicit
comparison table against the earlier 18-area profile
(`corridor_v2_vs_earlier_profile.csv`), which shows the new V2 numbers broadly track the old
ones on the shared Haifa segment (busiest link 1,379–1,629 per route versus the old
1,650–1,661), while overall totals differ because of the changed area definitions — this is
documented as an explanation, not treated as a pass/fail test.

**Caveats.** These remain potential movements, not observed loads (the same limitations as
steps 17/20 apply — no station access, route choice, within-period peaking, or off-line trip
ends). Totals are not directly comparable to the earlier 18-area profile because of the
changed TAZ coverage (62 areas' worth of TAZs dropped, 31 added); only the shared
Haifa-segment link values are safely comparable across the two geographies. The V2
route-specific peak-hour factors depend on a later step (27) and fall back to the older,
less specific step-20 factors when that file is missing.

---


### Step 25 — LRT line and stations: stop-to-stop times (`LRT_line_stations_travel_time.ipynb`) — [STATUS: current — trunk only (no branches)]

**What it's for.** Converts the planned physical LRT alignment geometry into a station
table and station-to-station in-vehicle travel times, under two scenarios that bound how
much of the line is built underground versus at ground level.

**Inputs.** `Input/GeneralHalufa/` (the planned alignment shapefile and 46 platform points);
`docs/Transit_Travel_Time_Calibration_Report_Operator22.md` — a separately calibrated
travel-time model fitted on real operating data: operator reference 22 (a light-rail-type
operator, likely the existing "Red Line"), 132 Thursdays from May 2023 to September 2026,
26,653 clean journeys.

**How it works.**
1. Start from the calibration report's function: `T [min] = 1.960792 × N_UG + 2.392690 ×
   N_Other` per 500-metre section of line, where `N_UG` counts underground 500m sections and
   `N_Other` counts everything else (ground level). Converted to speeds under the
   calibration's own 500m-spacing assumption, this is 3.921585 minutes per km underground
   (15.30 km/h) and 4.785381 minutes per km at ground level (12.54 km/h), with normal dwell
   time already included.
2. A given section of line (between two adjacent stations) counts as underground only if
   **both** its stations are underground; that is why only two pure scenarios are run
   (all-underground, all-ground) rather than a realistic mixed case — a mixed case would
   need a station-by-station underground/ground assignment that isn't part of this step.
3. Coordinates are converted from WGS 84 (GPS) to the Israel TM Grid, a local flat
   coordinate system needed for accurate distance measurement.
4. The 46 platform points (all within 80 m of the planned alignment, confirming they belong
   to it) are grouped into actual stations: points whose position along the line
   ("chainage") is less than 150 m from a neighbour are merged into one station. This gives
   24 stations (22 merged pairs plus 2 single points), numbered S01 (Tirat Carmel end) to
   S24 (Hamifrats end), with chainage measured from the Tirat Carmel end to match the V2
   route-direction convention.
5. Each station is located to a TAZ (by point-in-polygon spatial matching) and to a V2
   corridor area (using the same lookup key used elsewhere).
6. Two mathematical forms of the calibrated function are kept side by side: the **distance
   form** (time proportional to the actual distance between two given stations — the primary
   figure) and the **section form** (one calibrated 500 m section's worth of time applied per
   real inter-station link, regardless of that link's actual length — kept as a sensitivity
   check). Both are kept because the calibration's coefficients were fit assuming 500 m
   spacing (with dwell time baked in at that spacing), while this line's real planned station
   spacing averages 815 m — so how you extend the calibration to a longer-spaced real line
   matters.
7. For the ten trunk corridor areas the line passes through, each area is represented by
   whichever station sits nearest to that area's population-and-employment-weighted centre
   point.

**Revision 2 (22 September 2026) — the 500 m assumption checked against real data.** The
calibration's speed conversion assumes 500 m between stops. The team checked this against the
actual, currently-running "Red Line" (the same system the calibration was fitted on), using
its published national GTFS timetable (operator 22, routes 34447/34448: 32 stops, 21.4 km,
70.6 minutes scheduled), which records the real distance between every consecutive pair of
stops. Measured result: the Red Line's real underground sections average **970 m**, and its
surface sections average **577 m** — not 500 m. This means the calibrated 1.961 minutes "per
underground section" actually corresponds to roughly 30 km/h (given the real 970 m spacing),
not the ~15 km/h implied by dividing that same coefficient by the assumed 500 m — so revision
1's underground scenario had come out **twice too slow**.

To correct this, revision 2 refits the relationship in a different mathematical form — a
"running-time plus stop-penalty" form — fitted directly on the Red Line's actual 14,477
scheduled inter-stop sections (real timetable, real distances): underground = 0.81 minutes
fixed (a stop penalty — the time spent slowing, stopping and dwelling at every stop,
regardless of distance) plus 1.31 minutes per km of actual running distance (46 km/h running
speed, roughly a 49-second stop penalty); surface = 1.23 minutes fixed plus 1.94 minutes/km
(31 km/h, roughly a 74-second stop penalty). These freshly fitted numbers are then "levelled"
— scaled by ×0.94 (underground) and ×1.02 (surface) — to match the calibration report's own
observed average speeds, so the corrected form stays anchored to what was actually calibrated
rather than purely to the Red Line's specific stop pattern. Applied at Haifa's real average
station spacing of 815 m, one typical section now takes 1.77 minutes underground (27.6 km/h)
and 2.86 minutes at ground level (17.1 km/h) — substantially faster and more realistic than
revision 1's figures. The section form is now kept as a fast bound, and the original
revision-1 nominal-500 m form is explicitly relabelled as a superseded, too-slow lower bound,
kept only for the record.

**Formulas.**
- Original per-section function: `T [min] = 1.960792 × N_UG + 2.392690 × N_Other`, per 500 m
  section (N_UG / N_Other = number of underground / other sections).
- Revision-2 running-time + stop-penalty form: underground `0.81 min + 1.31 min/km`; surface
  `1.23 min + 1.94 min/km`; each then multiplied by a levelling factor (×0.94 underground,
  ×1.02 surface) to match the calibration's observed averages.

**Results.** The alignment is 18.94 km long; the 24 stations span 18.74 km of it, with
spacing ranging from 354 m (closest pair) to 1,396 m (farthest), averaging 815 m. End-to-end
travel time, S01 → S24: headline (revision-2, decomposed) form — **40.7 minutes all
underground (27.6 km/h) / 65.8 minutes all at ground level (17.1 km/h)**; section form — 45.1
/ 55.0 minutes; the superseded nominal-500 m form (revision 1) — 73.5 / 89.7 minutes. Going
underground instead of ground level saves 38% of travel time under the corrected figures —
revision 1 had said only 18%, because its two speed coefficients embedded inconsistent
assumed section lengths, distorting the underground-vs-ground comparison. Two further data
notes: station S13 falls in TAZ 1509, which is not listed in the V2 area-mapping key, so it
cannot be assigned a V2 area directly; and Bazan-Hutsot, Tsomet Kiryat Ata, and all three
branches have no station at all on this line geometry.

**Addendum, 22 September 2026 — a third, specified regime.** At the study team's request, a
third scenario runs the entire line at a flat design speed of 50 km/h between stops, with a
fixed 10-second dwell at each stop (same 5-minute service headway as before), and explicitly
with no allowance for acceleration or braking time. The section-time formula is:
`section time = distance / 50 km/h + 10 s`. Result, end to end S01 → S24: **26.3 minutes
(42.7 km/h)** — 35% faster than even the corrected, calibrated all-underground scenario. The
source explains the gap plainly: the two calibrated, real-data-based forms put 49–74 seconds
of stop penalty into every stop — where real dwell time, acceleration and deceleration all
actually happen — versus only 10 seconds assumed here. The source is explicit that this is
**not** a third realistic operating regime, but a theoretical performance ceiling for the
alignment's geometry, to be read alongside the two calibrated scenarios for context, not as
an equally credible third estimate.

**Outputs.** `Output/lrt_v2/lrt_stations_hf_lrt_3.csv` / `.geojson`,
`lrt_station_distances_km.csv`, `lrt_station_times_{all_underground,all_ground}.csv` and
`…_section_form.csv`, `lrt_line_profile.csv`, `lrt_area_representative_station.csv`,
`lrt_area_ivt_{all_underground,all_ground}.csv`; figure `lrt_line_profile_hf_lrt_3.png`.
The addendum adds `lrt_station_times_design_50kmh.csv`, `lrt_area_ivt_design_50kmh.csv`, plus
a row in `lrt_end_to_end_summary.csv` and columns in `lrt_line_profile.csv`.

**Tests / checks and what they showed.** The central check in this step is revision 2's
comparison of the calibration's built-in 500 m-spacing assumption against the real Red
Line's actual GTFS timetable data. The check found the assumption was wrong (real spacing:
970 m underground, 577 m surface — not 500 m), and that this error had made revision 1's
underground travel-time estimate roughly twice too slow. The fix — refitting on the real Red
Line data in a different mathematical form, then levelling the result to match the
calibration report's own observed average speeds — produced corrected end-to-end times of
40.7/65.8 minutes (versus revision 1's 73.5/89.7 minutes) and an underground time-saving of
38% (versus revision 1's mistaken 18%). No further stated pass/fail test is described beyond
this internal correction and cross-check against real timetable data.

**Caveats.** Two calibrated forms (distance and section) are deliberately kept side by side
as a fast bound and a superseded slow bound, rather than the team picking one as definitively
correct — Haifa's actual 815 m station spacing sits between the Red Line's underground
(970 m) and surface (577 m) spacings used to refit the model, so some extrapolation is still
involved. Station S13 cannot be matched to a V2 area. Bazan-Hutsot, Tsomet Kiryat Ata and all
three branches have no station on this geometry and so get no travel time from this step. The
addendum's 50 km/h design-speed scenario is explicitly a theoretical ceiling, not a credible
third real-world estimate, and should not be treated as equally valid to the two calibrated
scenarios.

---

## Part 4 — Generalized cost, the LRT ridership estimate, the output files, and how to reproduce this (Steps 26 – 32)


This part covers the final stretch of the model build: putting a "cost" number on every way of
getting around the corridor (car, bus, BRT, LRT), checking those costs against how people
actually travel today, and using that to guess how many riders the new LRT line would pull in
— now and in 2040/2050. It ends with a guide to the output files, a list of things to watch out
for, and instructions for running it all yourself.

A few terms used throughout, in plain words:

- **Generalized cost (GC)**: a single number, in "minutes," that stands in for how unpleasant or
  costly a trip is on a given mode. It adds up in-vehicle time, plus walking and waiting time
  (counted extra, because people hate those more than riding), plus a penalty for changing
  vehicles, plus money converted to minutes. Lower GC = a more attractive trip.
- **TAZ**: Traffic Analysis Zone, the small geographic unit trips are counted between.
- **"V2 areas"**: 25 larger areas along the LRT corridor (grouped from TAZs) used for these
  steps, because that's a manageable size for building cost matrices and comparing to survey
  data.
- **"Trunk pairs"**: the 90 area-to-area pairs where all trip ends are among the 10 areas that
  sit directly on the planned LRT line (the `hf_lrt_3` alignment). These are the areas where we
  actually know the LRT's geometry, as opposed to the 15 "branch" areas that don't have a drawn
  line yet and have to reach the LRT through a bus or BRT feeder.

---

### Step 26 — Generalized cost on the V2 areas: data inventory, first-fill skims, gaps (`GC_data_inventory_and_skims.ipynb`) — [STATUS: current result is Addendum 5, 22 September 2026 — a design-speed LRT option added on top of the two calibrated LRT scenarios; money (fares/parking) removed from the comparison per Addendum 4]

**What it's for.** Before you can compare car vs. bus vs. LRT, you need a cost number for each
mode, for each pair of the 25 areas. This step builds those cost numbers piece by piece (travel
time, walking, waiting, transfers, money), keeps score of which numbers are real data versus
educated guesses versus placeholders, and reports the gaps that still need to be filled.

**Inputs.**
- The trips file (survey), for car door-to-door travel times.
- `Input/BusSpeedData` — a street network with measured bus speeds on each link, for a first-pass
  ("floor") bus travel time.
- Step 25's LRT station-to-station travel time function, for the 10 trunk areas.
- TAZ centroids, population and employment (for splitting trips and for walk-access weighting).

**How it works.**
1. **Car in-vehicle time**: take AM car trips from the survey, split them onto area-to-area pairs
   using population/employment shares (this is the same method as an earlier step, §6r). Because
   many pairs have very few sampled trips, blend each pair's measured average time with a smooth
   trend line fitted across all pairs (an "empirical-Bayes blend" — basically: trust the pair's
   own data more when there's a lot of it, and lean on the overall trend when there's little).
   The trend line found is: travel time ≈ 7.0 minutes + 1.85 minutes per km of straight-line
   distance between area centers.
2. **Bus in-vehicle time (first pass)**: build a road network of bus-served street links, each
   with a measured speed from a fixed weekday morning hour (07:00–08:00). Find the fastest path
   between the area centers using this network (a standard shortest-path search, Dijkstra's
   algorithm). This gives a "floor" — the fastest a bus could possibly go, with no waiting, no
   transfers, no stopping for passengers built in.
3. **LRT in-vehicle time**: taken from step 25's calibrated station-to-station times for the 10
   trunk areas. Walking time to/from the nearest LRT station is estimated as straight-line
   distance times a 1.3 detour factor, at a fixed walking speed. Waiting time is assumed to be
   half the planned headway (how often trains come).
4. **Everything not yet known** is filled with a flagged placeholder (e.g., "assume 8 minutes
   walk to a bus stop," "assume a 10-minute bus headway") so that no cell in the cost table is
   ever blank — but its status is recorded as "assumed" rather than "derived" or "measured," so
   later steps know how solid each number is.
5. Later addenda (dated 22 September 2026) revise pieces of this as better data becomes
   available: a GTFS-based bus in-vehicle time and wait (Addendum 1, uses step 29), a corrected
   LRT speed function and 5-minute headway (Addendum 2, uses a step-25 revision), *observed*
   (not just scheduled) bus running times (Addendum 3, uses step 30), a decision to drop money
   from the comparison entirely (Addendum 4), and a third "design speed" LRT option as an upper
   ceiling (Addendum 5).

**Formulas.**

```
GC = IVT + 2·walk + 2·wait + 8·transfers + (fare + parking)/VOT
```

Plain meaning of each term:
- **IVT** — in-vehicle time: minutes actually riding.
- **2·walk** — walking minutes counted double. People find walking about twice as unpleasant
  per minute as riding, so this weighting makes the cost number reflect that.
- **2·wait** — waiting minutes, also counted double, for the same reason.
- **8·transfers** — a flat penalty of 8 "generalized minutes" for every time you have to change
  vehicles (get off one bus/train and board another). Changing vehicles is disliked well beyond
  the few minutes it physically costs, so this fixed penalty stands in for that.
- **(fare + parking)/VOT** — money terms converted into minutes by dividing by VOT (value of
  time — how many shekels an hour of a person's time is "worth"), so a $ cost and a time cost
  can be added together on the same scale. (Note: by Addendum 4, this whole term is dropped —
  see Caveats.)

Car door-to-door trend line: `t = 7.0 + 1.85 × centroid_km` (minutes, as a function of
straight-line distance between area centers).

**Outputs.** Component tables in `Output/gc/`: `car_ivt_survey_area_v2.csv`,
`bus_ivt_network_area_v2.csv`, `bus_path_km_area_v2.csv`, `lrt_access_taz_v2.csv` /
`lrt_access_area_v2.csv`, the long-format `gc_components_area_v2_long.csv` (one row per
origin-destination-mode-component, with its value and a status flag), per-mode generalized-cost
tables `gc_area_v2_{car,bus,lrt_all_underground,lrt_all_ground,lrt_design_50kmh}.csv`, the
**gap inventory `gc_data_inventory.csv`** (the master to-do list of what's missing per
component), and comparison/figure files.

**Tests / checks and what they showed.** On the 90 trunk pairs (trip-weighted): car
door-to-door 14.5 min; first-pass bus in-vehicle time 12.5 min, versus **27.1 min door-to-door
reported by bus riders in the survey** — over twice as long, because the "floor" ignores
walking, waiting, stops and detours. Early LRT estimates put its door-to-door time (≈30–37 min
depending on the version) at or slower than today's bus (27 min) — meaning the LRT's raw speed
advantage doesn't survive once you add the time to walk to a station and wait for a train. Later
addenda change this picture (see below). The overall conclusion at this step: LRT's *speed* is
not obviously a winner over the bus once access and wait are included, and the missing pieces
that matter most are the LRT geometry beyond the 10 trunk areas (15 of 25 areas had no LRT time
at all at this point) and getting a real (not first-pass) bus travel time.

By Addendum 3 (after step 30 supplies *observed*, not scheduled, bus running times): bus
in-vehicle time on the trunk pairs rises to 14.4 min (was 10.4 min on the timetable), because
buses run slower than scheduled during the actual morning peak. The partial generalized cost on
trunk pairs settles at: bus 27.0, Metronit (BRT) 22.1, LRT 43.9 (underground) / 51.1 (ground),
car 14.5. So the LRT is *more expensive in generalized-cost terms* than the bus on every single
trunk pair (by 4–31 "generalized minutes," typically about 17) — mostly because of the extra
walking time to a station (about 13.6 minutes to a station vs. about 4.7 minutes to a bus stop).
But its raw riding time (in-vehicle time alone) is now *faster* than the bus: about 11.7 minutes
underground versus 14.4 minutes observed bus time. In short: the train itself is quick, but
getting to it costs more than getting to a bus stop, so on a pure "cost" basis the bus still
often wins — the LRT's case has to rest on things this cost formula doesn't fully capture (reliability, comfort, capacity) or on better station access.

**Caveats.**
- Fare and parking data were missing everywhere at first; by Addendum 4 the study team decided
  money doesn't matter for this comparison at all (see below), so this gap is now closed by
  decision rather than by data.
- Bus walking time, bus headway, and value-of-time (VOT) started as flat assumed placeholders,
  not measured values.
- The LRT geometry (line and stations) only existed for 10 of 25 areas at first; the other 15
  need a "feeder" treatment that is developed in step 31.
- Addendum 4: the transit fare in the area is flat, and a daily cap effectively makes transfers
  and return trips free — so the fare is *the same number* on bus, BRT and LRT and on every
  pair. Since it's identical across the modes being compared, it drops out of the transit-vs-
  transit comparison entirely (it can't tip the choice one way or the other). Against the car,
  it's treated as a constant absorbed elsewhere in the model, not something this generalized-cost
  formula needs to carry. Car operating cost and parking were excluded on the same decision. This
  means the generalized-cost numbers in this whole file never actually include money, even
  though the formula written above has a money term.

---

### Step 27 — Peak-hour factors on the V2 routes (`Corridor_peak_hour_V2_routes.ipynb`) — [STATUS: current, single result set]

**What it's for.** Earlier corridor totals were 3-hour totals (06:00–09:00). To know how many
trips happen in the single busiest hour (what actually stresses a train or road), you need a
"peak-hour factor" — the fraction of the 3-hour total that falls in the busiest 60 minutes. This
step recalculates those factors specifically for the new V2 route geometry (three routes T1/T2/T3,
each with an "up" and "down" direction), rather than reusing factors calculated for an older,
simpler 18-area version of the line.

**Inputs.** Survey trip departure times, the V2 route/area definitions, and the same statistical
method as an earlier step (§6r): 15-minute departure time bins, weighting by how many route
links each sampled trip crosses, and a 200-round bootstrap (repeatedly resampling households) to
get a stable estimate.

**How it works.**
1. For each route and direction, and for the "tree network" (the shortest path between every
   pair of the 25 areas, going through the corridor), count trips by 15-minute departure bin.
2. Find the busiest continuous 60-minute window and compute what share of the full 3-hour count
   falls inside it — that share is the peak-hour factor.
3. Do this separately by mode (car, bus, taxi-type; rail borrows the bus factor).
4. Only trust a route-and-direction-specific factor if there are at least 100 sampled trips
   behind it; otherwise fall back to a factor calculated for the whole study area.

**Formulas.** No new formula beyond "peak-hour factor = trips in the busiest hour ÷ trips in the
full 3-hour window," applied per route/direction/mode as described above.

**Outputs.** `Output/corridor_v2/peak_hour_factors_v2.csv` (the factors themselves) and
`peak_hour_factors_v2_applied.csv` (the factors already applied to link flows, which the earlier
step 24 reads in as its own peak-hour flows); a profile chart.

**Tests / checks and what they showed.** Car has enough sampled trips (203–447 per
route-direction) to get its own solid factor everywhere: roughly 0.62–0.65 going "up" (away from
Tirat Carmel) and 0.57–0.58 going "down," lower than the number used previously (from the older
18-area version), by about 1–17% depending on route and direction. Because step 24 (an earlier
step) re-reads this step's output, this correction *reduces* the peak-hour flow numbers reported
there — for example, one trunk link's peak-hour car count drops from about 9,956 to about 8,792
trips. Bus and taxi-type modes don't have enough samples per route to get their own reliable
factor, so they keep the broader study-area factor (about 0.59); the individual bus route values
scatter widely (0.43–0.69) around that number, and taxi-type values all sit above it, hinting
the taxi-type peak might be under-estimated by using the flat study-area number.

**Caveats.** Same as an earlier step (§6r): a bootstrap can measure how noisy an estimate is
but can't fix having too few sampled trips on some routes; the fallback to the study-area factor
is a reasonable but imperfect substitute where samples are thin.

---

### Step 28 — Corridor transit profiles on the V2 routes: calibrated survey vs ticketing (`Corridor_profile_V2_survey_vs_ticketing.ipynb`) — [STATUS: current, single result set]

**What it's for.** Repeat an earlier comparison (§6p) — checking the survey-based transit
numbers against real ticketing (smart-card) data — but on the new V2 route geometry, to see
where the two sources agree and disagree along the actual planned corridor.

**Inputs.** TAZ-level survey-based bus + rail trips (from an earlier step); ticketing data
(RavKav smart card boardings × the "OnBoard" survey pattern, from another earlier step) and the
station-level train matrix; the V2 route and area definitions.

**How it works.**
1. Aggregate both the survey-based and the ticketing-based transit trip counts onto the V2
   route links, in both directions, and onto the "tree network" (all 25 areas' shortest paths).
2. Compare the two sources link by link and by route.
3. Repeat with a couple of calibration variants (using the raw 2018 survey bus numbers, and an
   "all-RavKav" variant) plus the separate taxi-type layer, to see how sensitive the comparison
   is to those choices.

**Formulas.** None beyond simple ratios (survey ÷ ticketing) per link, route and direction.

**Outputs.** `Output/corridor_v2/corridor_v2_survey_vs_ticketing.csv` and summary/pairs
versions; a comparison figure.

**Tests / checks and what they showed.** Across the 25 areas, the survey counts a bit more
total transit trips than ticketing (18,839 vs. 16,363), but the *pattern* differs: the survey
undercounts almost every specific link relative to ticketing, running at about 78–83% of the
ticketing number on the main Haifa segment. This means the survey captures more short, local
transit trips, while ticketing captures more long, corridor-spanning trips. The biggest gap is
around Nazareth: the survey shows only 1,070 transit trips starting there heading into the
corridor, versus 2,402 in the ticketing data — a difference of over 13,000 link-trips once
spread across the network. Other localities (Kiryat Yam, Tsur Shalom, the Hamifrats hub) show
similar, smaller gaps. The T2 route is where the two sources come closest to agreeing; on the T1
branch (toward Nazareth), ticketing shows roughly 2.3 times as much transit demand toward Haifa
as the survey does — a big enough gap that any Nazareth-branch demand estimate should be
reported as a range, not a single number.

**Caveats.** As with the earlier version of this comparison (§6p), the two data sources measure
different things (survey = reported trips by surveyed households; ticketing = actual boardings)
and neither is a clean "ground truth" — the gap tells you where to be cautious, not which number
is right.

---

### Step 29 — Bus level of service per TAZ from the national GTFS, bus and BRT (`GTFS_bus_LOS_TAZ.ipynb`) — [STATUS: current, single result set; some parts ("178 pairs without direct service") explicitly left open for a future step]

**What it's for.** Build a real timetable-based picture of bus and BRT (Metronit) service for
every TAZ in the study, using the official national GTFS feed (the standard format transit
agencies publish their schedules in), and a direct area-to-area "skim" (travel time table)
between the 25 corridor areas that replaces the crude fastest-path "floor" used in step 26 with
an actual scheduled travel time and a real headway-based wait.

**Inputs.** The national GTFS feed (`Input/GTFS`), containing stops, routes, trips and their
schedules; TAZ boundaries for locating stops inside zones.

**How it works.**
1. Locate every GTFS stop inside a TAZ by checking which zone polygon contains its coordinates.
2. Pick a representative weekday (the Tuesday in the feed with the most scheduled service) and
   pull all trips that run on it, applying the feed's calendar exceptions.
3. Read the (very large) stop-times table in chunks, keeping only stops in the study area and
   trips that run on the chosen day, and narrow to two time windows: 06:00–09:00 (a wider check
   window) and 07:00–08:00 (the peak hour used for headway calculations).
4. For each TAZ, compute: how many stops it has, how many distinct routes serve it, how many
   trips depart in each window, a combined peak-hour headway (60 minutes ÷ number of trips,
   across all lines), a standard frequency grade (A = every ≤10 min, down to F = worse than
   every 60 min), the best single line's headway, how many other TAZs it can reach without
   changing vehicles, and distance to the nearest stop.
5. Separately, for BRT (the Metronit), tag routes by their official line codes to distinguish
   real Metronit service from other lines that happen to share similar codes in the feed (some
   supplied codes turned out not to be Metronit lines at all, or not to exist).
6. Build the area-to-area direct-service skim: for every pair of the 25 areas, find GTFS trips
   that run from a stop in one area to a stop in the other without changing vehicles, and record
   the median scheduled travel time and the implied headway from how many such trips run in the
   peak hour.

**Formulas.** Combined peak-hour headway per TAZ = 60 minutes ÷ (number of trips serving it in
the peak hour, all lines combined). Frequency grades follow the standard TCQSM scale (A: ≤10
min headway ... F: essentially unserved).

**Outputs.** `Output/gtfs/bus_los_taz.csv` (one row per TAZ, 781 rows) and
`Output/gtfs/bus_direct_skim_area_v2.csv` (the area-pair direct-service travel times and
headways); a figure.

**Tests / checks and what they showed.** Of the five Metronit line codes supplied, only one
turned out to actually be a Metronit line in the feed — the others were either local lines in
unrelated towns or codes that don't exist in the feed at all; the notebook cross-checked and
identified the real five Metronit lines by other means (an audit table is printed). Coverage:
12,845 stops sit in 730 of the 781 TAZs; 719 TAZs have at least one peak-hour bus departure, 62
have none (mostly because they simply have no stop — some of these are in the corridor study
area itself, e.g. Bazan, the port, Kiryat Ata industrial zone). Service quality varies sharply:
the Haifa "trunk" areas get frequent service (grade A/B, buses every 3–7 minutes on the best
line), while branch areas like Kiryat Ata North, Shefaram, Hamovil and Nazareth have much worse
service (12–30 minute headways, some TAZs unserved). On the direct-service skim, 422 of 600
area pairs have at least one bus service that goes directly between them without a change (278
of those with a direct Metronit trip); on the 90 trunk pairs, 82 have direct service. Comparing
this scheduled skim to step 26's crude "floor" travel time: the schedule is on average 1.12
times the floor (i.e., roughly 12% slower, which makes sense since it now includes actual stops
and route shape) — but on the longest Krayot-area pairs the floor turns out to have been *far*
too optimistic (the schedule can be almost twice as long).

**Caveats.** The remaining 178 area pairs (out of 600) have no direct bus service in the feed —
reaching them requires a transfer, which this step doesn't yet route through; this is flagged
as an open item, later addressed partly by step 31's feeder-composite approach. This step uses
*scheduled* times only, not what buses actually achieve in real traffic — that gap is what step
30 addresses next. An earlier "dry run" using synthetic/placeholder data is kept in
`Output/gtfs/dry_run/` for reference but superseded by this real run.

---

### Step 30 — Observed bus in-vehicle time: GTFS trips routed over the measured bus link speeds (`GTFS_bus_observed_times.ipynb`) — [STATUS: current, single result set]

**What it's for.** The GTFS schedule (step 29) tells you what the timetable *promises*, not what
actually happens on the road. This step estimates what bus in-vehicle time actually looks like
in the real morning peak, by taking each GTFS trip's real stop-by-stop path and "driving" it
over a street network where each link has a measured average speed (from May 2026 AVL/GPS
speed data), then comparing that observed time to the scheduled time.

**Inputs.** Step 29's GTFS trips and their stop sequences; `Input/BusSpeedData` — the same
measured-speed street network used as a first-pass floor in step 26, this time for 07:00–08:00
on a representative weekday.

**How it works.**
1. Snap every study-area bus stop to the nearest street-network intersection (median snapping
   error about 24 meters — small enough not to matter).
2. For each distinct pair of consecutive stops appearing across all the peak-period trips
   (15,929 distinct pairs, taken from 7,324 trips), find the shortest path between them on the
   directed street network (respecting one-way streets) using one shortest-path search per
   origin — fast, because many trips share the same stop pairs.
3. For each such path, sum the travel time on however much of it has a measured speed; for
   any short remaining stretch without a measured speed, assume it travels at the same speed as
   the rest of that segment (rather than leaving it blank).
4. A minority of segments (about 2%) don't route sensibly on the directed network — usually a
   short hop where the stop snapped to the wrong end of a one-way street, forcing an unrealistic
   loop around the block. These are re-tried ignoring street direction; if that still doesn't
   give a sane result, they simply keep the scheduled time and are flagged, rather than getting
   a broken observed time.
5. Add up each trip's observed segment times along its full stop sequence to get an observed
   trip time, and build an area-to-area skim the same way step 29 did (median over trips per
   area pair), so the two are directly comparable.
6. As a sanity check, this method's output reproduces step 29's *scheduled* skim numbers almost
   exactly (within 0.003 minutes) when applied to schedule-derived link speeds instead of
   observed ones — confirming the routing and cumulation logic is correct before trusting the
   observed numbers.

**Formulas.** No new formula — this step's core idea is: **observed trip time = sum, over the
trip's real stop sequence, of (segment length on measured-speed links ÷ that measured speed)**,
with a small extrapolated correction for any unmeasured stretch. It's essentially routing GTFS
trips as if they were vehicles moving over a speed map, rather than trusting the printed
schedule.

**Outputs.** `Output/gtfs/bus_segments_observed.csv` (per street segment), `bus_trips_observed.csv.gz`
(per trip), `bus_observed_skim_area_v2.csv` (area-pair observed skim, matching step 29's
format); a comparison figure.

**Tests / checks and what they showed.** 84% of trip-segments route cleanly on the directed
network; another 13.5% need the direction-ignoring fallback; only 2% fall back to the scheduled
time. Overall, 94% of the routed distance has an actual measured speed behind it. The headline
result: on a per-trip basis, the median bus runs at about 1.09 times its scheduled time (i.e.,
9% slower than scheduled) — but this varies a lot with distance. Short hops under 500 meters
(about 65% of all stop-to-stop hops) match the schedule almost exactly (ratio 1.00), meaning the
timetable already has realistic dwell/stop time built in for short distances. But hops between
500 meters and 1 km run about 11% slower than scheduled, 1–2 km hops about 25% slower, and hops
over 2 km about 42% slower — long arterial and inter-city bus segments run noticeably slower in
the real 07:00–08:00 peak than the timetable assumes. On the 82 direct trunk-area pairs,
demand-weighted observed in-vehicle time is 12.7 minutes versus 10.4 minutes scheduled (about
22% higher); for Metronit specifically it's 8.6 vs 7.8 minutes on its 72 trunk pairs. As a
result of this step, step 26 switches to using these *observed* bus times (keeping the scheduled
value alongside as `ivt_scheduled` for reference).

**Caveats.** This work was implemented by "a lighter model" (i.e., a smaller/faster AI model)
against a written specification and then reviewed by the study team, who added the
direction-ignoring fallback and the ratio-of-sums statistic during review — worth knowing if
auditing the code closely. The measured-speed data is May 2026 only, a single representative
day; day-to-day or seasonal variation in bus speeds isn't captured. Related background: a
separate calibration report (`Transit_Travel_Time_Calibration_Report_Operator22.md`) performs a
similar kind of exercise — estimating real running speed from AVL data, splitting underground vs.
other sections — but for the LRT itself (used to set the LRT's commercial speed in step 25), not
for buses; it's a useful parallel example of the same "calibrate from real vehicle-location data"
approach applied to a different mode.

---

### Step 31 — Mode skim matrices and the flow comparison (`Mode_skims_and_flow_comparison.ipynb`) — [STATUS: current central numbers are from the main run plus a design-speed addendum, both dated 22 September 2026; this is the step that produces the headline LRT capture estimate]

**What it's for.** This is the step where everything comes together. It builds one complete cost
table ("skim") per mode — car, bus, Metronit (BRT), LRT (two building scenarios: all underground,
all at ground level) — covering every pair of the 25 areas. It then tries to measure how
sensitive today's travelers actually are to cost differences between driving and taking transit
(that sensitivity is called λ, described below). Because that attempt doesn't work cleanly, it
instead *assumes* a value for λ and uses it to estimate how many of today's bus and car riders
would switch to the new LRT line. Finally, it loads those switched riders onto the actual LRT
line segments and compares the load to how many people the bus already carries on the same
stretches today.

**Inputs.** Step 26's generalized-cost components (car, bus, LRT), updated with step 30's
observed bus running times; step 29's Metronit-specific skim; the 2022 observed car and transit
trip counts between the 25 areas (from earlier steps); step 25's LRT station geometry and step
24's trunk-link bus/car/transit flows (for the final loading comparison).

**How it works.**
1. **Build a full skim per mode.** For car and Metronit, reuse step 26's numbers as-is. For bus,
   use step 30's observed in-vehicle time wherever a direct service exists (422 pairs), and a
   scaled fastest-path floor plus an assumed transfer elsewhere.
2. **Fill in the LRT skim for the 15 "off-line" areas with a feeder composite.** These 15 areas
   don't sit directly on the drawn LRT line, so a rider there has to first get to a station area
   that *is* on the line (a "gateway"), then ride the LRT. The model computes the cost of getting
   to the nearest gateway by bus (with a transfer penalty) or, if a direct Metronit service
   reaches that gateway, by Metronit instead (with **no** transfer penalty — LRT and Metronit are
   assumed to be free to transfer between, since they're imagined as integrated, same-platform
   operations). It picks whichever feeder option is cheaper, then adds the LRT leg itself (a
   short wait, the station-to-station ride, and a walk at the end). Areas at *both* ends off the
   line need two such feeder legs. The chosen feeder route and mode are recorded for every pair.
3. **Try to measure real-world cost-sensitivity (λ).** Take the 2022 observed choice between car
   and transit (bus + rail) for every area pair, and fit a logit model — a standard statistical
   model used in transport for "given two options with different costs, what fraction of people
   pick each one?" — using the *difference* in generalized cost between bus and car
   (`GC_bus − GC_car`) as the explanatory variable. If this works, the fitted coefficient (λ)
   tells you how strongly people react: a bigger λ means people are very sensitive to cost
   differences (a small time saving pulls a lot of riders), a smaller λ means people barely
   react to cost at all (habit, necessity, or unmeasured factors dominate).
4. **The fit fails.** It's tested two ways — see Results — and both come back unusable, so λ is
   *assumed* by hand instead of being estimated from data (see Results and Caveats for why, and
   what value is used).
5. **Run the "incremental logit" capture model with the assumed λ.** This is the core switching
   calculation. In plain words: for every existing traveler between two areas, compare the
   generalized cost of their *current* trip (however they travel today — mostly bus, plus a
   smaller slice from car) against the generalized cost of the *new* LRT option for the same
   trip. The bigger the LRT's cost advantage for a given group of travelers, the larger the share
   of them the model shifts onto the LRT — but it's never an all-or-nothing switch; it's a smooth,
   probability-based shift ("incremental" — moving trips gradually as the cost gap grows, rather
   than a hard cutoff). Two things move riders: (a) *within* the group of people already using
   transit, some who currently ride the bus switch to the LRT because it beats the bus's cost;
   (b) a smaller number of people who currently drive switch out of the car entirely, because the
   LRT makes the *overall* transit option more attractive than it was. A "premium" is added:
   the model assumes riders value rail 5 generalized minutes more than a bus trip of literally
   equal time — a stand-in for rail's extra comfort/reliability/prestige that a plain travel-time
   comparison misses.
6. As a sanity check, if the LRT option is removed from the model entirely, it must reproduce the
   observed 2022 travel pattern exactly — a way of proving the modeling machinery isn't secretly
   inventing demand.
7. **Load the results onto the physical line.** Every rider the model predicts for the LRT is
   assigned onto the actual trunk line segments between their gateway stations, and the total on
   each segment is compared against how many bus riders that same segment already carries today.

**Formulas.**

```
GC = IVT + 2·walk + 2·wait + 8·transfers          (money dropped, per step 26 addendum 4)
```

The binary logit fit for cost-sensitivity (this is the fit that **fails**):

A logit model estimates the probability of choosing transit over car as a function of the cost
difference between them. The coefficient it tries to estimate, **λ**, measures how strongly that
probability responds to a change in relative cost: mechanically, a bigger λ means a given cost
gap produces a bigger swing in mode share. Fitting it on the 2022 data (573 area pairs, 67,700
trips) using just the plain cost difference gives **λ = −0.011 per generalized minute** — a
**negative** number, which is nonsensical here: it would mean that making the bus *more*
expensive relative to the car makes *more* people take transit, backwards from what should
happen. Adding a control for distance band doesn't fix it either — the fitted λ becomes
+0.0002, technically the right sign but so close to zero (statistically indistinguishable from
"no effect") that it's still unusable.

**Why the fit fails, in plain words:** the pairs where the bus looks expensive compared to the
car (in generalized-cost terms) are, in the real world, mostly the pairs where people have the
*least* access to a car in the first place — the northern branch localities with captive transit
riders. These people still ride transit heavily *despite* the high relative cost, not because
cost doesn't matter to anyone, but because they don't have the car alternative in practice. The
skims used here don't record whether someone owns or has access to a car, so the model can't
tell these two very different situations apart, and the resulting fit gets it backwards. This is
a classic case of a hidden variable (car availability) confounding the relationship the model is
trying to measure.

Because the fit can't be trusted, **λ is assumed** instead: central value **0.03** per
generalized minute, with a tested range of **0.02 to 0.05**, and within the "transit nest" (the
comparison between bus and LRT specifically) a doubled value, **λ_T = 2λ = 0.06**, on the logic
that people distinguish more sharply between bus and rail than between transit overall and
driving.

The incremental-logit switching formulas:

```
P_LRT|T = 1 / (1 + exp(λ_T · (GC_LRT − premium − GC_bus)))
```
This gives the *share* of transit riders on a given pair who use LRT rather than bus, once LRT
exists. Reading it: if LRT's generalized cost (minus its 5-minute "premium" credit) is much
lower than the bus's, the term inside the exponential is very negative, `exp(...)` is near zero,
and `P_LRT|T` approaches 1 (almost everyone who rides transit takes the LRT). If LRT is much more
expensive than the bus even after the premium, the opposite happens and almost nobody switches.
When the two costs are equal, the formula gives 50/50.

```
S' = S · e^(−λΔ) / (S · e^(−λΔ) + 1 − S)
```
This is the second, separate switching step: how many people move from car (S = the current
transit share of car+transit) to transit overall, given that adding the LRT improves the overall
transit option by an amount Δ (a "logsum improvement" — a standard way, in mode-choice modeling,
of measuring how much better an entire group of options has gotten when you add a new one to it,
not just how good the new option itself is). `S'` is the new, larger transit share after the LRT
is added. Because Δ is modest for most trips (LRT only helps a minority of transit riders, and
car riders don't directly benefit from it), this shift is described as "a modest shift, as it
should be" — this step deliberately doesn't let the LRT single-handedly pull huge numbers of
committed drivers out of their cars, only a plausible trickle.

**Outputs.** Per-mode skim files `Output/skims/skim_{mode}_{component}.csv` (in-vehicle time,
walk, wait, transfers, generalized cost, and a status flag, for each mode); a combined workbook
`skims_area_v2.xlsx` and long-format `skims_area_v2_long.csv`; the failed logit-fit diagnostics
(`logit_calibration_car_vs_transit.csv`, `logit_calibration_binned.csv`,
`logit_calibration_by_distance_band.csv`); the capture results
(`lrt_capture_scenarios.csv`, `lrt_trips_2022_{scenario}_central.csv`,
`lrt_share_of_transit_{scenario}_central.csv`, `pair_flows_and_skims_2022.csv`,
`lrt_trips_by_path_type.csv`, `lrt_boardings_by_station_area_central.csv`); the final link
loading (`trunk_link_flows_bus_vs_lrt.csv`); figures.

**Tests / checks and what they showed.**

- Skim completeness: car fully filled (625 of 625 cells); bus mostly filled (598 of 625, the
  rest are the excluded diagonal); Metronit only on the 278 pairs it actually serves directly;
  LRT fully filled for both scenarios once the feeder composite covers the off-line areas
  (though many of those cells are "assumed" quality, not directly derived).
- Trip-weighted costs on the 90 trunk pairs: car 14.7 min, bus 27.8 min, Metronit 25.6 min (on
  its own 72 trunk pairs), LRT underground 44.0 min, LRT ground 51.8 min. So on generalized-cost
  terms, driving is still cheapest, followed by Metronit and bus, with LRT the most expensive
  option on the trunk — again mainly because of station-access walking time, not the ride itself.
- The logit fit for λ fails as described above (wrong sign, then statistically meaningless even
  after controlling for distance) — this is the central methodological finding of this step: the
  2022 data as collected cannot tell you how price-sensitive people are, because it's confounded
  by who has a car and who doesn't.
- **The headline capture numbers** (central case: λ=0.03, λ_T=0.06, LRT premium=5 minutes, free
  LRT–Metronit transfer): the model predicts **3,332 LRT trips per morning (06:00–09:00) for the
  all-underground scenario** (3,037 of them switched from bus, 295 from car — so almost all new
  LRT riders are former bus riders, not former drivers), raising the transit share of car+transit
  from 0.171 to 0.185 on the corridor. The all-ground scenario predicts **2,544 trips** (2,375
  from bus, 169 from car). These numbers are **sensitive to the assumed λ**: over the tested
  range (0.02 to 0.05), the underground case swings from 2,357 to 4,855 trips, and the ground
  case from 1,472 to 4,277 — roughly plus-or-minus 40–50% around the central number. They're
  also sensitive to the assumed LRT premium: with no premium at all, underground capture falls
  to 2,658; with a 10-minute premium it rises to 4,122.
- A design-speed "ceiling" LRT scenario (faster, more idealized operation) predicts a central
  capture of **3,970 trips**, about 19% more than the calibrated underground case — notably,
  *less* than the swing caused just by varying λ, meaning the assumed cost-sensitivity parameter
  currently matters more to the final number than the LRT's actual design speed does.
- Loaded onto the physical trunk line, the busiest segment (Namal-Giborim → Hamifrats, toward the
  Krayot) carries 995 LRT trips over the three-hour morning in the central underground case,
  which is roughly a third to 45% of what the *bus* already carries on the same segment today —
  i.e., the LRT is predicted to be a substantial but not dominant share of corridor transit
  capacity, at least at this stage of the estimate.

**In short: is this number solid?** No — it should be read as "our best current estimate given
an assumed, not measured, sensitivity to cost," not as a validated forecast. The single biggest
reason is that λ (how strongly people react to cost/time differences) could not be estimated from
the 2022 data and had to be assumed; the range tested (0.02–0.05) alone moves the headline
underground number between about 2,400 and 4,900 trips. Two further assumptions — the 5-minute
LRT "premium" and the free LRT–Metronit transfer — carry the same standing (assumed, not
measured or fitted).

**Caveats (as stated in the source).**
- Only counts trips where *both* ends are among the 25 corridor areas — no trips to/from outside
  the study area are included, so this understates any true region-wide ridership.
- This is all based on 2022 conditions, not the 2040/2050 forecast years (that's step 32).
- No capacity limits and no modeling of route choice against parallel bus services that would
  keep running alongside the LRT.
- Money is completely excluded from the comparison by the study team's decision (see step 26,
  Addendum 4) — the flat, integrated fare structure means this doesn't distort mode share, but it
  does mean this model can't say anything about fare policy changes.
- **λ is assumed, not estimated** — the single biggest source of uncertainty in the whole
  result; a more careful statistical fit using individual survey respondents' data (including
  whether they have access to a car) is planned as the next step, but hasn't been done yet.
- The LRT premium (5 minutes) and the free LRT–Metronit transfer are both stated assumptions of
  the same, unproven standing as λ.
- The feeder-bus access calculation assumes the feeder bus conveniently stops right at the
  gateway station — a simplification of real walking/transfer geography.
- Station walking access/egress times are a population-weighted "nearest station from area
  centroid" estimate, not an actual per-trip walking-route calculation.

---

### Step 32 — LRT capture on the 2040/2050 forecast matrices (`LRT_capture_forecast_2040_2050.ipynb`) — [STATUS: current, main run plus a design-speed addendum, both dated 22 September 2026 — this is the most current LRT ridership estimate in the file]

**What it's for.** Re-run step 31's exact same switching model, but on future-year demand
forecasts instead of 2022 observed trips, to see how many LRT riders to expect as the area grows
— under two different demographic growth outlooks ("BU" and "HS") and two forecast years (2040,
2050).

**Inputs.** Step 31's skims and capture-model logic (unchanged); the four demographic-forecast
matrix sets from an earlier step (BU_2040, BU_2050, HS_2040, HS_2050), aggregated from TAZ level
up to the 25 V2 areas.

**How it works.**
1. Aggregate each of the four future-year demand forecasts (already built by an earlier step)
   up from individual TAZs to the 25 corridor areas.
2. Reuse step 31's skims *exactly as they are* — meaning: no assumption of future road
   congestion, no change to the bus network, no branch LRT lines, and travel costs frozen at
   today's (2026) levels. Only the number of trips being made changes; the cost of each mode does
   not.
3. Run the identical nested incremental-logit switching calculation from step 31 (same central
   λ=0.03/λ_T=0.06, premium 5, free transfer) on each of the four future-year trip sets, for both
   LRT scenarios (underground, ground).

**Formulas.** Identical to step 31 — no new formula. The only thing that changes between this
step and step 31 is which set of *underlying trip counts* gets fed through the same switching
equations.

**Outputs.** Per-scenario forecast trip matrices `Output/skims/forecast/{car,transit,taxi}_{scenario}_area_v2.csv`;
`forecast_market_v2_growth.csv` (how much the market grows); `lrt_capture_scenarios_forecast.csv`,
`lrt_trips_{year}_{lrt_scenario}_central.csv`, `trunk_link_flows_forecast.csv`,
`lrt_boardings_forecast.csv`; a figure `lrt_capture_forecast_2040_2050.png`.

**Tests / checks and what they showed.** Overall transit demand in the corridor is forecast to
grow from 11,664 trips today (2022) to somewhere between 14,836 (BU_2040, ×1.27) and 18,291
(HS_2050, ×1.57), depending on which demographic outlook and year you pick; the corridor's
no-build transit *share* of car+transit stays roughly flat (0.16–0.17) in every scenario, because
the forecasting method used to build these future matrices carries the 2022 mode split forward
by construction (it's not itself predicting behavior change).

**Central-case LRT capture (underground):** grows from 3,332 (2022) to 4,114 (BU 2040), 4,498
(BU 2050), 4,520 (HS 2040), and **5,354 trips (HS 2050)** — the highest single number reported in
this entire methodology file. All-ground scenario: 2,544 → 3,105 / 3,386 (BU) → 3,430 / 4,047
(HS). Importantly, the LRT's *share* of no-build transit trips barely moves across all these
scenario-years — staying about 0.28–0.29 underground and 0.21–0.22 ground in every single year.
That's because, as the method above explains, only the *market size* changes between scenarios;
the cost-based switching rate is held completely fixed at the 2026 skim values. So this step is
really answering "how much bigger does the corridor's transit market get," not "does the LRT get
relatively more or less attractive over time" — the latter isn't tested here at all.

Over the tested λ range, the uncertainty band is wide: BU_2040 underground ranges 2,889–6,093
trips; HS_2050 underground ranges 3,828–7,815 trips. The busiest physical link stays
Namal-Giborim → Hamifrats in every scenario-year, growing from 995 trips (2022, three-hour
morning total) to as much as 1,717 trips (HS 2050); in peak-hour terms (applying step 27's
factor), that's roughly 588 trips today rising to about 1,014 in the highest-growth scenario.

A design-speed ceiling variant follows the same pattern one level higher: central case grows from
3,970 (2022) to 5,416/6,432 (HS 2040/2050), consistently about a fifth above the calibrated
underground case in every year.

**Caveats.** Same corridor-internal-only limitation as step 31 (both trip ends must be among the
25 areas). The 2026 cost skims are applied unchanged to every future year — so this result
explicitly does **not** account for future road congestion getting worse, the bus network
changing, or any LRT branch lines being built; all future growth in the number is pure market
growth, not a changing competitive position for the LRT. The future-year mode split (car vs.
transit) is carried forward from 2022 by the construction of the demographic-forecast step, not
independently predicted. No capacity limits are modeled. The three "perception" assumptions
carried over from step 31 — the assumed λ, the LRT premium, and the free LRT–Metronit transfer —
have exactly the same uncertain standing here as they did there; nothing about running the model
on future years makes those assumptions any more validated.

---

### 7. Output inventory (`Output/`)

A plain guide to what lives in the main output subfolders relevant to this document (the folder
also holds many earlier-step outputs described in prior parts of this file):

- **`Output/gc/`** — Step 26's generalized-cost work: per-mode cost tables for car, bus and the
  LRT scenarios, the walking-access tables for LRT stations, and — most importantly —
  `gc_data_inventory.csv`, the running "gap list" of which cost components are real data, which
  are calculated, and which are still just assumed placeholders.
- **`Output/gtfs/`** — Steps 29–30's transit-schedule work: a level-of-service table for every
  TAZ built from the national bus/BRT timetable, the scheduled area-to-area travel-time skim, and
  the *observed* (real-world, speed-corrected) version of that same skim from step 30, plus the
  underlying routed-trip intermediates.
- **`Output/corridor_v2/`** — The V2-route corridor flow work (steps 24, 27, 28): area-to-area
  trip matrices, link-by-link flows on the three routes (T1/T2/T3) for both the 3-hour and
  peak-hour periods, the recalculated peak-hour factors, and the survey-vs-ticketing comparison
  specific to the V2 geography.
- **`Output/lrt_v2/`** — Step 25's LRT line geometry products: the station table (as CSV and as a
  mappable GeoJSON file), distances between stations, and the calibrated station-to-station
  travel times for the different speed scenarios.
- **`Output/skims/`** — Step 31's complete per-mode cost tables (car, bus, Metronit, LRT
  underground/ground) with a status flag on every cell, an Excel workbook version, the failed
  logit-fit diagnostics, and — the key deliverable of this whole section — the LRT capture
  results: how many 2022 riders switch, broken down by scenario, by origin/path type, and loaded
  onto the physical trunk-line segments.
- **`Output/skims/forecast/`** — Step 32's future-year (2040/2050) version of the same capture
  results: the aggregated future demand matrices, market-growth summaries, and the LRT capture
  counts, boardings, and link loads for each of the four demographic scenario-years.
- **`Output/figures/`** — Supporting charts throughout the pipeline (this section's additions
  include the LRT-vs-bus link-flow comparison and the 2040/2050 capture-growth chart).

---

### 8. Known caveats and open questions

Below are the open issues that matter to a reader of *this* part of the model (generalized cost
and LRT capture), explained in terms of what could go wrong if they're ignored:

1. **The corridor's forecast branch is a demographic projection, not a demand forecast.** The
   step-23 future-year matrices grow *population and employment*, but freeze how people choose
   where to go and what mode to take at 2022 levels. If you read "5,354 LRT trips by 2050" as "the
   model predicts changing travel behavior by 2050," that's wrong — it predicts a *bigger market*
   at *today's* behavior. Real changes in congestion, fuel prices, remote work, or the corridor's
   own transit competitiveness aren't in this number at all.
2. **λ (cost sensitivity) is assumed, not measured**, and this is by far the largest source of
   uncertainty in the whole LRT capture estimate — varying it across the tested range alone swings
   the central capture number by roughly ±40–50%. If someone eventually fits λ properly from
   person-level survey data (accounting for who actually has a car available), the whole capture
   number could shift meaningfully in either direction. Treat every specific ridership number in
   this document as conditional on this one unverified assumption.
3. **The LRT "premium" (5 extra generalized minutes of value) and the free LRT–Metronit transfer
   are both stated assumptions**, not measured facts. They matter: removing the premium
   entirely drops the underground capture from about 3,332 to about 2,658; the free-transfer
   assumption alone is estimated to add roughly 400 trips. If either assumption turns out to be
   wrong (e.g., the operators don't actually integrate LRT and Metronit ticketing/platforms), the
   capture estimate would need to be revised down.
4. **Only 10 of the 25 corridor areas have a drawn, real LRT alignment.** The other 15 areas are
   handled with a "feeder composite" — a modeled bus-or-Metronit trip to the nearest real station
   — rather than an actual planned branch line. If real branch alignments turn out to run faster,
   more direct, or differently routed than this feeder approximation, the capture from those
   branch areas (which is a meaningful chunk of the total) could be quite different from what's
   reported here.
5. **Money (fares, parking) has been removed from the entire cost comparison by a policy
   decision**, on the reasoning that the fare is flat and daily-capped so it can't tip the choice
   between transit modes. This is a reasonable simplification for *transit-vs-transit* choices,
   but it also means this model currently has nothing to say about car-side policy levers like
   parking pricing or congestion charging, should those become relevant to the 2040/2050 planning
   picture.
6. **Station walking access is a straight-line estimate** (distance × 1.3 detour factor from a
   TAZ's population-weighted center to the nearest station), not a real street-network walking
   route. Since station-access walking time turned out to be the single biggest reason LRT's
   generalized cost exceeds the bus's, an error here directly and substantially affects the
   headline capture number — a more careful walking-network calculation (already flagged as a
   next step) could move the result noticeably.
7. **178 of 600 area pairs have no direct bus service in the GTFS feed**, so their bus travel time
   still rests on a scaled version of the crude "fastest path" floor from step 26 rather than a
   real routed transfer trip. This could understate or overstate the true bus cost on those
   pairs, which in turn affects how attractive the LRT looks relative to the bus there.
8. **The observed-vs-scheduled bus speed correction (step 30) is based on a single representative
   May 2026 weekday.** Bus running times vary with weather, events, and season; a single day's
   AVL data, however carefully processed, is a snapshot rather than a robust seasonal average.
9. **The corridor-internal scope leaves out a large share of total trips.** Only trips with both
   ends inside the 25 study areas are counted (about 75,000 of 184,000 total study-area trips
   noted elsewhere in project docs) — so the reported capture numbers are a lower bound on the
   corridor's *true* total ridership if the LRT also attracts trips with one end outside these 25
   areas.
10. **The 2022 transit base itself is uncertain on the Nazareth branch**, where survey and
    ticketing data disagree by roughly a factor of two (step 28's finding). Since the incremental
    logit model pivots off exactly this observed 2022 transit base, an error in that base number
    on the Nazareth branch would carry straight through into the branch's LRT capture estimate.

---

### 8b. Related work — PCA-based analysis and structural comparison of OD matrices

A separate family of diagnostic notebooks (not part of the main forecasting chain, kept under
`notebooks/diagnostics/`) re-examines the earlier comparison between survey-based and
cellular-phone-based travel matrices, but using a different statistical lens: instead of checking
individual origin-destination cells one at a time, it looks at whether the *whole pattern* of
trips can be boiled down to a small number of underlying "shapes" or components (a technique
called PCA, principal component analysis), and then compares whether the survey and the cellular
data produce similar shapes. This is mentioned here mainly as background/context — it's a
cross-check on data quality for the survey/cellular comparison discussed elsewhere in this
document, not something the LRT capture numbers in steps 26–32 depend on directly. The section
also traces this approach's roots in the broader transport-research literature (its authors,
published papers, etc.), for anyone who wants to dig into the statistical technique further —
that detail isn't needed to follow the capture model itself.

---

### 9. Reproduction

A short practical guide to actually running this part of the pipeline yourself:

**First, get the data.** Some input files are stored via Git LFS (Large File Storage — a way of
keeping big files out of the main git history) rather than committed directly, so they need to be
pulled explicitly before running anything:

```bash
pip install pandas numpy scipy matplotlib jupyter openpyxl pyshp shapely pyproj
git lfs pull --include="Input/*.xlsx,Input/*.csv"   # required as of 22 Sep 2026
git lfs pull            # optional — needed for the historical cellular chain, raw RavKav/train files, and the 2040/2050 zonal forecasts
```

For this section specifically, you'll also need:
```bash
git lfs pull --include="Input/BusSpeedData/std_202605.csv"       # needed by step 26 (and step 30)
git lfs pull --include="Input/GTFS/israel-public-transportation.zip"  # needed by step 29 (else it runs a placeholder dry run instead)
git lfs pull --include="Input/Demographic_Forecast/Zonal_*.csv"  # needed by step 32 (and the earlier forecast step it depends on)
```

**Then, run the notebooks in this order** (each is self-contained — it loads its own inputs and
writes its own outputs — but later steps in this chain depend on earlier ones' output files
existing, so the order matters):

```bash
# step 27 must run before step 24 (which reads its peak-hour factors)
jupyter nbconvert --to notebook --execute --inplace notebooks/current/Corridor_peak_hour_V2_routes.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/current/Corridor_flow_profile_V2_routes.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/current/Corridor_profile_V2_survey_vs_ticketing.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/current/LRT_line_stations_travel_time.ipynb

# GTFS steps must run BEFORE step 26 (which reads their output)
jupyter nbconvert --to notebook --execute --inplace notebooks/current/GTFS_bus_LOS_TAZ.ipynb            # step 29
jupyter nbconvert --to notebook --execute --inplace notebooks/current/GTFS_bus_observed_times.ipynb      # step 30 (needs step 29's output + the bus-speed LFS file)

jupyter nbconvert --to notebook --execute --inplace notebooks/current/GC_data_inventory_and_skims.ipynb  # step 26

jupyter nbconvert --to notebook --execute --inplace notebooks/current/Mode_skims_and_flow_comparison.ipynb   # step 31 (needs steps 24, 26, 27, 29, 30)
jupyter nbconvert --to notebook --execute --inplace notebooks/current/LRT_capture_forecast_2040_2050.ipynb   # step 32 (needs step 23's forecast sets + step 31)
```

If you only change something in steps 25/26/31/32 and want to re-check the LRT capture number,
you don't need to rerun the whole chain — just steps **25 → 26 → 31 → 32**, in that order,
takes about ten minutes. Every notebook moves its own working directory to the repository root
in its first cell, so you can run them from anywhere inside the repo. Outputs under `Output/` are
committed as ordinary git files (not LFS), so you can compare your reproduced output against
what's already in the repo to check you got the same result.

---

### Where things stand today

As of this writing, the single most current, defensible answer to "how many riders will the LRT
capture" is: **about 3,332 morning (06:00–09:00) corridor-internal trips in 2022** for the
all-underground alignment (about 2,544 for an all-ground alignment), growing to roughly **4,500
to 5,400 trips by 2040/2050** purely because the surrounding travel market grows — not because
the LRT becomes relatively more attractive over time, since the same 2026 costs are applied to
every forecast year. This number depends most heavily on one specific unproven assumption: the
cost-sensitivity parameter λ, which the 2022 revealed-choice data could not actually pin down (the
statistical fit returned the wrong sign, confounded by car availability) and so was simply
assumed at a central value of 0.03 per generalized minute. Varying that single assumption across
its tested range alone moves the central estimate by roughly plus or minus 40–50%. Two further
assumptions — a 5-minute "rail premium" and a free LRT–Metronit transfer — sit on the same
unproven footing and together account for a meaningful share of the predicted capture. What
remains genuinely open, going forward: fitting λ properly from person-level survey data (the
planned next step), replacing the straight-line station-walking-access estimate with a real
street-network calculation, and obtaining actual branch-line geometry for the 15 of 25 corridor
areas that currently rely on an approximated bus/Metronit feeder rather than a real drawn LRT
line — any of these could shift the headline number in either direction.

---

## Part 5 — What changed on 23 September 2026: the mode-code correction, the person-level λ, the 2025 smart-card data, the matrix tests, and the rebuild of the bus calibration (Steps 33 – 35 and the rerun of 15 – 32)

*Added 23 September 2026. Everything above reads at the 22 September state; this part says
what moved, why, and what the numbers are now.*

### 5.1 The short version

Four things happened in one day, and each led to the next:

1. **The survey's mode codes were wrong in the chain.** Code 4 is the group taxi (sherut) and
   code 5 is the Matronit (Haifa's bus rapid transit). The chain had them the other way round,
   so every Matronit rider in the survey had been sitting in the "taxi-type" layer — a layer
   the ridership model left out of the choice set. The chain was rerun with the codes fixed.
2. **λ, the cost sensitivity, was estimated properly** from the survey's person records, with
   car availability held constant. The estimate (0.035 per generalized minute) supports the
   0.03 the model had assumed. For the people who actually choose between their own car and
   transit, it still cannot be pinned down.
3. **New smart-card (RavKav) data for 2025 arrived** — one row per boarding tap for the
   Metronit, every rail station in the country, and all the buses of the north. It was turned
   into a boarding layer for a representative Tuesday, a bus + Metronit origin–destination
   table, a rail table measured from the entry and exit gates, and boarding-hour peak factors.
4. **The matrix tests were rerun on everything**, and they found something the project had
   not seen: the survey's bus matrix and the raw RavKav journeys of 2022 have the *same*
   destination structure, to within the survey's own day-to-day noise — while the ticketing
   matrix the chain had been calibrating to, which spreads the RavKav volumes using the
   on-board survey's alighting pattern, matches the survey no better than a random shuffle of
   the geography. **The on-board pattern, not the ticketing volume, was what separated the two
   sources.** So the bus calibration (step 15) was rebuilt on RavKav's own alightings, and steps
   16–35 rerun on the result.

The rebuilt base is smaller in total (the calibrated bus layer is 8 % below the survey rather
than 1 % above it) but larger inside the corridor, and the long-standing disagreement between
the survey and the ticketing along the LRT line is gone. The LRT ridership figure barely moved
(4,114 → 4,250 morning trips, all-underground central case), because the capture *rate* did not
change; what changed is that it now rests on a transit base whose two sources agree.

### 5.2 The mode-code correction (what was wrong, what it moved)

The survey's activities file, which came with the person and household tables, carries the
mode labels in Hebrew alongside the codes. Matching the two files record by record showed that
code 3 is the public bus, **4 the group taxi, 5 the Matronit**, 7 the train, 8 the special taxi.
Steps 15–32 had used `BUS = [3, 4]` and `TAXI = [5, 8]`. Inside the 25 corridor areas, at the
2018 survey level, the transit layer was 6,747 trips before the fix and 12,673 after; the
taxi-type layer 6,650 before and 723 after. The Matronit is the corridor's main transit
service, so this mattered most exactly where the LRT study looks.

The rerun (before the rebuild of 5.4, so these are intermediate values) moved the corridor
transit market from 11,664 to 13,778 trips and the central LRT capture from 3,332 to 4,114; the
survey-to-ticketing comparison towards Haifa went from a 20 % shortfall to parity.

### 5.3 λ from the person records (step 33)

The 2022 cross-section could not identify λ because the places where the bus is dearest
relative to the car are also the places with the fewest cars (Part 4, 7.2). Step 33 goes to the
individual trip records instead: each surveyed car-or-transit trip within the 25 areas, joined
to its person (age, licence, sector) and household (cars, size), with the generalized-cost
difference from the step-31 skims, and a logit fitted with the survey's `new_wf` weights and
standard errors that respect the household clustering. Result: **λ = 0.035 per generalized
minute, with a range of 0.002–0.068**, the right sign, a good fit (ρ² 0.43). The assumed 0.03
stands as the central case. Split by car availability: households without a car give 0.083,
people without a licence 0.027, and **licence holders in car-owning households — the people
the LRT would take from the car — give 0.008 ± 0.017, which is not distinguishable from zero.**
That group is the one a stated-preference survey is for.

### 5.4 The 2025 smart-card data (step 34)

Three files, 51–52 Tuesdays each, 06:00–09:00, one row per boarding tap with a transfer tag.
Two things had to be handled first: stop codes are **not unique across operators** (Tel Aviv
and Jerusalem operators tap "northern" codes at places far outside the area), so every stop
is keyed by operator cluster and code and located from the taps' own coordinates; and the
representative day is the average of the 42 Tuesdays common to the three files after dropping
holidays, the June war and data gaps.

What came out: **bus 88,728 journey origins + 2,911 transfer boardings a day, Metronit 13,078 +
1,029**; a bus + Metronit journey table of 101,680 journeys with both ends in the study area
(destinations borrowed from the 2022 RavKav alighting pattern, since the 2025 file has no
alightings); a **rail table measured from the taps** — the zero-passenger rail rows turned out
to be the exit gates, so entries and exits could be matched card by card: 20 northern stations,
23,408 entries a day, 9,437 trips between northern stations, agreeing with the 2019 station
matrix at a cosine of 0.97; and boarding-hour peak factors (bus 0.475, Metronit 0.433 of the
three hours in the busiest 60 minutes, 07:15–08:15 — flatter than the survey's 0.589, which is
a departure-time figure).

Two cautions. The transfer tag marks only 3.7 % of boardings as transfers, where the 2022
linked journeys had a third of their legs as transfers — so the 2025 "journey origins" are
closer to legs than to journeys, and the question of what the tag means under the daily fare
cap goes to the provider. And the base was **not** moved to 2025: doing so needs that answer,
a 2025 alighting inference of its own, and a 2025 car observation, none of which exist yet.
The 2025 layer is used as a check on the 2022 anchor (boardings by area agree at 0.98), not as
its replacement.

### 5.5 The matrix tests, and what they found (step 35)

The same tests as Part 2 (cosine similarity, GEH, Kolmogorov–Smirnov on trip lengths, MSSIM,
PCA subspace overlap) were run on today's products, with the survey's two days as the "how
close can two honest measurements be" reference. At the superzone level:

| Pair | Cosine | KS D | PCA overlap |
|---|---|---|---|
| Survey day 1 vs day 2 (the reference) | 0.89 | 0.04 | 0.83 |
| Survey bus vs RavKav 2022 spread on the **on-board survey's** pattern (the old calibration reference) | 0.62 | 0.21 | 0.62 — no better than chance |
| Survey bus vs RavKav 2022 on **RavKav's own** alightings | **0.89** | **0.05** | **0.81** |

Read plainly: the survey and the raw ticketing agree as well as the survey agrees with itself.
The matrix that had been used to calibrate the bus layer does not agree with either, and its
trips are twice as long (median 6.4 km against 3.2–3.6). Step 9 had chosen the on-board pattern
over RavKav's own alightings on a fine-grained (TAZ-level) correlation; every coarser test says
the reverse. There are two possible readings — the on-board survey over-represents long lines,
or RavKav's alighting inference cuts journeys short at the transfer hub — and the data cannot
choose between them. But for the chain the choice was clear: calibrate to the source the survey
agrees with.

### 5.6 The rebuild of step 15, and what it changed

Step 15 now takes its ticketing prior (the superzone destination pattern the survey rows are
shrunk towards), its within-superzone destination split and its coverage-rule volumes from the
2022 RavKav journeys on RavKav's own alightings. The held-out validation (households split in
half at random, 40 times; one half's blend predicts the other half's rows) now prefers the
ticketing pattern outright: the best shrinkage constant went from 2 to 100, and the pure
ticketing rows predict held-out survey households *better than the survey's own rows do*
(JSD 0.267 against 0.336; the on-board rows had scored 0.422).

| Quantity | Before (on-board pattern, corrected codes) | After (RavKav's own alightings) |
|---|---|---|
| Calibrated bus, 2018 / 2022 | 127,185 / 130,779 | **115,430 / 117,961** |
| Bus base against the survey's 125,439 | 1 % above | 8 % below |
| Guarded origin × segment cells (survey kept) | 31 | 30 |
| Deliverable transit set (bus + rail), 2022 | 134,829 | **122,011** |
| Transit share of car + transit, all study area | 9.1 % | 8.3 % |
| Corridor-to-corridor bus trips | 9,837 | **10,255** |
| Corridor-internal transit market, 25 V2 areas | 13,778 | **14,133** |
| Trunk inflow link (Bazan-Hutsot → Tsomet Kiryat Ata), transit, 3 h | 3,886 | **4,420** |
| Survey ÷ ticketing, Haifa segment, towards Haifa (network) | 0.62 | **0.98** |
| Survey ÷ ticketing, Nazareth origin | 962 vs 2,402 (ticketing 2.5 ×) | 517 vs 185 (ticketing 0.36 ×) |
| LRT trips, central, underground / ground / design regime | 4,114 / 3,201 / 4,814 | **4,250 / 3,207 / 5,095** |
| LRT capture rate (share of transit, underground) | 0.277 | 0.277 |
| Busiest LRT trunk link, 3 h / peak hour | 1,452 / 663 | **1,671 / 764** |
| LRT trips 2040 / 2050, underground: BU, HS | 5,329 / 5,962; 5,335 / 6,245 | **5,390 / 6,094; 5,598 / 6,516** |

Why the total fell and the corridor rose: the on-board pattern had moved journeys from the outer
superzones' local market to inter-superzone, Haifa-bound cells, which passed the coverage test
and pushed the total up; RavKav's own alightings keep 40,816 journeys local (against 23,277),
so more local segments pass the test and take the lower ticketing volumes, while more of the
Krayot and Kiryat Ata journeys stay inside the corridor.

**The survey and the ticketing now agree along the whole line.** The 2.5–3 × ticketing excess
towards Tirat Carmel, and the Nazareth-branch excess, that Parts 3 and 4 discuss at length
were the on-board pattern. What remains is the Nazareth branch itself: the two ticketing
readings (on-board pattern 2.5 × the survey, RavKav's alightings 0.36 ×) disagree with each
other by 13 × and bracket the survey. Only a passenger count on that branch settles it, and
until then the Nazareth-branch market is carried as a range.

### 5.7 Where things stand now

The single most current answer to "how many riders will the LRT capture" is **about 4,250
morning (06:00–09:00) corridor-internal trips in 2022** for the all-underground alignment
(3,207 all-ground, 5,095 in the specified 50 km/h design regime), growing to **5,400–6,500 by
2040/2050** with the market. The λ range alone moves the central figure between 3,161 and
6,028; the rail premium between 3,406 and 5,232. These dependencies are unchanged from Part 4.
What has changed is the footing: the transit base is now calibrated to a ticketing source
the survey agrees with, and the transit market the capture is applied to includes the Matronit
riders it had been leaving out. Still open, in order of value: a passenger count on the Haifa
trunk and the Nazareth branch; the meaning of the 2025 transfer tag; the branch alignments and
operating plan; the walking network for station access; and a stated-preference survey for
the choice riders' λ.
