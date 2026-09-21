**Nofit LRT demand methodology review**

Technical assessment and recommended research programme • 21 September 2026

**Overall assessment.** The repository has a useful data preparation and diagnostic foundation. Its strongest contributions are the investigation of journey identifiers, disclosure of inconsistent source definitions, use of household rather than cross-day splits for bus calibration, and recognition that BU and HS require separate forecasts. I would use the outputs for exploratory analysis and identifying data gaps. I would not yet treat either matrix branch as a validated estimate of corridor demand, or use the current corridor profiles as forecasts of passengers on the LRT.

My preferred starting point is the latest survey-based branch, with separately reconciled transit observations. The cellular hybrid should remain a sensitivity case until the cellular trip definition, expansion, and spatial allocation have been resolved. This preference is provisional: the survey expansion also requires external checks.

The README's explicit goal is a 06:00–09:00 OD matrix for the 778-zone study area. The later inventory extends the work into demographic forecasts and LRT markets. These are two deliverables with different completion criteria: first a credible travel-demand baseline, then an estimate of the share and paths using the proposed service. A matrix can be useful for the first without establishing the second.

This assessment covers the complete text, tables and figures of the five supplied files. The notebooks, raw records, matrices, codebooks, `TRANSIT_DEMAND_PLAN.md` and `CORRIDOR_DEMAND_TASKS.md` were not supplied. Numerical findings below are reported results, except for explicitly identified mathematical examples. Potential implementation problems are distinguished from demonstrated properties of the documented methods. The international research and guidance are methodological references; they do not establish compliance with Israeli appraisal requirements.

**1. Assessment of each supplied file.** The files describe successive stages of the work, and should be read as a development history until a current authoritative pipeline is declared.

| File | What is useful | What needs changing |
|---|---|---|
| `README-2.md` | Detailed notebook and output inventory; records negative findings as well as successes. | The opening diagram still describes the older activities/cellular chain, while later entries describe a new survey-based baseline. Identify the accepted baseline, its date and status, and which forecasts consume it. |
| `METHODOLOGY.md` | Substantial audit trail, explicit formulas, and clear accounts of data corrections. | Early claims about diagonal-only divergence and reliable cellular detail survive alongside later contradictory evidence. The reproduction instructions cover only the old four-notebook chain. Separate the current specification from historical experiments. |
| `Nofit_LRT_OD_Demand_Report.docx`, 8 September | Explains the linked-journey correction and makes the vintage and hub-attribution problems visible. | Its confidence in ticketing coverage and the hybrid is overtaken by later findings. The 0.91 ticketing/survey ratio does not establish equivalent measurement frames or a real decline. The reported all-mode shares mix doorstep and boarding locations. |
| `Survey_Matrices_Car_Bus_Rail_Report.docx`, 20 September | Better separation of car/bus/rail; household-split calibration; explicit synthetic TAZ detail; important coverage diagnosis. | Similarity tests mostly assess the earlier matrices, not independent performance of the final three-mode baseline. The coverage rule, taxi grouping, and claims of a day-to-day agreement ceiling need revision. |
| `Demographic_Scenario_Comparison_Report.docx` | Strong evidence that growth location matters; four scenario-year matrices are justified. | Equal aggregate margins are insufficient to establish equivalence for station access or service response. Major land-use changes require new OD patterns, not just new margins. The two scenarios also differ in total growth. |

**2. The forecast branch needs an explicit decision.** The README calls the cellular hybrid the primary TAZ product. The September 20 report builds a cellular-free survey baseline. Meanwhile, the methodology's forecast inventory still describes a 25-area base made from `car_other` plus ticketing bus and station rail. The supplied documentation therefore does not demonstrate that the 2040/2050 products incorporate the latest survey-based work.

Before interpreting forecasts, produce a lineage table linking every published result to its exact base matrix, geography, mode definition, reference period, code revision, and calibration inputs. Rebuild all downstream outputs from the selected branch. Keep historical products with unmistakable status labels. The 25 GS zones and the 25 retained research areas are different geographies despite equal matrix dimensions; identifiers and zone-system metadata must prevent accidental joins.

The older 276,355-trip result is a 25-area, all-mode composite. The latest full-study three-mode result is 1,489,352 trips, calculated from the reported 1,353,798 car, 131,504 bus including taxi-type, and 4,050 rail. These totals have different domains and mode coverage and should not be presented as a before-and-after comparison.

**3. Agree what one trip represents before combining sources.** The household survey describes activity-to-activity person journeys. Bus ticketing describes first boarding to final bus alighting. Rail ticketing describes station pairs. The population frames differ as well: surveyed residents versus recorded riders. Consequently, adding these matrices does not automatically produce one coherent person-trip population.

Two specific checks are essential. First, establish whether the OnBoard conditional probabilities describe a single boarding leg, a linked bus journey, or the complete activity-to-activity journey. As documented in methodology §6g, they are boarding-to-alighting probabilities, but they redistribute linked-journey totals. If they describe legs, the multiplication preserves totals while potentially assigning journeys to intermediate transfer points. Second, test whether a bus-to-rail traveller appears in both the bus journey matrix and the station rail matrix. A correct within-bus journey deduplication does not resolve cross-mode duplication.

Maintain distinct products for complete person journeys and for boardings, alightings and onboard loads. Link them through access, egress and transfer assumptions. DfT explicitly treats complete journeys and mixed-mode legs separately, including the bus-to-rail double-counting problem. [TAG M3.2, §2.1.9–2.1.10](https://assets.publishing.service.gov.uk/media/666af32effd07973a043d110/tag-unit-m3.2-public-transport-assignment-modelling.pdf)

For this project, a practical implementation is to retain the survey geography for person-trip origins while using stop observations to constrain boarding demand through a small catchment/transfer allocation model. When the necessary allocation evidence is unavailable, publish separate doorstep and station-based estimates. A hub's apparent 74% transit share is not a defensible behavioural probability for residents of that zone. Blending boarding and household origins changes the meaning of the matrix; aggregation alone does not guarantee compatibility.

**4. The cellular replication caveat is a substantive method problem.** Methodology §2 assigns each coarse cellular flow at full value to every child TAZ pair. Section 6j reports that this replicated version totals 6.4 times the mass-preserving cellular allocation. Later tests correct the volume allocation, but the documentation still describes the earlier hybrid as inheriting the replicated structure.

Row normalization removes the overall row scale, but it does not generally remove destination bias. A coarse destination split into more child zones receives more copies of its flow. For example, equal flows to two coarse destinations become aggregate probabilities of one-third and two-thirds if one destination has one child and the other has two. This is a mathematical consequence of replication, independent of the empirical data.

Use a nonnegative allocation matrix on each trip end whose shares sum to one within every source zone:

\[
T_{\mathrm{target}}=S_o^\top T_{\mathrm{source}}S_d.
\]

Account explicitly for destinations outside the target geography. Verify conservation of each source OD block, not only the grand total. Recompute comparisons and any retained hybrid after changing the mapping.

The 2636→1250→778 chain also discards native survey detail. Investigate whether source polygons or original geocodes allow a direct source-to-study crosswalk. If they do not, represent the lost detail as allocation uncertainty. Cellular observations at a coarse resolution cannot supply empirically observed differences among their own child TAZs.

**5. Superzone correction followed by row normalization does not guarantee superzone targets.** Methodology §6 multiplies fine-zone cells by a superzone correction factor and then normalizes each fine-zone row. Fine-zone origin totals are subsequently set using the original cellular outflow shares. These operations generally change the intended superzone destination distribution.

Here is an illustrative calculation, not a result from the repository. Two equally weighted fine origins in one superzone have destination-superzone probabilities `(0.9, 0.1)` and `(0.1, 0.9)`. Their aggregate is `(0.5, 0.5)`. A target of `(0.8, 0.2)` gives correction factors `(1.6, 0.4)`. After multiplication and row normalization, the two rows are `(0.9730, 0.0270)` and `(0.3077, 0.6923)`. Restoring the original equal origin weights gives `(0.6403, 0.3597)`, not the target.

This does not prove that the implementation has a large error; special structures can make the discrepancy small. It does show that the stated guarantee needs direct testing. Reaggregate the final trips matrix and report deviations for every constrained superzone pair, as well as origin totals. If origin totals and coarse OD blocks must both be respected, impose them jointly through constrained balancing. Treat uncertain survey targets as soft constraints or intervals where appropriate.

**6. Use the source comparisons to diagnose disagreement, not declare a winner.** The survey/cellular ratio of 3.56 and KS distance of 0.423 establish a major disagreement. The remaining KS distance of 0.301 after excluding intra-cellular-zone pairs shows that the discrepancy extends beyond the diagonal. These results do not, by themselves, identify which source has the correct population total, mode mix or trip-length distribution.

The short-trip explanation is plausible. Other contributors require source metadata: minimum dwell time and distance, age coverage, operator market share, device-to-person expansion, privacy suppression, trip chaining, time attribution, and the treatment of visitors. DfT identifies these as material limitations of mobile-network matrices. Its fusion guidance also requires consistent definitions and source-specific assessments of accuracy. [TAG M2.2, §5.3 and Appendix B.5](https://assets.publishing.service.gov.uk/media/5fbfbd998fa8f559e32b4d25/tag-m2-2-base-year-matrix.pdf)

My recommendation is to compare like-for-like segments at the native compatible geography before fusion: public transport where identifiable, motorised trips where identifiable, longer-distance movements, local movements, and internal/external travel. The survey's 645,111 OTHER trips in the study area are substantial. An all-mode comparison with a phone product that observes a different mix cannot establish the accuracy of car or bus demand.

The claim that using the same centroid-distance proxy makes the comparison fully fair also needs qualification. Different matrices allocate different weights to different zones and therefore to different geometric errors. The repository's own survey comparison gives median reported distance 1.11 km versus centroid proxy 1.95 km. Retain native-zone and intrazonal sensitivities and use reported distances for survey diagnostics wherever possible.

**7. The validation language overstates what the tests establish.** Two survey days from the same households are correlated measurements. They are useful for examining temporal repeatability. Their agreement is neither an independent test of population truth nor a universal upper bound on another estimator's agreement with the survey. Indeed, the report's superzone log-MSSIM of 0.938 for hybrid versus survey exceeds its 0.686 day-to-day value.

The household-split bus calibration is a real improvement. Apply household-level separation to any retained cellular shrinkage exercise as well. Keep both days from each household in the same fold. Where the survey design supplies strata or clusters, preserve them in variance estimation. Estimate uncertainty around the chosen shrinkage constant rather than presenting a flat minimum as precise.

Raw trip count also overstates independent information when observations share households or repeated commuters. Unequal weights further reduce precision. The unequal-weight effective sample size, `(sum w)^2 / sum(w^2)`, is a useful diagnostic, but it does not by itself correct household clustering. Weighted proportions combined with raw counts should be described as a shrinkage estimator inspired by empirical Bayes unless the sampling/likelihood model is specified.

| Diagnostic | What it contributes | What it does not establish |
|---|---|---|
| Cosine and PCA | Similarity of broad distributional patterns and dominant movements. | Correct volumes, correct local flows, or accurate LRT capture. |
| GEH on OD cells | A descriptive comparison sensitive to both size and difference. | A universal acceptance threshold for weighted OD estimates. Dividing by three gives average hourly flow, not the busiest hour. |
| Weighted KS and household bootstrap | Where trip-length distributions differ and the sampling variability of the survey comparison. | The direction or magnitude of systematic error in either source. |
| Log-MSSIM | An exploratory local-pattern diagnostic. | A transport-behaviour model or a measure of station accessibility. Hilbert windows do not have a fixed physical size. |
| Better fit to RavKav after calibration | Evidence that the calibration changed the matrix in the intended direction. | Independent validation against the source used to calibrate it. |

The finding that raw MSSIM cannot distinguish the null is appropriately acknowledged. I would keep these diagnostics in the audit record and direct further effort toward external counts, independent observations and forecast responsiveness. Fitting a source more closely is not evidence that its own coverage error has been removed.

**8. Ticketing undercoverage is a strong hypothesis whose correction must be segmented.** The September 20 report finds ticketing/survey ratios of 0.21–0.43 in seven superzones and preserves survey volumes whenever the ratio is below 0.5. This protects against a potentially serious omission, but a discrepancy cannot identify its own cause. Survey expansion, service change, incomplete payment coverage, operator omissions and missing destinations all need consideration.

The strongest evidence is the later breakdown in methodology §6p. In the Nazareth superzone, ticketing records about 8% of survey local trips, 34% of inter-superzone trips, and 74% of trips to the Haifa superzones. Applying one origin-wide rule can protect the missing local market while misrepresenting the corridor-bound market.

Replace the binary origin rule with a coverage audit by operator/route where obtainable, locality, local/intercity movement, destination sector and time period. Historical route identifiers may support an operator crosswalk; check its validity for the extract's dates. Obtain counts or a provider reconciliation before attributing the entire gap to missing operators. Preserve alternative estimates where the cause remains unresolved. The reported demographic association helps target the audit but is not itself a correction factor.

**9. Taxi-type demand is materially influencing the transit conclusion.** The latest matrix places special taxi and group taxi modes inside the bus output. Methodology §6p attributes the approximately 1.5-fold difference in one direction's transit profile to the taxi-type layer, including about 9,300 sub-area trips and 1,000–1,400 trips on some links.

That is a first-order modelling issue. Keep mode 5 and mode 8 separate until the codebook confirms their exact meanings. Hired taxis and scheduled/shared services need not have the same fare, access, availability or transfer behaviour as bus/Matronit. Retain separate outputs for scheduled bus, each relevant taxi category and heavy rail, even if a broader reporting total is also useful. A simple public-transport capture rate applied to all these trips can materially distort the LRT estimate.

**10. Spatial splitting needs trip purpose and explicit uncertainty.** Population-weighted origins and employment-weighted destinations are reasonable initial assumptions for some home-to-work trips. They are weak for education, shopping, escorting, hospital visits, and non-home-based movements. Employment is also not a substitute for the residential origin of a new mixed-use development.

Split at least work, education and other purposes before allocating trip ends. Use residents or relevant population groups for home ends, sector-specific jobs for work, student places for education, and appropriate opportunities for other destinations. Keep observed door-to-door OD origins distinct from home-based production rates: the reported 0.829 rate is attributed to residents' home zones, while not every AM trip starts at home.

At fine scale, compare defensible allocation alternatives and show their effect on station catchment totals and corridor loads. A uniform allocation is not automatically worse than an unsupported detailed allocation; both are assumptions. Preserve the observed coarse totals and quantify the consequences of the choices below them.

**11. Retain external demand and low-observation zones.** The survey study-area conversion excludes 116,473 weighted trips with an end outside the north, disproportionately affecting rail. The later 205-TAZ and 25-area subsets additionally omit movements from elsewhere in the north. A trip from outside the reporting area can still use the extension or transfer at Hamifrats.

Retain external origin/destination sectors or gateway/station demand alongside the internal matrix. Keep reporting boundaries separate from the travel market. Likewise, Adi, Alon Hagalil and Tzipori should not disappear from future demand estimation merely because current recorded bus activity is below 50 trips. A low observed count may indicate a thin sample, poor coverage or weak current service. Retain the areas, pool where needed, and report the uncertainty.

**12. Vintage alignment is an assumption, not a validation result.** The `(X2025 / X2020)^(4/5)` factor extrapolates a forecast trend to represent 2018–2022 change. It does not measure that change. The rail multiplier applies national annual ridership change to a regional AM matrix and assumes the survey's 2018 rail level is equivalent to 2019. The two-mode table's so-called 2018 bus base is already partly anchored to 2022 ticketing.

Publish a component-level vintage ledger and relabel mixed-vintage intermediates. Prefer observed zonal population and mode-specific ridership changes where available. Use the national rail ratio as a sensitivity when local AM evidence is unavailable. Keep documented evidence behind the claim that May 2022 bus demand represents normal conditions; a team assertion alone cannot be independently reviewed.

The older report's 0.91 ticketing/survey ratio cannot simultaneously be treated as proof of source equivalence and as an estimate of real 2018–2022 decline. Different population frames and geographic attribution remain confounded. Similarly, the assertion that missing nonresident car trips is mildly conservative for LRT analysis has no guaranteed direction once mode shares and calibration are affected.

**13. Keep four demographic forecasts, but strengthen their construction.** The separate BU/HS × 2040/2050 recommendation is sound. The reported Tirat Carmel difference, approximately 120,100 versus 38,600 residents in 2050, is large enough to change the location and direction of demand. However, the two scenarios are not simply equal regional totals moved around: the supplied table shows whole-study population 8.8% higher under HS in 2050, and employment 6.7% higher.

The report's 'if and only if the per-area margins differ' criterion is true only within its restricted fixed-seed, fixed-rule matrix procedure. Identical area totals can still place homes and jobs at different distances from stations or change purpose and car-availability composition. Compare within-area station accessibility as well as area totals.

Furness produces a matrix of the form `T_future[i,j] = a[i] × T_base[i,j] × b[j]`. It therefore preserves zero cells and multiplicative association structure. Adding residents to a marginal total does not, by itself, create realistic new destination choices for those residents. The documented new-resident production term is useful, but the destination allocation and zero-cell treatment need to be shown.

Develop a purpose-sensitive synthetic component for major residential conversions and new developments, using suitable donor areas and travel impedance. Combine its changes with the observed baseline using explicit zero and extreme-growth rules. Daly and colleagues discuss these problems and the value of aggregation and normalization in observed-base forecasting. [Daly et al., 2012, Pivoting in Travel Demand Models](https://alogit.com/papers/2012_Daly_Fox_Patruni_Milthorpe.pdf)

**14. The frozen-share result should be labelled a demographic reference.** The inventory describes future mode shares formed by multiplying future total OD demand by smoothed 2022 shares. The aggregate transit decline from 8.9% to 7.5–8.0% therefore reflects the changed spatial composition under those fixed shares. It does not demonstrate an observed or modelled weakening of public-transport competitiveness.

A future without-extension case needs its own service assumptions: the existing or committed Nofit service, bus/Matronit arrangements, heavy rail, feeder connections, fares, parking, travel times and availability. The build case must add only the intervention being evaluated, with both cases using the same background land-use scenario. DfT distinguishes demographic reference forecasts from without-scheme and with-scheme forecasts. [TAG M4, definitions and §7](https://assets.publishing.service.gov.uk/media/6a0c3ab4fcae986635db919a/tag-unit-m4-forecasting-and-uncertainty.pdf)

The mode-share smoothing also needs documentation: why `k = 50`, what information count it acts on, how zero/empty cells are handled, and how unavailable modes are excluded. Expanded trip volume should not be interpreted as a sample size. Smoothing toward a stratum average can place rail shares in OD pairs without a credible rail path unless availability is handled explicitly.

**15. Corridor profiles are potential movement profiles.** Methodology §6o places every OD pair between line areas onto each intervening corridor link. This is useful for showing the longitudinal distribution of a selected demand pool. It does not establish that those travellers can reach stations conveniently, would choose the LRT, or would follow that line rather than a parallel service.

The reported peak-link transit value of 2,966 covers the three-hour analysis window. It is not a peak-hour passenger load. Capacity assessment requires within-period peaking and actual service frequency. The current profiles also omit some external and feeder markets, so they are not guaranteed upper bounds on total future LRT demand even when all selected internal trips are placed on the line.

Retain the alignment-market tiers as an initial screen. Compute actual route/station alternatives before estimating capture. Both ends in a corridor area does not imply convenient station access, and an outside origin can be a relevant feeder market. Intra-area trips can also use the LRT when an aggregated area contains several stations.

**16. A proportionate route to the stated OD goal.** The first deliverable should be a reconciled baseline whose measured and estimated elements are explicit. DfT's base-matrix guidance supports weighting sources according to their accuracy and constraining aggregate demand within the accuracy of the observations. [TAG M2.2, §5.3.9–5.3.15](https://assets.publishing.service.gov.uk/media/5fbfbd998fa8f559e32b4d25/tag-m2-2-base-year-matrix.pdf) My proposed application is:

1. Define the target as representative-weekday person journeys departing 06:00–09:00, with explicit resident/nonresident coverage and internal/external sectors. Publish main-mode and trip-purpose rules.
2. Reconstruct each source independently at its native resolution. Record all exclusions, weights, timing rules and unknown destinations. Keep a separate observation ledger for persons, vehicles, journeys and boarding legs.
3. Resolve the bus journey/OnBoard compatibility, cross-mode linkage, taxi categories and geographic coverage before setting transit targets. Keep unresolved cases as alternatives with stated assumptions.
4. Use mass-preserving geographic conversion. Build credible broad-zone/purpose estimates before distributing to fine TAZs. Preserve new-development and station-catchment detail where it has an observed geographic basis.
5. Reconcile survey, transit and any trustworthy cellular evidence with uncertainty-aware constraints. Avoid declaring a universal 'best source': reliability may vary by movement, mode, distance and location.
6. Validate a frozen candidate baseline against observations that did not determine it. Release detailed provenance and uncertainty alongside the matrices.

For external checks, match like units. Survey car driver plus passenger trips are persons; road counters record vehicles. Use driver trips or a justified occupancy conversion. Compare a road count only with demand plausibly crossing that location through an explicit route/screenline mapping. A geographic sum of OD pairs is not automatically a screenline flow. For transit, compare predicted boardings and loads with boarding/load observations, keeping complete-journey totals separate.

The minimum independent evidence programme should target the most consequential uncertainties: Haifa corridor directional bus loads, Nazareth local and Haifa-bound services separately, transfer activity at Hamifrats, a small set of road screenlines, and local rail boarding/OD totals. A later representative observed period can test the demographic update, provided service and measurement definitions are harmonised. Identify the reused and independent observations in the validation report.

**17. Add a compact behavioural model when the goal becomes LRT passengers.** A full regional model is not the only defensible route. FTA's STOPS is an example of project ridership forecasting using streamlined procedures without developing a complete regional forecasting model. Its architecture is relevant here; applying its US implementation and parameters directly to this corridor would require separate justification. [FTA STOPS user guide overview](https://www.transit.dot.gov/funding/grants/grant-programs/capital-investments/stops-user-guide-version-253-full-resolution)

I recommend a corridor model built around observed demand, a limited set of realistic travel alternatives, and changes in their attractiveness. This keeps the present work useful while adding the missing link to scheme response. Incremental forecasting from observed demand is an established approach, with explicit treatment required for major land-use change and zero cells. [TAG M2.1, §4.3 and Appendix G](https://assets.publishing.service.gov.uk/media/69a034423e672177d0bc7710/tag-unit-m21-variable-demand-modelling.pdf)

Create a table of feasible paths for each relevant OD segment in both the without-extension and with-extension cases. Include direct bus/Matronit, heavy rail, LRT, relevant combinations, and car where available. Represent walk access, feeder access and parking only where credible. Measure access from distributed homes/jobs or representative points rather than treating an entire large area as a single doorstep. Haifa's slopes, railway crossings and barriers make station entrances and actual access paths especially important to check.

A schematic generalised-cost expression, in minutes, is:

\[
G_{ij}^{m}=t_{iv}+\alpha_a(t_{access}+t_{egress})
+\alpha_w t_{wait}+\alpha_x t_{transfer\ walk}
+\pi_x N_{transfers}+\frac{\mathrm{monetary\ cost}}{\mathrm{VOT}}
+R+C.
\]

Here `R` and `C` are equivalent-minute reliability and crowding terms when supported by evidence. Costs and values of time must use consistent units and traveller/purpose definitions. Car costs should represent the appropriate perceived fare/parking/operating components; transit costs should reflect integrated fares and transfers. Record physical boarding and station circulation time, and ensure dwell or transfer penalties do not count the same component twice.

DfT's public-transport guidance covers these components and makes clear that half-headway waiting assumes random arrivals and reliable service. [TAG M3.2, §3](https://assets.publishing.service.gov.uk/media/666af32effd07973a043d110/tag-unit-m3.2-public-transport-assignment-modelling.pdf) For the corridor, estimate times from available operating data and engineering assumptions, then test speed, frequency, feeder connections and parking as explicit scenarios. A table of these costs can support an initial model without equilibrium traffic assignment.

Use locally estimated or carefully transferred response parameters. Matching one observed base share does not identify sensitivity to time or fare changes: several very different response slopes can reproduce that share. Calibration must therefore include responsiveness checks and independent evidence where possible.

**18. Separate public-transport choice from choice of a path using the extension.** One suitable candidate is a nested choice structure in which the attractiveness of available public-transport paths affects the higher-level decision to use public transport. The inclusive value connects the two decisions; the nesting parameters require behavioural consistency and calibration. [Train, Discrete Choice Methods with Simulation, chapter 4](https://eml.berkeley.edu/books/choice2nd/Ch04_p76-96.pdf)

For illustration, with traveller segment `s`, the desired project output can be expressed as:

\[
Q_{\mathrm{extension}}=
\sum_{i,j,s}T^F_{ijs}\,
P(\mathrm{PT}\mid i,j,s,\mathrm{build})\,
P(\mathrm{path\ uses\ extension}\mid\mathrm{PT},i,j,s,\mathrm{build}).
\]

This is an accounting identity for the chosen market, not an estimated model or a proposed numerical forecast. Availability, access and alternative paths enter the probabilities. A new LRT alternative cannot gain users through a purely multiplicative update to its zero observed base share. Introduce it through an explicit path utility; pivot the existing higher-level market shares or use a suitable zero-cell procedure.

Start with a few supported segments, such as work/education/other and car availability. Do not let travellers without a usable car choose that alternative, or interpret children and car passengers as independent car drivers. Use the same travellers and reference demand in paired build/no-build runs so that reported changes have a clear counterfactual.

Report at least: journeys using the extension, existing transit journeys diverted to it, changes in car travel, net change in public-transport journeys, boardings by station, and directional link loads. Existing heavy-rail or bus passengers transferring to the LRT contribute to project use but do not all represent new public-transport demand. Where possible, track switching at traveller/segment level rather than inferring all gross switches from aggregate share differences.

**19. Treat an LRT image premium as a parameter to investigate.** The service can be more attractive because of measurable improvements in time, reliability, comfort, crowding, access or legibility. A residual preference may also exist, but it should not automatically be added on top of already represented improvements.

Ben-Akiva and Morikawa's study found no evident inherent rail preference when the compared service characteristics were equal, while higher-quality rail could attract a preference. Cain and Flynn's Los Angeles perception study found that full-service BRT could reproduce qualities associated with rail. Neither establishes a transferable Israeli mode-shift coefficient. [Ben-Akiva and Morikawa, 2002](https://doi.org/10.1016/S0967-070X(02)00009-4); [Cain and Flynn, 2013](https://digitalcommons.usf.edu/jpt/vol16/iss4/4/)

For this study, a defensible starting scenario sets an unmeasured residual rail bonus to zero while explicitly modelling service advantages. Test an evidence-supported residual in sensitivity analysis, or estimate it with local revealed/stated preference evidence. Avoid a blanket percentage capture assumption solely because the technology changes from BRT to LRT.

**20. Carry uncertainty to the decision outputs.** Run the four demographic cases through both service counterfactuals, then vary the assumptions that materially change corridor results: coverage correction, fine-zone allocation, new-development destination choice, source reconciliation, access times, service frequency, choice sensitivity and rail recovery. Preserve plausible relationships between inputs rather than varying every parameter independently.

Use a stratified household bootstrap, where the design supports it, to carry survey uncertainty through the entire estimation pipeline. Separately represent sampling variation across ticketing dates and uncertainty in inferred destinations. Keep alternative structural assumptions visible instead of assigning arbitrary probabilities to them. BU and HS are scenarios, not confidence-interval endpoints.

Publish conditional quantiles only when the probability assumptions justify them. Otherwise report named scenarios and the range of results. Show which assumption changes the preferred alignment or the required service capacity. This applies the distinction between input uncertainty and model uncertainty used in forecasting guidance. [TAG M4, §2](https://assets.publishing.service.gov.uk/media/6a0c3ab4fcae986635db919a/tag-unit-m4-forecasting-and-uncertainty.pdf)

**21. Recommended order of work and completion criteria.** These priorities are based on likely effect on the Nofit decision, not the sophistication of the method.

| Priority | Action | Concrete completion evidence |
|---|---|---|
| P0 | Choose the authoritative baseline and trace every forecast to it. | One lineage table; consistent geography/mode/time metadata; a reproducible current run order. |
| P0 | Reconcile journeys, legs, station pairs and person/vehicle units. | Documented OnBoard unit; bus/rail overlap treatment; separate journey and boarding products. |
| P0 | Correct spatial replication and test aggregate constraints. | Source-block mass conservation; final matrix reaggregation against every intended coarse target; explicit treatment of uncertainty. |
| P0 | Audit ticketing coverage and taxi categories. | Local/intercity/operator evidence where available; separate taxi outputs; named alternatives where unresolved. |
| P1 | Validate the baseline externally. | Holdout observations and unit-consistent mappings; residuals with uncertainty; documented reasons for any remaining mismatch. |
| P1 | Retain external markets and improve growth for new developments. | External sectors; retained low-volume areas; purpose-based growth; auditable zero/new-flow treatment for BU/HS. |
| P1 for LRT forecasting | Define service counterfactuals and station access. | Feasible path/cost tables for each alignment, including feeders and competing services. |
| P2 for LRT forecasting | Estimate response and report project use. | Calibrated choice sensitivities; realistic response tests; station/link outputs and distinctions between transfers and new transit trips. |
| P2 | Evaluate robustness. | Paired scenario results; major uncertainty contributions; identification of assumptions that change the recommendation. |

Useful numerical invariants include nonnegative trips, intended modal sums, conservation under crosswalks, successful and feasible balancing, and exclusion of unavailable alternatives. Behavioural checks should test whether an isolated worsening of LRT cost lowers its choice probability and whether a no-change scenario reproduces the reference case. Specify tolerances before choosing the favoured matrix, with regard to the accuracy and intended use of the observations.

For corridor screening, a baseline may be released with bounded and clearly located uncertainty once definitions, conservation and external checks are satisfactory. Station design and investment appraisal require credible path choice, peak loads and response to the intervention. No universal cosine, KS or MSSIM threshold can replace those checks.

My first implementation sequence would be: resolve the authoritative branch; reconcile transit units and the Nazareth/taxi issues; rebuild mass-preserving baseline estimates; and validate the resulting corridor movements externally. The existing matrix diagnostics can then serve as regression and explanatory checks while the project advances to forecast and service-response work.
