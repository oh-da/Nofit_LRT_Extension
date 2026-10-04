# Validation plan under the Ministry of Transport guideline (written 4 October 2026)

**Source.** *תיקוף המודלים המטרופוליניים 2024*, Ministry of Transport, Systems Planning Division, Round Table on
Transport Models, **draft 6, 16 September 2024** (uploaded to the session as `…_6.docx`). It sets, for the new
metropolitan models, a three-stage list of validation checks, each with a level of detail, a numerical
criterion, the data to compare with, and a statistical appendix (R², MAE, chi-square, coincidence ratio,
RMSE%, GEH, KS).

**What this plan does.** Goes through every check in the guideline, decides which apply to *this* project, which of
those we have the data to run, and specifies how they are run and reported. Numbers in the "expected" lines are
from the existing tests (METHODOLOGY §6j–§6ah) and are forecasts of the outcome, not results.

---

## 1. How the guideline fits this project

The guideline is written for a **full four-step (or activity-based) model with a trip-generation / population
synthesis stage, a destination-choice model, a mode-choice model, a time-of-day model and equilibrium
assignments**. Our project is different:

| | Guideline's model | This project |
|---|---|---|
| Demand | Estimated generation, distribution and split models | A **survey-expanded OD matrix** (THS 2017/18) calibrated to RavKav (bus) and moved to 2022 by demographic factors |
| Mode split | Estimated logit | Observed in the survey; the LRT is added by an incremental logit pivoted on the 2022 transit share (λ assumed 0.03, person-level 0.035) |
| Time of day | Estimated model | One AM period, 06:00–09:00, plus survey-based peak-hour factors |
| Assignment | Equilibrium, car and transit | None. Corridor *potential movements*; a car all-or-nothing link check is planned (step 42) |
| Externals | Modelled belt | Excluded (≈ 5 % of survey weight; trips with one end outside the 778 TAZs) |

Three consequences for selection:

1. **Checks of an estimated model against the data it was estimated on are circular here** (the matrix *is* the
   survey). They are not validation. They are run only where they test a *step we added* (zone allocation, growth
   to 2022, bus calibration, Furness), and labelled "consistency check".
2. **Checks against independent data are the valuable ones**, and the repository has four independent sources:
   RavKav (2022 and 2025), road counts on 3,241 links, the GTFS and measured bus speeds, and the cellular matrix.
3. **Some criteria cannot be met by design** (a residents-only, AM-only, assignment-free car layer against all
   traffic). Per the guideline's own rule — gaps are explained, *the model is not changed* — these are reported as
   misses with the reason, not tuned away.

**Freeze.** The guideline requires the scenario and model to be frozen during the validation. The frozen version is
the 23 September 2026 rebuild (step 15 on RavKav's own alightings; steps 16–36 rerun). No product is changed by
this plan; any fix goes to a later version.

---

## 2. Check-by-check decision

Legend: **RUN** = applicable and data in hand · **RUN\*** = applicable, run as a consistency check (circular or
partial) · **DEFER** = applicable, one input missing (named) · **N/A** = does not apply to this project.

### Stage 1 (guideline §3)

| Guideline check (criterion) | Decision | Reason / data |
|---|---|---|
| 3.1 Zone system presented and approved (super-zones, core/rings/sectors) | **RUN** (documentation) | 778 TAZ → 36 super-zones → 28 sub-areas → 25 V2 areas exist. External sectors N/A |
| 3.2 Population segments: Jewish non-Haredi, Haredi, Arab; urban / suburban / rural | **RUN** (documentation) | THS household table has `HHTYPE` (arab / orto / religious / secular / other), which gives the three groups directly (decision D2); `Zonal_2020.csv` has `SETTL_SIZE` for the settlement type |
| 3.3 Residents by super-zone ±5 %; by segment ±5 % (CBS) | **RUN\*** | Compare THS-*expanded* residents (sum of `new_wf` by home TAZ) with `Zonal_2020.csv` / `Zonal_BU_2025.csv`. CBS itself is not in hand (standing data request 6) → CBS part **DEFER** |
| 3.3 Employed by residence / by workplace ±15 %; household size; employment rate; car availability by household ±5 % | **DEFER** | Needs CBS tables and the labour-force survey. Household size and car availability from `HHfinal.csv` can be shown against the zonal file as a partial check |
| 3.3 Network size and class; prices against external sources | **RUN** (documentation) | Emme link table (counts of links by `TYPE`), GTFS stop and route counts, fare assumptions (none in GC: money out by decision) |
| 3.4 Population generator, car-ownership model, trips per person / household / worker, activities per tour, tour structure | **N/A** | No generation model; no tours. Trips per resident enter only through the survey and the 2018→2022 growth, covered by T3 below |
| 3.4 Total person trips by purpose / super-zone ±20 %; per resident by segment ±15 % | **RUN\*** | See T3: tests that the growth step kept trip rates, not that a model reproduces the survey |
| 3.5 Trip-length distribution passes KS, by purpose and segment | **RUN** | See T4 (against the survey's *reported* distances, which are independent of the zone-centroid proxy) |
| 3.5 Daily and period OD matrix, super-zone level, coincidence ratio > 0.6 vs the survey and vs the cellular survey | **RUN** | See T5 (cellular) and T7 (survey-based layers against each other). Survey-only comparison is circular and shown only for the allocation step |
| 3.5 Trips outside the metropolis by sector ±15 % vs cellular | **N/A** | External trips are excluded from the layers. The sector flows exist in the cellular file; report them as context only |
| 3.5 Share of intra-zonal trips by super-zone and settlement type; through trips | **RUN** | See T6. Through (external–external) N/A |
| 3.5 Employed working inside / outside the locality ±15 % (CBS) | **DEFER** | Needs CBS locality-of-work tables |

### Stage 2 (guideline §4)

| Guideline check (criterion) | Decision | Reason / data |
|---|---|---|
| 4.1 Trip start time by segment, CR > 0.6 vs the survey | **RUN** (against independent profiles) | See T8: survey departure profile against road-count hourly profile (car) and RavKav boarding profile (bus, Metronit, rail). Activity start time / duration (activity-based) N/A |
| 4.2 Mode split by origin / destination super-zone, by segment, by locality type, by period; CR > 0.6 vs THS | **RUN\*** | See T9. Circular for the survey part; independent for bus share by super-zone (RavKav) |
| 4.2 Value of time in range; out-of-vehicle ÷ in-vehicle time 2–3 | **RUN** (documentation) | GC = IVT + 2·walk + 2·wait + 8·transfer; money is out by decision, so no VOT. The 2 and 2 weights sit in the 2–3 range; person-level λ gives the time scale |
| 4.3 Average car occupancy by super-zone, segment, locality type, period; CR > 0.6 | **RUN\*** | See T10. Occupancy 1.33 is taken from the survey (range 1.25–1.45 carried) |
| 4.4 Commercial vehicles / trucks (cordon counts by class) | **N/A** | No commercial model. The counts include trucks; this is part of the expected shortfall in T11 / T12 |
| 4.5 External car trips ±5 % per sector; external rail ±5 %; through matrix | **N/A** | No external belt in the layers. The six cordons of T12 are the closest analogue and carry the "through" allowance |

### Stage 3 (guideline §5)

| Guideline check (criterion) | Decision | Reason / data |
|---|---|---|
| 5.1 Link volumes vs counts: R² > 0.85, slope 0.9–1.1, RMSE% < 35 %; RMSE% by volume class (> 50 % under 500 … > 12 % over 8,000) for inter-urban and urban roads; local roads and toll roads: RMSE% only | **RUN** after step 42 | See T11. Counts: 3,241 links, hourly PCE (`YARAM6…19`). Needs an assignment (planned, step 42) and the Emme links pulled from LFS |
| 5.1 Screenlines / cordons: external ±10 %, others ±15 %, RMSE% < 35 %, 2–4 sectors per cordon | **RUN** | See T12. Step 36 already has six closed cordons; add sectors and the guideline's format |
| 5.1 Turning movements | **N/A** | No turn counts |
| 5.1 Road travel times: ±15 % in ≥ 85 % of measurements | **DEFER** | Needs the Google Distance Matrix sample (step 37, `GOOGLE_MAPS_API_KEY` missing). Today's car skim is a survey door-to-door time |
| 5.2 Bus boardings: total by sector / super-zone ±15 %; per line by size class | **RUN\*** (by origin zone, not by line) | See T14. No line-level assignment exists, so the per-line row is N/A |
| 5.2 Heavy-rail boardings and alightings by station (RMSE% by size class), belt stations ±10 %, station-pair matrix R² > 0.85 / slope 0.9–1.1 | **RUN** | See T15. 2025 station taps for 20 northern stations vs the 2019 station matrix scaled to 2022; the 2025 file is not 2022 (gap stated) |
| 5.2 Light-rail / BRT boardings by station, link passengers ±20 % | **RUN\*** (Metronit only, area level) | See T16. The LRT does not exist; the Metronit is the only BRT. Link passengers need alightings the 2025 files lack → **DEFER** (step 41) |
| 5.2 Transit travel times: bus ±15 %, Metronit ±10 %, rail ±10 % in ≥ 85 % of measurements | **RUN** (bus, Metronit) / **DEFER** (rail) | See T17. `bus_trips_observed.csv.gz` has scheduled and observed minutes per trip. Rail: no Israel Railways times in the repository |
| 5.2 Transfers and transit matrix: R² > 0.85, slope 0.9–1.1 at super-zone level vs on-board or clearing-house matrix | **RUN** | See T7. RavKav 2022 / 2025 journeys on RavKav's own alightings; the on-board survey is kept as the comparison it already is |
| 5.3 Special trip generators | **N/A** | None modelled |
| 5.4 Intra-zonal share < 5 % | **RUN** | See T6 (the criterion's wording is ambiguous: question Q4) |
| 5.5 Convergence (assignment, demand–supply loop) | **N/A**; **RUN\*** for Furness | There is no iteration to converge. The Furness and the step-15 margins are checked in T19 |
| 5.6 Individual route checks | **N/A** | The guideline itself marks it "to be completed" |

### Appendix (statistics)

| Statistic | Use |
|---|---|
| R², slope through the origin, MAE, RMSE%, CR, KS, chi-square | Implement all in one place (T0) |
| GEH | The guideline **drops** GEH ("criticised, not used in the validation guidelines"). Our earlier GEH tables (steps 12–14, 21, 35) stay in the repository as supplementary and are not part of the guideline pack |

---

## 3. The selected tests

Nineteen checks are selected (T0–T19). Priority: **A** run first (data in hand, high value), **B** run after a data
pull or step 42, **C** cheap descriptive checks, **D** deferred until the named input exists.

Common conventions (from the guideline's "general instructions", all followed): data source, date and processing
stated before each test; table with the control value, the model value (absolute) and the difference in %;
scatter plots with **observed on x, model on y, regression through the origin with its equation and R²**,
outliers named and explained; a summary table per test against the criterion; **one Excel workbook with one sheet
per test** holding the matched data and the computed metrics; the vintage of every comparison data set and any
growth applied to it. The guideline asks for three periods (AM peak, PM peak, midday); **the layers are AM only today**.
Extension X1 (build the PM and midday survey matrices) is **approved (D3)** and scheduled as wave 1b, so the tests
that the guideline wants in three periods are first run for AM (06:00–09:00 and the 07:00–08:00 peak hour) and then
repeated for PM and midday when X1 lands.

### T0. Metrics module — priority A, ½ day
`tools/validation_metrics.py` (a library, not a notebook, so the "do not import across notebooks" rule does not
apply): `r2_origin`, `slope_origin`, `mae`, `rmse_pct`, `coincidence_ratio`, `ks_stat` (with the guideline's
critical value at α = 0.05), `chi2_stat`, `within_pct(share of measurements within ±x %)`, and
`size_class_rmse(table)` for the guideline's volume-class thresholds. Unit tests on synthetic data and on a hand
calculation. **Output:** the module plus `tools/test_validation_metrics.py`.

### T1. Zone system and segment definitions (§3.1–3.2) — C, ½ day
Document the 778 / 36 / 28 / 25 hierarchy with a map (Output/figures), the sector coding (from `HHTYPE`: Arab = `arab`,
Haredi = `orto`, Jewish non-Haredi = `secular` + `religious` + `other`; see D2) and settlement type from `SETTL_SIZE`. **Needs the steering decision on the levels** (guideline: "the
committee approves the geography"). **Output:** workbook sheet `T1_zones`; two paragraphs in the report.

### T2. Residents by super-zone (§3.3) — A, ½ day, partly deferred
**Data:** `HHfinal.csv` + `PersonsFin2.csv` (LFS, pull) and the trips file's `new_wf`; `Zonal_2020.csv`,
`Zonal_BU_2025.csv`. **Method:** expanded residents by home super-zone and sector vs zonal population (grown to
the scenario year with the step-16 factor); criterion ±5 %. Also expanded household size and household car
availability (`HHVEHICLE`) vs the zonal file's fields. **Why it matters:** the whole base rests on the expansion
(METHODOLOGY §8); this is the first test of it that does not need new data. **Expected:** reasonable at
super-zone level, weaker for small super-zones; this also bears on the survey-to-cellular volume ratio of 3.6.
**CBS comparison:** deferred until standing data request 6 is met.

### T3. Trip rates preserved through the 2018→2022 growth (§3.4) — C, ½ day
Person trips per resident (by sector, by super-zone) and per household: THS 2018 vs the 2022 car + bus + taxi +
rail layers over the grown population (±15 %); total trips by purpose and by super-zone (±20 %). **Consistency
check:** the growth step is designed to keep the rates; the test proves it did, and shows where the
small-zone fallback to the super-zone factor distorts them. **Data:** `three_mode_2022/growth_factors_taz_2018_2022.csv`,
final matrices, zonal files.

### T4. Trip-length distribution (§3.5) — A, ½ day
KS between the matrix's distribution and the **survey's reported trip distances** (not the centroid proxy), by
purpose and by sector. **Criterion:** pass the KS test (D below the critical value). **Data:** trips file (distance
field), `Output/ths2017/three_mode_2022/*_2022_taz.csv`, TAZ centroids. **Expected:** the centroid-based distance is
about 1.8 × the reported distance for short trips (median 1.95 vs 1.11 km): a **miss**, explained by zone geometry
and by the TAZ allocation being population/employment rather than observed. State it, show the TAZ-allocation
effect by also running the test at the 1,250-zone level, where the allocation does not enter.

### T5. Matrix against the cellular survey (§3.5) — A, ½ day
Coincidence ratio (CR) of the AM and the daily super-zone matrix against the cellular matrix; criterion CR > 0.6.
Existing cosine / KS / MSSIM results are reported beside it. **Data:** `Input/Matrices/AvgDayHourlyTrips201819_1270_weekday_v1.csv`
(LFS, pull), zone keys. **Expected:** cosine 0.92 at super-zones; CR is stricter and may fall near or under 0.6 for
the sparse off-diagonal cells; report both the full matrix and the matrix without the diagonal, since 87 % of the
survey–cellular divergence sits on the diagonal. **Extension:** the same for the external-trip rows, as context.

### T6. Intra-zonal share (§3.5, §5.4) — C, ¼ day
Share of trips that start and end **inside the same TAZ** (decision D4), by super-zone and settlement type, for each
layer, and the survey-minus-cellular difference. **Criterion:** < 5 % of person trips. **Preview (not a result of this
test):** on the final 2022 car + transit matrix the diagonal holds 304,600 of 1,475,809 trips, **20.6 %**, so this will
be a miss; the survey's short trips (47 % stay inside one cellular zone) and the size of the 778 TAZs explain it, and
the cellular matrix shows the opposite pattern. Reported as a miss with that explanation. **Data:** final matrices.

### T7. Survey-based transit matrix against RavKav matrices (§3.5, §5.2) — A, ½ day
R² and slope (through the origin) at super-zone and sub-area level, CR > 0.6, between the calibrated bus layer
(2022) and the RavKav 2022 journeys on RavKav's own alightings, and against the 2025 layer. Criterion R² > 0.85,
slope 0.9–1.1. **Two versions:** the raw survey bus matrix (independent of the calibration) and the calibrated
layer (a check of direction, since RavKav volumes enter the calibration). **Data:** `Output/ths2017/two_mode/`,
`Output/ravkav_2025/bus_od_*`, `Output/ths2017/tests/ravkav2025_*.csv`. **Expected:** the existing cosine of 0.89
suggests the raw survey passes CR but misses slope (ratio 0.74); calibrated layer passes. The on-board pattern
matrices are shown as a negative control.

### T8. Time-of-day profile against independent profiles (§4.1) — A, ½ day
The survey's quarter-hour departure profile 06:00–09:00 (and the hourly profile over the day) by mode group,
against: the hourly car-count profile on the cordon links (`Output/validation/car_cordon_count_hourly_profile.csv`),
and the RavKav boarding profile by quarter-hour (`Output/ravkav_2025/boarding_profile_15min_2025.csv`). CR > 0.6 on the
shape. **Why:** the existing finding that the survey's peak is sharper (0.62 vs 0.38–0.43 on the road; 0.59 vs
0.43–0.48 for transit) is turned into the guideline's metric. **Output:** a table of the three profiles and the
design-hour consequence (the `PHF_SOURCE` switch of handover C11 is the follow-up).

### T9. Mode split (§4.2) — C, ½ day
Mode shares by origin super-zone, destination super-zone, sector and locality type, calibrated layers vs the raw
survey (CR > 0.6): shows what the calibration changed and where the guarded cells sit. Independent part: bus share by
origin super-zone against RavKav (the existing ratio table, now with CR). Time weights and the VOT range
documented (GC weights 2 / 2 / 8 against the 2–3 range). **Data:** `two_mode/mode_share_sz.csv` and neighbours.

### T10. Car occupancy (§4.3) — C, ¼ day
AM occupancy by super-zone, sector and locality type vs the global 1.33 (CR > 0.6 of the zone pattern against the
global value, plus the range). It matters because the cordon test (T12) depends on it. **Data:** trips file
(`new_wf`-weighted driver / passenger).

### T11. Link volumes against counts (§5.1) — B, 1–2 days after step 42
All-or-nothing assignment of the 2022 car layer (plus an explicit allowance for the non-resident components) on the
Emme network; 3,241 counted links, direction by direction, AM peak hour and 06:00–09:00; counts in vehicles
(PCE ÷ 1.10), filtered to counts dated 2021–2023 as the primary set (2017–2023 as the sensitivity).
**Reported three ways, because the layer is residents-only and assignment-free:** (a) raw, against the guideline
criteria (R² > 0.85, slope 0.9–1.1, RMSE% < 35 %, and the volume-class RMSE% table); (b) after one global scale
factor (judges the *pattern*); (c) by road class and sub-network (corridor vs rest). **Expected:** (a) fails on
slope, since cordon totals say 0.58–0.90 of counted vehicles, before the AON bias; (b) is the informative one.
**Data:** `Emme_Links_Final_Res 2026-09-23.*` (LFS), `car_2022_taz.csv`, the step-36 factors. **Dependency:** step 42
(handover C10), with free-flow speeds stated by `TYPE`.

### T12. Cordons and screenlines (§5.1) — A, ½ day
Reformat step 36 in the guideline's form: the six closed cordons, each split into 2–4 directional sectors,
inbound and outbound, 06:00–09:00 and the 07:00–08:00 peak hour; difference in %, RMSE% across sectors.
Criteria ±15 % (±10 % for an external belt). **Expected:** most cordon-sectors miss ±15 % (ratios 0.58–0.90 where counts
dominate), by a margin explained by trucks and vans, taxis, buses, non-residents, one-end-external trips and
through traffic. Add the explained part: an allowance for each is out of reach without data, so the report states
the criterion, the result and the unexplained gap, and does not adjust. **Data:** `Output/validation/car_cordon_*.csv`
(exist), `Car_cordon_counts_validation.ipynb`.

### T13. Road travel times against Google (§5.1) — D, ½ day once the key exists
Step 37 (handover C1) produces a Tuesday 07:30 Google duration sample (≈ 40 pairs). Compare with the car skim
(survey door-to-door times, `Output/gc/car_ivt_survey_area_v2.csv`); criterion ±15 % in ≥ 85 % of pairs.
**Blocker:** `GOOGLE_MAPS_API_KEY`. Not started.

### T14. Bus boardings by origin zone (§5.2) — A, ½ day
Calibrated bus origin totals by super-zone and by TAZ vs RavKav 2022 journey boardings (±15 %), RMSE% by size
class using the guideline's thresholds (applied to zone totals, not lines). Separate the **anchored** cells (by
construction equal) from the **guarded** cells (survey volume kept), so the test measures the guard, not the
anchor. Also against RavKav 2025 boardings by TAZ (Output/ravkav_2025/boardings_by_taz_2025.csv) with the 2022→2025
growth of 1.08 stated. **Expected:** the 30 guarded origin × segment cells miss by design; that is the finding.

### T15. Rail stations (§5.2) — A, ½ day
Station entries and exits and station-pair matrix: the 2019 station matrix scaled to 2022 (× 0.793) and the survey
rail layer, against the 2025 RavKav rail taps (`Output/ravkav_2025/rail_stations_north_2025.csv`,
`rail_od_station_2025_north.csv`). R² > 0.85 / slope 0.9–1.1 on the station-pair matrix; RMSE% by station size class
(the guideline's table); the belt-station ±10 % row for the stations at the study boundary. **Expected:** the
2019-scaled vs 2025 stations agree on shape (cosine 0.97) but 2025 carries 2.0 × the trips, so slope ≈ 0.5 unless
the 2022 growth is revisited; the door-to-door survey layer is a different frame and is reported as such.

### T16. Metronit boardings (§5.2) — C, ½ day
Survey Metronit trips (mode code 5) by origin TAZ vs RavKav Metronit boardings by stop → TAZ
(`Metronit_RavKav_Data.csv`, 2025, LFS), RMSE% by station size class, at area level because the survey sample is
thin. Link passengers (±20 %) are **deferred** to step 41 (no 2025 alightings).

### T17. Transit travel times (§5.2) — A, ½ day
(i) Observed vs scheduled bus running time per trip from `bus_trips_observed.csv.gz` (scheduled_min, observed_min):
share within ±15 % (bus) and ±10 % (Metronit, `is_brt`), criterion ≥ 85 % of measurements; the same for the
**skim** values (GTFS-based door-to-door) vs the survey-reported bus times (`Output/gc/bus_gtfs_vs_survey_pairs.csv`).
**Expected:** per-trip observed ÷ scheduled is 1.09 (Metronit 0.87), so the bus ±15 % share is high and the
Metronit ±10 % is borderline; the door-to-door vs survey comparison misses by the ≈ 9-minute overhead already
known (handover C4). (ii) Rail: **deferred**, no train timetable or measured times in the repository.

### T18. LRT time function hold-out (not in the guideline; recommended) — B, ½ day
The guideline has no light-rail-not-yet-built case, but the capture rests on the stop-to-stop function of
`docs/Transit_Travel_Time_Calibration_Report_Operator22.md` (MAPE 5.45 % in sample). Hold out one line / year of
the AVL data, predict, and report MAPE, plus the Metronit sections as an independent check (T17's `is_brt` trips
against the function). **Dependency:** the calibration data set (not in the repository; Q5).

### T19. Furness and margin convergence (§5.5) — C, ¼ day
Residual margin error after the car Furness (step 16) and the step-15 row / column targets, iterations used, and
the rebalance sizes. **Data:** notebook logs and `three_mode_2022/growth_factors_taz_2018_2022.csv`.

---

## 4. Order, effort and dependencies

| Wave | Tests | Prerequisites | Effort |
|---|---|---|---|
| 0 | T0 metrics module | none | ½ day |
| 1 (data in hand, no pull beyond LFS) | T4, T5, T7, T8, T12, T14, T15, T17 | LFS pulls: `trips_ths_2017.xlsx`, cellular matrix, RavKav 2025 rail | ≈ 4 days |
| 1b (approved extension X1) | PM peak (16:00–19:00) and midday (10:00–14:00) survey matrices; repeat T7, T8, T12, T14, T15, T17 for the two periods | steps 15–16 rerun with other windows; RavKav hourly boardings (in hand) | ≈ 1½ days + ≈ 1 day for the repeats |
| 2 (consistency, descriptive) | T1, T2, T3, T6, T9, T10, T16, T19 | LFS: `HHfinal.csv`, `PersonsFin2.csv`, Metronit 2025 | ≈ 3 days |
| 3 (needs an upstream step) | T11 | step 42 (AON); Emme links from LFS | 1–2 days |
| 4 (needs data not in hand) | T13, T18, CBS parts of T2/T3, rail times of T17, Metronit link loads of T16 | Google key; Operator 22 AVL data; CBS tables; Israel Railways times; step 41 | as the inputs arrive |

Execution: `tools/lfs_pull.py` for the LFS inputs; `MPLBACKEND=Agg jupyter nbconvert --execute --inplace`; one
diagnostic notebook per guideline stage in `notebooks/diagnostics/` (`MOT_Validation_Stage1_Inputs_Distribution.ipynb`,
`MOT_Validation_Stage2_Timing_Mode_Occupancy.ipynb`, `MOT_Validation_Stage3_Counts_Transit.ipynb`) so the outputs map
one-to-one to the guideline's working-paper structure. The chain (steps 15–36) is not touched.

## 5. Reporting

* **Workbook:** `Output/validation_mot/validation_workbook.xlsx`, a sheet per test (matched data, differences, metrics)
  and a `Summary` sheet — one row per check: guideline reference, level, criterion, result, pass / miss / not run,
  data vintage, one-line explanation. Also written to CSV (the repository convention).
* **Figures:** scatter plots as specified (observed on x, model on y, through the origin, equation and R²),
  cordon bars, profile overlays, a map of the count and station points by type; `Output/figures/mot_*.png`.
* **Document:** a new chapter in `METHODOLOGY.md` (§6ai onward, the next free section letter), a section in the
  plain-English companion, and a **"Validation against the Ministry of Transport guideline"** chapter in the
  survey-matrices report (revision 3.1) with the summary table, the misses and their explanations, and the
  not-applicable list. Hebrew version updated alongside.
* **Status words:** *pass*, *miss (explained)*, *miss (unexplained)*, *not run (input missing)*, *not applicable*.
  No criterion is relaxed to pass.

## 6. Reading the outcome honestly

Expect these structural misses, which the report should say in advance rather than discover:

* **Absolute car volumes** (T11, T12): residents-only, AM-only, no trucks, externals or through traffic. Pattern
  tests (after one scale factor) are the informative ones.
* **Slope of the bus layer against RavKav** (T7, T14): RavKav records 0.74 of the survey study-wide; it is a coverage
  question for the data provider, not a model error.
* **Rail** (T15): 2019 vs 2025 timing and the door-to-door frame.
* **Distance distribution** (T4): the TAZ allocation is population / employment, not observed.
* **Single peak period**: the guideline's three periods cannot be met until X1.

Passing the guideline's list would still not make the matrices fit for loads or a forecast: the guideline's
criteria test reproduction of the base year, not response to the LRT. Section 10 of the survey-matrices report
(fitness for use) stays the governing statement.

## 7. Extensions to consider (not in the selected list)

* **X1. PM peak and midday survey matrices (approved, D3).** The trips file covers the whole day; rerunning step 15–16 with the
  16:00–19:00 and 10:00–14:00 windows would give the guideline's three periods for T7, T8, T11, T12, T14, T15, T17.
  About 1½ days plus review; the calibration needs the RavKav hourly boardings (available).
* **X2. External-trip segment** (the 5 % set aside), which would make T5's external row and the guideline's belt checks
  possible; listed as open in CORRIDOR_DEMAND_TASKS B2.
* **X3. Sensitivity tests** the guideline defers to a separate document (factorial uncertainty experiment, handover C8).

## 8. Decisions (4 October 2026) and what is still open

* **D1. Scope.** Accepted: the guideline is applied to a survey-based matrix + capture model through the selection above.
* **D2. Sector coding.** `migzar` is **not** the sector variable. The dictionary has no entry for it, and its values are area strata:
  1–3 cover Jewish areas (123 Arab households sit there) and 4–5 are Arab localities (1,466 of 1,497 households are Arab).
  The household-level sector is `HHTYPE`. Mapping used: **Arab = `arab`; Haredi = `orto`; Jewish non-Haredi = `secular` +
  `religious` + `other`.** Step 33 used `migzar` 4–5 as "Arab-sector"; that remains a locality proxy and the
  validation sheets will carry both versions.
* **D3. PM peak and midday matrices (X1).** Approved: wave 1b.
* **D4. Count years.** 2021–2023 primary; 2017–2023 as the sensitivity.
* **D4b. Intra-zonal criterion.** "< 5 %" is the share of trips that start and end inside the same TAZ (T6).
* **Open: Q5.** Can the Operator 22 AVL data used for the travel-time function be shared for the hold-out (T18)? Until then T18 stays deferred.

---

## 9. Status after wave 1 (4 October 2026)

Run: **T0** (metrics module, hand-checked), **T4, T5, T7, T8, T12, T14, T15, T17** (three executed notebooks, METHODOLOGY §6ai, `Output/validation_mot/validation_workbook.xlsx`, 50 summary rows) and the bus destination-pattern experiment **T7b**.
Outcome by row: **18 pass**, **26 miss (explained)**, 3 not applicable, 3 findings.

| Test | Result against the guideline criterion |
|---|---|
| T4 trip length (KS) | car: miss (D 0.22-0.26; median 2.4 vs 1.5 km reported, intra-TAZ trips); transit: D 0.060-0.064 vs 0.055, **pass** once the detour (0.97) is allowed for |
| T5 CR vs cellular | super-zone AM 0.43, whole day 0.47 (0.54 / 0.63 off-diagonal): miss; survey day 1 vs 2 is 0.88-0.89 |
| T7 transit OD vs RavKav | super-zone R2 0.74-0.78, slope 1.06-1.41: miss (the survey's own day 1 vs 2 is R2 0.78); sub-area R2 0.94-0.95, slope 1.05-1.09: **pass** |
| T8 time of day | car 12 cordon-directions CR 0.63-0.79, bus 0.75, Metronit 0.74: **pass**; the survey's peak is sharper than both independent profiles |
| T12 cordon sectors | 44 testable cells: 0.71 of the count in three hours, 16 % within +/-15 %; peak hour 1.19 (1.00 on the well-counted cells): miss |
| T14 bus origins | anchored zones 0.99 of RavKav (four zones off by 18-35 %: explained by the thin-segment rule); guarded zones 2.36 (the coverage rule); all 1.28 |
| T7b destination pattern | RavKav's own alightings beat RavKav-production x on-board probabilities against the survey's bus destinations at every resolution (JSD 0.37 vs 0.54 at 1250-zone level; 0.29 vs 0.36 inside the super-zone); on-board trips are 2 x too long |
| T15 rail | 14 common stations: pattern R2 0.94-0.96, slope 0.44-0.49 (2025 = 2.03 x 2019); after one scale factor RMSE% 18 (entries): miss as is |
| T17 running times | bus 52 % within +/-15 % (criterion 85 %), Metronit 8 % within +/-10 %, door-to-door vs survey 6 %: miss |

**Decisions (4 October 2026)**
* **Zone system (T1).** The keys table the chain uses is authoritative; `Zonal_2020.csv`'s `SZ_NEW` (different on 142 of 778 TAZs) is not used for super-zones.
* **Anchored bus zones 3, 12, 13, 20.** Explained: the segmented rule gives segments with fewer than 5 sampled survey trips the origin-wide factor, so the origin total is not RavKav's. A refinement (use RavKav's own volume in a thin segment when the origin is not guarded) is possible in a later version; the frozen version is unchanged.
* **Destination pattern.** Using the on-board probabilities instead of RavKav's alighting zone (RavKav as production only) is worse against the survey at every resolution, including the split inside a super-zone (T7b). No change proposed; the OnBoard codebook remains the open request.
* **T6 intra-zonal share.** 20.6 % against "< 5 %": a miss by construction; not part of wave 1's notebooks.

**Next waves.** 1b (X1): PM and midday survey matrices and the repeats of T7, T8, T12, T14, T15, T17. 2: T1-T3, T6, T9, T10, T16, T19. 3: T11 after step 42. 4: T13, T18, the CBS parts, rail times.

---

## 10. Status after wave 1b (4 October 2026)

**Built:** the PM-peak (16:00-19:00) and midday (10:00-14:00) survey-based layers (step 8 for the windows, steps 15 and 16 with `NOFIT_PERIOD`; AM unchanged, verified file by file). 2022: car 1,259,603 / 1,150,868, bus 88,817 / 129,528, taxi-type 5,790 / 12,538, rail 3,599 / 1,702.
**Repeated for PM and midday:** T4, T5, T7, T8 (stage 2b: the three windows, car against the cordon counts and bus against RavKav 2022 hourly journeys), T12, T14. 102 summary rows in the workbook (AM 53, PM 24, midday 24, whole-day 1).
**Not repeated:** T15 (needs the 2025 rail taps re-extracted for the window) and T17 (needs steps 29 and 30 for the window's timetable and hourly speeds): both are extensions of existing steps with other hours, not new methods.

| Test | PM 16-19 | Midday 10-14 |
|---|---|---|
| T7 transit OD, 36 super-zones, calibrated 2022 layer vs RavKav (R2, slope) | 0.77, 1.28: miss | 0.85, 1.06: **pass** |
| T7 at 28 sub-areas | 0.93, 0.94: **pass** | 0.95, 1.10: **pass** |
| T8 time-of-day shape (car, 12 cordon-directions) | 11 of 12 above CR 0.6 | all 12 |
| T12 car vs counts (44 testable cordon-sector cells) | 0.64 of the count | 0.50 of the count |
| T14 bus origins, anchored zones | 0.99 of RavKav | 0.99 |

**New finding.** RavKav / survey bus trips is 0.74 in the AM and 0.96 / 0.93 in the PM / midday; home-based education is 40 % of the AM survey bus trips and 13 % / 19 % in the other windows (RavKav / survey without education: 1.22 / 1.10 / 1.13).
The AM coverage gap therefore looks like student and school travel, not a general ticketing gap; to be put to the data provider, with a coverage rule by purpose as the candidate refinement (METHODOLOGY caveat 20). **Decision for the steering group:** keep the AM rule (30 guarded cells, bus base 115,430) as the frozen version, or rerun the calibration with a purpose-specific rule for a later version.

**Next waves.** 3: T11 after step 42. 4: T13, T18, the CBS parts, rail and running times for the three windows.

## 11. Status after wave 2 (4 October 2026)

Run: **T1, T2, T3, T6, T9, T10, T16, T19** (notebooks `MOT_Validation_Stage1d_Zones_Population_Rates` and `_Stage2c_Mode_Occupancy_Convergence`; T3, T6, T9, T10, T19 also for PM and midday; METHODOLOGY §6ai wave 2). Workbook: 212 summary rows (AM 99, PM 56, midday 56, whole-day 1).

| Test | Result against the criterion |
|---|---|
| T1 zone system | documented; 1250-zones nest in the super-zones (17 of 396 span two), the 28 sub-areas, 25 V2 areas and 25 GS zones do not (13, 15, 11 groups span more than one) |
| T2 residents | +5.2 % over the zonal 2020 population; 14 of 36 super-zones within +/-5 % (29 after one factor); Haredi +26 %, Arab +11 %; household size 3.39 vs 3.02: **miss (explained)**; CBS parts not run |
| T3 trip rates | window rate per resident +6.7 % (AM), +7.6 % (PM), +7.4 % (midday) from the 2018 to the 2022 layers; 33, 32, 33 of 35 super-zones within +/-15 %: miss (explained, mostly the resident base) |
| T6 intra-zonal | 20.6 % (AM), 15.4 % (PM), 16.2 % (midday) of trips inside one TAZ vs 5 %: **miss (explained)**; bus alone 4.5 % passes |
| T9 mode split | CR 0.98-0.995 study area, all 36 super-zones above 0.6 in every window: **pass**; GC out-of-vehicle weight ratio 2 (guideline 2-3) |
| T10 occupancy | **correction:** right-hour AM occupancy 1.52, not 1.33; T12 rerun (0.71 -> 0.62); 29 of 36 super-zones within +/-10 %; vehicle-trip pattern CR 0.951 / 0.919 / 0.925 |
| T16 Metronit | survey 22,812 vs 2025 boardings 13,078 (+74 %); super-zone R2 0.05, CR 0.39: miss; link loads not run |
| T19 convergence | car exact; **taxi-type does not converge** (largest row residual 28 %, shortfall 3-5 % of the layer, 0.6 % of motorised trips); aggregations exact |

## 12. Status after wave 3 (4 October 2026)

Run: **T11** (= step 42, `MOT_Validation_Stage4_Link_volumes`, AM, PM, midday). All-or-nothing assignment of the 2022 car layer, 1,346 counts 2021-2023: assigned / counted 0.93 (AM), 0.84 (PM), 0.69 (midday); R2 0.47 / 0.51 / 0.50, slope 0.89 / 0.87 / 0.70, RMSE% 113 / 95 / 87: **miss (explained)**; no peak-hour volume class inside its limit; free-flow routing beats shortest distance; best on type-2 arterials (slope 0.87). Workbook: 226 summary rows.

**Cannot be run with what is in the repository:** T13 (Google key, step 37), T18 (Operator 22 AVL data, open question 5), the CBS parts of T2 and T3 (standing request 6), T15 / T16 / T17 for the PM and midday (the 2025 smart-card extracts hold taps 06:00-08:59 only; T17 also needs steps 29-30 for the window). Each needs one input from the user or the data provider; the code path for T13 and T18 is specified above and is a half day each once the input exists.


## 13. Parked: T18 waits for the Operator 22 AVL file (decision of 4 October 2026)

The user will share the raw extract later (`New_Query_2026_09_17_15_46_30 (1).csv`: 1,078,845 stop records, lines 34447 and 34448, 132 Thursdays, 25 May 2023 to 10 Sep 2026). Nothing else is needed from the user; open question 5 is answered in principle.
**Ready-to-run protocol (half a day once the file is in `Input/`):**
1. Rebuild the calibration sample exactly as the report does (canonical 31-stop journeys, timing QA, 500 m spacing) and check it reproduces 26,653 journeys, 799,590 sections and the coefficients 1.961 (underground) / 2.393 (other) min per section.
2. Hold-outs, refitting on the rest each time: (a) by year (2023, 2024, 2025, 2026); (b) by line (34447 vs 34448); (c) random 80/20 by date, repeated 20 times; (d) by time of day if the extract carries it.
3. Report trip-level MAE and MAPE for each hold-out against the in-sample 3.67 min / 5.45 %, the coefficient stability across refits, and the share of held-out trips within +/-15 % (guideline 5.2 style).
4. Independent check on the Metronit: `is_brt` trips of `Output/gtfs/bus_trips_observed.csv.gz` against the function (not an LRT test, a sanity check of the speed level).
5. Add a notebook `MOT_Validation_Stage5_LRT_time_function.ipynb`, summary rows for T18, METHODOLOGY 6ai wave 4, README, plan status; no change to the function unless the hold-out shows a bias the user decides to correct.
Until then T18 stays "not run" in the workbook, with the reason "data to be shared".
