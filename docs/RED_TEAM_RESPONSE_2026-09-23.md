# Response to the methodology red-team review — next steps and data needed

*Written 23 September 2026. Responds to the external red-team review of the methodology
(the review text is reproduced in §6 below). Step numbers and sections refer to
`METHODOLOGY.md`; task numbers to `docs/CORRIDOR_DEMAND_TASKS.md`; plan items to
`docs/PLAN_TIGHTENING_AND_SCENARIOS.md`.*

## 1. Verdict

The review's core conclusion and its gate are accepted. The 2022 base is fit for corridor
screening and ranking. The step 31 / 32 LRT numbers are scenario results under assumed
behavioural parameters, not forecasts. `METHODOLOGY.md` §0 already says this, so the review
confirms a self-diagnosis rather than overturning one.

The diagnosis most strongly agreed with is the identification point. The failed
cross-sectional logit (§6ac: λ = −0.011, wrong sign, ρ² 0.003) is evidence that OD-level
cost differences cannot explain observed shares without car availability and purpose. The
response was to assume λ = 0.03 and continue. That is the weakest link in the chain, and the
LRT-versus-bus split then manufactures an LRT share from an uncalibrated 5-minute premium.
The λ range alone moves the underground result from 2,357 to 4,855 trips, wider than the
difference between the underground and ground alignments (3,332 vs 2,544). The behavioural
assumptions currently matter more than the infrastructure question the study is meant to
answer.

### 1a. Where the review is adjusted

| Review finding | Adjustment | Reason |
|---|---|---|
| Money components — BLOCKER | HIGH for the forecast years; not a blocker for the 2022 capture | The fare is flat and integrated, so it cancels within the transit nest. Against the car it is a constant per trip, and an incremental logit pivoted on observed shares absorbs a constant (§6x addendum 4). It becomes real in 2040 / 2050, where destination parking at Matam and the Lower City and any fare change are policy variables, and in any disaggregate λ estimation. |
| RavKav vs OnBoard unit — BLOCKER | Stands, but narrower | RavKav is already a linked-journey product: step 8 links legs by `bus_trip_id`, counts each journey once, and corrected the ×1.52 leg-inflation error (§6f). The unresolved unit is the OnBoard survey's P(alight \| board), applied to those journey totals (§8 caveat 7). |
| External zones — HIGH | Add the market truncation at the same weight | The capture runs on the corridor-internal market: 75,000 trips within the 25 areas out of 184,000 study-area trips; 109,000 intra-area trips excluded; 230,000 trips with one end in the corridor and the other outside (`docs/PLAN_TIGHTENING_AND_SCENARIOS.md` §2, `docs/CORRIDOR_DEMAND_TASKS.md`). That scope cut is a structural omission at least as large as the missing external zones. |
| Hold out part of the counts for validation | Replace with a simpler rule | With the count data the project can realistically obtain, a hold-out is a luxury. The rule is: never feed counts into matrix estimation. The current chain does not, so every count obtained stays independent as long as that rule holds. |

### 1b. What is not redone

As the review says: the THS trip-extraction logic (§2, §6c); the cellular hybrid branch, kept
historical and usable as a coarse diagnostic; the PCA / KS / MSSIM notebooks as regression
records; step 25's running-time model as an interim sensitivity tool; the 2040 / 2050
demographic datasets and the step 23 machinery as scenario inputs.

## 2. The gate, written down

No number from steps 31 or 32 goes into a report as ridership until:

1. step 33 identifies λ from person-level records with the right sign and a plausible value,
   or a stated-preference survey supplies λ and the LRT constant; **and**
2. the rebuilt 2022 base has been compared with at least one independent count on the Haifa
   trunk, by direction and hour, without tuning to it.

Until then every LRT figure is labelled *"scenario result under assumed behavioural
parameters"*, with the λ and premium whiskers attached.

## 3. Next steps — two tracks in parallel

The review's sequence is right in logic, but several items wait on data the project does not
hold. Track A uses only data already in Git LFS and starts now. Track B is the data request,
sent on day one because it gates the longest path.

### Track A — in-house, no new inputs

| # | Work | What it closes | Depends on | Output |
|---|---|---|---|---|
| A1 | **Person-level mode choice (step 33).** Binary car vs transit logit on the survey's AM trip records: car availability from the household file, purpose, age / sex, the step 31 pair skims, distance-band constants. Report λ with its standard error. | E7; the identification test the review asks for. If λ fails again, that result is the documented reason SP data are needed. | `households_with_weights.csv` (LFS), THS codebook | `Mode_choice_person_level.ipynb`; λ replaces 0.03 or the failure is reported |
| A2 | **RavKav leg-level segment loads on the trunk.** Aggregate every leg's physical boarding / alighting stop by stop group along the trunk, by direction and `bus_trip_hour`, weighted by `total_boardings`. | Bus loads per link, direction and hour; the boarding-hour peak factor (B1e); a direct test of the 2–3 × Nazareth-end discrepancy (§6p). Not fully independent of the calibration (RavKav volumes enter step 15), but the leg-level link profile is different information from the journey OD totals. | `Input/BusRavKav/*.csv` (LFS) | `RavKav_trunk_segment_loads.ipynb`; link loads vs step 24 / 31 profiles |
| A3 | **Trip-universe definition, one page.** Person trip, PT journey, boarding leg, transfer; the frame of each source (THS residents door-to-door; RavKav all riders, journey; OnBoard unit pending; rail station-to-station); how external trip ends and the one-end-in-corridor market enter; external zones. | Review blocker on definitions; B1d, B2, B3. Precedes any rebuild of step 15. | nothing | `docs/TRIP_UNIVERSE.md` |
| A4 | **Purpose-segmented fine-zone allocation.** HBW / HBE / other split per superzone pair from the trips file's activity codes; destination proxies per purpose (employment; school enrolment; retail / services) instead of total employment. | Review blocker on the TAZ allocation; A3 in the task list. | THS activity codebook | revised step 15 zone conversion; corridor profiles retested |
| A5 | **TAZ-level capture on the trunk with a walking network** (plan items 3a.2, 3a.3). | E6, A2. The logit is nonlinear in access time, so the area-level average biases the result. | A1 first, so the rerun is done once | `LRT_capture_TAZ_trunk.ipynb` |

### Track B — data requests (see §4)

Critical items, in order of value: the OnBoard survey unit; bus counts on the Haifa trunk;
the branch geometry and operating plan; the national model's mode-choice parameters.

### Then, in this order

1. **Rebuild step 15** with a coverage model in place of the 0.5 threshold, using the
   provider's answer on operators and cash fares (B1c). Publish low / base / high bus
   matrices, not one.
2. **Rerun steps 16–22** with a direct 2018 → 2022 demographic change where the CBS data allow
   it, and rail scaled to Haifa station boardings rather than the national series.
3. **Validate the rebuilt base** against the track-B counts. Do not tune to them.
4. **Rebuild the skims** (steps 25–26, 29–31): branch geometry, operating plan, the bus
   network of the opening year, money components for the forecast years (parking by
   destination, fare policy), several representative speed days.
5. **LRT preference term.** From the SP survey if collected; otherwise anchored on the
   Metronit 2013 before / after and the Red Line first-year outturn, with a formal new-mode
   treatment rather than the binary split at equal cost.
6. **Strengthen step 23:** purpose-segmented margins, attraction variables by employment type
   and education; fix the taxi Furness non-convergence (structural zeros); future Do-Minimum
   and Do-Something skims with a congestion uplift.
7. **Rerun steps 31–32 with a designed uncertainty experiment.** The chain reruns in about
   ten minutes, so a factorial design over the six or seven main factors (coverage threshold /
   model, TAZ allocation, LRT regime, λ, premium, land-use scenario, bus-network response)
   is affordable and more informative than a Monte Carlo at this stage. Report central, low
   and high LRT boardings and critical-link loads; once assignment exists, distinguish unique
   passengers, boardings, transfers and maximum sectional load.

## 4. Data needed

| Item | What it resolves | Who holds it | Priority |
|---|---|---|---|
| OnBoard survey codebook and method note: unit per row (leg or journey), sampling frame, expansion | Blocker on the transit unit; whether step 9 blends legs with journeys | Survey contractor or Ministry of Transport | **Blocker** |
| RavKav extract metadata for May 2022: operators covered, cash and unvalidated boardings, alighting inference method | Cause of the sub-0.5 coverage ratios; replaces the threshold with a coverage model | RavKav data provider | **Blocker** |
| Bus passenger counts on the Haifa trunk by section, direction and hour (APC or manual); Hamifrats terminal; Nazareth local vs Haifa-bound services | Independent validation of the transit base and the Nazareth discrepancy | Operators via the Ministry, or a commissioned count | **Blocker** |
| THS 2017/18 household and person file with codebook: cars, licences, income, activity codes | Person-level λ, purpose segmentation, car-availability segmentation | In LFS; codebook from the survey owner | **Blocker**, largely in hand |
| National transport model: mode-choice parameters, VOT, walk / wait weights, its 2040 / 2050 matrices for the study superzones | Transferred λ if estimation fails; external check on step 23 (D4) | Ministry of Transport model custodian | High |
| LRT branch alignments, station points, underground / ground regime per section, headways, through-running pattern | Replaces the feeder composite for 15 of 25 areas; the mixed-alignment case (E1) | Planning team | High |
| Bus network plan for the opening year: lines truncated to feeders, lines kept in parallel | Route competition in the capture (S3) | Planning team | High |
| Israel Railways station boardings, Haifa stations, 2018 / 2019 / 2022 | Local rail vintage instead of the national ratio; validates the rail layer | Israel Railways or CBS | High |
| CBS population and employment by statistical area, 2018 and 2022 | Direct 2018 → 2022 change instead of the extrapolated 2020 → 2025 trend (§8 caveat 11) | CBS, public | High |
| Road traffic counts on two or three corridor screenlines, AM by direction | Validates the car layer and the car peak factors (B1) | Netivei Israel, Haifa municipality | High |
| Metronit ridership before and after 2013; Red Line first-year ridership vs its forecast | Anchors the LRT preference term until SP data exist | Operators, Ministry, published reports | High |
| Stated-preference survey, 300–500 corridor travellers: LRT vs bus vs car, with in-vehicle time, access, wait, transfer, fare, reliability and seat attributes | Calibrated λ, LRT constant, transfer penalties; the proper fix for the new-mode problem | New collection | High, longest lead time |
| Cellular product trip definition: dwell and minimum-distance thresholds | Whether cellular can arbitrate short-trip volumes (B1) | Cellular provider | Medium |
| Parking supply and price at Matam, the Lower City and Bat Galim, current and planned | Car cost component for the forecast years (S5) | Municipality, planning team | Medium |
| Google Distance Matrix sample, ≈ 40 pairs, Tuesday 07:30 | 2026 car time uplift on the 2017/18 survey times (E5) | Public API | Medium |
| OSM footway network for the study area | Walking access to stations and stops (E6) | Public | Medium, in-house |

## 5. Status table after this response

| Use | Now | After the gate in §2 |
|---|---|---|
| Compare broad corridor markets | Yes | Yes |
| Compare approximate LRT alignments | Yes, with uncertainty caveats | Yes |
| Identify areas with strong potential demand | Yes | Yes |
| Exploratory LRT capture scenarios | Yes, labelled as such | Yes |
| A single forecast ridership number | No | With the low / base / high band |
| Vehicle / frequency sizing from modelled load | No | After assignment (step 4 of §3) |
| Economic appraisal | No | After the full chain of §3 |
| Alternatives differing by 10–20 % | Not reliably | After the uncertainty experiment |
| Defensible 2040 / 2050 patronage | No | After steps 6–7 of §3 |

## 6. The review as received

> ### Executive assessment
>
> The project is currently strong enough for corridor screening, relative comparisons,
> diagnostic analysis, and order-of-magnitude demand assessment. It is not yet
> methodologically strong enough to treat the Step 31/32 LRT ridership outputs as formal
> forecasts, particularly for design capacity, service planning, economic appraisal, or
> comparing relatively close alternatives. The work does not need to be restarted from
> Step 1. The main components that need to be revisited are Steps 8–9, 15–16, the TAZ
> disaggregation, Steps 26 and 29–31, and then Step 32. Step 23 also needs strengthening
> before the future scenarios are treated as forecasts.
>
> ### Findings (priority — issue — required adjustment)
>
> - **BLOCKER** — No genuinely independent validation of the 2022 base demand; most tests
>   compare one survey day against another, one source against another, or a calibrated
>   product against a source involved in its construction. — Assemble independent
>   screenline / link / station observations reserved for validation; validate direction ×
>   time period × geography.
> - **BLOCKER** — The unit represented by the OnBoard records is unresolved (bus leg vs
>   complete journey). — Resolve from metadata before another calibrated bus matrix is
>   accepted; define person-trip, PT journey, leg and transfer throughout.
> - **BLOCKER** — The bus volume calibration rule is heuristic and asymmetric (0.5
>   RavKav / survey threshold); the final total can exceed both sources; sensitivity
>   117.5k–131.7k. — Replace with an explicit coverage model or derive coverage classes
>   from operator / route / ticketing completeness; propagate low / base / high.
> - **BLOCKER** — The fine TAZ distribution is weaker than the coarse OD matrix, yet the
>   LRT calculation is highly sensitive to fine spatial location; population / employment
>   allocation without trip purpose. — Rebuild fine-zone allocation by purpose and
>   land-use category, constrained by observed stop boardings / alightings.
> - **HIGH** — The demand universe is inconsistent between sources (THS residents
>   door-to-door; RavKav riders boarding inside the network; rail another frame; external
>   trip ends excluded). — Define one modelling universe and external-zone treatment.
> - **HIGH** — The 2018 → 2022 uplift is weakly anchored temporally (2020 → 2025 trend
>   extrapolated; rail on a tiny sample scaled by the national series). — Reconstruct 2018
>   and 2022 directly; validate rail with station counts.
> - **BLOCKER** — The generalized-cost specification removes money components; a flat
>   fare does not cancel in car vs transit; parking and operating cost vary by mode and
>   destination. — Restore fare, car operating cost, parking, tolls; segmented VOT;
>   reliability / crowding where data permit.
> - **BLOCKER** — The RP mode-choice calibration failed, but the methodology proceeds with
>   λ = 0.03, λ_T = 2λ and a 5-minute LRT premium; the sensitivity tests show λ changes
>   ridership more than some infrastructure scenarios. — Treat the failed calibration as
>   a stop condition; re-estimate at person / trip level with car availability, purpose,
>   household characteristics and accessibility; combine RP with SP.
> - **BLOCKER** — The LRT-vs-bus submode equation contains a new-mode problem: at equal
>   adjusted cost the LRT takes ≈ 50 % of transit; the premium is an uncalibrated ASC. —
>   Calibrate an LRT ASC from SP / RP or apply a formal new-mode method.
> - **HIGH** — The PT supply representation is too approximate for line ridership
>   (synthetic transfers, no branches, simplified access, fixed parallel bus system). —
>   Build a multimodal or restricted-corridor PT assignment with access, station choice,
>   frequencies, transfers, feeders and competing routes.
> - **HIGH** — The 2040 / 2050 forecast freezes travel behaviour and LOS. — Rename the
>   outputs "demographic growth scenarios"; build future Do-Minimum and Do-Something
>   networks / skims.
> - **HIGH** — Step 23's trip-end growth model is too aggregate for transformational
>   land-use scenarios (R² ≈ 0.5; same structure across modes; destination behaviour
>   frozen). — Segment by purpose; improve attraction variables; treat the taxi Furness
>   non-convergence as a QA failure.
> - **MEDIUM / HIGH** — Peak-hour conversion is not equivalent to peak-link loading. —
>   Time-sliced loading or departure times propagated along paths.
> - **HIGH** — Uncertainty is tested piecemeal. — A structured uncertainty experiment
>   across the full pipeline with distributions / intervals for total LRT ridership and
>   critical-link demand.
>
> ### The most important conceptual problem
>
> Three levels of evidence quality — observed, modelled-but-defensible, and
> weakly-identified / assumed — are blended into a single ridership number, and the final
> LRT forecast is especially sensitive to the third. Additional PCA / MSSIM / KS tests will
> not solve this; the next marginal hour should go to validation data and behavioural
> calibration.
>
> ### Step 31
>
> A negative or approximately zero λ says that aggregated OD-level generalized-cost
> differences do not explain the observed transit shares; the specification or aggregation
> level is inadequate (ecological aggregation). The overall transit-vs-car incremental step
> is conceptually close to the standard incremental logit; the LRT-vs-existing-transit split
> is not, because there is no observed LRT share to pivot on. The ≈ 3.3k 2022 LRT trips
> (underground) should be described as scenario results under assumed behavioural
> parameters.
>
> ### Recommended sequence
>
> 1. Resolve the data definitions. 2. Create an independent validation dataset. 3. Rebuild
> Step 15. 4. Re-run Steps 16–22. 5. Upgrade the supply / skims. 6. Replace Step 31's
> behavioural calibration. 7. Strengthen Step 23 and rerun the future scenarios. 8. Only
> then rerun Steps 31–32 and propagate uncertainty end to end.
>
> ### What does not need to be redone
>
> The THS trip-extraction logic; the cellular-hybrid branch (historical); the PCA / KS /
> MSSIM notebooks (kept, not refined further now); Step 25's running-time model (interim);
> the 2040 / 2050 demographic datasets and Step 23 machinery (scenario inputs).
>
> ### Bottom line
>
> The central problem is no longer how to construct an OD matrix; it is identification —
> proving the model explains observed transit flows and mode shares before predicting
> behaviour for a mode that does not yet exist. The critical chain: validated 2022 OD →
> validated PT assignment → locally calibrated behavioural model → new-mode treatment →
> future Do-Minimum / Do-Something supply → uncertainty propagation → LRT forecast.
