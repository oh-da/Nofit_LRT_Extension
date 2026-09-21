# LRT Capture Model — Generalized Cost Plan

Agreed approach for the final step of the forecast hierarchy: estimating the LRT
matrix from the market and no-build products already built
(`LRT_alignment_markets.ipynb`, `NoBuild_and_LRT_market.ipynb`,
`Base_mode_shares_2022.ipynb`). The guiding principle: **the skims are the easy
half** — the ridership numbers are determined by the cost-sensitivity
calibration against revealed behavior, not by skim precision. An uncalibrated λ
inside a well-dressed GC formula is still an assumed capture rate.

## 1. Generalized cost formula

In generalized minutes (money converted via VOT, so fares/parking do not
dominate the formulation):

```
GC_m = IVT + 2.0·walk + 2.0·wait + 8·transfers + (fare + parking)/VOT
```

| Component | Default | Notes |
|---|---|---|
| walk / wait weight | 2.0 | standard range 1.5–2.5 |
| wait | headway/2, capped ~10 min | |
| transfer penalty | 8 generalized min | range 5–10; applies to the Main-alignment "influenced" tier (tier 1 in `Output/forecast/lrt_market_tiers_*.csv`) |
| VOT, fares, parking | align with נוהל פר"ת | the study will be appraised against it |
| LRT commercial speed | 22–26 km/h | Jerusalem ~19–20 observed; Tel Aviv Dankal ~24 design |
| LRT peak headway | ~6 min | |

## 2. Skims — mixed sourcing, not a single Google pull

- **Car**: survey-observed door-to-door times from `Input/trips_ths_2017.xlsx` —
  5,484 AM-peak car trips with 100%-complete `TrvlTime`/`TrvlDist` — smoothed
  per area pair (time ≈ a + b·distance where cells are thin). Internally
  consistent with the demand data and AM-peak by construction. Add a small
  Google Distance Matrix sample (~40 key pairs, `departure_time` = typical
  Tuesday 07:30) to derive a 2017→today congestion uplift factor, instead of
  querying all 625 pairs. (Full Google coverage is also cheap if preferred;
  note Google ToS on storing results.)
- **Bus**: the survey is too sparse (~265 AM transit observations) — use the
  **Israeli national GTFS** (open, MOT) for scheduled in-vehicle times and
  headways between area centroids; free, storable, reproducible. Google transit
  mode is the fallback.
- **LRT**: no external service — build from geometry already in the repo:
  cumulative distance along the alignment between area centroids (computed in
  `Base_mode_shares_2022.ipynb`) ÷ commercial speed + dwell; access/egress from
  centroid-to-alignment distance. The assumptions reduce to three numbers:
  speed, headway, dwell.

## 3. Calibrate, then pivot

Fit λ by binary logit on revealed behavior: observed 2022 transit share vs
(GC_transit − GC_car) across the 625 cells (volume-weighted) or the 12
corridor-class × distance-band strata (`Output/forecast/share_strata_2022.csv`).

Capture is then a nested incremental logit, consistent with the pivot
philosophy of the whole pipeline:

- **Bus vs LRT** (transit nest — the biggest flow, bus→LRT):

  `P_LRT|T = 1 / (1 + exp(λ_T · (GC_LRT − GC_bus)))`

- **Car → transit**: the LRT improves the transit-nest logsum; apply
  incremental logit pivoted off the smoothed no-build transit share per cell —
  a modest shift, as it should be.
- **LRT matrix**, per alignment × scenario-year, on market cells only:

  `T_LRT = T_ALL,y × S'_transit × P_LRT|T`

  with the transfer penalty added to GC_LRT on tier-1 (influenced) pairs and
  tier-0 pairs excluded.

Key property: with the LRT removed, the model reproduces observed 2022 behavior
by construction — the first thing reviewers will test.

## 4. Sanity anchors and sensitivity

- Benchmark the resulting corridor transit share against Metronit's observed
  experience (and Jerusalem LRT as a secondary reference).
- Sensitivity on the three drivers: commercial speed, headway, λ.

## 5. Inputs needed to run

1. Station/alignment assumptions per alignment scenario (speed, headway, dwell,
   station spacing) — or proceed with the defaults above, clearly flagged.
2. Optional: Google API key for the congestion-uplift sample; the first pass
   runs entirely on GTFS + survey + geometry with no external services.
