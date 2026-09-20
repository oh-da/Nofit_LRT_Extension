# Methodology — OD Demand Matrix from THS 2018 and Cellular Data

This document records what has been done in this repository so far: the reasoning behind
each step, the exact methodology, the inputs consumed and the outputs produced. Every
step is implemented as an executed Jupyter notebook at the repository root, and every
number quoted here can be reproduced by re-running the corresponding notebook.

**Goal.** Build an AM-peak (6:00–9:00) origin–destination demand matrix for the Nofit
LRT extension study area (778 traffic analysis zones, northern Israel), by fusing two
independent sources:

- the **2018 Travel Habits Survey (THS)** — detailed, behaviorally rich, but a small
  sample (5,108 households), and
- a **cellular-derived OD matrix** — population-scale coverage, but coarser zones and
  blind to trips that do not move a phone between cell areas.

The guiding idea throughout: treat cellular as the *prior* spatial distribution and the
survey as *evidence*, and combine them at the spatial scale where each is reliable.

---

## 1. Input data (`Input/Matrices/`)

| File | Content | Key facts |
|---|---|---|
| `ACTIVITIES_DEC18_corrected.csv` | THS 2018 activity diary: one row per activity per individual per survey day | 172,529 rows; 5,108 households; two survey days per household (`ACT_DAY` = 10: 86,978 rows, `ACT_DAY` = 20: 85,465; a residue of 86 rows on days 11/22 is ignored). Columns include `HHID`, `INDIVID`, `ACT_DAY`, `ACT_ID`, `StartTime`, `EndTime`, `mainActivity`, `taz`, `tourID` |
| `households_with_weights.csv` | Household expansion weights | 5,108 rows, one per `HHID` — exactly matching the activities file (no missing, no duplicates). Columns: `HHID`, `TAZ`, `SuperZone`, `wf` (original weight), `wf_new` (revised weight; mean ≈ 159, range 5–350). **`wf_new` is the weight used throughout.** |
| `AvgDayHourlyTrips201819_1270_weekday_v1.csv` | Cellular OD trips, average weekday 2018–19, hourly (`h0`–`h23`), national 1270-zone system | Only the AM-peak hours `h6`, `h7`, `h8` are used |
| `1270_02_09_2021_TAZ_North_keys.csv` | Zone correspondence table (windows-1255 encoded) | Maps the national 1270-zone system (`TAZ_1270`) to the 778 study TAZs (`TAZ_NUMBER`) and to 36 superzones (`SZ_NEW`). 400 national zones cover the study area; one national zone contains up to 8 study TAZs (mean ≈ 2) |
| `../TAZ_GSnew.csv` (in `Input/`) | TAZ → GS zoning | 781 TAZs → 25 GS zones; covers every study TAZ including 105 |
| `../trips_ths_2017.xlsx` (in `Input/`) | THS trips file: one row per activity per person per survey day | 146,394 rows, 16,401 persons (same panel as the activities file), `SurveyDay` 1/2; `placeno` orders activities per `PerID3`, `actTaz` locates them, `Dep_h` is the hour of departing the activity, `mode` is pre-aggregated (CAR/TRANSIT/RAIL/OTHER, `IRR` = first activity), `new_wf` carries the weight |

**Data-version note.** The activities file currently in the repository contains more
records than the file used by the original `THS_2018_MTX.ipynb` Colab run: identical
processing yields 14,912 unweighted Day-10 AM-peak trips here vs 11,303 recorded in that
notebook's outputs. Spot-checked OD cells present in both versions match exactly, so the
processing is the same and the difference is additional survey records (concentrated in
zones 0 and 103–106). All results below are on the current file; they are therefore not
directly comparable to numbers recorded inside `THS_2018_MTX.ipynb`.

## 2. Common trip-extraction rule (all steps)

Inherited from the original analysis (`THS_2018_MTX.ipynb`) and kept fixed so results
stay comparable across steps:

1. Slice the activity diary by survey day (`ACT_DAY` = 10 / 20).
2. Order activities by `INDIVID`, `tourID`, `ACT_ID`.
3. Within each individual's tour: **origin** = `taz` of the previous activity,
   **destination** = `taz` of the current activity.
4. **Leaving time** = `EndTime` if the previous state is captured by
   `mainActivity == 'Home'`, otherwise `StartTime` (timestamps parsed day-first).
5. Keep trips with leaving hour in **[6, 9)**.
6. **Model-area filter** (added after an audit of the trip definition): keep only trips
   whose origin **and** destination have a real TAZ (non-null and ≠ 0), and drop trips
   whose destination-activity mode is `Default` (code 99 — no reported travel).

The audit behind rule 6: `Default`/99 turns out to be almost exclusively the survey
day's *first* activity (20,511 of 20,585 records), which never forms a trip anyway —
only 3 of ~29.6k extracted AM-peak trips had a Default arrival, so phantom trips from
"stayed at home" records were negligible. Persons who never left home (10.9% of
person-days, single all-day activity) already produce zero trips by construction. The
material cleanup is **taz 0**: 998 trips (204k weighted, 3.4% of trips) touched an
unlocatable zone and previously sat in the raw matrices (e.g. the 0→0 cell). Removing
all of the above leaves the intra-superzone share of trips unchanged (75%), i.e. the
survey–cellular diagonal divergence is genuine survey content, not an artifact.

The original notebook also contains a "v2" timing rule (departure = previous activity's
`EndTime` for all trips); the work below uses the original ("v1") rule throughout.

**Cellular processing** (reconstructed — the original notebook's saved code references
`fromTaz`/`ToTaz` columns whose creation cell was not preserved): sum `h6+h7+h8`, map
`fromZone`/`ToZone` (1270 system) to `TAZ_NUMBER` through the key table deduplicated by
`TAZ_NUMBER`, aggregate to a 778×778 matrix, row-normalize. The reconstruction was
validated cell-by-cell (6 decimal places) against the probability matrix recorded in the
original notebook's outputs. *Caveat:* this mapping assigns each coarse national flow at
full value to every child TAZ pair (up to 8×8 replicas). Row normalization absorbs much
of it, but superzone aggregates inherit some over-weighting of finely subdivided zones.

---

## 3. Step 1 — Household-weighted matrices (`THS_2018_MTX_weighted.ipynb`)

**Reasoning.** Raw trip counts describe the *sample*; multiplying each trip by its
household's expansion factor describes the *population*. Since every activity record
carries `HHID`, the join to `wf_new` is exact (all 5,108 households match 1:1).

**Method.** Identical trip extraction; the OD cross-tabulation sums `wf_new` per
origin–destination pair instead of counting trips.

**Results.**

| | Day 10 | Day 20 |
|---|---|---|
| Sampled trips (raw count) | 14,420 | 14,197 |
| Expanded trips (Σ `wf_new`) | 2,193,422 | 2,163,320 |
| Matrix shape (observed zones) | 656 × 706 | 650 × 695 |

Average expansion ≈ 152 trips per sampled trip, consistent across days. (Under the
original pre-filter definition the totals were 14,912 / 14,705 sampled and
2,296,819 / 2,264,158 expanded.)

**Outputs.** `Output/matrix_10_weighted.csv`, `matrix_20_weighted.csv` (weighted OD
counts) and `prob_matrix_10_weighted.csv`, `prob_matrix_20_weighted.csv`
(row-normalized).

## 4. Step 1b — Validation against cellular (`THS_2018_MTX_weighted_vs_cellular.ipynb`)

**Reasoning.** Before fusing the sources, quantify how well they agree, at two spatial
scales, and isolate what the weighting changed.

**Method.** Both sides as row-normalized probability matrices; compared at TAZ level
(778 zones) and at superzone level (`SZ_NEW`, 36 zones, aggregating raw weighted counts
before normalizing — the approach that performed best in the original analysis). Metrics:
Pearson correlation and RMSE over flattened matrices; plus correlation/MAE restricted to
the dense range [0, 0.25]. Unweighted matrices recomputed alongside as reference.

**Findings.**

1. **Weighting rescales, it does not reshape.** Weighted and unweighted superzone
   probability matrices correlate at r ≈ 0.998 on both days.
2. **Fit to cellular is unchanged by weighting**: superzone r = 0.855 (Day 10) / 0.856
   (Day 20) weighted vs 0.854 / 0.855 unweighted. At TAZ level weighting slightly
   *lowers* correlation (0.283–0.288 vs 0.294–0.300) — multiplying single trips by large
   factors amplifies noise in sparse cells.
3. **Spatial scale dominates the fit**: r ≈ 0.29 at TAZ level vs ≈ 0.86 at superzone
   level on the same matrices — survey sparsity, not systematic bias, drives TAZ-level
   disagreement.
4. **The one systematic divergence is intra-zone travel.** All 36 diagonal
   (intra-superzone) cells lie above the identity line: the survey holds on average
   **72%** of a superzone's AM-peak departures inside that superzone vs **34%** in the
   cellular data (off-diagonal means 0.008 vs 0.019). Likely driver: short local trips
   that never move a phone between cell areas are invisible to cellular tracking.
5. Day 10 and Day 20 behave near-identically on every metric.

**Outputs.** `Output/prob_matrix_cellular.csv` (778×778 cellular probabilities),
`prob_sz_cellular.csv`, `prob_sz_10_weighted.csv`, `prob_sz_20_weighted.csv` (36×36),
scatter figures under `Output/figures/`.

## 4b. Step 1c — Weighted matrices by mode (`THS_2018_MTX_weighted_by_mode.ipynb`)

**Reasoning.** Split the weighted Day 10 / Day 20 matrices by an aggregated travel mode
for mode-specific demand analysis.

**Method.** Identical trip extraction and weighting; `MODE_NAME` (14 values, full
coverage, no nulls) is mapped to four groups — **CAR** (Vehicle as Driver/Passenger,
Motorcycle/Moped), **TRANSIT** (Public Bus, Matronit, Special/Group Taxi), **RAIL**
(Train), **OTHER** (Pedestrian, Default, Chartered Bus, Bicycle, Other, Truck). A trip's
mode is the `MODE_NAME` of its *destination* activity row (the mode used to arrive). The
four matrices per day sum exactly to the corresponding all-mode weighted matrix.

**Results** (expanded AM-peak trips; shares stable across days):

| | CAR | TRANSIT | RAIL | OTHER |
|---|---|---|---|---|
| Day 10 | 1,234,371 (56.3%) | 143,215 (6.5%) | 3,990 (0.2%) | 811,847 (37.0%) |
| Day 20 | 1,202,092 (55.6%) | 143,776 (6.6%) | 4,669 (0.2%) | 812,783 (37.6%) |

The model-area filter hits RAIL hardest: expanded rail trips drop from ≈ 14.7k to ≈ 4k
per day — most surveyed rail trips have an end outside the model area — leaving only
11×14 / 17×15 observed zones. The RAIL matrices are indicative only.

**Outputs.** `Output/matrix_{10,20}_weighted_{CAR,TRANSIT,RAIL,OTHER}.csv` (eight
matrices, weighted OD totals over observed zones).

## 4c. Step 1d — Sub-area matrices (`THS_2018_MTX_submatrix.ipynb`)

**Method.** Restricts the weighted matrices (all-mode and the four mode groups, both
days) to a given list of 119 study TAZs — keeping only trips with origin **and**
destination inside the list. Every sub-matrix is reindexed to the full 119-zone list in
the given order (unobserved zones become zero rows/columns), so all ten files share the
identical 119×119 layout and the four mode files per day sum to that day's all-mode file.

**Results.** ≈ 6.5% of expanded AM-peak trips have both ends inside the sub-area
(142,532 on Day 10 / 139,007 on Day 20 — unchanged by the model-area filter, since the
119 listed zones exclude taz 0). By mode: CAR ≈ 5%, TRANSIT ≈ 9.5%, OTHER ≈ 7.5%; RAIL
is empty on Day 10 and nearly empty on Day 20 (169 expanded trips). 16 of the 119 zones
never appear as an AM-peak survey origin across the two days pooled (15 never as a
destination).

**Outputs.** `Output/submatrices/` — same ten filenames as the parent matrices,
119×119 each.

## 4d. Step 1e — AM-peak trip generation rates per person (`THS_2018_MTX_trip_generation.ipynb`)

**Method.** A trip *production* rate by residence zone, per survey day. **Home zone =
the zone where the person's `mainActivity` was Home at 3:00 AM** — the survey day starts
at 03:00 and every person-day's first diary activity begins exactly then, so the home
zone is the `taz` of that first activity when it is Home (96.4% of person-days; the rest
— night workers, people away — are excluded from both sides of the ratio for that day;
individuals Home on both days sit in the same taz 99.99% of the time). Numerator:
expanded AM-peak trips made that day by persons home in the zone (same extraction rule,
attributed to the home zone regardless of where they occur). Denominator: expanded
persons home in the zone at 3:00 (`wf_new` per person). Superzones via the keys table's
`SZ_NEW`.

**Results.** Overall rate: **0.837 (Day 10) / 0.833 (Day 20) → 0.835 AM-peak trips per
person** over ≈ 2.60M expanded persons home at 3:00 (model-area trips only; under the
pre-filter definition the rate was 0.872). Superzone rates span 0.63 (SZ 4)
to 1.25 (SZ 25); 35 superzones and 520 home TAZs are covered (93 TAZs have < 20 sampled
person-days — flagged, indicative only). This diary-based home definition agrees with
the household register (`households_with_weights.csv` TAZ) for ~95% of households, with
disagreements almost all in adjacent zones.

**Outputs.** `Output/trip_generation_taz.csv`, `trip_generation_sz.csv` (per zone and
day: sampled and weighted persons, weighted trips, rates, and the two-day average);
`trip_generation_summary.csv` — a compact one-row-per-TAZ table with `TAZ`, `SuperZone`,
`trips_per_person` (two-day average) and `population` (`wf_new` × observed persons home
at 3:00, averaged over the two days; total ≈ 2.59M — SuperZone is blank for the few home
zones outside the keys-table mapping); rate figure under `Output/figures/`.

## 5. Step 2 — Superzone hybrid via empirical-Bayes shrinkage (`THS_2018_MTX_hybrid.ipynb`)

**Reasoning.** Rather than replacing cellular with survey, blend them per origin
superzone in proportion to how much survey evidence exists:

```
P*(B|A) = λ_A · P_survey(B|A) + (1 − λ_A) · P_cell(B|A),    λ_A = n_A / (n_A + k)
```

Two deliberate design choices: `P_survey` is the **weighted** probability row (the
population-representative pattern), while `n_A` is the **unweighted** observation count
(statistical information is the number of observations, not the expanded weight).

**Choosing k by cross-day validation.** Blend Day 10 with cellular and score how well it
predicts Day 20, and vice versa, over k ∈ {20, 50, 100, 200, 500} (extended with
{0, 1, 2, 5, 10, 1000, ∞} to expose the full curve). Primary metric: mean row-wise
Jensen–Shannon divergence (base 2); MAE tracked alongside and agreeing throughout.

**Result — the data ask for (almost) no shrinkage at this scale:**

| k | 0 | **2** | 20 | 100 | 500 | ∞ (pure cellular) |
|---|---|---|---|---|---|---|
| mean JSD | 0.0157 | **0.0156** | 0.0177 | 0.0350 | 0.0904 | 0.1964 |

The curve is flat over k ∈ [0, 5] and rises monotonically after; among the original
candidates, k = 20 is best. An off-diagonal-only variant (destinations outside the
origin superzone, rows renormalized) agrees: optimum k = 5, ≈ 1% better than k = 0.

**Why**: every origin superzone has n_A ≥ 91 observations per day (pooled ≥ 194, median
≈ 700), so superzone rows are already well-estimated — and the survey–cellular gap is
systematic (the diagonal), not sampling noise.

**Honest caveat**: Days 10 and 20 are reported by the *same households*, so this
validation measures the survey's self-consistency, not its truth. It cannot detect
biases shared by both days, and it structurally favors the survey wherever the sources
disagree.

**Outputs.** `Output/hybrid_sz_prob.csv` (pooled two-day survey blended at k\* = 2;
λ_A = 0.990–0.999, effectively survey with a light cellular floor),
`hybrid_sz_prob_k100.csv` (sensitivity variant, λ_A = 0.66–0.95), `hybrid_sz_trips.csv`
(rows scaled to average-weekday expanded AM-peak departures, ≈ 2.28M trips),
`hybrid_lambda.csv` (n_A and λ per origin), `hybrid_cv_results.csv`, CV-curve and
λ-curve figures. Hybrid trips total ≈ 2.15M average-weekday AM-peak trips (superzone-
mapped model-area trips).

## 6. Step 3 — TAZ-level matrix via superzone correction factors (`THS_2018_MTX_hybrid_taz.ipynb`)

**Route A (tested, rejected): direct λ-blending of TAZ survey rows.** The same
shrinkage estimator at 778-zone resolution, with two priors (raw cellular rows, and the
superzone hybrid disaggregated through cellular within-superzone shares). Convention:
origins with n_i = 0 receive the prior row (λ_i := 0) at every k, so all k are compared
on identical rows. Cross-day validation again selects k = 0 monotonically — but at TAZ
resolution an origin row is a handful of specific households (median 11 trips, 125 empty
origins on Day 10), and the same people repeat the same TAZ-to-TAZ commutes on both
survey days. The validation measures **within-person habit persistence**, not population
accuracy, and is therefore disqualified for calibrating λ at this scale.

**Route B (adopted): superzone correction factors on cellular structure.** Survey
information enters only at the superzone level, where it is reliable. For TAZ i ∈ A and
j ∈ B:

```
R_AB = P*(B|A) / P_cell(B|A)          (from the pooled superzone hybrid)
C̃_ij = C_ij · R_AB                    (scale the individual cellular OD cells)
P̃(j|i) = C̃_ij / Σ_j C̃_ij            (row-normalize)
```

Each TAZ keeps its own cellular destination profile (within-superzone heterogeneity
survives); the superzone-to-superzone pattern follows the calibrated hybrid.

**Validation.** Used to predict a held-out survey day — with *no TAZ-level survey
input* — the corrected matrix scores mean row JSD **0.671 vs 0.775 for raw cellular**
(≈ 13% better), on par with a proportional downscale (0.667).

**Correction-factor diagnostics** (pooled hybrid, k_SZ = 2): diagonal R median 2.21
(max 13.7) — the intra-superzone boost; 45% of off-diagonal superzone pairs have zero
pooled survey observations, so their R falls toward the shrinkage floor (off-diagonal
median ≈ 0.10). The correction transfers the survey's pattern *and its sparsity*, which
motivates the second variant: at k_SZ = 100 the off-diagonal median is ≈ 0.26, keeping a
substantial cellular floor on survey-unobserved OD pairs.

**Trips version.** The hybrid probabilities are converted to trips with an origin-volume
vector built on the same principle (survey sets the scale, cellular the structure):
each superzone's average-weekday expanded survey departure total is split among its
member TAZs by cellular outflow shares, then spread over destinations by the hybrid
probabilities. Total ≈ 2.15M average-weekday AM-peak trips (matching the superzone
trips file — under the model-area trip definition both cover the same trips).
Superzone-level origin totals match the survey expanded departures exactly
(asserted in the notebook); the within-superzone split inherits the cellular replication
caveat. A 119×119 sub-area extraction (same zone list, order and layout as
`Output/submatrices/`) captures 121,179 trips (5.6% of the total).

**Outputs.** `Output/hybrid_taz_prob.csv` (778×778, k_SZ = 2 — follows the survey
wherever it speaks), `hybrid_taz_prob_k100.csv` (safer where coverage of rare OD pairs
matters), `hybrid_taz_trips.csv` (778×778 trips), `submatrices/hybrid_taz_trips.csv`
(119×119), `sz_correction_factors.csv` / `sz_correction_factors_k100.csv` (36×36 R
tables), `hybrid_taz_cv_results.csv`, CV-curve and R-heatmap figures.

## 6b. Step 4 — GS zoning pipeline (`THS_2018_MTX_GS.ipynb`)

**Reasoning.** `Input/TAZ_GSnew.csv` introduces a second aggregation geography — **GS**
(25 zones, covering every study TAZ, including TAZ 105 which the keys table lacks an
`SZ_NEW` for). This step recreates the superzone-level products on GS with identical
methodology (only the TAZ→GS mapping replaces TAZ→`SZ_NEW`).

**Results.** GS-level expanded trips: 2,193,422 / 2,163,320 (equal to the full matrix
totals — the GS mapping covers every model-area TAZ). Weighted survey vs cellular at GS
level: r = 0.840 / 0.838 (Day 10/20).
Cross-day validation of the shrinkage constant finds a genuine but tiny interior
optimum, **k\* = 1** (JSD 0.0248 vs 0.0252 at k = 0; monotone rise beyond), so the GS
hybrid is again survey-dominant (λ = 0.909–0.9999; the smallest GS origin has only 10
pooled observations). Hybrid trips total ≈ 2.18M average-weekday AM-peak trips. GS
correction factors applied to cellular TAZ cells: diagonal R median 1.89 (max 5.7),
off-diagonal median 0.09, 48% of off-diagonal GS pairs have zero pooled survey
observations. Hybrid GS trips total ≈ 2.18M (slightly above the superzone-based 2.15M
because GS also maps TAZ 105). TAZ-level GS-based trips match GS survey departure
totals exactly (asserted).

**Outputs.** `Output/prob_gs_{10,20}_weighted.csv`, `prob_gs_cellular.csv` (25×25);
`hybrid_gs_prob.csv` (k\* = 1), `hybrid_gs_prob_k100.csv`, `hybrid_gs_trips.csv`,
`hybrid_gs_lambda.csv`, `hybrid_gs_cv_results.csv`; `gs_correction_factors.csv` (25×25);
`hybrid_taz_prob_gs.csv`, `hybrid_taz_trips_gs.csv` (778×778 TAZ matrices calibrated
through GS instead of superzones).

## 6c. Step 5 — Matrices from the THS 2017 trips file (`THS_2017_trips_matrices.ipynb`)

**Method.** An independent trip extraction from `Input/trips_ths_2017.xlsx`: within each
person (`PerID3`) and survey day, activities ordered by `placeno` form trips from the
previous activity's `actTaz` to the current one's; the trip's departure hour is the
*origin* row's `Dep_h` (kept for `Dep_h` ∈ {6,7,8}); its mode is the *destination* row's
pre-aggregated `mode`; each trip contributes its `new_wf`. `IRR` marks first activities
only and never becomes a trip mode (asserted). No `actTaz` is 0; zones beyond the
778-zone system keep their real TAZ, so out-of-region trip ends are retained.

**Results** (expanded AM-peak trips):

| | CAR | TRANSIT | RAIL | OTHER | All |
|---|---|---|---|---|---|
| Day 1 | 1,380,188 (62.8%) | 142,924 (6.5%) | 17,219 (0.8%) | 656,482 (29.9%) | 2,196,813 |
| Day 2 | 1,343,321 (61.8%) | 140,585 (6.5%) | 19,210 (0.9%) | 669,334 (30.8%) | 2,172,451 |

All-mode totals agree with the activities-based matrices within 0.2–0.4%
(2,196,813 vs 2,193,422 on day 1/10), a strong cross-validation of the two extractions.
Mode composition differs: this file assigns more trips to CAR (≈ 62% vs 56%) and fewer
to OTHER, and RAIL keeps out-of-region destination zones (17–19k expanded vs 4k under
the model-area-restricted activities extraction).

**Day-averaged matrices.** The two survey days are different by activity, so the
representative weekday set is the cell-wise average `(day1 + day2) / 2` over the union
of observed zones: `matrix_avg_{CAR,TRANSIT,RAIL,OTHER,ALL}.csv` — 2,184,632 average-
weekday AM-peak trips (CAR 1,361,754 / OTHER 662,908 / TRANSIT 141,755 / RAIL 18,214),
with the mode matrices summing exactly to ALL.

**Zone systems.** `actTaz` uses the national 2636-zone system — not the study system
(the ~310 shared zone numbers are coincidental collisions). `Input/TAZ_2636_Keys.xlsx`
bridges it: `actTaz` (2636) → `TAZ_1250` (same ids as the study keys' `TAZ_1270`) →
study `TAZ_NUMBER`. The keys cover 100% of trip ends; 95.9% of weighted trips have both
ends in the northern study area. Because the last link is one-to-many (a 1250-zone holds
up to 8 study TAZs), each trip's weight is allocated proportionally to child TAZ pairs by
cellular outflow (origin side) / inflow (destination side) shares — `M_taz = Sₒᵀ M₁₂₅₀ S_d`
— and `SZ_NEW`/GS aggregations follow exactly from the allocated TAZ matrices.

**Study-system results** (averaged weekday, trips with both ends in the study area:
2,068,158 after excluding 116,473 weighted with an end outside): CAR 1,283,589 /
OTHER 645,111 / TRANSIT 134,349 / RAIL 5,109. Validation: the superzone probability
pattern correlates at **r = 0.994** with the activities-based pipeline — the two
independent extractions agree at distribution level, not just in totals.

**Outputs.** `Output/ths2017/matrix_day{1,2}_{CAR,TRANSIT,RAIL,OTHER,ALL}.csv`,
`matrix_avg_{CAR,TRANSIT,RAIL,OTHER,ALL}.csv` (trips-file zonation);
`Output/ths2017/study_taz/matrix_avg_{CAR,TRANSIT,RAIL,OTHER,ALL}_taz.csv` (778×778,
allocation-based) and `matrix_avg_ALL_sznew.csv` / `matrix_avg_ALL_gs.csv` (36×36 /
25×25).

## 6d. Step 6 — Hybrid pipeline on the THS 2017 trips file (`THS_2017_hybrid_pipeline.ipynb`)

**The primary fusion products**, rebuilding the full chain with the trips file as the
survey source (superseding the activities-based `Output/hybrid_*` set, which remains as
the historical version). Methodology identical: EB shrinkage with cross-day validation,
then correction factors on cellular structure. Survey side: study-area trips (13,476 /
13,387 sampled; 2,068,158 average-weekday expanded), day-averaged for the final
matrices, pooled counts for λ (dominant SZ/GS per 1250-zone for the counts).

**Results.** Cross-day validation now finds a genuine interior optimum: **k\* = 5** at
both superzone and GS levels (SZ JSD 0.0191 at k = 5 vs 0.0195 at k = 0, monotone rise
beyond). Hybrids: λ = 0.962–0.997 (SZ), 0.706–0.999 (GS). Correction factors: SZ
diagonal median 2.04 / off-diagonal median 0.18; GS 1.79 / 0.17 — off-diagonals sit
higher than in the activities-based run because the survey side already carries cellular
sub-structure from the allocation step. All trips totals preserved exactly (asserted).

**Sub-matrices (aggregated areas).** `Input/Submatrix_tazs.xlsx` defines the sub-area:
205 TAZs grouped into 28 named aggregated areas (`AggAreaCode`/`AggAreaName`) with an
`IsLRT_Corridor` flag — its 119 corridor TAZs are identical to the earlier sub-matrix
list, extended by 86 non-corridor TAZs (2 areas mix both). Each matrix (averaged
ALL + four modes + hybrid trips) is restricted to trips with both ends among the listed
TAZs and aggregated to the 28 areas: ALL 276,977 avg-weekday trips in the sub-area
(110,641 with both ends in the LRT corridor — matching the previous 119-TAZ submatrix
exactly); hybrid trips 273,320 (94,610 in-corridor); RAIL 131.

**Outputs** (all under `Output/ths2017/study_taz/`): `hybrid_sz_prob/trips/lambda.csv`,
`hybrid_gs_prob/trips/lambda.csv`, `hybrid_cv_results.csv`, `sz_correction_factors.csv`,
`gs_correction_factors.csv`, `hybrid_taz_prob.csv` / `hybrid_taz_trips.csv`
(SZ-calibrated, 778×778), `hybrid_taz_prob_gs.csv` / `hybrid_taz_trips_gs.csv`
(GS-calibrated), and `submatrices/` (28×28 aggregated-area matrices: avg ALL + four
modes + hybrid trips, plus `area_legend.csv` with names, TAZ counts, and corridor
flags).

## 6e. Step 7 — Trip generation rates on the trips file (`THS_2017_trip_generation.ipynb`)

**Method.** Mirrors step 1e on the new source: home = the 3:00 AM location (the
`placeno = 1` row, always starting at 03:00) when `mainActivity = 1` (Home; 96.9% of
person-days, rest excluded from both sides), numerator = the person-day's AM-peak trips
(validated extraction) × `new_wf`, denominator = expanded persons home at 3:00. Rates at
the native 2636-zone resolution and, via the dominant study zone of the home 1250-zone,
at `SZ_NEW` and GS levels. Unlike the activities-based rates, **all** AM-peak trips
count (every trip in this file has a real TAZ), so this is the total generation rate
including trips leaving the study area.

**Results.** Overall **0.831 (Day 1) / 0.827 (Day 2) → 0.829 AM-peak trips per person**
over ≈ 2.60M expanded persons — versus 0.835 on the activities-based source, and with an
almost identical superzone ranking (SZ 25 and 39 highest at ≈ 1.18/1.12, SZ 19 and 4
lowest at ≈ 0.60/0.63). 478 home 2636-zones covered (89 with < 20 sampled person-days,
flagged); 209 person-days have homes outside the northern study area (2636-zone table
only).

**Outputs.** `Output/ths2017/trip_generation_taz2636.csv`, `trip_generation_sz.csv`,
`trip_generation_gs.csv`, `trip_generation_summary.csv` (TAZ_2636, TAZ_1250, SZ, GS,
rate, population — total 2,601,228), figure `ths2017_trip_generation.png`.

## 6f. Step 8 — Bus RavKav AM-peak matrix by TAZ (`BusRavKav_matrix.ipynb`)

**Inputs.** `Input/TAZ_North/TAZ_North.shp` (781 TAZ polygons, Israeli TM CRS,
`TAZ_NUMBER` field) and four RavKav bus-trip files (`Input/BusRavKav/`, Tuesdays
2022-05-03/17/24/31, ~2.5–2.9M records each; national coverage). Each record is one
**boarding (leg)** with its physical `board`/`alight` stops, plus journey-level fields
that are constant across a journey's legs: `orig`/`dest` stops (first boarding → final
alighting), `bus_trip_hour` (journey start hour) and `total_boardings` (expansion
weight). `passanger_trip_id` embeds the boarding timestamp, so it is unique per leg;
**`bus_trip_id` is the linked-journey id** (passenger + journey-of-day number). The
`date` column has no time.

**Method.** 27,186 unique stops spatially joined to the TAZ polygons (9,924 = 36.5%
fall inside the northern study area). Exact repeated records (≈ 7% of rows) are dropped
first; a **journey** is then one `bus_trip_id` and a **leg** one deduplicated record.
Filters: `weekday = 3` and **`bus_trip_hour`** ∈ {6,7,8}. Weighted by
`total_boardings`, averaged over the four Tuesdays: an OD matrix from journey
`orig`→`dest` stops (each journey once — transfers not double-counted — both ends
inside `TAZ_North`), and per-TAZ boarding / alighting totals from each leg's physical
`board`/`alight` stops. *(An earlier revision deduplicated journeys by
`passanger_trip_id`, which counted every transfer leg as a full journey and inflated
the OD matrix ×1.52 area-wide; fixed 2026-09-08.)*

**Results.** ≈ 510–560k AM-peak bus journeys nationally per Tuesday, of which ≈ 17%
(94,203 on the average day) have both journey ends inside the northern study area —
about 70% of the THS TRANSIT estimate of 134,349 in-study AM-peak trips (the ticketing
OD requires both ends geocoded inside `TAZ_North` and carries no taxi-type modes, which
THS TRANSIT includes). Per-TAZ totals: 157,264 average boardings / 147,632 alightings
across 730 TAZs (leg-level by design — a transfer journey counts at each boarding
point); the largest generator is TAZ 1219 (≈ 6,500 boardings, ≈ 8,900 alightings — a
major terminal). A fifth date file (`Input/trips_table_2022-05-10.csv`) sits outside
the `BusRavKav` directory and is excluded per the four-file instruction.

**Outputs.** `Output/bus/bus_stops_taz.csv` (stop → TAZ tags),
`bus_od_taz_avg.csv` (722×711 average-Tuesday OD journeys),
`bus_boardings_alightings_taz.csv` (per-TAZ averages),
`neve_yosef_stops.csv` (the 30 stops in the Neve Yosef TAZs with per-stop AM volumes).

## 6g. Step 9 — Bus OD combined with OnBoard survey probabilities (`BusOnBoard_matrix.ipynb`)

**Input.** `Input/6_9_BusProbability_ByTAZ.xlsx` (OnBoard survey): P(alight at `toTAZ` |
board at `fromTAZ`) for 6:00–9:00, 599 origins, rows summing exactly to 1 including a
`toTAZ = NaN` unknown-alighting share (median 7.4% where present).

**Method.** (1) Probability matrix: NaN destinations dropped, rows renormalized
(unknown alightings assumed to distribute like known ones). (2) "New" matrix: each
origin's RavKav volume (row sum of `bus_od_taz_avg.csv`) distributed over destinations
by the OnBoard probabilities — RavKav sets the volumes, OnBoard the destination
pattern. Origins without OnBoard coverage (6.4% of volume) keep their RavKav row.

**Results.** Total preserved at 94,203 average-Tuesday journeys; 93.6% of the volume
redistributed by OnBoard probabilities. The two sources genuinely disagree on fine-grain
destinations (r ≈ 0.09 at TAZ level even for high-volume origins) while agreeing
regionally (r ≈ 0.70 at superzone level) — RavKav's destinations are algorithmically
inferred alightings, OnBoard's are passenger-reported, which is the rationale for the
substitution.

**Outputs.** `Output/bus/bus_probability_matrix.csv` (594×548, row-stochastic),
`bus_od_taz_new.csv` (722×728, combined matrix), `bus_od_area_new.csv` (28×28 — the
combined matrix restricted to the 205 sub-area TAZs and aggregated to the named areas),
`bus_od_area_new_filtered.csv` (25×25 after the noise cut), `bus_growth_2018_2022.csv`.

**Comparison with THS TRANSIT at area level.** Sub-area totals: RavKav×OnBoard 23,995
vs THS TRANSIT 26,247 average-weekday passengers (ratio 0.91) — with journeys counted
once, the two independent sources corroborate each other's scale. Cell-level
correlation r = 0.76 on counts; the large residential areas sit near parity
(Kiryat Yam 0.96, Kiryat Motzkin-Bialik 0.89, Tirat Carmel 0.99), while hub/boundary
areas remain the outliers — Hamifrats 9.0×, Kiryat Ata Center 1.9×, Neve Yosef 1.8× —
where ticketing attributes to the boarding area journeys the household survey
attributes to the traveler's true origin. Read as 2018→2022 change, the sub-area ratio
is −8.6% total (−2.2%/yr) — a real, modest decline (the study team verified May 2022
ridership was not COVID-suppressed), confounded by frame; the full-study −30%
additionally reflects the ticketing frame (both ends geocoded, no taxi-type modes).
Figure: `Output/figures/bus_vs_ths_transit_area.png`.

## 6h. Step 10 — Train matrix, complete transit, adjusted all-mode (`Transit_complete_matrix.ipynb`)

Executes `TRANSIT_DEMAND_PLAN.md`. **Train**: `Input/Matrices/Train_mtx_table.csv`
(2019 smartcards, windows-1255; station-to-station by station TAZ, hourly columns) —
hours 6+7+8 summed, the `TAZ 9999` "rest of stations" rows ignored (13,624 out-of-area
trips): 5,535 avg-day trips between the 19 named stations, of which 962 have both ends
in the sub-area. **Complete transit** = filtered bus (23,909) + train (962) = 24,871
passengers at the 25 areas. **Adjusted all-mode**: `ALL_adjusted = (survey ALL −
TRANSIT − RAIL) + measured transit` = 260,770 trips; transit share is **9.5%**
(corridor areas: **10.7%**) against the survey's own 10.1% — with journeys counted
once, the substitution is nearly scale-neutral and changes the *pattern and frame*
of the transit layer rather than its size. Vintage mix documented (base 2018, bus
2022, train 2019). Mode-share table per area in `Output/transit/mode_share_area.csv`;
hub areas (Neve Yosef 75%, Hamifrats 50%) reflect boarding-location and non-resident
frame effects, not residential mode choice.

**Outputs.** `Output/train/train_od_taz_6_9.csv`, `train_od_area.csv`;
`Output/transit/transit_od_area.csv`, `all_adjusted_area.csv`, `mode_share_area.csv`.

## 6i. Step 11 — Vintage alignment to 2022 (`Vintage_alignment_2022.ipynb`)

**Purpose.** The adjusted all-mode matrix mixes vintages (CAR/OTHER base 2018, bus
2022, train 2019). This step levels everything to **2022**, the RavKav anchor year —
patterns untouched, only margins moved.

**Inputs.** `Input/Zonal_2020.csv` (observed zonal socioeconomics, 781 TAZs) and
`Input/Zonal_BU_2025.csv` (forecast): `POPULATION` and `EMPL_TOT` per study TAZ.

**Method.** Per-area growth factors `g = (X_2025/X_2020)^(4/5)` — the 2020→2025 annual
rate applied over 2018→2022 — with `POPULATION` on the origin side (AM-peak origins are
predominantly homes; areas with 2020 population < 500 — the pure employment districts
Namal, Hutzot, Kiryat Nahum, Haifa Airport, Hamifrats, Matam — fall back to the
employment factor) and `EMPL_TOT` on the destination side. The 2018 CAR/OTHER area
matrix is Furnessed to the grown margins (column targets rescaled to the origin-side
grand total). Train is scaled by the national heavy-rail ridership factor 2019→2022
(69M → 54.7M passengers, ×0.793 — rail recovery lagged; May 2022 **bus** ridership was
verified by the study team as not COVID-suppressed, so no pandemic correction is
applied anywhere else). Bus is the untouched anchor.

**Results.** CAR/OTHER 235,899 → 251,684 (+6.7%; origin factors 0.948 Nesher to 1.256
Tirat Carmel, trip-weighted mean 1.067); train 962 → 763; `ALL_adjusted_2022` =
276,355 trips; transit share **8.9%** overall, **9.9%** in the corridor (vs 9.5% /
10.7% on the mixed-vintage table — largest per-area change just −1.4 pp).

**Outputs.** `Output/transit/car_other_area_2022.csv`, `all_adjusted_area_2022.csv`,
`mode_share_area_2022.csv`, `area_growth_factors_2018_2022.csv` (derived factor table
with population/employment levels per area).


## 6j. Step 12 — Cosine similarity and GEH tests on the three matrices (`THS_2017_cosine_GEH_tests.ipynb`)

**Question.** Two standard similarity measures applied to the three AM-peak matrices —
THS survey (trips file, days 1 / 2, rebuilt with the step-5 chain and asserted equal to
`matrix_avg_ALL_taz.csv`; the activities file is not read), cellular, and the primary
hybrid — at superzone (36), GS (25), 28-sub-area and TAZ (778) resolution. Cosine
similarity is scale-free and asks whether demand sits in the same cells; GEH is the
link-count tolerance (`√(2(m−c)²/(m+c))`, hourly flows = 3-hour matrix / 3) and needs a
common scale. Reference for every statistic: survey day 1 vs day 2 (sampling-noise
ceiling) and a permuted-geography null (chance level).

**Cellular volumes.** For volume tests the cellular matrix is allocated to TAZs with the
same `Sₒᵀ · C₁₂₅₀ · S_d` chain as the survey (each cellular trip counted once, study-area
total preserved: 580,506 AM trips over 396 native zones). The pipeline's replicated
variant (`prob_matrix_cellular.csv`) sums to 6.4 × that and is used only as a probability
sensitivity.

**Results.**

| | SZ | GS | 28 areas | TAZ |
|---|---|---|---|---|
| Cosine (raw) day 1 vs day 2 / survey vs cellular / hybrid vs cellular | 0.996 / 0.915 / 0.917 | 0.999 / 0.953 / 0.963 | 0.997 / 0.897 / 0.902 | 0.972 / 0.442 / 0.734 |
| Cosine (row-normalized) same pairs | 0.998 / 0.870 / 0.874 | 0.986 / 0.852 / 0.891 | 0.885 / 0.681 / 0.805 | 0.675 / 0.437 / 0.825 |
| Permuted-geography null, mean (raw) | 0.58 | 0.28 | 0.20 | 0.14 |
| GEH < 5, flow-weighted share of cells: day 1 vs day 2 / survey vs cellular (row-matched) / hybrid vs cellular (row-matched) / hybrid vs survey | 46 % / 6 % / 5 % / 94 % | 39 % / 1 % / 2 % / 52 % | 63 % / 9 % / 13 % / 15 % | 79 % / 46 % / 67 % / 39 % |

1. **Pattern agreement is real but well below the survey's own ceiling.** Survey vs
   cellular cosine is 0.92 at SZ against a day-to-day ceiling of 0.996 and a chance level
   of 0.58 (p < 0.0005 in 2,000 permutations at every level). Per origin, the
   flow-weighted cosine of destination profiles is 0.89 (SZ) and the worst rows are the
   corridor superzones 10 and 11 (0.33 / 0.46) — driven by the diagonal: off-diagonal
   they score 0.75 / 0.69.
2. **The hybrid is the survey at superzone level and cellular below it**, by
   construction: hybrid vs survey cosine 1.000 at SZ (GEH < 5 in 94 % of flow), while at
   TAZ the hybrid is closer to cellular (0.83 row-normalized) than to the survey (0.48),
   whose TAZ pattern is itself only an allocation of cellular shares. The correction
   factors move 33 % of TAZ-level flow beyond GEH 5 relative to the row-matched cellular.
3. **Scale audit (task B1).** The survey expansion carries 3.56 × the cellular AM volume
   (2,068,158 vs 580,506); the ratio is 2.19 on inter-1250-zone trips and far higher on
   intra-zone ones (survey 47 % intra-1250-zone, cellular 14 %). Origin-total ratios
   cellular / survey range 0.19–0.78 across superzones (median 0.29); after one global
   factor only 11 % of superzones have origin totals within GEH 5 (cosine of the origin
   vector 0.985, of the destination vector 0.967) — the cellular product under-detects
   short trips and its zonal margins differ from the household expansion by more than
   scale alone.
4. **GEH is unforgiving at aggregate levels** because the cells are large (SZ cells run
   to 6,000 trips/h, where GEH 5 means ± 4 %): even the two survey days pass GEH 5 in
   only 46 % of SZ flow. Read GEH relative to that ceiling: survey / hybrid vs cellular
   reach 5–13 % at SZ / GS / sub-area level versus 39–63 % for the two survey days.
5. **Corridor.** Row-matched cellular puts 1.8 × the hybrid's outside → corridor flow
   (253k vs 138k) and 0.75 × its corridor-internal flow (71k vs 95k): cellular sees the
   corridor as a stronger attractor of inbound trips and a weaker container of local
   ones. Among the 148 sub-area cells above 100 trips/h, 14 % are within GEH 5 of the
   row-matched cellular (day-to-day: 57 %); the largest disagreements are the
   intra-area cells of Kiryat Motzkin–Bialik, Kiryat Ata South, Tirat Carmel and Kiryat
   Yam (hybrid 2–3 × cellular) and cellular's larger Krayot → Lower City / Bat Galim /
   Kiryat Nahum flows.

**Outputs.** `Output/ths2017/tests/`: `cosine_geh_summary.csv` (headline table),
`cosine_whole_matrix.csv`, `cosine_by_origin_sz.csv`, `cosine_by_origin_summary.csv`,
`cosine_permutation_null.csv`, `geh_scale_audit_{totals,sz,1250}.csv`,
`geh_margins_scaled.csv`, `geh_cells_summary.csv`, `geh_by_flow_band.csv`,
`geh_corridor_classes.csv`, `geh_area_cells.csv`; figures
`Output/figures/cosine_geh_{whole_matrix,by_origin,cdf,corridor}.png`.


## 6k. Step 13 — Kolmogorov–Smirnov tests on the three matrices (`THS_2017_KS_tests.ipynb`)

**Question.** A two-sample KS test compares one-dimensional distributions, so it is
applied to the distributions an OD matrix implies, each weighted by trips: the trip
length distribution (TLD, straight-line centroid km from `Input/TAZ_North`, intra-TAZ =
half the nearest-centroid distance) — overall, without the diagonal, per origin
superzone and per corridor class — and the flow-concentration curve (share of trips
carried by cells of a given size). Same three matrices as step 12 (trips-file survey
days 1 / 2, allocated cellular, primary hybrid). No classical p-values: expansion
weights would make everything "significant", so `D` is judged against the survey's
day-1-vs-day-2 `D` and a 200-replicate household bootstrap of the survey.

**Results.**

| `D` (max gap in cumulative trip share) | day 1 vs day 2 | survey vs cellular | hybrid vs cellular | hybrid vs survey |
|---|---|---|---|---|
| TLD, all cells | 0.009 | 0.423 (at 3.7 km; bootstrap 0.41–0.43) | 0.249 | 0.192 |
| TLD, excl. intra-TAZ | 0.011 | 0.374 | 0.242 | 0.153 |
| TLD, excl. intra-cellular-zone | 0.009 | 0.301 | 0.179 | 0.185 |
| per-origin TLD, flow-weighted (SZ) | 0.034 | 0.450 (range 0.28–0.72) | 0.284 | 0.236 |
| TLD, corridor → corridor | 0.017 | 0.387 | 0.276 | 0.123 |
| flow concentration, SZ / TAZ | 0.087 / 0.028 | 0.459 / 0.499 | 0.449 / 0.310 | 0.078 / 0.252 |

1. **The length distributions are different populations, not noisy versions of one.**
   Median centroid trip length: survey 1.95 km, cellular 7.6 km, hybrid 3.8 km; share
   under 3 km 62 % / 21 % / 43 %. `D` = 0.42 against a day-to-day `D` of 0.009 and a
   bootstrap spread of ± 0.01.
2. **It is not only the diagonal.** Dropping intra-TAZ cells leaves `D` = 0.37, and
   dropping every cell inside one native cellular zone still leaves `D` = 0.30 with the
   gap at 4.5 km — the cellular product is short of *inter*-zone trips below ~5 km as
   well, consistent with the step-12 scale audit (survey / cellular = 2.19 off the
   diagonal).
3. **Every origin shows it.** Per-superzone `D` runs 0.28–0.72 with the corridor
   superzones 10 and 11 at the top (0.72 / 0.63; survey medians 1.5 / 0.8 km against
   cellular 13.1 / 8.3 km), against a day-to-day `D` of 0.01–0.12.
4. **The hybrid keeps the survey's lengths inside the corridor** (corridor → corridor
   `D` vs survey 0.12, median 1.6 vs 1.0 km) and sits between the two elsewhere
   (outside → outside: 3.7 km against survey 1.8 / cellular 7.6).
5. **Cellular is far more diffuse.** At TAZ level 52 % of cellular trips (scaled to the
   survey total) sit in cells below 10 trips/h against 11 % for the survey and 29 % for
   the hybrid; Gini 0.84 vs 0.99 / 0.94; at superzone level the top 1 % of cells carry
   24 % of cellular trips against 47 % of the survey's.
6. **Distance-proxy calibration (KS0).** Against the survey's own reported `TrvlDist`
   the centroid proxy overstates short trips (`D` = 0.23 at 0.7 km; median 1.95 vs
   1.11 km reported). Both matrices carry the same proxy, so the comparisons are fair,
   but absolute lengths below ~1 km are a zone-geometry artefact.

**Outputs.** `Output/ths2017/tests/ks_summary.csv`, `ks0_distance_proxy.csv`,
`ks1_tld.csv`, `ks1_tld_stats.csv`, `ks3_by_origin_sz.csv`, `ks4_corridor_classes.csv`,
`ks5_concentration.csv`, `ks5_concentration_stats.csv`; figures
`Output/figures/ks_{tld,by_origin,corridor,concentration}.png`.


## 6l. Step 14 — MSSIM tests on the three matrices (`THS_2017_MSSIM_tests.ipynb`)

**Question.** The structural similarity index (Wang et al. 2004; adapted to OD matrices
by Djukic, van Lint & Hoogendoorn 2013) compares two matrices window by window on local
means (luminance), local standard deviations (contrast) and local correlation
(structure), and MSSIM is the mean over windows. It rewards getting the *neighbourhood*
right, so neighbouring rows and columns must be spatial neighbours: TAZs are ordered
along a Hilbert curve of their centroids (77 % of adjacent rows share a superzone; the
native numbering is the ordering sensitivity). Same three matrices as steps 12–13
(trips-file survey days 1 / 2, allocated cellular scaled to the survey total, primary
hybrid); windows 5 / 9 / 15 / 25 at TAZ, 3 / 5 at superzone, 3 on the 28 sub-areas; raw
trips (Djukic-standard) and log(1 + trips). Chance level: a **broken-correspondence
null** — one matrix's zones permuted, the other kept in Hilbert order (20–40 replicates).
A random ordering applied to *both* matrices is only an ordering sensitivity: it keeps
every cell pair aligned and homogenises the windows, which pushes the luminance and
contrast terms up, so it can score above the spatial ordering.

**Results** (MSSIM, Hilbert order; null in brackets).

| | day 1 vs day 2 | survey vs cellular | hybrid vs cellular | hybrid vs survey |
|---|---|---|---|---|
| TAZ, window 9, raw trips | 0.999 (0.98) | 0.993 (0.99) | 0.978 (0.93) | 0.994 (0.99) |
| TAZ, window 9, log | 0.814 (0.14) | 0.128 (0.02) | 0.475 (0.03) | 0.388 (0.11) |
| TAZ, window 25, log | 0.753 (0.08) | 0.112 (0.02) | 0.498 (0.04) | 0.332 (0.09) |
| superzone, window 3, log | 0.686 (0.07) | 0.362 (0.09) | 0.441 (0.09) | 0.938 (0.06) |
| 28 sub-areas, window 3, log | 0.619 (0.07) | 0.257 (0.05) | 0.678 (0.08) | 0.370 (0.06) |
| TAZ, window 9, log — luminance / contrast / structure terms | 0.92 / 0.91 / 0.92 | 0.29 / 0.69 / 0.70 | 0.67 / 0.87 / 0.77 | 0.60 / 0.80 / 0.74 |

1. **On raw trips the index says nothing.** Every pair scores 0.97–0.999 and so does the
   null: the constants $C_1, C_2$ are set from the matrix maximum (intra-zonal cells of
   tens of thousands of trips), which swamps the small-cell windows that make up almost
   all of the matrix. The log scale is the informative one for OD matrices whose cells
   span five orders of magnitude.
2. **Survey vs cellular is close to chance at TAZ level** (0.13 against a null of 0.02
   and a day-to-day ceiling of 0.81) and its weakest term is luminance (0.29): in the
   same neighbourhoods the two matrices carry very different local levels — the
   diagonal / short-trip gap of steps 12–13 seen window by window. Contrast and
   structure (0.69 / 0.70) say the local texture is only moderately shared.
3. **The hybrid sits between its sources and above both pairings**: 0.48 vs cellular,
   0.39 vs the survey at TAZ level; at superzone level it is the survey (0.94) and at
   sub-area level it is closer to cellular (0.68) — the correction factors keep the
   superzone pattern and let cellular shape the cells below it.
4. **Where.** Per origin superzone, survey-vs-cellular local SSIM is 0.05–0.28 with the
   corridor superzones 19, 21, 20, 11, 4 and 10 at the bottom (≤ 0.08); the hybrid lifts
   every origin to 0.36–0.57. Corridor-to-corridor windows: 0.12 survey vs cellular,
   0.53 hybrid vs cellular (day-to-day 0.67). Intra-superzone blocks agree better than
   inter-superzone ones for survey vs cellular (0.25 vs 0.11) and much better for the
   hybrid (0.76 vs 0.44).
5. **Ordering barely matters** (Hilbert vs native within 0.01–0.05), and window size
   moves the survey-vs-cellular result by < 0.03, so the conclusions do not hinge on
   those choices.

**Outputs.** `Output/ths2017/tests/mssim_summary.csv` (every level × window × scale ×
ordering × pair with the term decomposition and off-diagonal MSSIM), `mssim_headline.csv`,
`mssim_by_origin_sz.csv`, `mssim_corridor_classes.csv`, `mssim_sz_blocks_*.csv`; figures
`Output/figures/mssim_{window,maps,sz_blocks}.png`.


## 6m. Step 15 — Two-mode matrix from the trips file, transit calibrated to RavKav × OnBoard (`THS_2017_two_mode_matrix.ipynb`)

**Purpose.** A second base-year matrix built **entirely from the survey trips file**
(days 1 / 2) — no cellular data in the chain — split into **car** (`mainmode` 10 / 11)
and **transit** = bus (3 Public Bus, 4 Matronit) + taxi-type (5, 8) + rail (7), with the
bus part calibrated against the ticketing / on-board products of steps 8–9. OTHER
(walk, bicycle, …; 645k trips) is excluded from the two-mode base and reported.

**Zone conversion without cellular.** `actTaz` → `TAZ_1250` → study TAZ, the one-to-many
last link split by 2020 **population** (origins) and **employment** (destinations) from
`Input/Zonal_2020.csv` (fallback to the other variable, then uniform; 396 zones: 331 /
47 / 18 on the origin side, 378 / 0 / 18 on the destination side). Superzones and the 28
sub-areas follow from the TAZ matrices.

**Calibration design (bus).** Each source does what it measures well, at the scale
where it is reliable:

1. *Destination pattern, superzone level* — empirical-Bayes blend
   `P* = λ_A P_survey + (1 − λ_A) P_prior`, prior = RavKav × OnBoard
   (`bus_od_taz_new.csv`) aggregated to superzones, `λ_A = n_A / (n_A + k)`.
   **`k` by household-split validation** (households split at random into halves,
   40 splits, the blend on one half predicts the other's rows, mean row JSD): interior
   optimum **k\* = 5** (JSD 0.331 vs 0.353 for raw survey rows and 0.433 for pure
   ticketing rows); λ = 0.29–0.97, trip-weighted 0.86. Cross-day validation — the
   selector of the cellular hybrid — would give k = 0 because the two survey days are
   the same households repeating the same commutes; it is reported but not used.
2. *Origin volumes* — RavKav journey boardings per superzone replace the survey's
   departures (ratio RavKav / survey applied as a factor), **with a coverage guard**:
   where the ratio is below 0.5 the survey volume is kept. Regional ratio 0.80;
   superzone ratios 0.9–1.5 across the Haifa metropolitan area but 0.21–0.43 in seven
   superzones — Nazareth / Kafr Kanna (0.21, 88 sampled trips), Sakhnin, Ma'alot /
   Beit Jann, Safed, Beit She'an, Shefa-'Amr / Tamra, Daliyat al-Karmel / Isfiya —
   76 % Arab-sector population against 19 % elsewhere. The raw extract records ≈ 3,500
   AM boarding legs in the Nazareth superzone against 12,400 survey-expanded bus
   trips, so the gap is in the ticketing volume itself, not in the OD geocoding; the
   files carry route ids but no operator field, so the coverage question goes to the
   provider. Transfer hubs (leg boardings ≫ journeys: SZ 12, 13) and thin survey rows
   with large upward factors (SZ 31, 38: 2 sampled trips) are flagged.
3. *TAZ detail* — origin split within a superzone = λ-blend of survey home-based
   departure shares and RavKav boarding shares; destination split = μ-blend of survey
   arrival shares and OnBoard alighting shares (`μ_B = m_B / (m_B + k)`).

**Results.** Bus 116,083 (survey 2018) → **110,654** calibrated (all-RavKav variant
92,713); transit total 134,029; transit share of the car + transit base 9.8 % → 9.5 %
(corridor-to-corridor 12.7 % → 14.7 %, corridor → outside 17.9 % → 21.2 %,
outside → outside 8.2 % → 7.4 %). Against the RavKav × OnBoard matrix the calibrated
bus scores cosine 0.658 at superzone level (survey 0.589; all-RavKav variant 0.735) and
0.882 on the 28 sub-areas (survey 0.745), with 67 % of sub-area flow within GEH 5
(survey 30 %; day-to-day 67 %); the column totals, never imposed, reach cosine 0.86
with OnBoard-informed alightings (survey 0.78).

**Outputs** (`Output/ths2017/two_mode/`): `car_{taz,sz,area}.csv`,
`transit_{taz,sz,area}.csv` (calibrated), `transit_survey_*.csv`,
`bus_calibrated_{taz,sz,area}.csv`, `bus_survey_*`, `taxi_survey_taz.csv`,
`rail_survey_taz.csv`, variants `bus_calibrated_all_ravkav_{taz,sz}.csv` and
`bus_calibrated_uniform_factor_taz.csv`; calibration tables `bus_calibration_cv.csv`,
`bus_calibration_lambda_sz.csv`, `bus_calibration_factors_sz.csv`,
`bus_pattern_sz_prob.csv`, `bus_calibration_validation.csv`,
`bus_calibration_destinations_sz.csv`; `mode_share_sz.csv`,
`mode_share_corridor_classes.csv`; figures `two_mode_bus_cv.png`,
`two_mode_transit_share.png`.

**Caveats.** Frames (boarding-stop vs doorstep origins, non-residents) as in
`TRANSIT_DEMAND_PLAN.md`; vintage mix (calibrated superzones at May 2022, guarded ones,
car, taxi-type and rail at 2018); below the 1250-zone the survey's TAZ detail is a
population / employment split, not observation.


## 6n. Step 16 — Three-mode matrices for 2022: car, bus, rail (`THS_2017_three_mode_2022.ipynb`)

**Purpose.** Moves the survey-only two-mode matrix (step 15) to the **2022 base** with
the vintage conventions of step 11, at TAZ level, and splits it into three matrices:
**car**, **bus** (calibrated Public Bus + Matronit plus the survey's taxi-type modes —
all road public transport; the parts are saved separately) and **rail**.

**Method.** Growth factors `g = (X_2025 / X_2020)^(4/5)` per TAZ from
`Input/Zonal_2020.csv` / `Input/Zonal_BU_2025.csv`, used where the 2020 base is ≥ 500
(population for origins: 606 TAZs; employment for destinations: 506), pure-employment
zones taking the employment factor on the origin side (72), and all smaller zones their
superzone's factor (100 origins / 272 destinations). Car: Furness to the grown margins
(one grand total from the origin side). Bus: RavKav-calibrated superzone rows are the
2022 anchor and untouched; the seven coverage-guarded superzones' rows × their TAZ
origin factor; taxi-type Furnessed like car. Rail: survey rail × 54.7 / 69.0 = 0.793
(national heavy-rail ridership 2019 → 2022, the series used in step 11; 2018 taken at
the 2019 level); the 2019 smartcard station-to-station matrix scaled the same way is
saved beside it for corridor-loading work.

**Results.**

| | 2018 base | 2022 base |
|---|---|---|
| Car | 1,283,589 | 1,353,798 (+5.5 %) |
| Bus (incl. taxi-type) | 128,920 | 131,504 (anchored rows 85,452 unchanged; guarded rows 25,203 → 26,693; taxi-type 18,266 → 19,359) |
| Rail (survey, door-to-door) | 5,109 | 4,050 |
| Bus / rail share, all | 9.1 % / 0.4 % | 8.8 % / 0.3 % |
| Bus share, corridor → corridor | 14.7 % | 14.0 % |

Origin factors: median 1.050, car-trip-weighted 1.055 (largest ≈ 1.28 in Pardes
Hanna-Karkur and Tirat Carmel TAZs); destination factors: weighted 1.135 before the
grand-total rescaling. Corridor-bound car trips fall 5.8 % while every other class grows
because the BU-2025 forecast puts corridor employment growth below the regional average
— a property of the demographic scenario, not of the survey. The station-based rail
alternative carries 763 trips with both stations in the sub-area against 104
door-to-door survey rail trips there.

**Outputs** (`Output/ths2017/three_mode_2022/`): `{car,bus,rail}_2022_{taz,sz,area}.csv`,
`bus_2022_excl_taxi_taz.csv`, `taxi_2022_taz.csv`, `all_three_modes_2022_taz.csv`,
`rail_station_smartcard_2022_taz.csv`, `growth_factors_taz_2018_2022.csv`,
`summary_2018_2022.csv`, `summary_sz_2018_2022.csv`; figure `three_mode_2022.png`.

---

## 7. Output inventory (`Output/`)

| File | Shape | Produced by | Content |
|---|---|---|---|
| `matrix_10_weighted.csv`, `matrix_20_weighted.csv` | 660×707 / 651×696 | Step 1 | Weighted OD trip totals (Σ `wf_new`), observed zones |
| `prob_matrix_10_weighted.csv`, `prob_matrix_20_weighted.csv` | same | Step 1 | Row-normalized versions |
| `matrix_{10,20}_weighted_{CAR,TRANSIT,RAIL,OTHER}.csv` | observed zones | Step 1c | Weighted OD totals by aggregated mode |
| `submatrices/*.csv` | 119×119 | Step 1d | Sub-area versions of the ten weighted matrices |
| `trip_generation_taz.csv`, `trip_generation_sz.csv` | 520 / 35 rows | Step 1e | AM-peak trips per person by home zone (Home at 3:00 AM) |
| `trip_generation_summary.csv` | 520 rows | Step 1e | Compact table: TAZ, SuperZone, trips per person, expanded population |
| `prob_matrix_cellular.csv` | 778×778 | Step 1b | Cellular AM-peak probabilities (validated reconstruction) |
| `prob_sz_cellular.csv`, `prob_sz_10_weighted.csv`, `prob_sz_20_weighted.csv` | 36×36 | Step 1b | Superzone probability matrices |
| `hybrid_sz_prob.csv`, `hybrid_sz_prob_k100.csv` | 36×36 | Step 2 | Superzone hybrid (k\* = 2 / k = 100) |
| `hybrid_sz_trips.csv` | 36×36 | Step 2 | Hybrid scaled to average-weekday expanded departures |
| `hybrid_lambda.csv`, `hybrid_cv_results.csv` | 36 rows / k-grid | Step 2 | Per-origin n_A and λ; validation table |
| `hybrid_taz_prob.csv`, `hybrid_taz_prob_k100.csv` | 778×778 | Step 3 | **Final TAZ-level OD probability matrices** |
| `hybrid_taz_trips.csv`, `submatrices/hybrid_taz_trips.csv` | 778×778 / 119×119 | Step 3 | Hybrid as average-weekday AM-peak trips, full area and sub-area |
| `sz_correction_factors.csv`, `sz_correction_factors_k100.csv` | 36×36 | Step 3 | R_AB tables |
| `hybrid_taz_cv_results.csv` | k-grid | Step 3 | Route-A validation table |
| `prob_gs_*.csv`, `hybrid_gs_*.csv`, `gs_correction_factors.csv` | 25×25 | Step 4 | GS-level survey/cellular/hybrid matrices, λ table, CV results, correction factors |
| `hybrid_taz_prob_gs.csv`, `hybrid_taz_trips_gs.csv` | 778×778 | Step 4 | TAZ matrices calibrated through GS zoning |
| `ths2017/matrix_day{1,2}_*.csv`, `ths2017/matrix_avg_*.csv` | observed zones (trips-file zonation) | Step 5 | Day × mode and day-averaged matrices from the THS 2017 trips file |
| `ths2017/study_taz/matrix_avg_*` | 778×778 / 36×36 / 25×25 | Step 5 | Averaged trips-file matrices converted to the study TAZ / SZ_NEW / GS systems |
| `ths2017/study_taz/hybrid_*`, `*_correction_factors.csv` | various | Step 6 | **Primary hybrid products** on the trips-file source (SZ/GS hybrids, TAZ matrices, trips) |
| `ths2017/study_taz/submatrices/*` | 28×28 areas | Step 6 | Sub-area matrices aggregated to the 28 named areas (205 TAZs, LRT-corridor flags in `area_legend.csv`) |
| `ths2017/tests/*.csv` | various | Step 12 | Cosine / GEH similarity tests: headline summary, per-origin cosine, permutation null, scale audit, GEH pass rates by level / flow band / corridor class, 28-area cells |
| `ths2017/tests/ks*.csv` | various | Step 13 | KS tests: trip length distributions (all / off-diagonal / per origin / corridor class), flow concentration, distance-proxy calibration |
| `ths2017/tests/mssim_*.csv` | various | Step 14 | MSSIM tests: index by level / window / scale / ordering with term decomposition, broken-correspondence null, per-origin and superzone-block local SSIM, corridor classes |
| `ths2017/two_mode/*.csv` | 778×778 / 36×36 / 28×28 | Step 15 | Survey-only two-mode matrices (car, transit) with the bus part calibrated to RavKav × OnBoard (coverage-guarded), calibration tables, mode shares |
| `ths2017/three_mode_2022/*.csv` | 778×778 / 36×36 / 28×28 | Step 16 | 2022-base car / bus / rail matrices from the survey-only two-mode set (demographic growth, RavKav anchor, rail ridership series), TAZ growth factors, summaries |
| `ths2017/trip_generation_*.csv` | 478 / 35 / 25 rows | Step 7 | Per-person AM-peak generation rates on the trips-file source |
| `bus/bus_stops_taz.csv`, `bus/bus_od_taz_avg.csv`, `bus/bus_boardings_alightings_taz.csv` | 27k stops / 722×711 / 730 rows | Step 8 | RavKav stop tags, average-Tuesday AM-peak bus OD (journey-level), per-TAZ boardings/alightings (leg-level) |
| `bus/bus_probability_matrix.csv`, `bus/bus_od_taz_new.csv`, `bus/bus_od_area_new{,_filtered}.csv` | 594×548 / 722×728 / 28×28, 25×25 | Step 9 | OnBoard destination probabilities; RavKav volumes × OnBoard pattern; area aggregation and noise-filtered version |
| `train/train_od_taz_6_9.csv`, `train/train_od_area.csv` | 19×19 / 25×25 | Step 10 | Train OD 6–9 (2019 smartcards), station TAZs and areas |
| `transit/transit_od_area.csv`, `transit/all_adjusted_area.csv`, `transit/mode_share_area.csv` | 25×25 | Step 10 | Complete transit matrix, adjusted all-mode matrix, mode shares (mixed vintages) |
| `transit/car_other_area_2022.csv`, `transit/all_adjusted_area_2022.csv`, `transit/mode_share_area_2022.csv`, `transit/area_growth_factors_2018_2022.csv` | 25×25 / 28 rows | Step 11 | 2022-leveled base, all-mode matrix, mode shares; per-area growth factors |
| `demographics/scenario_totals_by_class.csv`, `demographics/scenario_comparison_area.csv` | 5 / 28 rows | `Demographic_scenario_comparison.ipynb` | BU vs HS forecast comparison (2040/2050, `Input/Demographic_Forecast/`): totals by corridor/research/study class; per-area growth factors and HS−BU deltas |
| `forecast/all_modes_area_{BU,HS}_{2040,2050}.csv`, `forecast/forecast_margins_growth.csv` | 25×25 / 100 rows | `Forecast_matrices_2040_2050.ipynb` | Four forecast all-modes AM-peak matrices (2022 base Furnessed to scenario-year margins: population → origins, employment → destinations, 2020→2022 bridge via the BU-2025 interpolation, new-resident production term for sub-500-population areas); per-area growth factors and margin targets |
| `forecast/share_{car_other,bus,rail}_2022_{raw,smoothed}.csv`, `forecast/share_strata_2022.csv` | 25×25 / 12 strata | `Base_mode_shares_2022.ipynb` | Revealed 2022 modal shares per OD cell (components: car/other + RavKav bus + rail × 54.7/69) and EB-smoothed versions (k = 50, shrunk toward corridor-class × distance-band stratum shares, sum to 1 per cell); stratum behavioral baseline table |
| `forecast/nobuild_{car_other,bus,rail}_{scenario}.csv`, `forecast/lrt_market_flag.csv`, `forecast/lrt_market_{scenario}.csv`, `forecast/lrt_market_summary.csv` | 25×25 ×12 / 25×25 / ×4 / 4 rows | `NoBuild_and_LRT_market.ipynb` | No-build modal matrices (smoothed 2022 shares pivoted onto scenario-year totals; cell shares frozen, aggregate share moves by composition only — falls 8.9% → 7.5–8.0%) and the LRT market: core (both ends corridor) and per-scenario market trips |
| `forecast/lrt_market_tiers_{MainCorridor,FullLength}.csv`, `forecast/lrt_alignment_market_summary.csv` | 25×25 ×2 / 10 rows | `LRT_alignment_markets.ipynb` | Market tiers per OD (2 = core one-seat, 1 = transfer-influenced, 0 = outside) for the two alignment scenarios (`Input/lrt_alignment_flags.csv`: Main = areas 1–13 + influenced 24–28; Full = 1–19, 23), and market counts per alignment × scenario-year with the no-build transit conversion base |
| `figures/` | — | Steps 1b–3 | Scatter plots, CV curves, λ curves, R_AB heatmap |

All matrices are indexed by origin zone (rows) × destination zone (columns). Probability
matrices are row-stochastic: cell (i, j) is the probability that an AM-peak trip leaving
zone i ends in zone j.

## 8. Known caveats and open questions

1. **Input data version** — the activities file is newer than the one used by the
   original Colab run (§1); results are internally consistent but not comparable to the
   numbers stored in `THS_2018_MTX.ipynb`.
2. **Cellular zone mapping** — coarse national flows are replicated at full value to
   child TAZ pairs (§2); within-superzone allocation in Step 3 inherits this.
3. **Intra-zone divergence** — the largest survey–cellular disagreement (72% vs 34%
   self-containment) is exactly where their *measurement* differs (short trips invisible
   to cell towers). The hybrid resolves it in the survey's favor by construction; an
   independent source on short-trip volumes would arbitrate.
4. **Cross-day validation limits** — both survey days come from the same household
   panel, so CV can calibrate against self-consistency only; at TAZ level this bias is
   strong enough to disqualify CV entirely (§6, Route A).
5. **Volumes at TAZ level** — `hybrid_taz_trips.csv` scales the hybrid probabilities by
   superzone survey departure totals split among member TAZs by cellular outflow shares.
   The superzone-level scale is survey-based and solid; the within-superzone origin split
   rests on cellular structure (with its replication caveat), not on a production model —
   treat individual TAZ origin totals accordingly.

## 9. Reproduction

```bash
git lfs pull                       # the four input CSVs are stored in Git LFS
pip install pandas numpy matplotlib jupyter
jupyter nbconvert --to notebook --execute --inplace THS_2018_MTX_weighted.ipynb
jupyter nbconvert --to notebook --execute --inplace THS_2018_MTX_weighted_vs_cellular.ipynb
jupyter nbconvert --to notebook --execute --inplace THS_2018_MTX_hybrid.ipynb
jupyter nbconvert --to notebook --execute --inplace THS_2018_MTX_hybrid_taz.ipynb
```

Each notebook is self-contained (loads its own inputs from `Input/Matrices/` and writes
to `Output/`); the order above only matters in that later notebooks' documentation
refers to earlier findings. Outputs under `Output/` are committed as regular git files
(exempted from LFS in `.gitattributes`).
