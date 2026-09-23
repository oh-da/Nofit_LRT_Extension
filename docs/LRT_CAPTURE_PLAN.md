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
| LRT–Metronit transfer | **0** (free) | assumption of 22 Sep 2026: integrated operation, same platform; bus ↔ LRT keeps the 8 |
| LRT premium (rail bonus) | **5 generalized min** (range 0–10) | assumption of 22 Sep 2026: the LRT valued above the bus at equal times; subtracted from GC_LRT in the transit nest |
| VOT, fares, parking | **out of the comparison** (decision of 22 Sep 2026) | the transit fare in the area is flat and integrated with a daily cap (two fares pay for the day): identical for bus, Metronit and LRT and for every pair, so it drops out of the transit choice and is a constant per trip against the car, absorbed by the pivot; car operating cost and parking excluded on the same decision |
| LRT commercial speed | **calibrated function** (Red Line, 22 Sep 2026) transferred through the Red Line's actual spacing: running 46 km/h + 49 s per stop underground, 31 km/h + 74 s at the surface, levelled to the observed means — 27.6 / 17.1 km/h on `hf_lrt_3`'s 815 m spacing (METHODOLOGY §6w rev. 2) | the report's 500 m reading (15.3 / 12.5 km/h) is superseded; `docs/Transit_Travel_Time_Calibration_Report_Operator22.md` |
| LRT peak headway | 5 min (12 departures an hour) | assumption of 22 Sep 2026 |
| LRT design regime (third scenario) | 50 km/h between stops + 10 s per stop, headway 5 min | specification of 22 Sep 2026; no acceleration allowance, a ceiling beside the two calibrated scenarios: 26.3 min end to end (42.7 km/h), central capture 3,970 trips in 2022 (METHODOLOGY §6w / §6ac addenda) |

## 2. Skims — mixed sourcing, not a single Google pull

- **Car**: survey-observed door-to-door times from `Input/THS_2017-2018/trips_ths_2017.xlsx` —
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
- **LRT**: no external service — built from the planned geometry
  (`Input/GeneralHalufa/hf_lrt_3.shp` + `station_hf_lrt_3.geojson`, 24 stations on
  the Tirat Carmel – Hamifrats trunk) with the calibrated stop-to-stop function in
  `LRT_line_stations_travel_time.ipynb` (step 25): station-to-station matrices for
  an all-underground and an all-ground scenario; access / egress from TAZ centroid to
  nearest station (step 26). Still needed: the alignment and stations of the segment
  beyond Hamifrats and of the three V2 branches, the planned headway, and the
  underground / ground regime per section. **Status, step 31 (22 September 2026):**
  for the fifteen V2 areas without their own alignment, `Mode_skims_and_flow_comparison.ipynb`
  (METHODOLOGY §6ac) fills the LRT skim with a feeder composite (bus, or Metronit with a free transfer) instead — the
  observed bus skim to the least-cost gateway station area, an 8-minute transfer, then
  the LRT leg — as the interim for the branch areas until E1 is closed.

**Status (22 September 2026).** `GC_data_inventory_and_skims.ipynb` (step 26,
METHODOLOGY §6x) holds the component-by-component inventory on the 25 V2 areas
(`Output/gc/gc_data_inventory.csv`), the first-fill skims (car from the survey, bus
from the May 2026 speed network, LRT from step 25) and the partial generalized-cost
matrices with every cell's status. Money components are out of the comparison by decision
(flat integrated fare, METHODOLOGY §6x addendum 4); bus walk / wait / transfers come from
the GTFS (steps 29–30).

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

**Status (22 September 2026).** The cross-sectional fit was run
(`Mode_skims_and_flow_comparison.ipynb`, step 31, METHODOLOGY §6ac): a volume-weighted
binary logit of the observed 2022 transit share on `GC_bus − GC_car` (573 area pairs,
67,700 trips) returns the wrong sign (λ = −0.011 per generalized minute, se 0.0005,
ρ² 0.003), and adding a constant per centroid-distance band still returns no usable
cost sensitivity (λ = +0.0002, ρ² 0.036). The pairs where the bus is dearest relative to
the car are also the least car-available (captive riders, the northern-branch
localities) — car availability is not in the skims — so the revealed 2022 split cannot
identify λ from this cross-section, as anticipated
above. λ is therefore **assumed**: central 0.03 per generalized minute (range
0.02–0.05), with λ_T = 2λ within the transit nest. The pivot machinery of this section
(the nested incremental logit, Empirical-Bayes-smoothed toward the study-area share) is
implemented in step 31 and run on the 2022 corridor-internal flows for both LRT
scenarios, with an LRT premium of 5 generalized minutes and free LRT–Metronit transfers, giving
central-case captures of 4,114 (underground) / 3,201 (ground) LRT trips 06:00–09:00
(λ range 3,083–5,812 / 2,012–5,153; without the premium 3,307 / 2,535) — values of the
23 September 2026 rerun with the corrected mode codes (METHODOLOGY §0 "Rerun"; the run of
22 September gave 3,332 / 2,544 with the Metronit riders outside the transit nest).
Segmented estimation on the survey's person-level records was then done in step 33
(METHODOLOGY §6ae): λ = 0.035 (0.002–0.068) with car availability and purpose held constant,
so the assumed 0.03 stands, while the licence holders in car-owning households give no
identifiable λ (`docs/CORRIDOR_DEMAND_TASKS.md` E7). Step 32
(`LRT_capture_forecast_2040_2050.ipynb`, METHODOLOGY §6ad) reruns this same pivot on step
23's four 2040/2050 forecast sets (BU_2040, BU_2050, HS_2040, HS_2050), giving central-case
underground LRT trips of 5,329 / 5,962 (BU) and 5,335 / 6,245 (HS) against 4,114 in 2022,
and ground trips of 4,085 / 4,559 (BU) and 4,121 / 4,804 (HS) against 3,201. The capture
rate itself is unchanged across scenario-years — the LRT's share of no-build transit stays
0.29–0.30 underground and 0.22–0.23 ground in every year — because step 32 holds the
step-31 skims fixed and only the demographic-reference market grows.

## 4. Sanity anchors and sensitivity

- Benchmark the resulting corridor transit share against Metronit's observed
  experience (and Jerusalem LRT as a secondary reference).
- Sensitivity on the three drivers: commercial speed, headway, λ.

## 5. Inputs needed to run

1. Station/alignment assumptions per alignment scenario (speed, headway, dwell,
   station spacing) — or proceed with the defaults above, clearly flagged.
2. Optional: Google API key for the congestion-uplift sample; the first pass
   runs entirely on GTFS + survey + geometry with no external services.
