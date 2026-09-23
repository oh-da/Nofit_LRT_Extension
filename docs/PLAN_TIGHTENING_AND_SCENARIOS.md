# Plan — tightening the LRT capture and the scenarios to test

Written 22 September 2026 for the next working day. State of play, what moves the number,
what to do about it, and which scenarios to run on top. Task numbers refer to
`docs/CORRIDOR_DEMAND_TASKS.md`; step numbers and sections to `METHODOLOGY.md`.

## 1. Where the capture stands

*Updated 23 September 2026 after the rerun of steps 15–32 with the corrected mode codes and
the rebuild of step 15 on RavKav's own alightings (METHODOLOGY §0 "Rerun" and "Rebuild");
the earlier values are in the git history.*

Corridor-internal market (both trip ends in the 25 V2 areas, 06:00–09:00, 2022): 56,445 car,
14,133 transit (bus + Metronit + rail), 720 taxi-type trips. Central case of steps 31 / 32
(λ = 0.03 per generalized minute, λ_T = 0.06, LRT premium 5 generalized minutes, free
LRT–Metronit transfers, money out of the comparison, 5-minute headway):

| LRT scenario | IVT trunk pairs (min) | GC trunk pairs | LRT trips 2022 | share of transit | HS 2050 |
|---|---|---|---|---|---|
| all underground (calibrated) | 13.8 | 46.6 | 4,250 | 28 % | 6,516 |
| all ground (calibrated) | 22.4 | 55.2 | 3,207 | 21 % | 4,868 |
| design regime 50 km/h + 10 s (ceiling) | 8.8 | 41.6 | 5,095 | 36 % | 7,899 |

The capture rate is fixed by the skims, so the forecast years only scale the market
(transit × 1.30–1.50). Busiest link Namal-Giborim → Hamifrats towards the Krayot: 1,671 trips
in three hours today (764 peak hour on the network bus factor of 0.457), 2,617 by HS 2050.
(IVT and GC are transit-trip-weighted over the trunk pairs and moved with the weights.)

## 2. What moves the number, ranked

Effect on the 2022 underground central figure (4,250):

| Driver | Range today | Status | What closes it |
|---|---|---|---|
| Cost sensitivity λ | 3,161–6,028 (λ 0.05–0.02) | **assumed 0.03, now supported by the person-level estimate 0.035 (0.002–0.068), step 33** — the choice-rider λ is not identified | SP survey; TAZ-level skims to widen the estimation sample (E6) |
| Station access | 18 of the 17-minute median LRT–bus gap on the trunk is the access difference (13.2 vs 4.8 min walk) | derived, but crude: straight-line × 1.3 walk, population-weighted per area, feeder to the gateway area centroid | walking network, feeder buses truncated at stations, TAZ-level capture on the trunk (E6) |
| LRT premium | 3,406–5,232 (0–10 gen-min) | **assumed** | anchor on the Metronit's 2013 before / after ridership; Red Line first-year ridership vs forecast |
| Free LRT–Metronit transfer | material: the Metronit-fed pairs now carry 1,336 of the 4,250 | decision | none needed; keep as a stated assumption |
| Bus generalized cost | **ranged 2026-09-23: 4,250–4,879 underground (13–16 % across the three regimes) under the best-line wait rule** | 178 pairs without a direct service now state 1 transfer (matches step 31); the 7-minute door-to-door overhead itself still not in the bus GC | GTFS path building for the 178 pairs, so the wait/transfer figures are derived rather than assumed there (E3) |
| Branch geometry | 15 of 25 areas reach the LRT by feeder | **missing** | alignment and stations of the T1 / T2 / T3 branches and Hamifrats → Tsomet Kiryat Ata (E1) |
| External and intra-area trips | corridor-internal market is 75,000 of 184,000 study-area trips; 109,000 intra-area trips excluded | scope | TAZ-level capture with station catchments (A2) |
| Skims in the forecast years | held at 2026 | scope | congestion uplift on car times (E5); bus network of the LRT year |
| 2022 car base | on closed cordons the residents' car layer is 0.6–0.9 of the counted vehicles where the crossings are mostly counted; direction agrees except at Haifa city; the road peak hour is 0.38–0.43 of the three hours against the survey's 0.62 (step 36, §6ah) | validated to the order expected; the peak-hour factor is the open item | link-level check with an assignment; count coverage on the Krayot and Nazareth cordons |
| 2022 transit base | survey vs ticketing within ± 15 % along the whole line since step 15 was rebuilt on RavKav's own alightings; on the Nazareth branch the two ticketing readings (OnBoard pattern 2.5 × the survey, RavKav alightings 0.36 ×) bracket it | unvalidated against a count | Rav-Kav boardings by stop group on the trunk links; one car screenline (C3) |

The first three are perception parameters that no amount of skim precision fixes; the plan's
own caveat (`docs/LRT_CAPTURE_PLAN.md` §3). The branch geometry and the external trips are
the two structural gaps, and they are the two that need inputs from the client side.

## 3. Tightening — the work, in order

### 3a. Needs no new inputs (start tomorrow)

1. **λ from the person records (E7).** Binary logit car vs transit on the AM trips of
   `Input/THS_2017-2018/trips_ths_2017.xlsx` at person level, with car availability (household cars per
   licence, from the household file if in LFS, else the survey's own fields), purpose,
   age / sex, and the pair's `GC_bus − GC_car` from the step 31 skims; distance-band constants.
   Report λ with its standard error; if the sign is right and the value plausible, replace
   the assumed 0.03 in steps 31 / 32. If not, the transferred value stands and the estimation
   goes in the report as the reason. Notebook: `Mode_choice_person_level.ipynb` (step 33).
   *Done 23 September 2026 (METHODOLOGY §6ae): λ = 0.035 (0.002–0.068), right sign — the
   central 0.03 stands, the range 0.02–0.05 is narrower than the estimate's interval, and the
   choice-rider λ (licence holders in car-owning households) is not identified. Found on the
   way: mode codes 4 / 5 were swapped in steps 15–32 (Matronit in the taxi layer); the chain
   was rerun with the corrected codes the same day, and §1 above carries the rerun values.*
2. **Walking network for access (E6).** Fetch OSM for the study area, route every V2 TAZ
   centroid (and, for the trunk, every TAZ) to its nearest station and nearest served bus stop
   on the footway network; replace the 1.3 detour factor. Same notebook as 3.
3. **TAZ-level capture on the trunk (A2 / E6).** Run the step 31 pivot on the 174 TAZs of the
   V2 key instead of the 25 areas: the bus LOS and walk per TAZ exist (step 29), the LRT
   access per TAZ exists (`lrt_access_taz_v2.csv`), the 2022 TAZ matrices exist. The logit is
   nonlinear in access time, so averaging the walk before applying it biases the area-level
   result; expect more capture within 500 m of stations and less beyond 1.5 km. Notebook:
   `LRT_capture_TAZ_trunk.ipynb` (step 34).
4. **Bus GC with the survey overhead (E3).** Add the 7-minute door-to-door overhead as a
   wait / transfer allowance in the bus skim, or set the wait to the headway of the best
   single line rather than half the pooled headway; rerun steps 31 / 32. Small change in
   step 26's GTFS block. *Done 2026-09-23 (METHODOLOGY §6x addendum 6): the best-line-headway
   half of this item is now a `BUS_WAIT_RULE` switch (`'half_headway'` default / `'best_line'`)
   — central-case LRT capture rises 4,250 → 4,879 underground, 3,207 → 3,733 ground, 5,095 →
   5,777 design regime (13–16 %) under `'best_line'`, reported as an alternative
   (`Output/skims/bus_wait_best_line/`), not adopted as the default. The 178 non-direct pairs'
   transfer count was also fixed to match what step 31 already assumed (no capture change).
   The door-to-door overhead itself (as a wait/transfer addition, distinct from the headway
   rule) is not yet built.*
5. **Realistic speed regime (§6w).** Design speed with a 30–40 s acceleration and braking
   allowance per stop (constant in step 25), and a **mixed alignment** with the Haifa core
   underground (about S05–S14) and the rest at ground level. This is the case a decision
   would be made on; the two pure regimes and the 50 km/h ceiling bracket it.
6. **Headway 7.5 and 10 minutes** (step 26 constant), to show the dependence on the 5-minute
   assumption.

### 3b. Needs inputs from the client side

7. **Branch alignments and stations (E1)** — T1 Kiryat Ata → Nazareth, T2 Krayot, T3 Kiryat
   Yam, and Hamifrats → Tsomet Kiryat Ata; the regime (underground / ground) per section;
   the through-running pattern between branches. Until then: synthetic branch alignments
   along the V2 route orders with the calibrated function, flagged as such.
8. **Bus network of the LRT year** — which lines are truncated to feeders and which keep
   running in parallel. Today's capture assumes full competition (conservative).
9. **Rav-Kav boardings by stop group on the trunk (C3)** — to validate the 2022 transit base
   and the ticketing / survey factor on the Nazareth branch; one car screenline count.
   *Boardings by stop and TAZ for 2025 are now in hand (step 34, `Output/ravkav_2025/
   boardings_by_stop_2025.csv`, with the transfer tag); alightings are not, so a link load
   still needs an alighting inference or a count. The car screenline is still to obtain. Step
   15 now rests on RavKav's own 2022 alightings rather than the OnBoard pattern (23 September,
   METHODOLOGY §6m), which settled the Haifa-segment comparison and left the Nazareth branch
   as the one place a count is decisive.*
   *Road counts received 23 September (`Input/Network_with_Counts/`) and used in step 36 (§6ah):
   the car layer is validated to the order expected on the cordons that are mostly counted; a
   bus passenger count on the trunk and the Nazareth branch is still the missing item.*
10. **Parking and car policy** — not needed for the fare (flat, out of the comparison) but
    a destination-parking policy at Matam and the Lower City would enter as a car
    constant per destination in the 2040 / 2050 runs.
11. **The Metronit's 2013 before / after ridership** and any Red Line ridership-vs-forecast
    figure, as the anchors for the premium.

## 4. Scenarios to run (once 3a is in place)

| # | Scenario | Purpose | Where |
|---|---|---|---|
| S1 | Mixed alignment (core underground, rest ground) with the acceleration allowance | the realistic case | step 25 → 26 → 31 → 32 |
| S2 | Headway 5 / 7.5 / 10 min | operating-plan sensitivity | step 26 constant |
| S3 | Parallel buses kept vs truncated to feeders | bus-network response; upper bound on capture | step 31: remove the competing direct-bus alternative on trunk pairs |
| S4 | Synthetic T2 / T3 branches (and T1 to Kiryat Ata) | what the branches add; replaces the feeder composite for 15 areas | step 25 geometry + step 31 |
| S5 | Car congestion uplift 2040 / 2050 (+ 20–30 % on car IVT) and parking at Matam / Lower City | car side of the forecast years | step 32 |
| S6 | Park-and-ride at Tirat Carmel and Hamifrats | access policy at the ends | step 31 access component |
| S7 | Transit-oriented land use at stations (HS variant) | demographic side | step 23 margins |
| S8 | Whole-day expansion with the ticketing daily profile | ridership and revenue are daily numbers | new step on the Rav-Kav profile |
| S9 | λ, premium, transfer ranges (done) kept as whiskers on every scenario | uncertainty band | steps 31 / 32 cases |

Every scenario is reported with the same three lines (underground / ground / mixed) and the
same whiskers, on the same market, so the comparison is between scenarios and not between
assumption sets.

## 5. Suggested order for tomorrow

1. Person-level λ (3a.1) — a morning's work; it decides whether the central case changes.
2. Walking network + TAZ-level trunk capture (3a.2, 3a.3) — the afternoon; the largest
   likely revision of the number.
3. Realistic regime and headway sensitivities (3a.5, 3a.6) — quick reruns of the chain.
4. Bus GC overhead (3a.4) — quick; report before / after.
5. Ask for the inputs in 3b, in that order of value: branch geometry, bus network of the LRT
   year, Rav-Kav boardings.

The chain to rerun after any change: step 25 → 26 → 31 → 32 (`METHODOLOGY.md` §9), about
ten minutes; the report (`reports/…docx`, revision 1.3) takes its numbers from steps 31 / 32.

## 6. Open questions for the client side

- Acceleration / braking allowance to use with the 50 km/h design speed (30–40 s per stop is
  the usual range; the calibrated forms imply 40–65 s including dwell).
- Which sections of `hf_lrt_3` are planned underground.
- The operating plan: headway per branch, through-running, and the bus lines to be truncated.
- Whether a Metronit ridership series before and after 2013 can be obtained.
