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
