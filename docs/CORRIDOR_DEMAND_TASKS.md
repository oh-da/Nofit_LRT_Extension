# Corridor Demand — Task List

*Status: open, agreed 2026-09-19; updated 2026-09-22 with the generalized-cost inventory (section E); updated 2026-09-21 after the methodology review (`docs/Nofit_Demand_Methodology_Review.md`). Records what the base-year hybrid matrix still needs
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
- [~] **A2. Trip length / level of service per OD pair** *(first pass 2026-09-22 on the
      25 V2 areas, `GC_data_inventory_and_skims.ipynb`, METHODOLOGY §6x)*
  - [~] Build network skims (walk, car, existing bus, rail, proposed LRT) for the corridor
        TAZs; replace centroid-distance bands in `Base_mode_shares_2022.ipynb`. *Done at
        area level: car door-to-door from the survey (smoothed), bus fastest-path IVT on the
        May 2026 speed network (lower bound; survey door-to-door is 2.1–2.3 × it), LRT
        station-to-station on `hf_lrt_3` (step 25) with walk access from the TAZs. Open: the
        TAZ level, GTFS-based bus paths / headways / transfers, the LRT branches.*
  - [ ] Treat the diagonal explicitly: within-TAZ length distribution for intra-TAZ cells
        (the diagonal correction adds trips with a median reported length of 0.7 km), or
        exclude intra-TAZ cells from the LRT market with a documented rule.
- [x] **A0. Superzone conservation of the TAZ hybrid** *(done 2026-09-21,
      `Hybrid_superzone_conservation_test.ipynb`, METHODOLOGY §6q)*: the correction-factor
      hybrid misses its superzone OD blocks by up to 49 %; a jointly-constrained rebalanced
      version is published. The hybrids are historical; the replicated cellular mapping
      inside them (A1) is still open.
- [ ] **A3. Trip purpose**
  - [x] Obtain the THS activity codebook (`mainActivity` codes 2, 4, 11 …). *Done
        2026-09-23: the field metadata under `Input/THS_2017-2018/` plus step 33's join to
        the activities file fix `mainActivity` 1–12 (Home, Work, Work-related, Education,
        Shopping, Errands, Social, Medical, Entertainment, Sports, Transport / accompany,
        Other) and `mainmode` (3 Public Bus, 4 group taxi, 5 Matronit, 7 train, 8 special
        taxi) — the latter corrects steps 15–32 (METHODOLOGY §8, caveat 14).*
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
      rail shares, instead of frozen 2022 cell shares; depends on A2 and on closing the
      gaps in `Output/gc/gc_data_inventory.csv` (E1–E4 below).

## E. Generalized cost — data still missing (inventory of 2026-09-22, `Output/gc/gc_data_inventory.csv`)

- [ ] **E1. LRT geometry beyond the trunk** — alignment and stations from Hamifrats to
      Tsomet Kiryat Ata and for the three V2 branches (T1 Kiryat Ata – Shefaram – Nazareth,
      T2 Krayot, T3 Kiryat Yam); the underground / ground regime per section (the two
      scenarios of step 25 are the pure bounds); the planned AM headway per branch and the
      through-running pattern. Add TAZ 1509 (station S13) to the V2 aggregation.
      **Interim, step 31 (22 September 2026):** for the fifteen V2 areas with no alignment
      of their own, `Mode_skims_and_flow_comparison.ipynb` (METHODOLOGY §6ac) skims the LRT
      as a feeder composite (bus, or Metronit with a free transfer) instead — the observed bus skim to the least-cost gateway
      station area, an 8-minute transfer, then the LRT leg — which is what the capture
      numbers below currently rest on for the branch areas; it stands in for, not replaces,
      the actual branch geometry.
- [x] **E2. LRT speed on this spacing** *(resolved 2026-09-22, step 25 revision 2)* — the
      calibration report's 500 m section assumption was checked against the Red Line's
      timetable in the GTFS (underground sections 970 m, surface 577 m): the coefficients are
      now transferred through a running-time / stop-penalty decomposition, giving 27.6 km/h
      underground and 17.1 km/h at ground level on `hf_lrt_3` (40.7 / 65.8 min end to end).
      Remaining refinement: the regime per section of the actual design, and a check of the
      levelled fit against a year-specific calibration. The LRT's open question is now
      **station access** (13.6 min walk on the trunk pairs against 4.7 to a bus stop): an
      access / feeder model (feeder buses, walking network, park-and-ride) — added as E6.
- [ ] **E6. LRT access model** — replace the centroid-to-nearest-station walk with a walking
      network, feeder-bus access from the GTFS (bus to the nearest station + transfer) and
      park-and-ride where the station plan allows; this is what the generalized-cost
      comparison now turns on.
- [~] **E3. Bus level of service from GTFS** — *done 2026-09-22 for the direct services*
      (`GTFS_bus_LOS_TAZ.ipynb`, METHODOLOGY §6aa; feed of 22 May 2026): per-TAZ LOS for bus
      and for the Metronit (codes 83001, 67002, 67003, 62004, 52005 — the supplied 83002–83005
      were not Metronit codes in the feed), a BRT-access flag, and the direct-service skim
      between the V2 areas that step 26 now uses for the bus IVT, wait and stop access, with
      the Metronit as its own mode. Open: transfer paths for the 178 area pairs (8 of 90 trunk
      pairs) without a direct service; observed AVL running times instead of the timetable;
      the 8-minute gap between the timetable's best direct bus (18.6 min door to door on the
      trunk pairs) and the survey's reported 27.1 min as the bus calibration margin.
      *Observed running times done 2026-09-22 (step 30, METHODOLOGY §6ab): the trips routed over
      the May 2026 link speeds; the link speeds include dwell; step 26 uses the observed skim.*
- [x] **E4. Money components** — *closed by decision, 22 September 2026*: the transit fare
      in the area is flat and integrated with a daily cap (two fares pay for the day), so it
      is identical for bus, Metronit and LRT and for every pair and drops out of the transit
      choice; against the car it is a constant per trip absorbed by the pivot. Car operating
      cost and parking are excluded on the same decision (METHODOLOGY §6x addendum 4). Still
      open from this item: confirm the walk / wait / transfer weights against נוהל פר"ת.
- [ ] **E5. Car skim vintage** — the survey door-to-door times are 2017 / 18; a small
      Google Distance Matrix sample (≈ 40 pairs, Tuesday 07:30) or the national model's
      car skim gives the 2026 uplift.
- [~] **E7. Cost sensitivity λ** — *person-level estimate done 2026-09-23 (step 33,
      `Mode_choice_person_level.ipynb`, METHODOLOGY §6ae), on the THS person and household
      tables with `new_wf` as the only weight: with car availability, purpose, age and sector
      held constant, λ = 0.035 per generalized minute (95 % 0.002–0.068), 0.041–0.053 across the
      variants — the assumed 0.03 stands as the central case. Still open: for the licence
      holders in car-owning households λ is not identified (0.008 ± 0.017); λ_T and the LRT
      premium are untouched. Closing those needs the SP survey
      (`docs/RED_TEAM_RESPONSE_2026-09-23.md` §4) or TAZ-level skims that admit the whole
      study area's trips (E6).* What was tried before (22 September 2026, step 31,
      `Mode_skims_and_flow_comparison.ipynb`, METHODOLOGY §6ac): a volume-weighted binary
      logit of the observed 2022 transit share on `GC_bus − GC_car` across the 573 sampled
      area pairs (67,700 trips) returns the wrong sign (λ = −0.011 per generalized minute,
      se 0.0005, ρ² 0.003); adding a constant per centroid-distance band still returns no
      usable cost sensitivity (λ = +0.0002, ρ² 0.036) — the pairs with the largest bus
      handicap are also the least car-available (captive riders, the northern-branch
      localities); car availability is not in the skims, so it dominates the cross-section
      and masks any genuine cost response.
      `docs/LRT_CAPTURE_PLAN.md` §3 currently runs on an assumed central λ = 0.03 per
      generalized minute (range 0.02–0.05, λ_T = 2λ). What closes it: either a segmented
      logit on the survey's person-level records (car availability, trip purpose, distance
      band, so the captive-rider confound is held constant rather than
      averaged over), or a transferred λ from the national transport model's own mode-choice
      calibration, with its source and estimation sample cited.
- [~] **C2. Segmentation** — car availability by zone (check the raw survey household
      file **[needs LFS data]**; otherwise census / zonal files). *Person-level car
      availability (licence, cars per licensed driver) is now in hand from
      `Input/THS_2017-2018/PersonsFin2.csv` and used by step 33; the by-zone segmentation of
      the matrices is still to do.*
- [ ] **C3. Uncertainty** — carry as sensitivities into corridor numbers: survey
      correction within its bootstrap spread (self-containment 0.67–0.70, outbound
      TV ± 0.02), a cellular short-trip under-detection scenario, and the A1 allocation
      choice.

## D. Growth to 2050 (after A–C)

- [x] **D0. Rebuild the forecast branch from the current base** *(review §2, §13, §14)* —
      **method implemented 2026-09-21** in `Forecast_matrices_TAZ_2040_2050.ipynb`
      (`docs/FORECAST_METHODOLOGY_2040_2050.md`, METHODOLOGY §6u) and mechanics-tested on a
      dry run; *done 2026-09-22 (step 23 scenario run — the LFS zonal files were pulled and
      the notebook produced the four scenario sets BU_2040, BU_2050, HS_2040, HS_2050 under
      `Output/forecast_taz/{scenario}/`; car and transit margins converge to 10⁻⁶, taxi-type
      stops at 500 iterations with 10–15 % row-margin error; step 32 then reran the LRT
      capture on the four sets, METHODOLOGY §6ad)*. Original scope:
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

## F. Plan of 22 September 2026

The ordered plan for tightening the capture and the scenarios to test is in
`docs/PLAN_TIGHTENING_AND_SCENARIOS.md` (person-level λ, walking-network access, TAZ-level
trunk capture, bus-cost overhead, realistic speed regime, headways; then S1–S9).

## G. Red-team response of 23 September 2026

`docs/RED_TEAM_RESPONSE_2026-09-23.md` answers the external methodology red-team review:
the gate before any step 31 / 32 figure is reported as ridership (person-level λ or SP data,
plus one independent trunk count), two parallel tracks (in-house work on LFS data; the data
request), the rebuild order for steps 15–32, and the data-request sheet with priority and
holder. It supersedes the "suggested order" above where they differ.
