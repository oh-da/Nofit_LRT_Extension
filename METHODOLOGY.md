# Methodology — OD Demand Matrix from THS 2018 and Cellular Data

This document records what has been done in this repository so far: the reasoning behind
each step, the exact methodology, the inputs consumed and the outputs produced. Every
step is implemented as an executed Jupyter notebook at the repository root, and every
number quoted here can be reproduced by re-running the corresponding notebook.

**Goal.** Build an AM-peak (06:00–09:00) origin–destination demand matrix for the Nofit
LRT extension study area (778 traffic analysis zones, northern Israel). The first
generation of the work fused two independent sources:

- the **2018 Travel Habits Survey (THS)** — detailed, behaviorally rich, but a small
  sample (5,108 households), and
- a **cellular-derived OD matrix** — population-scale coverage, but coarser zones and
  blind to trips that do not move a phone between cell areas.

The guiding idea of the first generation of this work was to treat cellular as the
*prior* spatial distribution and the survey as *evidence*, combined at the scale where
each is reliable. The tests of steps 12–14 and the external review of 21 September 2026
(`docs/Nofit_Demand_Methodology_Review.md`) changed that: the current base is survey-only,
with the bus layer calibrated to ticketing, and the cellular hybrids are historical.

---

## 0. Status, authoritative baseline and lineage (21 September 2026)

**Authoritative base-year product:** the survey-only 2022 layer set
`Output/ths2017/three_mode_2022/{car,bus,taxi,rail}_2022_*.csv` (steps 15–16), delivered as
**car / transit / total** TAZ matrices in `Output/final_2022/` (step 22, §6t). It is a
*person-journey* product for residents with both trip ends in the study area, AM 06:00–09:00,
representative weekday, at 2022 vintage (bus cells that took RavKav volumes at May 2022;
everything else grown from 2018 by demographic factors, rail by the national ridership
series). It is fit for exploratory corridor screening with the caveats of §8; it is not
yet an externally validated estimate of corridor demand, and its corridor profiles are
potential movements — three-hour totals (§6o) and peak-departure-hour values (§6r) —
not passenger loads. The plain-language account of this base, its tests and its
corridor results is `reports/Survey_Matrices_Car_Bus_Rail_Report.docx` (revision 2.1,
21 September 2026); the older reports under `reports/historical/` carry dated status
notes saying which of their conclusions are overtaken.

**Conclusions for the corridor, as the base stands (21 September 2026).**

| Quantity (2022 layers, 06:00–09:00 unless stated) | Value | Where |
|---|---|---|
| Corridor-to-corridor trips: car / bus / taxi-type / rail | 72,331 / 9,366 / 3,812 / 0 | §6n |
| Bus share of corridor-to-corridor trips (bus + rail over all layers) | 11 % | §6n |
| Bus base 2018 under the segmented coverage rule (survey / ticketing / binary rule) | 126,117 (116,083 / 92,713 / 110,654); threshold sweep 117,500–131,700 | §6m |
| Busiest transit link, three hours (bus + rail) | 1,661 towards Nazareth (Ein Hayam – Bat Galim); 1,650 towards Tirat Carmel (Neot Peres – Neve David) | §6o |
| Ticketing-based transit profile against it | ≈ 0.63–1.05 × towards Nazareth; ≈ 2 × (Haifa segment) to 3 × (Nazareth end) towards Tirat Carmel — frame and allocation, not coverage | §6p |
| Peak hour (departures) | 07:00–08:00 for every layer; corridor car towards Nazareth 07:15–08:15 | §6r |
| Share of the three hours in the peak hour (PHF₃ₕ) | car 0.62 (corridor by direction 0.66 / 0.63), bus 0.59, taxi-type 0.58 — ≈ 1.8 × an average hour | §6r |
| Within-hour factor (PHF₆₀) | car 0.69, bus 0.75 | §6r |
| Busiest transit link, peak hour | 981 towards Nazareth, 974 towards Tirat Carmel (average hour ≈ 550); ± 15 % on the bus factor basis | §6r |
| Busiest link, all layers, peak hour | 4,609 towards Nazareth (Ein Hayam – Bat Galim); 4,205 towards Tirat Carmel (Bat Galim – Kiryat Eliezer) | §6r |
| Car vs transit destination structure (survey PCA, superzones) | overlap 0.75 (0.83 on well-sampled origins) against transit repeatability 0.81 (0.86): the same dominant structure | §6s |
| … where transit differs from car | less local (self-containment 0.45 vs 0.62), share moved to the Haifa core (+2–3 points; common direction p = 0.04 at superzones, p = 0.002 with TAZ origins) | §6s |
| … by resolution | corridor areas: at transit's noise floor (0.57 vs 0.65); TAZ × superzone: 0.75 vs 0.89 — clearly different; TAZ × TAZ: 0.27 vs 0.55 — only the coarse geography shared | §6s |
| V2 aggregation (25 areas, 174 TAZs): trips with both ends in the areas — car / bus / taxi-type / rail | 156,944 / 18,788 / 8,323 / 51 | §6v |
| Busiest transit link per route, three hours (up / down) | T1 1,379 / 1,489; T2 1,391 / 1,629; T3 1,437 / 1,410 — all on the Haifa trunk (Ein Hayam – Bat Galim up, Matam – Hof Carmel down) | §6v |
| Tree network (all 25 areas on their unique path): Bazan-Hutsot – Tsomet Kiryat Ata towards Haifa | 16,231 all layers / 2,898 transit in three hours; 8,792 / 1,710 in the peak hour | §6v, §6y |
| Peak-hour factors on the V2 routes (car, by direction): up / down | T1 0.626 / 0.578, T2 0.619 / 0.569, T3 0.652 / 0.569, network 0.556 / 0.522 (step 20: 0.661 / 0.626); bus and taxi-type stay at 0.590 / 0.580 | §6y |
| Calibrated survey vs ticketing transit on the V2 routes (Haifa segment, survey ÷ ticketing) | up 0.78–0.83 per route; down T2 0.92, T3 0.73, T1 0.66, network 0.63; Nazareth origin 1,070 vs 2,402 | §6z |
| Car vs transit PCA on the V2 areas | 14 origins (≥ 10 sampled transit trips): overlap 0.55 vs transit repeatability 0.76 (car 0.79); 7 origins (≥ 20): 0.76 vs 0.80 — sample-limited; the superzone / TAZ × superzone evidence stands | §6s |
| Busiest single link of any route | Kiryat Haim – Kiryat Bialik Center (T2), 10,144 towards Haifa, transit share 10 % | §6v |
| LRT `hf_lrt_3`: 24 stations, 18.74 km S01 → S24, mean spacing 815 m | end to end **40.7 min underground (27.6 km/h) / 65.8 min ground (17.1 km/h)** — calibrated function transferred through the Red Line's actual spacing (revision 2); section form 45.1 / 55.0; the revision-1 500 m reading 73.5 / 89.7 superseded; underground −38 % | §6w |
| Generalized-cost first fill on the trunk pairs (trip-weighted): car door-to-door / bus fastest-path IVT / LRT IVT underground, ground | 14.5 / 12.5 / 20.6, 25.1 min; survey bus door-to-door 27.1 min (2.3 × the network IVT) | §6x |
| Bus level of service from the GTFS (Tuesday 2 June 2026): TAZs with peak-hour service / best-line grade A–B / with a Metronit stop | 719 of 781 / 454 / 60 (41 in the V2 areas, 20 of 25 areas) | §6aa |
| Direct-service skim, trunk pairs: bus scheduled IVT, combined headway; Metronit | 13.3 min at 1.7 min (82 of 90 pairs); 10.0 min at 6 min (72 pairs) | §6aa |
| Generalized cost after the GTFS skims and the corrected LRT function, trunk pairs, trip-weighted: car / bus (observed running times) / Metronit / LRT underground, ground | 14.5 / 27.0 / 22.1 (on its pairs) / 43.9, 51.1 — LRT in-vehicle time (11.7 min) 3 min below the observed bus (14.4); the LRT dearer than the bus on every trunk pair by 4–31 generalized minutes, 18 of them station access (13.6 vs 4.7 min walk) | §6x addenda |
| GTFS-based bus door-to-door (observed running time + walk + wait) against the survey's reported time, same pairs | 24.3 vs 31.8 min (× 1.3): a fixed ≈ 7-minute overhead, 1.9 × under 3 km, 1.1–1.5 × at 3–20 km, 0.8 × beyond | §6x addenda 2–3 |
| Observed bus in-vehicle time (trips routed over the May 2026 link speeds) ÷ scheduled | per trip 1.09 (Metronit 0.87); hops < 500 m 1.00, > 2 km 1.42 — the link speeds include dwell, the long arterial hops run slower than the timetable; trunk pairs 12.7 vs 10.4 min demand-weighted | §6ab |
| Complete skims, trunk pairs, trip-weighted GC (generalized minutes): car / bus / Metronit (its 72 pairs) / LRT underground / LRT ground | 14.7 / 27.8 / 25.6 / 44.0 / 51.8 | §6ac |
| Complete skims, all 600 off-diagonal pairs, trip-weighted GC: car / bus / Metronit (278 pairs, 64 % of transit trips) / LRT underground / LRT ground | 20.2 / 38.5 / 31.0 / 64.6 / 70.0 (LRT off the line by feeder, Metronit feeder with a free transfer on 378 of 510 pairs) | §6ac |
| 2022 AM off-diagonal trips, 25 areas: car / transit (bus + rail) / taxi | 56,445 / 11,664 (share 0.171) / 6,982 | §6ac |
| Cost sensitivity λ from the 2022 cross-section (binary logit, transit share vs `GC_bus − GC_car`, 573 pairs / 67,700 trips) | wrong sign (−0.011, ρ² 0.003); with distance-band constants +0.0002 (ρ² 0.036) — not identifiable; λ assumed 0.03 (range 0.02–0.05), λ_T = 2λ | §6ac |
| LRT capture, central case (λ 0.03, λ_T 0.06, LRT premium 5, free LRT–Metronit transfer), 06:00–09:00 within the 25 areas: underground / ground trips (of which from bus / from car) | 3,332 (3,037 / 295) / 2,544 (2,375 / 169); λ range 2,357–4,855 (ug), 1,472–4,277 (ground); premium 0 / 10: 2,658 / 4,122 (ug) | §6ac |
| LRT trunk-link loads, three hours, central underground vs today's bus | 79–995 per link-direction against bus 200–2,030 (a third to 45 %; 84 % on Namal-Giborim→Hamifrats up); ground 44–595; peak hour ug 47–588 | §6ac |

What these support: relative questions — ranking alignments and segments, sizing the
market between line areas, locating the demand, and the design-hour scaling of that
market (1.8 × an average hour). They also settle one method question: the transit
market cannot be read off the car pattern by scaling. Transit trips from the outer
superzones are markedly more Haifa-bound and less local than car trips from the same
places (§6s), so a transit-specific destination pattern — as in the step-15 calibration
and the OnBoard pattern below superzone level — is required, and any cell-wise
mode-share shortcut on an all-mode matrix at TAZ level would mis-place transit demand. What they do not support: passenger loads, capacity or
frequency decisions, ridership forecasts, or appraisal — the volumes are unvalidated
externally, the bus total depends on an assumed coverage threshold, the two transit
frames disagree by 2–3 × at the Nazareth end in one direction, TAZ detail is a
purpose-blind allocation, and the peak-hour values are departure-hour potential
movements between line areas with no station access, route choice or off-line trips.
The forecast branch is rebuilt on this base by step 23 (§6u, `docs/FORECAST_METHODOLOGY_2040_2050.md`);
the four scenario sets are produced once the LFS scenario files are pulled.

**Update, 22 September 2026 (steps 24–26).** Three inputs were added — the **V2 corridor
aggregation** (`Input/Corridor_TAZ_Agg_V2.xlsx`: 25 areas, 174 TAZs, three route orders
T1 Nazareth / T2 Krayot / T3 Kiryat Yam sharing a twelve-area trunk), the **planned LRT
geometry** (`Input/GeneralHalufa/`: alignment `hf_lrt_3` and 46 platform points) and the
**May 2026 bus-speed street network** (`Input/BusSpeedData/`, LFS) — together with a
calibrated stop-to-stop travel-time function
(`docs/Transit_Travel_Time_Calibration_Report_Operator22.md`). Step 24 (§6v) re-analyses
the corridor potential movements on the V2 areas per route and as a tree network; step 25
(§6w) turns the geometry into a 24-station table and station-to-station times for an
all-underground and an all-ground scenario; step 26 (§6x) inventories the
generalized-cost components on the 25 areas, fills the skims that the data supports (car
from the survey, bus from the speed network, LRT from step 25) and lists the gaps
(`Output/gc/gc_data_inventory.csv`, task list section E). Step 29 (§6aa) adds the bus and Metronit level of service per TAZ from the national GTFS
(feed of 22 May 2026) and the direct-service skim that feeds the bus components of §6x; step 30
(§6ab) routes the same trips over the measured May 2026 link speeds for an observed in-vehicle
time, which §6x now uses. Step 31 (§6ac) turns these components into one complete skim set
per mode (car, bus, Metronit, LRT underground / ground, the LRT extended to the fifteen
off-line areas by a feeder composite — bus, or Metronit with a free transfer) and compares them with the observed 2022 flows: a
logit fit of the cross-section fails to identify the cost sensitivity λ (wrong sign), so λ
is assumed (0.03, range 0.02–0.05), with an LRT premium of 5 generalized minutes and free
LRT–Metronit transfers (assumptions of 22 September 2026), and used to pivot an
incremental-logit capture of LRT trips from bus and car, loaded onto the trunk links against
today's bus movements. The
plain-language account of steps
24–28 and of what every matrix product can be used for is
`reports/V2_Corridor_LRT_Times_and_GC_Inputs_Report.docx` (revision 1.3, 22 September 2026).
Headline additions to the table below: on the tree network the trunk link Bazan-Hutsot – Tsomet Kiryat Ata carries
16,231 potential movements towards Haifa in three hours (2,898 transit; peak hour
8,792 / 1,710 with the route-specific factors of step 27); the Krayot branch link Kiryat Haim – Kiryat Bialik Center is the busiest
single link at 10,144; the calibrated LRT function, once transferred through the Red Line's actual station
spacing (revision 2 of step 25 — the report's 500 m assumption had halved the underground
speed), gives 40.7 min (underground, 27.6 km/h) / 65.8 min (ground, 17.1 km/h) end to end;
on the trunk pairs the LRT in-vehicle time (11.7 min underground) is level with the bus
timetable and the LRT's remaining disadvantage in generalized cost is station access.

Every published product, what it was built from, and its status:

| Product (`Output/…`) | Built by | Base / inputs | Geography | Modes | Vintage | Status |
|---|---|---|---|---|---|---|
| **`final_2022/{car,transit,total}_2022_taz.csv`**, `*_incl_taxi_*`, `final_2022_long.csv.gz`, `MANIFEST.csv` | step 22 | the step-16 layers, summed | 778 TAZ | car; transit = bus + rail; total | 2022 | **current — the deliverable set** |
| `ths2017/three_mode_2022/{car,bus,taxi,rail}_2022_{taz,sz,area}.csv`, `all_modes_2022_taz.csv` | step 16 | `ths2017/two_mode/` + zonal 2020/2025 growth | 778 TAZ / 36 SZ / 28 areas | car; bus (Public Bus + Matronit); taxi-type (codes 5, 8); rail (survey door-to-door) | 2022 | **current** |
| `ths2017/three_mode_2022/rail_station_smartcard_2022_taz.csv` | step 16 | `train/train_od_taz_6_9.csv` × 0.793 | 19 station TAZs | rail, station-to-station, all riders | 2022 | current (separate frame) |
| `ths2017/three_mode_2022/corridor_link_flows_{total,transit,taxi}_2022.csv`, `corridor_profile_*.csv` | steps 17–18 | the row above | 18 line areas | as above | 2022 | current — three-hour potential movements |
| `ths2017/three_mode_2022/peak_hour_factors*.csv`, `corridor_link_flows_peak_hour_2022.csv`, `peak_hour_sensitivity.csv` | step 20 | survey departure times × the row above | 18 line areas | car, bus, taxi-type, rail | 2022 | current — peak-departure-hour potential movements |
| `ths2017/two_mode/car_*`, `bus_calibrated_*`, `transit_*`, `taxi_survey_*`, `rail_survey_*`, calibration tables | step 15 | `Input/trips_ths_2017.xlsx`, `bus/bus_od_taz_new.csv`, `bus/bus_boardings_alightings_taz.csv`, zonal 2020 | 778 / 36 / 28 | car; bus; taxi-type; rail | 2018 (bus cells with RavKav volumes: 2022) | current intermediate |
| `bus/bus_od_taz_avg.csv`, `bus/bus_boardings_alightings_taz.csv` | step 8 | RavKav May 2022 Tuesdays (LFS) | 722–730 TAZ | bus journeys (first boarding → final alighting), all riders | 2022 | current input |
| `bus/bus_od_taz_new.csv`, `bus_od_area_new*.csv` | step 9 | step 8 × OnBoard probabilities | 722 TAZ / 28 areas | bus; **unit of the OnBoard rows (leg or journey) unconfirmed** | 2022 | current input, open question |
| `train/train_od_taz_6_9.csv`, `train_od_area.csv` | step 10 | 2019 smartcards (LFS) | 19 stations | rail, station pairs | 2019 | current input |
| `ths2017/study_taz/hybrid_taz_trips_balanced.csv`, `hybrid_taz_prob_balanced.csv` | step 19 | `hybrid_taz_trips.csv` rebalanced to `hybrid_sz_trips.csv` blocks | 778 | all modes | 2018 | historical branch, corrected |
| `ths2017/study_taz/hybrid_*`, `submatrices/*` | step 6 | trips file × cellular (LFS), replicated mapping | 778 / 36 / 25 / 28 | all modes | 2018 | **historical** — superzone OD blocks not reproduced (§6q) |
| `ths2017/study_taz/matrix_avg_*`, `ths2017/matrix_*` | step 5 | trips file, cellular allocation shares | 778 / native | by mode | 2018 | current survey source (cellular used only for the 1250 → TAZ split) |
| `historical/ths2018/*` (`hybrid_*`, `prob_*`, `matrix_*`, `submatrices/*`, `trip_generation_*`) | steps 1–4 | activities file × cellular, replicated mapping | 778 / 36 / 25 | all modes | 2018 | **historical** |
| `ths2017/tests/*` | steps 12–14, 19, 21 | the matrices above; step 21: survey car vs transit profiles | various | — | — | diagnostics (regression record) |
| `transit/transit_od_area.csv`, `all_adjusted_area*.csv`, `mode_share_area*.csv`, `car_other_area_2022.csv` | steps 10–11 | survey ALL − TRANSIT − RAIL (cellular-allocated) + RavKav × OnBoard bus + station train | 25 areas | mixed frames (residents' car / other + all-rider boardings) | mixed → 2022 | **historical composite** |
| `forecast_taz/{BU,HS}_{2040,2050}/*` (after the LFS scenario files are pulled; `forecast_taz/dry_run/` here) | step 23 | `final_2022/` layers × scenario zonal files | 778 TAZ / 36 SZ / 28 areas | car; transit; taxi-type; total | 2040 / 2050 | **current method — demographic reference; scenario sets pending the LFS run** |
| `forecast/all_modes_area_*`, `share_*`, `nobuild_*`, `lrt_market_*`, `lrt_alignment_*` | forecast notebooks | `transit/all_adjusted_area_2022.csv` | 25 areas | composite | 2040 / 2050 | **historical** — superseded by step 23 |
| `demographics/*` | scenario comparison | zonal forecast files (LFS) | 28 areas | — | 2040 / 2050 | current input analysis |
| `corridor_v2/*` | step 24 | the step-16 TAZ layers × `Input/Corridor_TAZ_Agg_V2.xlsx`; step-20 peak factors | 25 V2 areas, 3 routes + tree network | car; bus; taxi-type; rail; transit; total | 2022 | **current** — three-hour and peak-hour potential movements |
| `lrt_v2/*` | step 25 | `Input/GeneralHalufa/` geometry × the calibrated travel-time function | 24 stations; 10 trunk areas | LRT in-vehicle time, two scenarios × two forms | planned line | **current** — trunk only (no branches) |
| `gc/*` | step 26 | survey car times, `Input/BusSpeedData/` (LFS), `lrt_v2/` | 25 V2 areas | car; bus; LRT (2 scenarios) — generalized-cost components with status | 2017/18 (car), May 2026 (bus), planned (LRT) | **current** — partial fill; money components missing |
| `skims/*` | step 31 | `gc/*` components, feeder composite (bus or Metronit) for the LRT, 2022 corridor flows | 25 V2 areas, 9 trunk links | car; bus; Metronit; LRT (2 scenarios) — complete skims, logit calibration, LRT capture scenarios, trunk-link loads | 2022 (flows), May 2026 (bus), planned (LRT) | **current** — money components still missing; λ assumed |

The 25 GS zones (`Input/TAZ_GSnew.csv`) and the 25 retained research areas of the
forecast tables are different geographies with the same matrix dimension; files are
labelled `_gs` and `_area` respectively and must not be joined on position.

**Response to the review, in one place.** Confirmed and acted on: the forecast branch
does not consume the current base (lineage above; rebuild is task D2); the TAZ hybrid
does not reproduce its superzone OD blocks (§6q: tested, rebalanced); the coverage rule is
now segmented (§6m); taxi-type is out of the bus layer (§6n); corridor values are
labelled three-hour potential movements (§6o–§6p) and, since step 20, given in
peak-departure-hour terms with sampling ranges (§6r); README diagram and reproduction
order describe the current chain; the final report (revision 2.1) describes all of it. Confirmed and still open (§8, tasks): the OnBoard unit and
bus-to-rail duplication; the replicated cellular mapping inside the hybrids' TAZ
structure; the k = 50 share smoothing acting on expanded volumes; purpose-blind
allocation; external sectors and the three dropped areas; the vintage ledger; external
validation against counts.

---

## 1. Input data (`Input/Matrices/`)

| File | Content | Key facts |
|---|---|---|
| `ACTIVITIES_DEC18_corrected.csv` | THS 2018 activity diary: one row per activity per individual per survey day | 172,529 rows; 5,108 households; two survey days per household (`ACT_DAY` = 10: 86,978 rows, `ACT_DAY` = 20: 85,465; a residue of 86 rows on days 11/22 is ignored). Columns include `HHID`, `INDIVID`, `ACT_DAY`, `ACT_ID`, `StartTime`, `EndTime`, `mainActivity`, `taz`, `tourID` |
| `households_with_weights.csv` | Household expansion weights | 5,108 rows, one per `HHID` — exactly matching the activities file (no missing, no duplicates). Columns: `HHID`, `TAZ`, `SuperZone`, `wf` (original weight), `wf_new` (revised weight; mean ≈ 159, range 5–350). **`wf_new` is the weight used throughout.** |
| `AvgDayHourlyTrips201819_1270_weekday_v1.csv` | Cellular OD trips, average weekday 2018–19, hourly (`h0`–`h23`), national 1270-zone system | Only the AM-peak hours `h6`, `h7`, `h8` are used |
| `1270_02_09_2021_TAZ_North_keys.csv` | Zone correspondence table (windows-1255 encoded) | Maps the national 1270-zone system (`TAZ_1270`) to the 778 study TAZs (`TAZ_NUMBER`) and to 36 superzones (`SZ_NEW`). 400 national zones cover the study area; one national zone contains up to 8 study TAZs (mean ≈ 2) |
| `../TAZ_GSnew.csv` (in `Input/`) | TAZ → GS zoning | 781 TAZs → 25 GS zones; covers every study TAZ including 105 |
| `../taz_keys_from_shapefile.csv` (in `Input/`, regular git) | Substitute for the keys table when only its LFS pointer is present | Built from `Input/TAZ_North/TAZ_North.shp` (`TAZ_NUMBER`, `SUPERZONE`, `ARZI_1270`): the same 778 TAZs, `SZ_NEW` identical for all of them, `TAZ_1270` identical except TAZ 3602, which the keys table places alone in zone 101000 (applied as an override). Verified: identical 396-zone set to `ths2017/tests/geh_scale_audit_1250.csv`, identical sibling partition to the committed cellular probability matrix, identical study-area trip filter (1,197 sampled / 116,473 weighted excluded). Steps 15, 16 and 18 fall back to it automatically |
| `../sz_localities.csv` (in `Input/`) | Two main localities per superzone | Extracted from the keys table's `CITY` field (population-weighted) for labelling only |
| `../trips_ths_2017.xlsx` (in `Input/`) | THS trips file: one row per activity per person per survey day | 146,394 rows, 16,401 persons (same panel as the activities file), `SurveyDay` 1/2; `placeno` orders activities per `PerID3`, `actTaz` locates them, `Dep_h` is the hour of departing the activity, `mode` is pre-aggregated (CAR/TRANSIT/RAIL/OTHER, `IRR` = first activity), `new_wf` carries the weight; `TrvlTime` / `TrvlDist` are the reported door-to-door minutes and km (used by step 26) |
| `../Corridor_TAZ_Agg_V2.xlsx` (in `Input/`, added 22 Sep 2026) | The V2 corridor aggregation | Sheet `AreaCodes`: 25 areas (`AggCode` 201–217 trunk + Nazareth branch, 101–104 Krayot branch, 301–304 Kiryat Yam branch) with three route orders `Order_T1` / `Order_T2` / `Order_T3` (0 = not on the route); sheet `TazAgg`: 174 TAZ → `AggCode` pairs, all present in the 778-TAZ matrices, none duplicated. TAZ 1509 (LRT station S13) is not listed |
| `../GeneralHalufa/hf_lrt_3.shp`, `station_hf_lrt_3.geojson` (in `Input/`, added 22 Sep 2026) | Planned LRT alignment and stations | One WGS 84 polyline of 18.94 km from Hamifrats to Tirat Carmel; 46 platform points (`halufa` attribute 1 / 2 / 999 / null — all points lie within 80 m of the line and are used) forming 24 stations. Projected to Israel TM Grid (EPSG:2039) for all distances |
| `../GTFS/israel-public-transportation.zip` (in `Input/`, LFS, added 22 Sep 2026; feed of 22 May 2026) | The Ministry of Transport's national GTFS feed (https://gtfs.mot.gov.il/gtfsfiles/) | Standard GTFS (`stops`, `routes`, `trips`, `stop_times`, `calendar`, `agency` …); `route_desc` carries the route code (מק"ט), direction and alternative as `code-dir-alt`; the Metronit BRT lines are codes 83001–83005. Used by step 29 for the bus level of service per TAZ and the direct-service skim between the V2 areas; the notebook dry-runs on a synthetic feed while only the LFS pointer is present. **Since 22 Sep 2026 every file directly under `Input/` is on LFS** (`Input/*` in `.gitattributes`): `git lfs pull --include="Input/*.xlsx,Input/*.csv"` is now required before any notebook runs |
| `../BusSpeedData/Streets/Streets.shp`, `std_202605.csv` (in `Input/`, CSV in LFS, added 22 Sep 2026) | Bus link speeds, May 2026 | 161,534 national street links (Israel TM Grid; `USERID`, `DIR` = 1 with / −1 against / 0 both directions); 157,618 speed records joined on `USERID` (99.9 % match), 336 columns `d_{weekday}_h_{hour}_{AB,BA}` in km/h with 0 = no bus observation. `Readme.txt`: weekday 3, 07:00–08:00 = `d_3_h_7_AB` / `d_3_h_7_BA`. 54,507 links (5,632 km) fall in the study area, 48,092 with a speed |

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
caveat. **The superzone OD blocks are not reproduced**: the block-wise correction is
followed by a per-row normalization on each fine row's own mix of corrected cells, so
rows with a strong intra-superzone share give part of the correction back. Step 19
(§6q) measures this — for the primary trips-file hybrid, 55 of the 627 superzone blocks
above 100 trips deviate by more than 10 % and the worst by 49 % — and publishes a
rebalanced matrix. Within a superzone, the origin split by cellular outflow shares also
gives a national zone weight in proportion to its number of child TAZs (the replicated
mapping of §2), which the rebalancing does not repair. A 119×119 sub-area extraction (same zone list, order and layout as
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
`bus_boardings_alightings_taz.csv` (per-TAZ averages).

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

Executes `docs/TRANSIT_DEMAND_PLAN.md`. **Train**: `Input/Matrices/Train_mtx_table.csv`
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
bus part calibrated against the ticketing / on-board products of steps 8–9. OTHER (walk,
bicycle, …; 645k trips) is excluded from the two-mode base and reported. From step 16 on,
taxi-type is a separate layer, not part of bus.

**Zone conversion without cellular.** `actTaz` → `TAZ_1250` → study TAZ, the one-to-many
last link split by 2020 **population** (origins) and **employment** (destinations) from
`Input/Zonal_2020.csv` (fallback to the other variable, then uniform; 396 zones: 331 /
47 / 18 on the origin side, 378 / 0 / 18 on the destination side). Superzones and the 28
sub-areas follow from the TAZ matrices. Zone keys: the LFS table or its committed
substitute (§1).

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
   the same households repeating the same commutes; it is reported but not used. The
   dominant superzone of a 1250-zone (for the counts n_A, m_B) is the one with the
   largest 2020 population among its child TAZs (the earlier TAZ-count rule broke ties
   by file order).
2. *Volumes, per origin superzone × destination segment* — three segments per origin:
   **local** (destination in the same superzone), **inter-superzone corridor-bound**
   (destination in an LRT-corridor superzone) and **inter-superzone other**. A segment
   with at least 5 sampled survey trips is judged on its own RavKav / survey ratio:
   **below 0.5 the survey volume is kept** (coverage guard), otherwise the segment takes
   the RavKav volume; thinner segments inherit the origin-wide decision (the first
   version's binary rule). Within a segment the blended pattern `P*` distributes the
   volume. Result: 28 guarded origin × segment cells — 17 local (the seven originally
   guarded superzones Nazareth / Kafr Kanna, Shefa-'Amr / Tamra, Sakhnin, Ma'alot / Beit
   Jann, Safed, Beit She'an, Daliyat al-Karmel / Isfiya, plus Haifa 14 and 16 at ratios
   0.44–0.48, Tiberias 0.05, Afula, Migdal HaEmek, Nof HaGalil, Karmiel, Zichron, Kiryat
   Shmona, Pardes Hanna, Hadera), 5 corridor-bound, 6 other. The Nazareth superzone's
   corridor-bound segment (ratio 0.74) is *calibrated* to ticketing; its local segment
   (0.08) and its other inter-superzone segment (0.13) keep the survey.
3. *TAZ detail* — origin split within a superzone = λ-blend of survey home-based
   departure shares and RavKav boarding shares; destination split = μ-blend of survey
   arrival shares and OnBoard alighting shares (`μ_B = m_B / (m_B + k)`).

**Results.** Bus 116,083 (survey 2018) → **126,117** with the segmented rule (binary
guard variant 110,654; all-RavKav variant 92,713); local segment 62,090 → 60,200 (ticketing
23,277), inter-superzone 53,992 → 65,917 (ticketing 69,436). Transit total (bus + taxi +
rail) 149,492; transit share of the car + transit base 9.8 % → 10.4 % (corridor-to-corridor
12.7 % → 16.2 %). Threshold sweep: bus total 117,515 at 0.3, 122,160 at 0.4, 126,117 at
0.5, 130,639 at 0.6, 131,650 at 0.7. Against the RavKav × OnBoard matrix the segmented
bus scores cosine 0.601 at superzone level (survey 0.589, binary variant 0.658,
all-RavKav 0.735) and 0.872 on the 28 sub-areas (survey 0.745, binary 0.882), with 64 %
of sub-area flow within GEH 5 (survey 30 %; day-to-day 67 %); destination totals, never
imposed, reach cosine 0.86 with OnBoard-informed alightings.

**The rule is asymmetric and the total shows it.** It adopts ticketing volumes wherever
ticketing records at least half of the survey's trips — usually more than the survey,
at transfer hubs up to 3 × — and keeps survey volumes wherever it records less than half.
The bus base therefore sits above both sources. A ratio below 0.5 cannot by itself say
whether ticketing misses trips (operators outside the extract, cash fares, un-geocoded
stops) or the survey expansion overstates short local bus travel (review §8), so the
threshold is a stated assumption and the variants are published beside the primary.
The raw extract records ≈ 3,500 AM boarding legs in the Nazareth superzone against
12,400 survey-expanded bus trips; the files carry route ids but no operator field, so
which operators the extract covers, and whether cash / unvalidated boardings are in it,
is a question for the provider.

**Outputs** (`Output/ths2017/two_mode/`): `car_{taz,sz,area}.csv`,
`transit_{taz,sz,area}.csv` (calibrated), `transit_survey_*.csv`,
`bus_calibrated_{taz,sz,area}.csv`, `bus_survey_*`, `taxi_survey_taz.csv`,
`rail_survey_taz.csv`, variants `bus_calibrated_binary_guard_{taz,sz}.csv`,
`bus_calibrated_all_ravkav_{taz,sz}.csv`, `bus_calibrated_uniform_factor_taz.csv`;
calibration tables `bus_calibration_cv.csv`, `bus_calibration_lambda_sz.csv`,
`bus_calibration_factors_sz.csv` (origin-wide ratios, the binary rule),
**`bus_calibration_factors_segments.csv`** (the segmented rule: per origin × segment
survey and RavKav trips, ratio, sampled count, basis, guarded flag, factor),
`bus_calibration_threshold_sensitivity.csv`, `bus_pattern_sz_prob.csv`,
`bus_calibration_validation.csv`, `bus_calibration_destinations_sz.csv`;
`mode_share_sz.csv`, `mode_share_corridor_classes.csv`; figures `two_mode_bus_cv.png`,
`two_mode_transit_share.png`.

**Caveats.** Frames (boarding-stop vs doorstep origins, non-residents) as in
`docs/TRANSIT_DEMAND_PLAN.md`; vintage mix (RavKav-volume segments at May 2022, guarded
segments, car, taxi-type and rail at 2018); below the 1250-zone the survey's TAZ detail
is a population / employment split, not observation; the OnBoard prior's unit (boarding
leg or journey) is unconfirmed (§8).


## 6n. Step 16 — 2022-base layers: car, bus, taxi-type, rail (`THS_2017_three_mode_2022.ipynb`)

**Purpose.** Moves the survey-only two-mode matrix (step 15) to the **2022 base** with
the vintage conventions of step 11, at TAZ level, and splits it into four layers: **car**,
**bus** (calibrated Public Bus + Matronit only), **taxi-type** (survey codes 5 / 8, its
own layer since the review — the codes' exact meaning is unconfirmed and hired or shared
taxis need not behave like scheduled bus) and **rail**. The output folder keeps its
historical name.

**Method.** Growth factors `g = (X_2025 / X_2020)^(4/5)` per TAZ from
`Input/Zonal_2020.csv` / `Input/Zonal_BU_2025.csv`, used where the 2020 base is ≥ 500
(population for origins: 606 TAZs; employment for destinations: 506), pure-employment
zones taking the employment factor on the origin side (72), and all smaller zones their
superzone's factor (100 origins / 272 destinations). Car: Furness to the grown margins
(one grand total from the origin side). Bus: cells whose origin × segment took RavKav
volumes are the 2022 anchor and untouched; the guarded cells × their TAZ origin factor.
Taxi-type: Furnessed like car. Rail: survey rail × 54.7 / 69.0 = 0.793 (national
heavy-rail ridership 2019 → 2022; 2018 taken at the 2019 level); the 2019 smartcard
station-to-station matrix scaled the same way is saved beside it.

**Results.**

| | 2018 base | 2022 base |
|---|---|---|
| Car | 1,283,589 | 1,353,798 (+5.5 %) |
| Bus (calibrated, excl. taxi) | 126,117 | 129,653 (anchored cells 69,066 unchanged; guarded cells 57,051 → 60,587) |
| Taxi-type | 18,266 | 19,359 |
| Rail (survey, door-to-door) | 5,109 | 4,050 |
| Bus / taxi / rail share, all | 8.8 % / 1.3 % / 0.4 % | 8.6 % / 1.3 % / 0.3 % |
| Bus share, corridor → corridor | 11.7 % | 11.0 % |

Origin factors: median 1.050, car-trip-weighted 1.055 (largest ≈ 1.28 in Pardes
Hanna-Karkur and Tirat Carmel TAZs); destination factors: weighted 1.135 before the
grand-total rescaling. Corridor-bound car trips fall 5.8 % while every other class grows
because the BU-2025 forecast puts corridor employment growth below the regional average
— a property of the demographic scenario, not of the survey. The station-based rail
alternative carries 763 trips with both stations in the sub-area against 104
door-to-door survey rail trips there.

**Outputs** (`Output/ths2017/three_mode_2022/`): `{car,bus,taxi,rail}_2022_{taz,sz,area}.csv`,
`all_modes_2022_taz.csv`, `rail_station_smartcard_2022_taz.csv`,
`growth_factors_taz_2018_2022.csv`, `summary_2018_2022.csv`, `summary_sz_2018_2022.csv`;
figure `three_mode_2022.png`. (The first version's `bus_2022_excl_taxi_taz.csv` and
`all_three_modes_2022_taz.csv` are removed; their content is `bus_2022_taz.csv` and
`all_modes_2022_taz.csv`.)


## 6o. Step 17 — Corridor profile of potential movements, survey-only 2022 layers (`Corridor_flow_profile_survey_2022.ipynb`)

**Method.** Same construction as the profile of the leveled hybrid-based matrix
(commit 7d07a91): the 18 corridor areas of the line sequence in `AggAreaCode` order
(Adi, Alon Hagalil and Tzipori left out as before — to be brought back with flagged
uncertainty, task B2), every OD pair with both ends on the line assigned to each link
between them in its direction of travel, on the step-16 area matrices — **total** = car +
bus + taxi + rail, **transit** = bus + rail, and **taxi-type** on its own. **Every value
is a three-hour total of potential movements between line areas**, not a passenger load:
it says nothing about station access, route choice against parallel services, peaking
within the three hours, or trips with one end off the line.

**Results.** Total: corridor-internal demand 71,113 trips (earlier matrix 101,004 — it
included the walk / other modes and a different car source); peak link Bat Galim –
Kiryat Eliezer, 6,852 towards Nazareth / 6,847 towards Tirat Carmel (earlier 7,671 /
7,576); the Haifa-side profile matches the earlier one closely, the Krayot-to-Nazareth
segment carries less in both directions. Transit (bus + rail): 8,622 corridor-internal
trips, peak link Ein Hayam – Bat Galim 1,661 towards Nazareth / 1,650 Neot Peres – Neve
David towards Tirat Carmel; taxi-type a further 3,606 corridor-internal trips, up to
1,415 on Ein Hayam – Bat Galim. Transit is 16–37 % of link flow on the Haifa segment.

**Outputs.** `Output/ths2017/three_mode_2022/corridor_link_flows_{total,transit,taxi}_2022.csv`,
`corridor_link_flows_comparison_2022.csv` (all profiles, the earlier ones and the
link-level transit share); figures `corridor_flow_profile_{total,transit}_survey2022.png`.


## 6p. Step 18 — Corridor transit profiles: calibrated survey vs ticketing (`Corridor_profile_hybrid_vs_ticketing.ipynb`)

**Question.** The step-17 transit profile (calibrated survey bus + survey rail) against
the step-11 ticketing profile (RavKav × OnBoard bus + station train), link by link and
per direction — like-for-like, taxi-type shown separately — with the calibration's
intermediate steps (raw 2018 survey bus, all-RavKav variant), the area pairs that drive
the differences, the transit share of link flow in both matrix sets, and a
local-vs-intercity split of the ticketing coverage in the guarded superzones.

**Results.** Towards Nazareth (1 → 23) the calibrated-survey transit sits at 0.63–1.05 ×
the ticketing transit along the Haifa segment (0.87 over the segment; raw survey 25–40 %
lower); the earlier 1.5 × was the taxi-type layer, now separate. Towards Tirat Carmel
(23 → 1) the ticketing profile is still ≈ 2 × from Bat Galim to Kiryat Bialik South and
≈ 3 × at the Nazareth end, driven by journeys ticketed from the Nazareth Area (1,363 vs
430 survey-based; −9,900 link-trips), Hamifrats (782 vs 561) and Neve Yosef (741 vs 296)
into Haifa's western districts. **The segmented coverage rule did not close this gap,
and could not**: at superzone level Nazareth's corridor-bound segment is calibrated to
ticketing (ratio 0.74); the shortfall sits in the superzone-to-area allocation and the
destination frame (survey trips land in Haifa TAZs by employment share, ticketed
journeys at trunk-route alighting stops in the line areas) and in hub attribution.
Coverage is the right diagnosis for the local market — Nazareth: ticketing records 8 %
of the survey's intra-superzone bus trips, 34 % of inter-superzone, 74 % to the Haifa
superzones; other guarded superzones local 0.05–0.24 — and the wrong one for the
corridor-bound market. Transit share of link flow: 16–26 % (1 → 23) / 14–37 % (23 → 1)
on the Haifa segment in the calibrated-survey set; 15–27 % / 18–55 % in the ticketing
set, whose total includes walk / other modes.

**Outputs.** `Output/ths2017/three_mode_2022/corridor_profile_hybrid_vs_ticketing.csv`,
`corridor_profile_components.csv`, `corridor_profile_pair_contributions.csv`,
`corridor_profile_coverage_local_vs_intercity.csv`; figures
`corridor_profile_hybrid_vs_ticketing.png`, `corridor_profile_transit_share.png`.

## 6q. Step 19 — Superzone conservation test of the TAZ hybrids, and a rebalanced hybrid (`Hybrid_superzone_conservation_test.ipynb`)

**Question (review §5).** Does the TAZ hybrid of steps 3 / 6 reproduce the superzone OD
blocks of the superzone hybrid it was built from? The notebooks asserted origin totals
only.

**Method.** Reaggregate `hybrid_taz_trips.csv` (primary, trips file; and the historical
activities-file version) to `SZ_NEW` blocks and compare with `hybrid_sz_trips.csv`. Then
rebalance the primary TAZ hybrid by iterative proportional fitting with two constraint
sets — every superzone OD block (hard) and every TAZ origin total (hard, unchanged) —
with the current hybrid as seed; column totals free; assert both within tolerance.

**Results.** Primary hybrid: origin totals exact; of 627 blocks above 100 trips, 55
deviate by more than 10 % and 12 by more than 25 % (worst SZ 35 → 3, +49 %; flow-weighted
mean 2.0 %); off-diagonal mass 3.6 % high, diagonals up to 6 % low. Historical hybrid:
origin totals off by up to 6.7 % (TAZ 105 mapping), 80 / 20 blocks beyond 10 / 25 %.
Rebalancing converges in 4 iterations (block error < 10⁻⁴), relocates 1.0 % of trips
(cell factors p5 0.86, median 0.97, p95 1.01), corridor → corridor 94,610 → 95,348. The
within-block cell structure still comes from the replicated cellular mapping (§2), which
this step does not repair.

**Outputs.** `Output/ths2017/tests/hybrid_sz_conservation_summary.csv`,
`hybrid_sz_conservation_worst_blocks.csv`;
`Output/ths2017/study_taz/hybrid_taz_trips_balanced.csv`, `hybrid_taz_prob_balanced.csv`;
figure `hybrid_sz_conservation.png`. The notebook ends with a pass / fail assertion
(blocks within 1 %, origin totals within 0.1 %) and runs on committed outputs alone.

## 6r. Step 20 — Peak hour on the corridor: peak-hour factors and peak-hour potential movements (`Corridor_peak_hour_2022.ipynb`)

**Question.** The corridor profiles of steps 17–18 are three-hour totals; design needs the
busiest hour. What is the peak hour, how peaked is it, and what do the link profiles look
like in peak-hour terms?

**Method.** The trips file records departure time to the minute (`STDep`; `Dep_h` is its
floor, agreeing in 99.5 % of trips). The AM trips of step 15, allocated to TAZs and to the
28 sub-areas with the same population / employment split, are binned in 15-minute
departure intervals over 06:00–09:00. For each layer the **peak hour** is the 60-minute
window (15-minute steps) with the largest share; **PHF₃ₕ** = peak-hour trips / three-hour
trips (an average hour is 0.333); **PHF₆₀** = peak-hour trips / (4 × busiest 15 minutes).
Profiles are computed (a) study-area-wide per layer, (b) for the trips between line areas
per direction and layer, weighted by links crossed, and (c) per link. A 200-replicate
household bootstrap gives the sampling range of (b). The factor applied to the 2022 link
profiles is the direction-level one where the corridor sample has at least 100 sampled
trips (car: 194 / 236), otherwise the study-area factor of the layer (bus 1,636, taxi-type
253 sampled trips; rail takes the bus factor). The factor is on departure time; the
link-crossing hour lags it by the travel time to the link.

**Results.**

| Layer | Peak hour (study area) | PHF₃ₕ study area | PHF₆₀ study area | PHF₃ₕ corridor 1 → 23 (n) | PHF₃ₕ corridor 23 → 1 (n) | Applied |
|---|---|---|---|---|---|---|
| Car | 07:00–08:00 | 0.621 | 0.69 | 0.661 (194; bootstrap 0.51–0.81) | 0.626 (236; 0.47–0.75) | direction-level |
| Bus | 07:00–08:00 | 0.590 | 0.75 | 0.655 (48; 0.54–0.84) | 0.435 (26; 0.43–0.79) | study area 0.590 |
| Taxi-type | 07:00–08:00 | 0.580 | 0.68 | 0.784 (35) | 0.837 (25) | study area 0.580 |
| Walk / other | 07:00–08:00 | 0.793 | 0.64 | — | — | not in the profile |

The peak hour carries ≈ 1.8 × an average hour. Per-link factors are identifiable only
for car (19 link-directions with ≥ 30 sampled trips) and scatter −0.12 to +0.19 around
the direction factor (mean +0.03); bus links have at most 25 sampled trips. Peak-hour
potential movements (2022 layers): transit (bus + rail) 981 on Ein Hayam – Bat Galim
towards Nazareth (three-hour 1,661, average hour 554) and 974 on Neot Peres – Neve David
towards Tirat Carmel (1,650 / 550); all layers 4,609 towards Nazareth on Ein Hayam – Bat
Galim and 4,205 towards Tirat Carmel on Bat Galim – Kiryat Eliezer. Sensitivity of the
busiest transit link to the bus factor basis (study area / corridor pooled / corridor
direction): 981 / 835 / 1,089 towards Nazareth, 974 / 829 / 718 towards Tirat Carmel.
These remain potential movements in the peak departure hour, not loads.

**Outputs.** `Output/ths2017/three_mode_2022/peak_hour_factors.csv` (all levels, with
hourly shares and bootstrap ranges), `peak_hour_factors_applied.csv`,
`peak_hour_factors_by_link.csv`, `corridor_link_flows_peak_hour_2022.csv` (per link and
direction: three-hour, average-hour and peak-hour flows by layer),
`peak_hour_sensitivity.csv`; figure `corridor_flow_profile_peak_hour_2022.png`.

## 6s. Step 21 — PCA within the survey: car vs transit destination structure (`THS_2017_PCA_car_vs_transit.ipynb`)

**Question.** Do car and transit trips share the same destination-choice structure, and
where do they diverge? The PCA suite of steps 12–14's companions (§6j–§6l, and the PCA
notebooks of §8b) is applied within the survey with the mode group as the grouping.

**Method.** Trips file, step-15 extraction (AM, both ends in the study area, weighted),
population / employment zone split; groups car (`mainmode` 10 / 11), transit (3, 4, 5, 8, 7),
bus (3, 4) as a sensitivity; levels 36 superzones (35 usable origins) and 28 sub-areas
(16 usable). Origins are observations, row-normalised destination profiles are features.
References: each mode's own day 1 vs day 2 repeatability and a permuted-geography null;
a 200-replicate household bootstrap of the overlap; a restricted run on the 26 origins
with ≥ 20 sampled transit trips. Tests T1–T6 as in the earlier suites.

**Results (superzone level, k = 20).** Car vs transit subspace overlap 0.75 (bootstrap
0.66–0.76; null mean 0.57, max 0.70, p = 0.0005) against car repeatability 0.95 and
transit repeatability 0.81; on the well-sampled origins 0.83 against transit repeatability
0.86. Car components capture 86 % of the transit variance that transit's own components
capture (transit repeatability 89 %). Leading pairs match one to one (0.72, 0.79): a
geographic axis and a self-containment / Haifa-bound axis. Divergence: mean
self-containment car 0.62 vs transit 0.45; only 44 % of the squared divergence is on the
diagonal (survey vs cellular: 87 %); removing the diagonal does not raise the overlap
(0.72); the sign-flip test finds a common direction (p = 0.04) — transit share moves from
peripheral destinations (Tirat Carmel, Umm al-Fahm, Beit She'an, Ma'alot: −2 points) to
the Haifa core (SZ 16, 14, 13, 12: +2–3 points). Displacement is 1.5 × transit's
day-to-day noise. Largest well-sampled departures: Rekhasim / Zevulun (45 % of transit
trips to the Haifa superzones vs 9 % of car), Shefa-'Amr / Tamra (66 % vs 14 %), Tirat
Carmel (71 % vs 23 %).

**By resolution.** Corridor aggregation areas (28 × 28; origins with ≥ 10 sampled transit
trips, 14): car vs transit 0.57 against transit repeatability 0.65 and car 0.91 (≥ 20
trips, 8 origins: 0.64 vs 0.70) — the modes are as alike as transit is to itself, and
nothing finer is resolvable there; self-containment car 0.42 / transit 0.23; the mean
shifts point the same way (Lower City, Kiryat Nahum, Matam, Neot Peres gain transit
share; Nesher Lower, Tirat Carmel, Hamifrats lose) but with 14 origins no common
direction is detectable (p = 0.6). Well-sampled outer areas: Kiryat Motzkin-Bialik sends
26 % of transit trips to the Haifa line areas vs 6 % of car trips, Kiryat Yam 13 % vs 7 %,
Kiryat Ata South 12 % vs 3 %; origins inside Haifa send 70–95 % of both modes there.
TAZ origins × superzone destinations (133 TAZs with ≥ 5 transit trips, k = 15): 0.75
against transit repeatability 0.89 and car 0.90, common direction p = 0.002 — the
resolution at which the systematic difference is best established. TAZ × TAZ (same
133 origins, k = 35): 0.27 against transit repeatability 0.55, car 0.71, chance 0.05;
car components capture 39 % of transit variance; self-containment car 0.13 / transit
0.06 — only the coarse geography is shared, not the fine destination cells.

**Reading.** Car and transit share the dominant structure, but transit is systematically
less local and more Haifa-core-bound; a transit market cannot be read off the car pattern
by scaling, and a transit-specific destination pattern (as in the step-15 calibration)
is warranted. Nothing follows at TAZ level or within Haifa from the survey's transit sample.

**Outputs.** `Output/ths2017/tests/pca_car_vs_transit_{summary,overlap,rcev,by_origin,levels,by_area}.csv`;
figures `Output/figures/pca_cvt_{scree,subspace_overlap,component_match,divergence,levels}.png`.

**Addendum, 22 September 2026 — the V2 corridor areas.** The same tests on the 25 V2 areas
(`Input/Corridor_TAZ_Agg_V2.xlsx`; rows `V2 areas × areas` in `pca_car_vs_transit_levels.csv`,
per-origin table `pca_car_vs_transit_by_area_v2.csv`): with 14 origins of ≥ 10 sampled transit
trips the overlap is 0.55 (k = 6) against transit's repeatability 0.76 and car's 0.79; with the
7 origins of ≥ 20 trips 0.76 against 0.80 / 0.97; on all 22 usable origins 0.59 against 0.62 /
0.79. Self-containment 0.42 (car) vs 0.25 (transit); no common direction (p = 0.28–0.54); the
12 trunk areas alone leave 4 usable origins. Which side of transit's noise floor the overlap
falls on depends on which handful of origins is in — the level is sample-limited and adds no
conclusion to the superzone and TAZ × superzone results. Per origin the Haifa pull repeats
(Kiryon 35 % of transit trips to the Haifa trunk areas vs 6 % of car, Kiryat Bialik Center
30 % vs 6 %, Kiryat Yam B+C 31 % vs 8 %); Nazareth (83 sampled) is 90 % self-contained in
transit and 96 % in car.

## 6t. Step 22 — Final 2022 TAZ matrices: car, transit, total (`Final_matrices_2022.ipynb`)

**Purpose.** The deliverable set, assembled from the step-16 layers without any further
modelling: **car** = `car_2022_taz`; **transit** = bus (calibrated) + rail (survey
door-to-door); **total** = car + transit. Taxi-type is carried as a variant
(`transit_incl_taxi`, `total_incl_taxi`), not in the headline transit matrix (§6n).
A long-format file (`orig_taz, dest_taz, car, bus, rail, taxi_type, transit, total`,
non-empty cells only, gzip) is written for SQL use, with a manifest and a summary.

**Totals (2022, AM 06:00–09:00, 778 × 778).**

| Layer | All | Corridor → corridor | Corridor → outside | Outside → corridor | Outside → outside |
|---|---|---|---|---|---|
| Car | 1,353,798 | 72,331 | 47,011 | 89,181 | 1,145,275 |
| Transit (bus + rail) | 133,704 | 9,366 | 10,104 | 18,799 | 95,434 |
| **Total (car + transit)** | **1,487,501** | 81,697 | 57,115 | 107,980 | 1,240,709 |
| Taxi-type (variant) | 19,359 | 3,812 | 1,359 | 5,479 | 8,709 |
| Transit share of total | 9.0 % | 11.5 % | 17.7 % | 17.4 % | 7.7 % |

Checks: the four layers add to `all_modes_2022_taz.csv` cell by cell; the long file's
total equals the matrix total; 351,223 of 605,284 cells carry demand (the bus layer is
dense because the calibration spreads each origin's volume over the blended
destination pattern; car has 24,173 non-zero cells).

**Outputs.** `Output/final_2022/{car,transit,total,transit_incl_taxi,total_incl_taxi}_2022_taz.csv`,
`final_2022_long.csv.gz`, `final_2022_summary.csv`, `MANIFEST.csv`.

## 6u. Step 23 — Growing the 2022 TAZ matrices to 2040 / 2050, BU and HS (`Forecast_matrices_TAZ_2040_2050.ipynb`)

**Purpose.** Four demographic-reference matrix sets (BU / HS × 2040 / 2050) at TAZ level
from the final 2022 layers (§6t), replacing the 25-area composite forecast of §7's
`forecast/` products (historical). Full method: `docs/FORECAST_METHODOLOGY_2040_2050.md`.

**Method in brief.** (1) 2022 demographic level bridged as `X_2020 (X_2025/X_2020)^(2/5)`.
(2) Composite land-use indices fitted once on total 2022 demand by non-negative least
squares — production `I = 0.506·P + 0.124·E`, attraction `J = 0.264·P + 0.814·E` (R² ≈ 0.5
at TAZ level) — because AM destinations are jobs *and* residents (schools, homes, shops).
(3) Margins per layer: `O_i^y = O_i + ρ_i ΔI_i`, `D_j^y = D_j + σ_j ΔJ_j`, own rate where the
TAZ is established (index ≥ 500 residents' worth, growth ≤ 3×), superzone rate on the
increment otherwise; destinations rescaled to the origin total. (4) Seed: existing demand
keeps its 2022 cells; established origins / destinations grow along their own row /
column; small-base or transforming ones receive the layer's superzone pattern spread by
targets. (5) Furness per layer (car, transit, taxi-type); total = car + transit. Mode
split, trip rates and destination choice stay at 2022 by construction.

**Status.** The scenario zonal files are Git-LFS-only; in the remote environment the
notebook ran a **dry run** (2022 → BU-2025, and a stress case with a synthetic
10,000-resident conversion of the Matam TAZs and a 1.5 × employment jump) to exercise
every path: margins met to 10⁻⁶ for car and transit (taxi-type, sparse, to 2–3 % after
500 iterations); no negative or unreachable cells; car mean centroid length 7.32 →
7.61 km on a 4.7 % growth (employment-only attractions would have given 7.91 km, the
all-synthetic seed 7.84 km); transit length unchanged; the Matam conversion adds ≈ 2,400
origin trips at the superzone rate. Outputs of the dry run are under
`Output/forecast_taz/dry_run/` and are not scenario results. The four scenario sets are
produced by running the notebook after `git lfs pull --include="Input/Demographic_Forecast/Zonal_*.csv"`;
they will appear under `Output/forecast_taz/{BU_2040,BU_2050,HS_2040,HS_2050}/`.

**Outputs (per scenario-year).** `{car,transit,taxi,total}_{scenario}_{taz,sz,area}.csv`,
`margins_{scenario}.csv` (indices, targets and the rule each TAZ took); across scenarios
`summary_by_class.csv`, `checks.csv`, `by_area.csv`, `trip_rates_by_sz.csv`,
`corridor_link_flows_scenarios.csv`, `landuse_indices.csv`; figure
`forecast_taz_profiles_{mode}.png`.

## 6v. Step 24 — Corridor potential movements on the V2 aggregation, three routes (`Corridor_flow_profile_V2_routes.ipynb`)

**Purpose.** Re-run the corridor profile (steps 17 and 20) on the new aggregation
`Input/Corridor_TAZ_Agg_V2.xlsx`: 25 areas from 174 TAZs with three route orders — **T1**
Tirat Carmel → Haifa → Tsomet Kiryat Ata → Kiryat Ata → Shefaram → Hamovil → Nazareth (17
areas), **T2** the same trunk → Kiryat Haim → Kiryat Bialik Center → Kiryon → Tsur Shalom
(16), **T3** the same trunk → Kiryat Haim West → Kiryat Yam B+C → Kiryat Yam A → Savyoney
Yam (16). The twelve trunk areas (201–212) are common; the routes branch at Tsomet Kiryat Ata.

**Method.** The step-16 TAZ layers are aggregated to the 25 areas (`{car,bus,taxi,rail,
transit,total}_2022_area_v2.csv`). Per route, as in §6o: every OD pair with both ends on
the route loads every link between them in its direction — **up** = away from Tirat Carmel
(the old 1 → 23), **down** = towards it. Peak-hour factors re-estimated on the V2 route sequences by step 27 (§6y) and applied per
route / network, layer and direction (car 0.62–0.65 up, 0.57–0.58 down, network 0.556 / 0.522;
bus 0.590, taxi-type 0.580, rail = bus); the step-20 factors are the fallback when that file is absent.
A fourth view loads every pair of the 25 areas on its unique path over the **tree** (trunk +
three branches), so the trunk carries the trunk-to-branch trips of all three branches at once
and branch-to-branch trips load the branch links. Same caveats as §6o / §6r: potential
movements, not loads. The V2 TAZ set shares 143 TAZs with the earlier 28-area set, drops 62
(Hadar Carmel, Neve Yosef, Kiryat Nahum, Kiryat Ata East, the influence areas …) and adds 31
(all of Nazareth city, Shefaram, Neot Peres), so totals are not one-to-one comparable with
§6o; the Haifa-segment link values are.

**Results.** Trips with both ends in the 25 areas: 184,106 (car 156,944, bus 18,788,
taxi-type 8,323, rail 51). Route-internal trips: T1 123,906 (transit 12,546), T2 73,964
(7,711), T3 55,519 (7,054). Busiest transit link on every route is on the Haifa trunk —
Ein Hayam – Bat Galim-Kiryat Eliezer up (1,379–1,437; peak hour 814–848) and Matam-Neot
Peres – Hof Carmel-Neve David down (1,410–1,629; 833–962). The T1 branch is one-directional
in the morning (Tsomet Kiryat Ata – Kiryat Ata North 5,809 down / 785 up; 1,174 transit down,
share 20 %; Shefaram – Nazareth links 650–920 transit down at a 20–23 % share, the highest
in the set). The Krayot branch holds the busiest single link of any route, Kiryat Haim –
Kiryat Bialik Center at 10,144 down (peak hour 5,812) with a 10 % transit share; T3's branch
peaks at 4,896 down on Tsomet Kiryat Ata – Kiryat Haim West (936 transit, 19 %). On the tree
network the trunk link Bazan-Hutsot – Tsomet Kiryat Ata carries 16,231 down (peak hour 8,792)
and 2,898 transit (1,710) — the inflow of all three branches — against 4,958 / 1,075 on the
same link in the T1 profile alone; the Haifa-side trunk changes little between views (7,183
up on Ein Hayam – Bat Galim vs 6,878–7,036 per route). The 14,688 branch-to-branch trips (8 %)
load only branch links. Down dominates every link east of Bat Galim; up dominates only Tirat
Carmel – Ein Hayam. Transit share of link flow on the trunk: 17–33 % down, 10–22 % up.
Against the earlier 18-area profile (busiest transit link 1,661 / 1,650): per route
1,379–1,437 / 1,410–1,629, network 1,518 / 2,898.

**Outputs.** `Output/corridor_v2/area_legend_v2.csv`, `{layer}_2022_area_v2.csv`,
`corridor_v2_link_flows_long.csv` (route × link × direction × layer, three-hour and
peak-hour), `corridor_v2_link_flows_wide.csv`, `corridor_v2_route_summary.csv`,
`corridor_v2_network_link_flows.csv`, `corridor_v2_vs_earlier_profile.csv`; figure
`corridor_v2_route_profiles_2022.png`.

## 6w. Step 25 — LRT line and stations: stop-to-stop times, underground vs ground level (`LRT_line_stations_travel_time.ipynb`)

**Purpose.** Turn the planned geometry (`Input/GeneralHalufa/`) into a station table and
station-to-station in-vehicle times under two scenarios — all stations underground, all at
ground level — with the calibrated function of
`docs/Transit_Travel_Time_Calibration_Report_Operator22.md` (OperatorRef 22, 132 Thursdays
May 2023 – September 2026, 26,653 clean journeys):
`T [min] = 1.960792 × N_UG + 2.392690 × N_Other` per 500 m section, i.e. 3.921585 min/km
underground and 4.785381 min/km at ground level (15.30 / 12.54 km/h, dwell included). A
section is underground only when both its stations are, so the two scenarios are the two
pure regimes.

**Method.** WGS 84 → Israel TM Grid; the 46 platform points are projected onto the
alignment (all within 80 m) and grouped into stations where consecutive chainages are
< 150 m apart (22 pairs + 2 singles = 24 stations, S01 at the Tirat Carmel end to S24 at
Hamifrats); chainage runs from the Tirat Carmel end to match the V2 route order; TAZ by
point-in-polygon on `TAZ_North.shp`, V2 area by the TazAgg key. Two forms of the function
are kept: the **distance form** (report §6; time ∝ actual inter-station distance) as the
primary value and the **section form** (one calibrated section per link) as the sensitivity,
because the coefficients embody dwell at 500 m spacing and this line's spacing averages
815 m. Area-to-area times for the ten trunk areas on the line use the station nearest each
area's population + employment weighted centroid.

**Revision 2 (22 September 2026) — the 500 m assumption checked.** The calibration report
converts its per-section coefficients to speeds under a modelling assumption of 500 m
between stops. The Red Line's own timetable is in the national GTFS (operator 22, routes
34447 / 34448: 32 stops, 21.4 km, 70.6 min scheduled), with the distance at every stop:
its underground sections average **970 m** and its surface sections **577 m**, so the
calibrated 1.961 min per underground section is a 30 km/h section, not 15 km/h, and
revision 1's distance form (which spread the section times over 500 m) made the
underground scenario twice too slow. The function is now applied in a running-time +
stop-penalty form fitted on the Red Line's 14,477 scheduled sections — underground
0.81 min + 1.31 min/km (46 km/h running, 49-second stop penalty), surface 1.23 min +
1.94 min/km (31 km/h, 74 seconds) — levelled to the calibration's observed means (× 0.94
underground, × 1.02 surface); at Haifa's 815 m spacing a section takes 1.77 min underground
(27.6 km/h) and 2.86 min at ground level (17.1 km/h). The section form is kept as the fast
bound and the revision-1 nominal 500 m form as the superseded slow bound
(`lrt_calibration_redline_spacing_check.csv`, `lrt_end_to_end_summary.csv`).

**Results.** 18.94 km alignment; 24 stations spanning 18.74 km, spacing 354–1,396 m
(mean 815). End to end S01 → S24: **40.7 min all underground (27.6 km/h) / 65.8 min all
ground (17.1 km/h)** in the decomposed form; section form 45.1 / 55.0 min; nominal 500 m
form 73.5 / 89.7 min (revision 1, superseded). Going underground saves 38 % (revision 1
said 18 %: the two coefficients embed different section lengths). Station S13 lies in TAZ
1509, which the V2 key does not list. Bazan-Hutsot (211), Tsomet Kiryat Ata (212) and the
three branches have no station on this geometry.

**Outputs.** `Output/lrt_v2/lrt_stations_hf_lrt_3.csv` / `.geojson`,
`lrt_station_distances_km.csv`, `lrt_station_times_{all_underground,all_ground}.csv` and
`…_section_form.csv`, `lrt_line_profile.csv`, `lrt_area_representative_station.csv`,
`lrt_area_ivt_{all_underground,all_ground}.csv`; figure `lrt_line_profile_hf_lrt_3.png`.

## 6x. Step 26 — Generalized cost on the V2 areas: data inventory, first-fill skims, gaps (`GC_data_inventory_and_skims.ipynb`)

**Purpose.** For the capture model's formula (`docs/LRT_CAPTURE_PLAN.md`:
`GC = IVT + 2·walk + 2·wait + 8·transfers + (fare + parking)/VOT`), establish component by
component and mode by mode what exists, what can be derived now, what is assumed and what is
missing, and fill a 25 × 25 matrix per component with the status recorded per cell.

**Method.** *Car IVT*: AM car trips of the trips file with door-to-door `TrvlTime`,
allocated to V2 area pairs with the population / employment split of §6r (2,387 sampled
trips, 296 of 625 pairs, 35 with ≥ 10), smoothed by an empirical-Bayes blend (k = 5) with
the weighted fit *t* = 7.0 + 1.85 × centroid km; intra-area 7.0 min. *Bus IVT*: the street
network of `Input/BusSpeedData` clipped to the study area (54,507 links, 48,092 with a
weekday-3 07:00–08:00 bus speed; `DIR` read as 1 = with, −1 = against, 0 = both — 99.9 % of
the speed records agree), Dijkstra on bus-served links within the giant strongly-connected
component (37,694 nodes) between the nearest served nodes to the area centroids, connector
legs at 15 km/h — a lower bound with no wait, transfer or stops. *LRT*: step-25 area times
on the ten trunk areas; walk access from every V2 TAZ centroid to the nearest station
(straight line × 1.3 at 4.8 km/h), population-weighted for access and employment-weighted
for egress per area; wait = half the plan's 6-minute headway; 0 transfers. *Assumed
placeholders*: bus walk 8 min, bus headway 10 min, VOT 30 ILS/h; fares and parking enter at
zero and are flagged missing.

**Results.** Trip-weighted on the 90 trunk pairs: car door-to-door 14.5 min; bus fastest-path
IVT 12.5 min against **27.1 min door-to-door in the survey** (2.26 ×; 2.12 × on all V2 pairs)
— walk, wait, stops and detours double the running time; LRT IVT **20.6 min underground /
25.1 min ground** (distance form; 13.3 / 16.2 section form), access + egress walk 13.6 min.
Partial generalized cost (IVT + 2·walk + 2·wait): LRT 53.8 / 58.4, bus 38.5, car 14.5; the
LRT beats the partial bus cost on 9 % of the trunk pairs. As door-to-door times the
distance-form LRT (≈ 37 min) is slower than today's bus (27 min) and the section-form LRT
(≈ 30 min) level with it: the LRT speed on this spacing (a 39 % swing in IVT) outweighs every
missing money component, and is the first input to obtain (task E2), followed by the branch
geometry (E1; 15 of 25 areas have no LRT time). Status of the fill: car IVT 35 measured /
590 derived; bus IVT 600 derived; LRT IVT 100 derived / 525 missing per scenario; fare and
parking missing everywhere; bus walk / wait assumed, bus transfers missing.

**Outputs.** `Output/gc/car_ivt_survey_area_v2.csv` (+ `_n_sampled`,
`car_dist_survey_area_v2.csv`), `bus_ivt_network_area_v2.csv`, `bus_path_km_area_v2.csv`,
`bus_survey_vs_network_check.csv`, `lrt_access_taz_v2.csv`, `lrt_access_area_v2.csv`,
`gc_components_area_v2_long.csv` (o, d, mode, component, value, unit, status, source),
`gc_area_v2_{car,bus,lrt_all_underground,lrt_all_ground}.csv`, `gc_cell_status_area_v2.csv`,
`gc_trunk_pairs_comparison.csv`, **`gc_data_inventory.csv`** (the gap table); figure
`gc_first_fill_trunk_v2.png`.

**Addendum, 22 September 2026 — the GTFS skim in the bus components.** With step 29's
direct-service skim (§6aa) the bus in-vehicle time is the scheduled time of the direct
services on the 422 pairs that have one (82 of the 90 trunk pairs, 89 % of their trips), the
wait half their combined 07:00–08:00 headway capped at 10 min, the walk the TAZ-to-nearest-
served-stop distance weighted by residents and jobs, and transfers 0; the other pairs keep
the fastest-path floor × 1.12 (the median scheduled ÷ floor ratio), the placeholder wait
and a missing transfer count. The Metronit is carried as its own mode (`brt`) on the 278
pairs it connects directly. Trunk pairs, trip-weighted: bus IVT 12.3 min (floor 12.5), walk
4.7, wait 1.6 → partial generalized cost 24.9 (was 38.5 on the placeholders); Metronit IVT
7.8, wait 2.4, partial cost 21.2 on its 72 trunk pairs against 20.0 for all buses on the
same pairs; LRT 53.8 / 58.4 — dearer than the bus on every trunk pair by 13–62 generalized
minutes (median 28), 9 of which are access (6.8 min to a station against 2.4 min to a bus
stop, trip-weighted). The timetable's best direct bus is 18.6 min door to door against the
27.1 min bus users report in the survey: the 8-minute gap (transfers, the line actually
needed, delay) is the calibration margin for the bus cost. Status of the fill after the
addendum: bus IVT 422 derived / 178 assumed, walk 625 derived, wait 420 derived / 203
assumed, transfers 422 derived / 203 missing; `gc_area_v2_brt.csv` added.

**Addendum 2, 22 September 2026 — the corrected LRT function, a 5-minute headway, and the
GTFS skim against the survey.** With step 25 revision 2 the LRT in-vehicle time on the trunk
pairs is 11.7 min all underground / 18.9 min all ground (trip-weighted; section form 13.3 /
16.2), level with the bus timetable's 12.3 min; the LRT wait is now half a 5-minute headway
(12 departures an hour). Partial generalized cost on the trunk pairs: LRT 43.9 / 51.1 against
bus 24.9 and car 14.5 — the LRT dearer than the bus on every trunk pair by 7–31 generalized
minutes (median 17), of which 18 are the access difference (13.6 min of walking to a station
against 4.7 to a bus stop, weighted twice). Door to door the underground LRT (≈ 28 min)
equals the bus users' reported time (27 min) and is 10 min slower than the timetable's best
direct bus (17 min). The GTFS skim against the survey on the same pairs: timetable
door-to-door 23.0 min (in-vehicle 15.8 + walk 5.3 + wait 1.9) against 31.8 reported, a
ratio of 1.4 that is a fixed overhead of ≈ 9 minutes rather than proportional (1.9 × on
pairs under 3 km, 1.3 × at 3–20 km, 0.9 × at 20–60 km; trunk-to-trunk 26.8 vs 17.4) — the
transfer, the wait for the line actually needed and delay; only three pairs hold ≥ 3
sampled trips, so it is a trip-level result by distance band
(`bus_gtfs_vs_survey_summary.csv`, figure `gc_bus_gtfs_vs_survey.png`). The open item on
the LRT side is no longer its speed but station access (24 stations against 12,845 stops):
an access / feeder treatment and the branch geometry (E1).

**Addendum 3, 22 September 2026 — observed bus running times (step 30).** The bus in-vehicle
time on the 422 direct pairs is now the observed running time of §6ab (the scheduled value
kept as `ivt_scheduled`): trunk pairs, trip-weighted, 14.4 min observed against 10.4
scheduled — the demand sits on the arterial hops that run 1.1–1.4 × slower than the
timetable in the peak hour. Partial generalized cost on the trunk pairs: bus 27.0 (was
24.9 on the timetable), Metronit 22.1 on its pairs (all-bus 20.2 there), LRT 43.9 / 51.1,
car 14.5; the LRT stays dearer than the bus on every trunk pair (4–31 generalized minutes,
median 17, of which 18 are access), while its in-vehicle time underground (11.7 min) is
now 3 min *below* the observed bus running time. GTFS-based door-to-door against the
survey on the same pairs: 24.3 vs 31.8 min (× 1.3; trunk 20.0 vs 26.8), a fixed overhead of
≈ 7 minutes that is now transfer and the wait for the line actually needed, the running
time being observed (`bus_gtfs_vs_survey_summary.csv`).

**Addendum 4, 22 September 2026 — money is out of the comparison.** Decision of the study
team: the transit fare in the area is flat and integrated — every bus, Metronit or LRT trip
costs the same, and a daily cap (two fares pay for the day's rides) makes transfers and
return trips free. The fare is therefore identical across the transit modes and across every
pair and drops out of the transit choice entirely; against the car it is a constant per trip
that the pivot on the observed 2022 shares absorbs. Car operating cost and parking are
excluded on the same decision. The fare and parking cells of `gc_components_area_v2_long.csv`
now carry the status `constant` (values zero) instead of `missing`, the inventory
`gc_data_inventory.csv` lists nothing to obtain for them, and VOT is no longer needed. No
generalized-cost value changes (money entered at zero before); task E4 of
`docs/CORRIDOR_DEMAND_TASKS.md` closes.

## 6y. Step 27 — Peak-hour factors on the V2 routes (`Corridor_peak_hour_V2_routes.ipynb`)

**Purpose.** Step 24's first pass applied the step-20 factors of the 18-area line to the V2
routes. This step re-estimates them on the V2 sequences themselves — per route (T1 / T2 / T3),
direction (up = away from Tirat Carmel, down = towards it) and layer, and on the tree
network (every pair of the 25 areas on its unique path, each link crossing counted in its
direction) — with the construction of §6r (15-minute departure bins, link-crossing weights,
200-replicate household bootstrap, direction-level factor applied where ≥ 100 sampled trips,
otherwise the study-area factor; rail = bus). Step 24 reads the result
(`Output/corridor_v2/peak_hour_factors_v2_applied.csv`) and runs after this step.

**Results.** Car is identifiable on every route and direction (203–447 sampled trips; 777 /
1,001 on the network): up T1 0.626, T2 0.619, T3 0.652 (peak hour 07:15–08:15); down 0.578 /
0.569 / 0.569 (07:00–08:00; T2 07:15–08:15); network 0.556 up / 0.522 down — the long trips
from Nazareth and the Krayot start earlier and flatten the pooled down profile. Against step
20 (0.661 / 0.626) the up factors are 1–6 % lower, the down factors 8–9 % lower per route and
16–17 % lower on the network; the peak-hour car and total values of step 24 fell by those
margins (network trunk link Bazan-Hutsot – Tsomet Kiryat Ata 9,956 → 8,792; T2 branch link
6,239 → 5,812). Bus (26–58 sampled per route-direction, 93–96 on the network) and taxi-type
(17–48) stay on the study-area factors 0.590 / 0.580; the bus route values scatter 0.43–0.69
(bootstrap 0.43–0.84) around 0.59, the taxi-type values (0.58–0.91) all sit above 0.58, so the
corridor taxi-type peak may be under-stated. Caveats as §6r.

**Outputs.** `Output/corridor_v2/peak_hour_factors_v2.csv`, `peak_hour_factors_v2_applied.csv`;
figure `corridor_v2_peak_hour_profiles.png`.

## 6z. Step 28 — Corridor transit profiles on the V2 routes: calibrated survey vs ticketing (`Corridor_profile_V2_survey_vs_ticketing.ipynb`)

**Purpose.** Repeat §6p on the V2 geography, from the TAZ-level products (survey bus + rail of
step 16; RavKav × OnBoard bus of step 9 and the station train matrix of step 10 × 0.793), per
route and on the tree network, with the calibration steps (raw 2018 survey bus, all-RavKav
variant) and taxi-type alongside.

**Results.** In the 25 areas the survey set holds 18,839 transit trips against 16,363 ticketed,
yet sits below the ticketing profile on almost every link: its transit is more local, the
ticketing's more corridor-long. Up: survey ÷ ticketing 0.78–0.83 on the Haifa segment per
route (network 0.82), same peak link (Ein Hayam – Bat Galim-Kiryat Eliezer, 1,379–1,437 vs
1,556–1,646; network 1,518 vs 1,730); beyond Hamifrats T1 1.08, T2 / T3 0.57–0.58. Down:
Haifa segment T2 0.92, T3 0.73, T1 0.66, network 0.63; beyond Hamifrats T2 / T3 0.79, T1
0.43; ticketing peaks on Lower City – Namal-Giborim per route (2,073–2,903) and on
Bazan-Hutsot – Tsomet Kiryat Ata on the network (4,476 vs survey 2,898), the survey further
west on Matam-Neot Peres – Hof Carmel-Neve David. Drivers, as in §6p: Nazareth as origin
(1,070 survey vs 2,402 ticketed corridor-bound trips, −13,020 link-trips; → Bat Galim-Kiryat
Eliezer 87 vs 521, → Hecht-Shprintzak 22 vs 271, → Lower City 132 vs 431), Kiryat Yam B+C
(568 vs 1,116), Tsur Shalom (290 vs 642), the Hamifrats hub (431 vs 1,049); by destination
Bat Galim-Kiryat Eliezer (1,161 vs 2,064), Lower City (894 vs 1,764), Hecht-Shprintzak (279
vs 1,035) — trunk-route alighting stops. The survey is higher from Kiryat Bialik Center, Ein
Hayam and Hecht-Shprintzak and to Kiryat Ata North and Kiryat Yam B+C. The T2 route is where
the frames nearly agree; on the T1 branch the ticketing set carries ≈ 2.3 × the survey's
transit towards Haifa, so a Nazareth-branch market should be carried as a range (tasks A1,
B1c, B2).

**Outputs.** `Output/corridor_v2/corridor_v2_survey_vs_ticketing.csv`,
`corridor_v2_survey_vs_ticketing_summary.csv`, `corridor_v2_survey_vs_ticketing_pairs.csv`;
figure `corridor_v2_survey_vs_ticketing.png`.

## 6aa. Step 29 — Bus level of service per TAZ from the national GTFS, bus and BRT (`GTFS_bus_LOS_TAZ.ipynb`)

**Purpose.** A level-of-service table for every study TAZ from the scheduled timetable —
bus (all operators) and the Metronit BRT separately — and a direct-service skim between
the 25 V2 areas that replaces the fastest-path floor of §6x for the bus in-vehicle time
and supplies a timetable wait (task E3). BRT lines are tagged by their route codes in
`routes.txt` (`route_desc` = code-direction-alternative): 83001 line 1 red (Krayot CBS –
Hof HaCarmel CBS), 83002 line 2 blue (Kiryat Ata – Bat Galim), 83003 line 3 green (Krayot
CBS – Hadar), 83004 line 4 purple (Krayot CBS – Hof HaCarmel via the Carmel tunnels),
83005 line 5 orange (HaMifrats CBS – Yagur / Nesher).

**Method.** Stops located in the 781 TAZs by point-in-polygon (Israel TM Grid); the
representative day is the Tuesday in the feed's validity with the most active services
(`calendar.txt`, `calendar_dates.txt` exceptions applied); trips of the active services
joined to routes; `stop_times.txt` read in 2-million-row chunks and reduced to study-area
stops and active trips; departures windowed to 06:00–09:00 and 07:00–08:00. Per TAZ and
per set (bus, BRT): served stops, distinct route codes, distinct trips in the two windows
(a trip calling at several stops of a TAZ counts once), the combined peak-hour headway
(60 / trips, all lines and directions) and its TCQSM frequency grade (A ≤ 10 min, B ≤ 15,
C ≤ 20, D ≤ 30, E ≤ 60, F), the best single line-direction headway, the number of TAZs
reachable without a transfer (all, and within 30 scheduled minutes), centroid distance to
the nearest served stop, stop density; `brt_access` = 1 where a Metronit line stops in the
TAZ, with the lines named. The area skim: for every trip and every ordered pair of V2 areas
it connects, the scheduled time from the first stop in the origin area to the first stop in
the destination area; per pair the median over the morning-peak trips, the trips in
07:00–08:00 and the implied headway, for all buses and for BRT only; compared with the
§6x floor where both exist.

**Results (feed of 22 May 2026, Tuesday 2 June 2026, 13,596 active services).** 12,845 stops in
730 of the 781 TAZs; 33,499 trips call at them, 7,324 departing a study-area stop in
06:00–09:00 (267 Metronit). *Route codes:* of the five supplied (83001–83005) only 83001 is a
Metronit line in the feed — 83003 and 83005 are local lines in Kiryat Malachi and Arara
BaNegev, 83002 / 83004 do not exist; the Metronit lines are 83001 (line 1), 67002 (line 2,
Bat Galim – Kiryat Ata), 67003 (line 3, Krayot loop), 62004 (line 4, Carmel tunnels) and
52005 (line 5, Yagur), all Superbus, printed as an audit table in the notebook. *Per TAZ:*
719 of 781 have a peak-hour bus departure, 62 none (59 without any stop, 18 of them in the
V2 areas — Bazan, port, Matam fringe, Kiryat Ata industry); on the combined headway 639
grade A, on the best single line 215 A / 239 B / 106 C / 97 D / 61 E; median centroid-to-stop
distance 194 m (72 TAZs beyond 1 km); the median TAZ reaches 47 TAZs without a transfer,
30 within 30 minutes. The Haifa trunk areas are A–B on the best line (3–7 min; Hamifrats
97 lines, Bat Galim 52); the branches are weaker — Kiryat Ata North / North-East 18–20 min
with 5 of 14 TAZs unserved and a direct reach of 10 TAZs, Shefaram 20 min, Hamovil 30 min,
Nazareth 12 min with 2,438 departures across 38 TAZs but local reach, Tirat Carmel 8 lines
at 12 min. *BRT access:* 60 TAZs, 41 in the V2 areas across 20 of the 25 areas (every trunk
area Matam – Tsomet Kiryat Ata, the Krayot by lines 1 / 4, Kiryat Yam and Savyoney Yam by
line 3, Kiryat Ata North by line 2); none in Tirat Carmel, Shefaram, Hamovil, Nazareth and
Kiryat Ata North-East. *Skim:* 422 of 600 area pairs have a direct bus service (278 a direct
Metronit); trunk 82 of 90 (72 Metronit) — Tirat Carmel to / from Bat Galim, Hamoshava,
Lower City and Hamifrats need a change at Hof HaCarmel; trunk median scheduled IVT 13.3 min
at a 1.7-minute combined headway (Metronit 10.0 min at 6 min); scheduled IVT ÷ the §6x floor
1.12 at the median (p10 0.53, p90 1.85 — the floor was far too fast on the long Krayot
pairs); from Nazareth 44–60 min to the trunk at 8–30-minute headways, from Shefaram 56 min,
and the Kiryat Ata branch has direct service to 15 of its 45 trunk pairs. Step 26 now takes
the bus IVT, wait and stop access from this skim where a direct service exists and carries
the Metronit as its own mode (§6x addendum). Open: transfer paths for the 178 pairs without
a direct service; observed (AVL) running times in place of the timetable. The earlier
synthetic dry run remains under `Output/gtfs/dry_run/`.

**Outputs.** `Output/gtfs/bus_los_taz.csv` (781 rows), `Output/gtfs/bus_direct_skim_area_v2.csv`,
figure `gtfs_bus_los_taz.png`.

## 6ab. Step 30 — Observed bus in-vehicle time: GTFS trips routed over the measured bus link speeds (`GTFS_bus_observed_times.ipynb`)

**Purpose.** Replace the timetable's in-vehicle time of §6aa with an observed one: every
morning-peak GTFS trip's stop sequence is routed over the May 2026 bus-speed street network
(§1: `Input/BusSpeedData`, weekday 3, 07:00–08:00, speeds by link and direction) and the
running time along the measured links is summed, then compared with the schedule. The
implementation was delegated to a lighter model against a written specification and
reviewed; the undirected second pass and the ratio-of-sums statistic were added in review.

**Method.** Study-area stops (step 29's intermediates) snapped to the nearest intersection
node (median 24 m); the 15,929 distinct consecutive stop pairs of the 7,324 trips routed
once each by shortest length on the directed graph (one dijkstra per source node, 6 s in
all); per segment the length on links with a measured speed and its time, the uncovered
remainder extrapolated at the segment's own covered speed. Segments whose directed path is
unreachable or implausible (> 2.5 × the straight line or > 8 km — mostly short hops where a
stop snapped to the far end of a one-way link forces a loop round the block) are routed
again ignoring link direction and accepted if plausible; the rest (2 %) take the scheduled
time, flagged. Trip times are cumulated along the stop sequence; the area skim uses §6aa's
pair definition (first stop in the origin area to the first later stop in the destination
area, departures 06:00–09:00; medians per pair; bus and Metronit) and reproduces §6aa's
scheduled values to 0.003 min.

**Results.** 84 % of trip-segments route in the directed graph, 13.5 % more after the
undirected pass, 2 % fall back; 94 % of routed length carries a measured speed and 97 % of
the area-pair segment length is observed. Observed ÷ scheduled in-vehicle time: per trip
1.09 (median; p10 0.86, p90 1.42), Metronit 0.87, other buses 1.10; per area pair 0.99
(Metronit pairs 0.86). By segment length (ratio of trip-segment-weighted sums): under 500 m
— 65 % of all hops — 1.00, 500–1,000 m 1.11, 1–2 km 1.25, over 2 km 1.42: the measured link
speeds therefore include dwell (short hops match the schedule, dwell and all), and the long
arterial and interurban hops run slower than the timetable in the 07:00–08:00 hour.
Demand-weighted on the 82 direct trunk pairs: 12.7 min observed against 10.4 scheduled;
Metronit 8.6 against 7.8 on its 72 trunk pairs; long pairs (> 30 scheduled minutes) 0.88 ×
the padded interurban timetables, except Nazareth → Haifa trunk at 8–9 min above schedule
(62 min to Bat Galim against 54). Step 26 takes the observed values (the scheduled ones kept
as `ivt_scheduled`).

**Outputs.** `Output/gtfs/bus_segments_observed.csv`, `bus_trips_observed.csv.gz`,
`bus_observed_skim_area_v2.csv`; figure `gtfs_bus_observed_vs_scheduled.png`.

---

## 6ac. Step 31 — Mode skim matrices and the flow comparison (`Mode_skims_and_flow_comparison.ipynb`)

**Purpose.** Turn step 26's generalized-cost components (§6x, with the observed bus
running times of §6ab) into one complete 25 × 25 skim set per mode — car, bus, Metronit
(BRT), LRT all underground, LRT all ground — extending the LRT skim beyond the ten
`hf_lrt_3` station areas with a feeder composite (bus, or Metronit with a free transfer), and use the skims to test whether
the 2022 car/transit split can identify the cost sensitivity λ that
`docs/LRT_CAPTURE_PLAN.md` §3 needs, then run the plan's pivoted capture model for the two
LRT scenarios and load the resulting trips onto the trunk links against today's bus
movements.

**Method.** Each mode's skim holds in-vehicle time, walk, wait, transfers and a partial
generalized cost (`GC = IVT + 2·walk + 2·wait + 8·transfers`; money out of the comparison by
decision — see §6x addendum 4) with a status matrix beside it. Car and Metronit carry over step 26's fills
unchanged (Metronit direct-service only, 278 pairs, elsewhere not available); bus takes
the observed in-vehicle time of §6ab on the 422 pairs with a direct service and, elsewhere,
the fastest-path floor with one transfer assumed. For the fifteen areas off `hf_lrt_3` the
LRT skim is a **feeder composite**: a feeder leg to a gateway station area — the observed
bus skim (in-vehicle time + 2·wait + 2·access walk) with an 8-minute transfer penalty, or,
where a direct Metronit service reaches the gateway, the Metronit skim with **no transfer
penalty** (LRT–Metronit transfers free by assumption, 22 September 2026), whichever is
cheaper — then the LRT leg (2.5-minute wait, station-to-station in-vehicle time, egress
walk); both ends off the line combine two such legs. The gateway pair and feeder modes
minimising the composite cost are chosen per origin–destination pair and recorded
(`gateway_o`, `gateway_d`, `legs`); `transfers` counts the penalised (bus ↔ LRT) transfers
only.
Intra-area cells are not skimmed for the transit modes and are excluded throughout. The
flow comparison then (i) fits a volume-weighted binary logit of the observed 2022 transit
share (bus + rail against car; taxi left out of the choice set) on `GC_bus − GC_car`, with
and without a constant per centroid-distance band, to read off λ; (ii) runs a nested
incremental logit pivoted on the observed 2022 transit share per pair
(Empirical-Bayes-smoothed toward the study-area share, k = 20): within the transit nest
`P_LRT|T = 1/(1+exp(λ_T(GC_LRT − premium − GC_bus)))` with an **LRT premium** (rail bonus)
of 5 generalized minutes, and the transit-nest logsum improvement Δ shifts car to transit
by `S' = S·e^{−λΔ}/(S·e^{−λΔ}+1−S)`, for a central case (λ = 0.03, λ_T = 0.06, premium 5),
a λ range (λ = 0.02/λ_T = 0.03, λ = 0.05/λ_T = 0.10) and a premium range (0, 10); with the LRT
removed the model returns the 2022 flows exactly, and taxi trips are carried unchanged;
(iii) loads every LRT trip onto the trunk between its gateway station areas, link by link
along the `Order_T1` sequence 201 → 210 in its direction, against step 24's bus / transit /
car potential movements on the same nine links, the peak hour using step 27's network bus
factor. All flows are corridor-internal (both trip ends among the 25 areas), 06:00–09:00,
2022.

**Results.** The skim fill: car 625 of 625 cells (590 derived, 35 measured); bus 598 of
625 (422 derived, 178 assumed, 25 not_skimmed on the diagonal); Metronit 278 of 625 (278
derived, 322 not_available, 25 not_skimmed); LRT all underground 600 of 600 off-diagonal
(90 derived direct, 402 derived_feeder, 108 assumed), LRT all ground 600 of 600 (90 / 370 /
140). Transit-trip-weighted on the 90 trunk pairs (10 station areas, 4,174 transit trips):
car 14.7 min, bus 27.8 (IVT 14.9, walk 4.8, wait 1.4), Metronit 25.6 on its 72 trunk pairs
(83 % of trunk transit trips), LRT underground 44.0 (IVT 12.6, walk 13.2, wait 2.5), LRT
ground 51.8 (IVT 20.4). On all 600 off-diagonal pairs (11,664 transit trips): car 20.2,
bus 38.5, Metronit 31.0 on 278 pairs (64 % of transit trips), LRT underground 70.5 (IVT
32.7 including the feeder bus, walk 9.9, wait 4.9, transfers 1.0), LRT ground 76.1.

Against the 2022 AM (06:00–09:00) off-diagonal trips within the 25 areas — car 56,445,
transit (bus + rail) 11,664 (share 0.171), taxi 6,982 — a trip-weighted binary logit of the
transit share on `GC_bus − GC_car` (573 pairs, 67,700 trips) returns λ = −0.011 per
generalized minute (se 0.0005, wrong sign, ρ² 0.003); adding distance-band constants gives
λ = +0.0002 (ρ² 0.036) — no cost sensitivity is identifiable within bands. Transit share by
centroid-distance band: < 3 km 0.114, 3–6 km 0.249, 6–10 km 0.169, 10–20 km 0.161, > 20 km
0.414 (mean `GC_bus − GC_car` 11, 16, 24, 29, 28 generalized minutes). The pairs where the
bus is dearest relative to the car are also the least car-available (captive riders, the
northern-branch localities) — car availability is not in the skims — so the cross-section
cannot identify λ, the plan's own caveat; λ is therefore
**assumed**, central 0.03 per generalized minute (range 0.02–0.05), with λ_T = 2λ within
the transit nest.

The pivoted capture (LRT trips 06:00–09:00 within the 25 areas; the incremental-logit growth
factor `S'/S` on the Empirical-Bayes-smoothed share is applied to each pair's *observed*
transit trips, so without the LRT the model returns 2022 exactly, and within the nest both
the existing and the induced transit trips split by `P_LRT|T`): all underground, central
**3,332** (3,037 from bus, 295 from car; transit share of car + transit 0.171 → 0.185), λ
range 2,357 (λ 0.05) – 4,855 (λ 0.02), premium 0 → 2,658, premium 10 → 4,122; all ground
central **2,544** (2,375 from bus, 169 from car), λ range 1,472–4,277, premium 0 / 10 →
1,999 / 3,200. Of the previous version's 2,257 (bus feeder only, no premium) the free
Metronit transfer adds about 400 and the 5-minute premium about 670. LRT share of transit:
underground 0.265 central (0.192–0.358 over λ), ground 0.206 (0.123–0.321). On the trunk
pairs, trip-weighted P_LRT|T is 0.340 underground / 0.247 ground (1,580 / 1,112 LRT trips).
By path type (underground, central; LRT trips ÷ 2022 transit trips): direct LRT 90 pairs,
4,174 trips → 1,580 (0.38); Metronit→LRT 102 pairs, 1,611 → 570 (0.35); bus→LRT 48 pairs,
815 → 283 (0.35); LRT→Metronit 81 pairs, 427 → 213 (0.50); Metronit→LRT→Metronit 110 pairs,
3,386 → 425 (0.13); pairs needing a bus at both ends next to nothing. Boardings by station
area (underground / ground): Hamifrats 995 / 595, Namal-Giborim 747 / 678, Hecht-Shprintzak
391 / 303, Bat Galim 353 / 255, Tirat Carmel 251 / 161; the largest pair flows are Bat Galim
→ Matam 122, Hecht-Shprintzak → Matam 116, Tirat Carmel → Matam 104, Nazareth → Lower City
75 (by feeder bus) and Kiryat Bialik → Bat Galim 43 (by Metronit feeder).

Loaded on the trunk links (three hours, central underground): 79–995 trips per
link-direction, largest on Namal-Giborim→Hamifrats down (995), LowerCity→Namal-Giborim down
(799) and Matam→HofCarmel down (678), against today's bus potential movements of 200–2,030
on the same links — a third to 45 % of the bus movements, 84 % on Namal-Giborim→Hamifrats
up (637 against 759) because of the Krayot feeder trips; the ground scenario loads 44–595;
the peak hour (step 27's factor) is 47–588 underground. The low-λ case reaches 1,656 on
Namal-Giborim→Hamifrats down.

**Outputs.** `Output/skims/skim_{mode}_{component}.csv` (ivt, walk, wait, transfers, gc,
status per mode, plus `ivt_scheduled` for bus and `ivt_lrt_only`, `gateway_o`, `gateway_d`,
`legs` for the two LRT scenarios), `skims_area_v2.xlsx` (one sheet per mode × component
plus an `areas` sheet), `skims_area_v2_long.csv`, `skims_summary_by_mode.csv`;
`logit_calibration_car_vs_transit.csv`, `logit_calibration_binned.csv`,
`logit_calibration_by_distance_band.csv`; `lrt_capture_scenarios.csv`,
`lrt_trips_2022_{scenario}_central.csv`, `lrt_share_of_transit_{scenario}_central.csv`,
`transit_share_2022_pivot.csv`, `pair_flows_and_skims_2022.csv`,
`lrt_trips_by_path_type.csv`, `lrt_boardings_by_station_area_central.csv`;
`trunk_link_flows_bus_vs_lrt.csv`; figures `skims_logit_car_vs_transit.png`,
`skims_trunk_link_flows_bus_vs_lrt.png`.

**Limits.** Corridor-internal trips only (both ends among the 25 areas; no external trips,
none to or from outside the study area); 2022 base year, not the 2040/2050 forecasts; no
capacity and no route choice against the parallel bus services that would still run; money
is out of the comparison by decision (flat integrated fare, §6x addendum 4); λ is assumed, not estimated — a
segmented logit on the survey's person-level records (car availability, purpose) is the
next step (`docs/CORRIDOR_DEMAND_TASKS.md` E7); the LRT premium (5 generalized minutes)
and the free LRT–Metronit transfer are assumptions of the same standing; the feeder-bus access assumes the bus stops
at the gateway station; station access / egress walk is the population-weighted
nearest-station walk of §6x, not a per-trip routing.

---

## 7. Output inventory (`Output/`)

*Layout note (21 September 2026).* The products of steps 1–4 (the 2018 activities-file chain, listed first below with bare file names) now live under `Output/historical/ths2018/`; every other path is as written. Notebooks live under `notebooks/current/`, `notebooks/diagnostics/` and `notebooks/historical/` and anchor their working directory to the repository root, so the `Input/…` and `Output/…` paths in this document are unchanged.

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
| `hybrid_taz_prob.csv`, `hybrid_taz_prob_k100.csv` | 778×778 | Step 3 | TAZ-level OD probability matrices of the activities-file chain — **historical** |
| `hybrid_taz_trips.csv`, `submatrices/hybrid_taz_trips.csv` | 778×778 / 119×119 | Step 3 | Hybrid as average-weekday AM-peak trips, full area and sub-area |
| `sz_correction_factors.csv`, `sz_correction_factors_k100.csv` | 36×36 | Step 3 | R_AB tables |
| `hybrid_taz_cv_results.csv` | k-grid | Step 3 | Route-A validation table |
| `prob_gs_*.csv`, `hybrid_gs_*.csv`, `gs_correction_factors.csv` | 25×25 | Step 4 | GS-level survey/cellular/hybrid matrices, λ table, CV results, correction factors |
| `hybrid_taz_prob_gs.csv`, `hybrid_taz_trips_gs.csv` | 778×778 | Step 4 | TAZ matrices calibrated through GS zoning |
| `ths2017/matrix_day{1,2}_*.csv`, `ths2017/matrix_avg_*.csv` | observed zones (trips-file zonation) | Step 5 | Day × mode and day-averaged matrices from the THS 2017 trips file |
| `ths2017/study_taz/matrix_avg_*` | 778×778 / 36×36 / 25×25 | Step 5 | Averaged trips-file matrices converted to the study TAZ / SZ_NEW / GS systems |
| `ths2017/study_taz/hybrid_*`, `*_correction_factors.csv` | various | Step 6 | Hybrid products on the trips-file source (SZ/GS hybrids, TAZ matrices, trips) — **historical**; TAZ trips do not reproduce the superzone blocks (Step 19) |
| `ths2017/study_taz/submatrices/*` | 28×28 areas | Step 6 | Sub-area matrices aggregated to the 28 named areas (205 TAZs, LRT-corridor flags in `area_legend.csv`) |
| `ths2017/tests/*.csv` | various | Step 12 | Cosine / GEH similarity tests: headline summary, per-origin cosine, permutation null, scale audit, GEH pass rates by level / flow band / corridor class, 28-area cells |
| `ths2017/tests/ks*.csv` | various | Step 13 | KS tests: trip length distributions (all / off-diagonal / per origin / corridor class), flow concentration, distance-proxy calibration |
| `ths2017/tests/mssim_*.csv` | various | Step 14 | MSSIM tests: index by level / window / scale / ordering with term decomposition, broken-correspondence null, per-origin and superzone-block local SSIM, corridor classes |
| `ths2017/two_mode/*.csv` | 778×778 / 36×36 / 28×28 | Step 15 | Survey-only two-mode matrices (car, transit) with the bus part calibrated to RavKav × OnBoard per origin × segment; binary-guard / all-RavKav / uniform variants; calibration tables incl. `bus_calibration_factors_segments.csv` and the threshold sweep; mode shares |
| `forecast_taz/*` | 778×778 / 36×36 / 28×28 per scenario-year | Step 23 | Demographic-reference matrices 2040 / 2050 × BU / HS (car, transit, taxi-type, total), margins, checks, corridor profiles; dry run only until the LFS scenario files are pulled |
| `final_2022/*` | 778×778; long | Step 22 | **Deliverable matrices**: car, transit (bus + rail), total, taxi-inclusive variants, long format, manifest and summary |
| `ths2017/three_mode_2022/*.csv` | 778×778 / 36×36 / 28×28 | Steps 16–18, 20 | **Current 2022-base layers** car / bus / taxi / rail (demographic growth, RavKav anchor, rail ridership series), `all_modes_2022_taz.csv`, TAZ growth factors, summaries; corridor link profiles (three-hour potential movements), the comparison with the ticketing profile, and the peak-hour factors and peak-hour link profiles |
| `ths2017/tests/hybrid_sz_conservation_*.csv`, `ths2017/study_taz/hybrid_taz_{trips,prob}_balanced.csv` | 3 / 12 rows; 778×778 | Step 19 | Superzone conservation test of the TAZ hybrids and the jointly-constrained rebalanced primary hybrid |
| `ths2017/tests/pca_car_vs_transit_*.csv` | various | Step 21 | PCA within the survey, car vs transit: overlap by k, RCEV, per-origin displacement and Haifa-bound shares, summary |
| `ths2017/trip_generation_*.csv` | 478 / 35 / 25 rows | Step 7 | Per-person AM-peak generation rates on the trips-file source |
| `bus/bus_stops_taz.csv`, `bus/bus_od_taz_avg.csv`, `bus/bus_boardings_alightings_taz.csv` | 27k stops / 722×711 / 730 rows | Step 8 | RavKav stop tags, average-Tuesday AM-peak bus OD (journey-level), per-TAZ boardings/alightings (leg-level) |
| `bus/bus_probability_matrix.csv`, `bus/bus_od_taz_new.csv`, `bus/bus_od_area_new{,_filtered}.csv` | 594×548 / 722×728 / 28×28, 25×25 | Step 9 | OnBoard destination probabilities; RavKav volumes × OnBoard pattern; area aggregation and noise-filtered version |
| `train/train_od_taz_6_9.csv`, `train/train_od_area.csv` | 19×19 / 25×25 | Step 10 | Train OD 6–9 (2019 smartcards), station TAZs and areas |
| `transit/transit_od_area.csv`, `transit/all_adjusted_area.csv`, `transit/mode_share_area.csv` | 25×25 | Step 10 | Complete transit matrix, adjusted all-mode matrix, mode shares (mixed vintages) |
| `transit/car_other_area_2022.csv`, `transit/all_adjusted_area_2022.csv`, `transit/mode_share_area_2022.csv`, `transit/area_growth_factors_2018_2022.csv` | 25×25 / 28 rows | Step 11 | 2022-leveled base, all-mode matrix, mode shares; per-area growth factors |
| `demographics/scenario_totals_by_class.csv`, `demographics/scenario_comparison_area.csv` | 5 / 28 rows | `Demographic_scenario_comparison.ipynb` | BU vs HS forecast comparison (2040/2050, `Input/Demographic_Forecast/`): totals by corridor/research/study class; per-area growth factors and HS−BU deltas |
| `forecast/all_modes_area_{BU,HS}_{2040,2050}.csv`, `forecast/forecast_margins_growth.csv` | 25×25 / 100 rows | `Forecast_matrices_2040_2050.ipynb` | **Demographic reference on the historical composite `transit/all_adjusted_area_2022.csv`, to be rebuilt from the current base.** Four forecast all-modes AM-peak matrices (2022 composite Furnessed to scenario-year margins: population → origins, employment → destinations, 2020→2022 bridge via the BU-2025 interpolation, new-resident production term for sub-500-population areas); per-area growth factors and margin targets |
| `forecast/share_{car_other,bus,rail}_2022_{raw,smoothed}.csv`, `forecast/share_strata_2022.csv` | 25×25 / 12 strata | `Base_mode_shares_2022.ipynb` | Revealed 2022 modal shares per OD cell (components: car/other + RavKav bus + rail × 54.7/69) and EB-smoothed versions (k = 50, shrunk toward corridor-class × distance-band stratum shares, sum to 1 per cell); stratum behavioral baseline table |
| `forecast/nobuild_{car_other,bus,rail}_{scenario}.csv`, `forecast/lrt_market_flag.csv`, `forecast/lrt_market_{scenario}.csv`, `forecast/lrt_market_summary.csv` | 25×25 ×12 / 25×25 / ×4 / 4 rows | `NoBuild_and_LRT_market.ipynb` | No-build modal matrices (smoothed 2022 shares pivoted onto scenario-year totals; cell shares frozen, aggregate share moves by composition only — falls 8.9% → 7.5–8.0%) and the LRT market: core (both ends corridor) and per-scenario market trips |
| `forecast/lrt_market_tiers_{MainCorridor,FullLength}.csv`, `forecast/lrt_alignment_market_summary.csv` | 25×25 ×2 / 10 rows | `LRT_alignment_markets.ipynb` | Market tiers per OD (2 = core one-seat, 1 = transfer-influenced, 0 = outside) for the two alignment scenarios (`Input/lrt_alignment_flags.csv`: Main = areas 1–13 + influenced 24–28; Full = 1–19, 23), and market counts per alignment × scenario-year with the no-build transit conversion base |
| `corridor_v2/*` | 25×25; link tables | Steps 24, 27, 28 | V2 area matrices per layer, per-route and tree-network link flows (three-hour and peak-hour), route summary, comparison with the 18-area profile; the V2 peak-hour factors; the survey-vs-ticketing comparison on the V2 routes |
| `lrt_v2/*` | 24 stations; 24×24; 10×10 | Step 25 | Station table (CSV + GeoJSON), station distances, station-to-station times for the two scenarios in distance and section form, line profile, representative stations and area IVT |
| `gtfs/*` | 781 rows; area pairs; 15,929 segments | Steps 29–30 | Bus and BRT level of service per TAZ from the national GTFS, the direct-service skim between the V2 areas (scheduled), the intermediates, and the observed skim from the trips routed over the measured link speeds |
| `gc/*` | 25×25; long | Step 26 | Car / bus / LRT skims, LRT access, generalized-cost component table with status, partial GC matrices, cell status, trunk-pair comparison, the data-gap inventory |
| `skims/*` | 25×25 per mode × component; long; 9 trunk links | Step 31 | Complete per-mode skims (car, bus, Metronit, LRT underground / ground) with status, `skims_area_v2.xlsx` and long-format table, the summary by mode; the logit calibration of the cost sensitivity λ against the 2022 flows; the LRT capture scenarios and pair-level flows; the trunk-link loads against today's bus movements |
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

Added after the methodology review of 21 September 2026:

6. **Superzone OD blocks of the TAZ hybrids are not conserved** by the correction-factor
   construction (§6q); use `hybrid_taz_trips_balanced.csv` if a hybrid is needed at all.
   The replicated cellular mapping (§2) also weights each national zone by its number of
   child TAZs inside the within-superzone origin split and the TAZ destination mix; a
   mass-preserving rebuild needs the cellular file (LFS) and the allocation-matrix
   conversion of step 5.
7. **Units of the transit sources are not reconciled.** The OnBoard file gives
   P(alight | board) — whether per boarding leg or per journey is unconfirmed — and it is
   applied to RavKav *journey* row totals; a bus-to-rail traveller may sit in both the
   RavKav bus OD (journey ending at the station stop) and the station train matrix. Both
   are untested. Keep person-journey products (the survey base) and boarding products
   (RavKav, station matrix) separate until an access / transfer allocation links them.
8. **The segmented coverage rule is an assumption with a threshold** (§6m): its bus
   total exceeds both sources and moves by ± 5 % over thresholds 0.3–0.7; the cause of
   sub-0.5 ratios (operator coverage, cash fares, survey over-expansion) is unresolved.
9. **Taxi-type codes 5 / 8** are a separate layer; their exact meaning awaits the survey
   codebook, and they should not be summed into an LRT market by default.
10. **The forecast branch** (`transit/all_adjusted_*`, `forecast/*`) rests on the
    historical 25-area composite, mixes a residents' door-to-door car / other layer with
    all-rider boardings, freezes 2022 modal shares (its 8.9 % → 7.5–8.0 % transit decline
    is composition, not behaviour), smooths shares with k = 50 applied to *expanded*
    volumes (inert for cells of thousands of trips; sampled counts are the right
    information measure), preserves the 155 zero cells of the base under Furness, and
    excludes the 116,473 weighted trips with one end outside the study area and the three
    line areas below 50 observed bus trips. It is a demographic reference, not a forecast
    of LRT demand, and is to be rebuilt from the current base (tasks D1–D4).
11. **Vintage alignment is an assumption**: `(X2025 / X2020)^(4/5)` extrapolates a forecast
    trend to represent 2018–2022; the national rail ratio stands in for local AM change;
    the claim that May 2022 bus ridership was not COVID-suppressed rests on the study
    team's statement and has no evidence in the repository.
12. **Corridor profiles are potential movements** between line areas — three-hour totals
    (§6o) and, since step 20, peak-departure-hour values (§6r) — not passenger loads or
    upper bounds on LRT demand. The peak-hour factors rest on survey departure times
    (car by direction, bus and taxi-type study-area-wide); a boarding-hour factor from
    RavKav is still to be derived.
13. **Similarity tests are diagnostics**: day-to-day agreement of the same households is
    a repeatability reference, not a ceiling (the hybrid exceeds it against the survey by
    construction); a better fit to RavKav after calibrating to RavKav is not validation.
    External counts (Haifa-segment bus loads, Nazareth local vs Haifa-bound services,
    Hamifrats transfers, road screenlines, station boardings) are still absent.

## 8b. Related work — PCA-based analysis and structural comparison of OD matrices

Context for the PCA validation notebooks (`THS_2018_MTX_PCA_vs_cellular.ipynb`,
`THS_2017_PCA_vs_cellular.ipynb`, and the eigenplaces typology `Cellular_eigenplaces_TAZ.ipynb`, all under `notebooks/diagnostics/`), which re-examine the survey↔cellular comparison
through component structure rather than cell-by-cell statistics. The approach is
grounded in four strands of literature:

**1. PCA on OD matrices for estimation and calibration.** The premise that OD
matrices carry a stable low-dimensional structure — the property the PCA notebooks
measure per source (T1) and compare across sources (T2/T3) — underpins a whole line
of demand-estimation work started at TU Delft:
[Djukic, van Lint & Hoogendoorn (TRR 2012)](https://www.researchgate.net/publication/255567936_Application_of_Principal_Component_Analysis_to_Predict_Dynamic_Origin-Destination_Matrices)
represent dynamic OD matrices by a few "demand principal components" and
[use PCA for efficient real-time OD estimation (IEEE ITSC 2012)](https://www.researchgate.net/publication/255567935_Efficient_real_time_OD_matrix_estimation_based_on_Principal_Component_Analysis);
[Prakash, Seshadri, Antoniou, Pereira & Ben-Akiva (TRR 2017)](https://journals.sagepub.com/doi/10.3141/2667-10)
([open PDF](https://dspace.mit.edu/bitstream/handle/1721.1/117154/ReducingthedimensionofonlinecalibrationinDynamicTrafficAssignmentsystems.pdf?sequence=1&isAllowed=y))
calibrate DTA demand inside the PC subspace; [PC-SPSA (Qurashi et al., IEEE
T-ITS)](https://discovery.ucl.ac.uk/id/eprint/10093641/) and
[joint Islands-GA + PC-SPSA calibration](https://www.sciencedirect.com/science/article/pii/S2352146521001320)
made this the standard dimensionality-reduction move in simulation calibration.

**2. Structural comparison of OD matrices — the critique of cell-by-cell metrics.**
A distinct line (largely QUT Brisbane) argues that RMSE/GEH/r neglect matrix
structure — the same motivation as the PCA notebooks, with windowed rather than
spectral instruments:
[geographical-window structural similarity, GSSI (Behara, Bhaskar & Chung, J. ITS 2022)](https://www.tandfonline.com/doi/full/10.1080/15472450.2020.1795651),
[Levenshtein distance for OD comparison (TR Part C 2020)](https://www.sciencedirect.com/science/article/abs/pii/S0968090X19307053),
[local-windows comparison tied to socioeconomic characteristics (J. Adv. Transp. 2021)](https://onlinelibrary.wiley.com/doi/10.1155/2021/9968698).

**3. Phone-derived vs survey OD, compared structurally.**
[A comparative analysis of mobile phone data and travel surveys (*Transportation*, 2025)](https://link.springer.com/article/10.1007/s11116-025-10708-4)
compares MPD and survey matrices with Pearson + MSSIM and finds more consistency at
macro-zone than transport-zone level — the same scale effect and complementarity
conclusion reached here (§4 and the PCA notebooks).

**4. Eigen-analysis of flow matrices as discovery.**
[Lakhina et al. (SIGMETRICS 2004)](https://www.cs.bu.edu/faculty/crovella/paper-archive/sigm04-odflows.pdf)
showed internet OD-flow ensembles have small intrinsic dimension ("eigenflows") —
the cross-domain ancestor of the T1 finding that the cellular matrix compresses to
~40–50 effective components; mobility siblings include
[Eigenbehaviors (Eagle & Pentland)](https://dspace.mit.edu/server/api/core/bitstreams/472df72e-ef98-43aa-8b9c-2ecd6aee7d8d/content),
[Eigenplaces (Reades, Calabrese & Ratti, 2009)](https://journals.sagepub.com/doi/abs/10.1068/b34133t),
and [low-rank forecasting of metro OD matrices](https://arxiv.org/pdf/2101.00466).

Against this literature, the combination used here — spectral comparison of two
*independent sources* (rather than model-vs-observed), formal benchmarks
(permuted-geography null plus the day-to-day internal-consistency ceiling, akin to
test–retest reliability in psychometrics, where Tucker congruence originates), and
the diagonal-ablation decomposition isolating *where* structures diverge — does not
appear assembled in any single prior work. Practitioner validation guidance still
standardizes on the cell-based toolkit (GEH, %RMSE), which is precisely what strand
2 pushes back on.

## 9. Reproduction

```bash
pip install pandas numpy scipy matplotlib jupyter openpyxl pyshp shapely pyproj
git lfs pull --include="Input/*.xlsx,Input/*.csv"   # required since 22 Sep 2026: the top-level Input files are on LFS
git lfs pull            # optional — needed only for the historical cellular chain, the raw RavKav / train files and the 2040 / 2050 zonal forecasts

# current chain (survey-only base; runs on committed inputs and the committed step-8/9/10 outputs)
jupyter nbconvert --to notebook --execute --inplace notebooks/current/THS_2017_two_mode_matrix.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/current/THS_2017_three_mode_2022.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/current/Corridor_flow_profile_survey_2022.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/current/Corridor_profile_hybrid_vs_ticketing.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/current/Corridor_peak_hour_2022.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/current/Final_matrices_2022.ipynb
# demographic reference 2040 / 2050 (needs git lfs pull --include="Input/Demographic_Forecast/Zonal_*.csv"; dry run otherwise)
jupyter nbconvert --to notebook --execute --inplace notebooks/current/Forecast_matrices_TAZ_2040_2050.ipynb
# V2 aggregation, LRT geometry and generalized cost (steps 24–26; step 26 needs git lfs pull --include="Input/BusSpeedData/std_202605.csv" and pip install shapely pyproj)
jupyter nbconvert --to notebook --execute --inplace notebooks/current/Corridor_peak_hour_V2_routes.ipynb          # step 27 first: step 24 reads its factors
jupyter nbconvert --to notebook --execute --inplace notebooks/current/Corridor_flow_profile_V2_routes.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/current/Corridor_profile_V2_survey_vs_ticketing.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/current/LRT_line_stations_travel_time.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/current/GC_data_inventory_and_skims.ipynb
# bus level of service from the national GTFS (step 29; needs git lfs pull --include="Input/GTFS/israel-public-transportation.zip", else a dry run); run it BEFORE step 26, which reads its skim
jupyter nbconvert --to notebook --execute --inplace notebooks/current/GTFS_bus_LOS_TAZ.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/current/GTFS_bus_observed_times.ipynb   # step 30: needs step 29's intermediates and the bus-speed LFS file; run before step 26
jupyter nbconvert --to notebook --execute --inplace notebooks/current/Mode_skims_and_flow_comparison.ipynb   # step 31: needs steps 24, 26, 27, 29, 30

# regression test of the hybrid branch (committed outputs only)
jupyter nbconvert --to notebook --execute --inplace notebooks/diagnostics/Hybrid_superzone_conservation_test.ipynb
# PCA within the survey, car vs transit (trips file + committed keys; needs scipy)
jupyter nbconvert --to notebook --execute --inplace notebooks/diagnostics/THS_2017_PCA_car_vs_transit.ipynb
```

Upstream of the current chain (all in `notebooks/current/`), with the LFS files: `BusRavKav_matrix` → `BusOnBoard_matrix`
(steps 8–9) and `Transit_complete_matrix` (step 10, for the station rail matrix only).
The historical cellular chain (`notebooks/historical/`) is `THS_2018_MTX_weighted` → `THS_2018_MTX_weighted_vs_cellular`
→ `THS_2018_MTX_hybrid` → `THS_2018_MTX_hybrid_taz`, and on the trips file
`THS_2017_trips_matrices` → `THS_2017_hybrid_pipeline`. The forecast notebooks
(`Vintage_alignment_2022` → `Forecast_matrices_2040_2050` → `Base_mode_shares_2022` →
`NoBuild_and_LRT_market` → `LRT_alignment_markets`) reproduce the demographic reference on
the historical composite; they are not part of the current chain until rebuilt.

Each notebook is self-contained (loads its own inputs from `Input/` and writes to
`Output/`); its first cell moves the working directory to the repository root, so the
notebooks can be run from any location inside the repository. Outputs under `Output/` are committed as regular git files (exempted from
LFS in `.gitattributes`), as are the substitute key files under `Input/`.
