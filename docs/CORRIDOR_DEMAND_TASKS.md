# Corridor Demand — Task List

*Status: open, agreed 2026-09-19; updated 2026-09-21 after the methodology review (`docs/Nofit_Demand_Methodology_Review.md`). Records what the base-year hybrid matrix still needs
before it is fit for corridor demand estimation, and the 2050 growth step that follows.
Ordered by how much each item changes the corridor answer. Tasks marked **[needs LFS
data]** require the raw inputs held in Git LFS (`git lfs pull` on the data machine):
`Input/Matrices/AvgDayHourlyTrips201819_1270_weekday_v1.csv` (cellular, 1270 national
zones, hourly), `ACTIVITIES_DEC18_corrected.csv`, `households_with_weights.csv`,
`1270_02_09_2021_TAZ_North_keys.csv`. Background: `reports/historical/PCA_Eigenvector_Report.docx` rev. 2
(§5–6) and `THS_PCA_review_tests.ipynb`.*

Key facts driving the list (2017 trips-file hybrid, `Output/ths2017/study_taz/`):

| Fact | Value |
|---|---|
| Corridor-to-corridor AM trips (both ends in the 119 corridor TAZs) | 94,610 = 4.6 % of study area |
| …of which inside one superzone / inside one TAZ | 71 % / 23 % |
| …by centroid distance: intra-TAZ / < 1 km / 1–2 km / ≥ 2 km | 23 % / 20 % / 10 % / 47 % |
| Trips with one end in the corridor, other end outside | 230,000 (2.4 × the core market) |
| AM 6–9 share of daily survey trips (PM 15–19) | 24 % (28 %) |
| Cellular native resolution | 398 zones over 781 study TAZs; corridor 119 TAZs in 67 cellular zones (37 zones hold 1 TAZ, 18 hold 2, 12 hold 3–8) |
| Below the cellular zone, the TAZ "cellular" structure is replication, not measurement | METHODOLOGY §2, caveat 2 |
| Absolute volumes | survey expansion only; cellular enters as probabilities |

## A. Resolution and content of the matrix

- [ ] **A1. Within-superzone allocation in the corridor** *(highest impact)*
  - [ ] **[needs LFS data]** Compare survey vs cellular destination splits at the
        1270-zone level inside the corridor superzones (the finest fair comparison);
        extend `THS_PCA_review_tests.ipynb` §6, which used hybrid volumes as a proxy.
  - [ ] Decide per corridor superzone how much to trust cellular's split (good: 13, 14,
        12, 4; poor: 19, 15, 24, 9 at 1250-zone resolution).
  - [ ] For the 30 corridor cellular zones that hold ≥ 2 TAZs (Hamifrats + Namal,
        Bat Galim + Kiryat Eliezer, Kiryat Ata Center + East, Tirat Carmel 2 zones / 13
        TAZs, …): replace the full-value replication with a stated split rule —
        population / employment shares from the zonal files (origin / destination ends),
        RavKav stop-level boardings for the transit component — and flag the split as
        synthetic. Ask the cellular provider whether a finer cut of the corridor is
        available.
  - [ ] Alternative to keep open: run the corridor analysis at the 67-zone cellular
        resolution and disaggregate to TAZ only for station-catchment work.
- [ ] **A2. Trip length / level of service per OD pair**
  - [ ] Build network skims (walk, car, existing bus, rail, proposed LRT) for the corridor
        TAZs; replace centroid-distance bands in `Base_mode_shares_2022.ipynb`.
  - [ ] Treat the diagonal explicitly: within-TAZ length distribution for intra-TAZ cells
        (the diagonal correction adds trips with a median reported length of 0.7 km), or
        exclude intra-TAZ cells from the LRT market with a documented rule.
- [x] **A0. Superzone conservation of the TAZ hybrid** *(done 2026-09-21,
      `Hybrid_superzone_conservation_test.ipynb`, METHODOLOGY §6q)*: the correction-factor
      hybrid misses its superzone OD blocks by up to 49 %; a jointly-constrained rebalanced
      version is published. The hybrids are historical; the replicated cellular mapping
      inside them (A1) is still open.
- [ ] **A3. Trip purpose**
  - [ ] Obtain the THS activity codebook (`mainActivity` codes 2, 4, 11 …).
  - [ ] Purpose shares per superzone pair from the trips file (HBW / HBE / other), applied
        to the hybrid, or three purpose-specific hybrids.
- [ ] **A4. Time of day and direction**
  - [ ] Check the `Dep_h` coding (16 % of daily trips fall in the 7:00 hour, 3 % at 6:00).
  - [ ] Hour-of-day and direction factors by purpose and corridor class from the survey
        (all hours), RavKav hourly boardings and **[needs LFS data]** the 24 cellular
        hourly matrices; produce PM-peak and daily corridor matrices. *(AM peak hour done —
        B1e.)*

## B. Scale and frame

- [ ] **B1. Scale validation** **[needs LFS data]**
  - [x] Survey-expanded origin / destination totals vs cellular AM volumes by superzone
        and by cellular zone; the diagonal magnitude in particular (does cellular miss
        ~70 % of intra-superzone trips, or does the survey over-record them?).
        *Done in `THS_2017_cosine_GEH_tests.ipynb` (G1, `Output/ths2017/tests/geh_scale_audit_*.csv`):
        survey 3.56 × cellular overall, 2.19 × on inter-1250-zone trips; cellular is 14 %
        intra-1250-zone vs survey 47 %; superzone origin ratios 0.19–0.78. Which side is
        right still needs the cellular trip definition (next bullet).*
  - [ ] Obtain the cellular product's trip definition (dwell-time, minimum-distance
        thresholds).
  - [ ] Car volumes vs screenline counts on the corridor, with an explicit assignment
        link (transit vs RavKav already done at area level: ratio 0.91).
  - [ ] Resolve the TAZ → superzone key precedence between the 2017 and 2018 chains
        (`prob_sz_cellular.csv` vs the 2017 rebuild; ≤ 0.07 in a handful of cells).
- [x] **B1b. Ticketing coverage — segmented rule** *(done 2026-09-21 in
      `THS_2017_two_mode_matrix.ipynb`, METHODOLOGY §6m)*: the coverage test is applied per
      origin superzone × destination segment (local / inter-SZ corridor-bound / inter-SZ
      other); the binary rule is kept as a variant, with a threshold sweep. Steps 16–18
      re-run. Result: the 23 → 1 corridor profile did **not** move towards the ticketing
      one — the remaining gap is allocation and destination frame, not coverage (§6p).
- [ ] **B1c. Cause of the sub-0.5 ratios** — ask the RavKav provider which operators the
      extract covers and whether cash / unvalidated boardings are included; cross-check
      route ids against an operator crosswalk valid for May 2022; obtain counts on Nazareth
      local services. Until answered, publish the four bus variants, not one.
- [ ] **B1d. Transit units (review §3)** — establish from the OnBoard codebook whether its
      P(alight | board) rows are per boarding leg or per journey; test whether bus-to-rail
      travellers sit in both the RavKav bus OD and the station matrix; keep person-journey
      and boarding products separate until an access / transfer allocation links them.
- [x] **B1e. Peak hour** *(done 2026-09-21, `Corridor_peak_hour_2022.ipynb`, METHODOLOGY
      §6r)*: peak-hour factors from survey departure times (07:00–08:00; PHF₃ₕ 0.59–0.66) and
      peak-hour link profiles. Still open: a boarding-hour factor from the RavKav files
      (`bus_trip_hour`, LFS) as the independent check for the bus layer, and a
      link-crossing (rather than departure) hour once travel times exist (A2).
- [ ] **B2. Population frames**
  - [ ] Reconcile the transit layer (RavKav journeys by boarding stop, incl. non-residents
        and transfers; Hamifrats 120 THS vs 1,079 RavKav) with the resident-household
        car / other base: add non-resident and external components on the car side or
        strip them from transit, consistently. Students and military traffic explicitly.
  - [ ] Bring back trips with one end outside the study area (5 % of survey weight,
        most rail trips) as an external segment; bring Adi, Alon Hagalil and Tzipori back
        into the line sequence with flagged uncertainty (review §11).
- [ ] **B3. Market definition**
  - [ ] Extended market (one end in the corridor, 230k trips) with access / egress modes
        (walk catchment, feeder bus, park-and-ride) — depends on A1 and A2.

## C. Behavioural layer

- [ ] **C1. Mode choice with level-of-service response** — incremental logit (or the
      generalized-cost model of `docs/LRT_CAPTURE_PLAN.md`) calibrated on existing bus and
      rail shares, instead of frozen 2022 cell shares; depends on A2.
- [ ] **C2. Segmentation** — car availability by zone (check the raw survey household
      file **[needs LFS data]**; otherwise census / zonal files).
- [ ] **C3. Uncertainty** — carry as sensitivities into corridor numbers: survey
      correction within its bootstrap spread (self-containment 0.67–0.70, outbound
      TV ± 0.02), a cellular short-trip under-detection scenario, and the A1 allocation
      choice.

## D. Growth to 2050 (after A–C)

- [ ] **D0. Rebuild the forecast branch from the current base** *(review §2, §13, §14)*:
      `Vintage_alignment_2022` → `Forecast_matrices_2040_2050` → `Base_mode_shares_2022` →
      `NoBuild_and_LRT_market` → `LRT_alignment_markets` currently consume the historical
      25-area composite `Output/transit/all_adjusted_area_2022.csv`. Re-point them at
      `Output/ths2017/three_mode_2022/` (TAZ level, four layers), change the share
      smoothing to act on sampled counts with rail availability handled explicitly, and
      relabel the frozen-share no-build as a demographic reference. Needs the LFS
      `Input/Demographic_Forecast/Zonal_*.csv` files.

- [ ] **D1.** Calibrate a doubly-constrained gravity model with K-factors to the 2022
      hybrid at superzone level (deterrence by purpose once A3 exists); check
      trip-length distributions before / after.
- [ ] **D2.** Apply hierarchically at TAZ with BU / HS 2050 margins (population → origins,
      employment → destinations; gravity-synthesized rows for zones growing > ~50 % or
      from < 500 residents), structure constrained to the superzone hybrid pattern;
      replaces the 25-area Furness of `Forecast_matrices_2040_2050.ipynb`.
- [ ] **D3.** Behaviour as an explicit scenario layer (ageing, telework, car ownership)
      on margins / mode split, never folded into the matrix.
- [ ] **D4.** External check against the national model's 2040 / 2050 matrices for the
      same superzones, if obtainable; implied 2050 trip rate per resident (2022: 0.65
      AM trips per resident in the matrix).

## Suggested order

1. A1 + A2 together (corridor resolution with network distances; settle the diagonal).
2. A3 + A4 from the survey (cheap, no LFS data needed except the cellular hourly check).
3. B1 as soon as the LFS data is on hand — it gates everything downstream.
4. B2, B3, C1–C3.
5. D1–D4.

## Can be done without the LFS data

A1 split rule from zonal files and RavKav; A2 skims; A3; A4 survey-side factors and the
`Dep_h` check; B2; B3; C1 (once A2 exists); C3; D1 (on the 2022 hybrid as is).
