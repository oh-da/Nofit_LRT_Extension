# Research plan — confirming the out-of-vehicle weights and times for transit

*4 October 2026. Status: **plan, not yet executed.** Only the sensitivity screen (§2) and a first scan of sources (§4) have been done. This plan closes the open item "confirm the walk / wait / transfer weights against `נוהל פר"ת`" (`docs/CORRIDOR_DEMAND_TASKS.md` E4; `Output/gc/gc_data_inventory.csv`, row `all, weights`: "assumed (plan defaults)").*

## 1. Aim, scope and what "confirmed" means

**Aim.** Replace the assumed out-of-vehicle (OVT) parameters of the generalized cost by values supported by studies, appraisal guidance and calibrated models — each with a central value and a low–high range — and order the work by the effect each parameter has on the LRT capture.

**Scope.** The transit OVT terms of `GC = IVT + w_walk·walk + w_wait·wait + w_tr·transfers` (`docs/LRT_CAPTURE_PLAN.md` §1) for bus, Metronit (BRT) and LRT: the walk and wait *weights*, the transfer *penalties*, and the walk, wait and station-access *times*. "Studies" means peer-reviewed and grey literature. "Models" means national, regional and activity-based transport models and active-mode (walk / cycle access) models.

**Out of scope.** The LRT premium and λ_T (the stated-preference survey was dropped on 23 September 2026, `docs/NEXT_STEPS_HANDOVER_2026-09-23.md` §D), crowding, fares and car cost. Two interactions must be reported, not hidden: λ is only meaningful with the weights it was fitted under (step 33 must be rerun after any change), and the 5-minute premium may partly proxy attributes the GC omits, so changing the OVT terms without revisiting it can double count.

**"Confirmed".** A parameter is confirmed when at least three independent sources from at least two stream types (§4), after normalisation (§5.3), agree within ±0.25 on weights, ±1 min on times and ±2 min on pure transfer penalties. Otherwise it stays at its current value and the evidence range is carried as a sensitivity.

**A policy anchor already in the repository.** The Ministry of Transport guideline *תיקוף המודלים המטרופוליניים 2024* (Systems Planning Division, draft 6, 16 September 2024) lists among its checks "out-of-vehicle ÷ in-vehicle time 2–3" for the new metropolitan models (`docs/MOT_VALIDATION_PLAN.md` §4.2 and T9). The model's walk and wait weights of 2.0 sit at its lower bound, and T9 records them as in range, which is a documentation check, not evidence. As far as that summary shows, the guideline covers the *weights* only, not transfer penalties, walk times or station access. Its full text is not in the repository.

## 2. Why now: a sensitivity screen

`tools/ovt_sensitivity_screen.py` rebuilds GC from the saved skim components with the weights and times varied, and reruns the step-31 pivot (METHODOLOGY §6ac). The identity `GC = ivt + 2·walk + 2·wait + 8·transfers` holds on every saved cell (max deviation 0.02 min). **At the base it reproduces the ten committed all-underground / all-ground capture cases in `Output/skims/lrt_capture_scenarios.csv` to within 0.7 trips**, and the script stops if that check fails. Everything else is held at the central case: λ 0.03, λ_T 0.06, premium 5, 5-minute headway, full bus competition, corridor-internal market of the 25 V2 areas, 06:00–09:00. Base: **4,254 underground / 3,206 ground** LRT trips.

| Parameter | Setting | Underground (4,254) | Ground (3,206) |
|---|---|---|---|
| Walk weight, all modes | 1.5 / 2.5 / 3.0 | +12.6% / −11.1% / −20.8% | +13.0% / −11.2% / −20.9% |
| Walk weight, LRT side only (bus 2.0) | 1.75 / 1.5 / 2.5 | +12.7% / +26.5% / −21.8% | +13.4% / +28.4% / −22.5% |
| Walk weight, bus side only (LRT 2.0) | 1.5 | −11.7% | −12.4% |
| Wait weight | 1.5 / 2.5 / 3.0 | +3.2% / −2.9% / −5.5% | +4.1% / −3.7% / −7.1% |
| Bus↔LRT and bus–bus transfer penalty (min) | 5 / 10 / 12 | −0.6% / +0.5% / +1.1% | −0.0% / +0.1% / +0.4% |
| BRT–LRT transfer penalty (min per Metronit feeder leg; base 0) | 3 / 5 / 8 | −7.6% / −12.1% / −17.9% | −8.4% / −13.2% / −19.4% |
| Walk time (detour 1.3, 80 m/min) | ×0.85 / ×1.154 / ×1.3 | +7.4% / −7.0% / −13.2% | +7.6% / −7.1% / −13.3% |
| Underground vertical access (min per station end; base none) | +1 / +2 / +3 | −16.1% / −30.3% / −42.4% | n/a |
| Generalized minutes added to the LRT side | +1 / +2 / +4 | −4.2% / −8.3% / −16.1% | −4.6% / −8.9% / −17.2% |
| Stacked bound, LRT-favourable (walk 1.5, wait 1.5, transfer 5, walk time ×0.85) | | +21.4% (5,165) | +23.8% |
| Stacked bound, LRT-unfavourable (walk 2.5, wait 2.5, transfer 10, walk time ×1.154, BRT–LRT 5) | | −31.8% (2,900) | −33.7% |
| … plus vertical access 2 min per end | | −58.2% (1,777) | n/a |

×1.154 is a detour factor of 1.5 at 80 m/min; ×1.2 is 4.0 km/h.

**Reading.**

1. **The OVT assumptions are first order, not tuning.** The stacked plausible bounds span 2,900–5,165 trips, about 80% of the width of the λ / premium band (3,166–6,031, §6ak), and wider than it once vertical access is added. They are bounds, not estimates.
2. **Exchange rate: one generalized minute on the LRT side is worth about 4.2% of LRT trips (about 180 trips).** The research target is therefore ±1 generalized minute on times and penalties, and ±0.25 on weights.
3. **Ranking by swing:** vertical access (not modelled) > the BRT–LRT transfer penalty (assumed 0; pairs with a Metronit feeder leg carry 2,007 of the 3,841 LRT trips drawn from existing transit, 52%) > the walk weight, above all a *difference* between LRT and bus walk weights > walk time > wait weight > the bus transfer penalty (≈ nil: confirm only).
4. **Why walking dominates.** On the trunk pairs the LRT's walk is 13.9 min against 5.1 for the bus, at weight 2 that is 27.8 against 10.2 generalized minutes, while its in-vehicle time is 13.8 against 16.1 (transit-trip-weighted, METHODOLOGY §6ac).
5. **The reference points disagree in direction.** The academic leads (§4) put walk and wait nearer 1.5–1.7, which would raise capture; the Ministry guideline expects 2–3, and a walk weight of 2.5 would lower it (−11% underground); a free BRT–LRT transfer and no vertical access are optimistic and would lower it too. The net direction is not known in advance, and whether the policy range or the evidence median governs the central case is a client decision (§5.5, §8).

**Limits of the screen.** It is screening grade. The feeder / gateway path choices of the LRT composites are held at their base-case values, so a re-optimisation would soften the penalty effects somewhat (at higher BRT–LRT penalties some pairs would switch to bus feeders). Vertical access is added as walk-weighted minutes on both station ends, without any information on the actual station design. The Metronit is only a feeder in the model, never the competitor the LRT must beat (step 31, `Mode_skims_and_flow_comparison.ipynb` cell 8: the LRT is compared with the bus GC only), so the BRT→LRT effect here is the feeder-transfer effect only. Before any decision the real chain (steps 26 → 31 → 32) must be rerun (§5.6).

## 3. Parameter register and research questions

| # | Parameter | In the model now | Where | Priority | RQ |
|---|---|---|---|---|---|
| 1 | Underground station access time (vertical, gates, boarding) | none | not in steps 25, 26 or 31 (no hit for escalator / vertical / depth / platform access / fare gate / boarding time in the three notebooks) | P1 | RQ1 |
| 2 | BRT↔LRT transfer penalty | 0, free (decision of 22 Sep 2026) | `BRT_LRT_TRANSFER_PEN`, `LRT_LRT_TRANSFER_PEN` = 0.0 (step 31) | P1 | RQ2 |
| 3 | Walk weight | 2.0, one value for bus-stop and LRT-station access | `W_WALK` (steps 26, 31) | P1 | RQ3 |
| 4 | Walk time | 80 m/min (4.8 km/h), straight line × 1.3, population-weighted per area, no slope, crossing or shade | `WALK_SPEED`, `DETOUR` (steps 26, 31); `Output/gc/lrt_access_*_v2.csv` | P2 | RQ3 |
| 5 | Wait weight and wait model | 2.0; wait = ½ headway capped at 10 min (LRT 5-min headway gives 2.5 min) | `W_WAIT`, `WAIT_CAP`, `BUS_WAIT_RULE` (step 26) | P3 | RQ4 |
| 6 | Bus↔LRT and bus–bus transfer penalty | 8 generalized min; one transfer assumed on the 178 non-direct pairs | `TRANSFER_PEN` (steps 26, 31) | P4, confirm only | RQ5 |

`docs/LRT_CAPTURE_PLAN.md` §1 records the walk / wait weight 2.0 as "standard range 1.5–2.5" and the transfer penalty 8 as "range 5–10". Neither range is sourced. The Ministry guideline's 2–3 applies to rows 3 and 5 only.

**Research questions.**

- **RQ1.** How much time or penalty do boarding, fare gates and level changes add at underground versus surface LRT stations, and how do appraisal guidance and models represent it?
- **RQ2.** What is the pure transfer penalty for same-platform, cross-platform and level-change BRT↔LRT interchanges, against 0 now?
- **RQ3.** What is the walk multiplier for transit access, egress and transfer? Does it differ for rail / LRT versus bus? What slope, crossing and environment adjustments are used, and what walk speed and detour does practice assume (Haifa is hilly)?
- **RQ4.** What are the multipliers for initial versus transfer wait, how do they depend on headway (random-arrival threshold, cap), and how are reliability and real-time information treated?
- **RQ5.** What is the pure bus-transfer penalty, net of the walk and wait that the GC already counts? (Confirmation only.)

## 4. Evidence streams and first leads

| Stream | What it is | Extract |
|---|---|---|
| S1 Appraisal guidance | `נוהל פר"ת` and the Ministry's 2024 metropolitan-model validation guideline (Israel); UK DfT TAG M3.2 and A1.3, plus the UK Passenger Demand Forecasting Handbook (PDFH) for rail; FTA / STOPS; TCRP 95 and the TCQSM; Australian ATAP, NZTA, Dutch and Nordic handbooks | weights, penalties, wait rules, walk speed |
| S2 Meta-analyses and reviews | Wardman and co-authors, ITF, interchange reviews | pooled multipliers and penalties, with ranges |
| S3 Primary SP / RP studies | studies on wait (random versus timetable-aware, real-time information), interchange design, vertical access, BRT / LRT specifics | estimates by context |
| S4 Models in practice | Israeli national and metropolitan models (to be requested), FTA STOPS, regional and activity-based models (MTC, SANDAG, ActivitySim examples, Sound Transit), national models abroad | calibrated weights by mode and access mode, boarding and transfer penalties, wait cap, station-specific access |
| S5 Active-mode evidence | walking speed by slope, crossing delay, catchment decay for rail versus bus, walk-environment weights | slope-aware walk times for Haifa (OSM plus a DEM, which ties into task E6), a test of mode-specific walk weights |

**First leads (4 October 2026). These come from search-result summaries only; nothing below has been read in full. Verify each before it is used as an input.**

- **Walk and wait multipliers.** One summary of Wardman's meta-analyses reports walk ≈ 1.66 ± 0.12, wait ≈ 1.47 ± 0.18 and headway ≈ 0.80 ± 0.08 × in-vehicle time (Wardman 2001 / 2004), and walk 1.45 (urban) / 1.70 (inter-urban) with wait 1.50 / 1.76 in Wardman et al. (2016), described as well below the "rule of two". Practice often still uses 2.0: a Sound Transit ST3 draft ridership methodology (2015) reportedly factors all out-of-vehicle time by 2.0. Sources: [Wardman, *Public transport values of time*](https://eprints.whiterose.ac.uk/id/eprint/3393/2/Public_Transport_Values_of_Time_se), [Abrantes & Wardman 2011](https://www.sciencedirect.com/science/article/abs/pii/S0965856410001242), [ITF, *Valuing convenience in public transport*](https://www.itf-oecd.org/sites/default/files/docs/dp201402.pdf), [UCLA ITS review of out-of-vehicle time](https://www.its.ucla.edu/wp-content/uploads/sites/6/2014/06/Appendix-A.pdf).
- **Interchange.** Reported values: an average interchange ≈ 5 min of uncrowded in-vehicle time; a cross-platform metro interchange valued 20–25% less negatively than one with a level change (so **not zero**); bus–bus ≈ 22 min against ≈ 8 min for subway heavy rail; ≈ 15.2 min for the first transfer of a multimodal trip in one survey; 28.8 min in one path-modelling study. The spread is largely definitional (total transfer cost versus pure penalty), hence rule N2 in §5.3. Sources: [Passenger valuation of interchanges in urban public transport](https://www.sciencedirect.com/science/article/pii/S1077291X24000092), [Transfer penalties in multimodal public transport networks](https://www.researchgate.net/publication/322598299_Transfer_penalties_in_multimodal_public_transport_networks).
- **Station access (RQ1).** FTA's STOPS reportedly lets users specify a fixed-guideway station's vertical profile, the within-station walk to the platform and station-specific time penalties by access mode; the Sound Transit ST3 draft reportedly uses a 2–3 min boarding penalty at rail stations and 0.5–1.0 min per escalator link, with a wait factor of 0.50 (presumably wait = ½ headway; check). A first search found no valuation *studies* of vertical access, so S4 and station-design guidance must carry RQ1, with a targeted search ("level change penalty", "station access time valuation", "escalator", "stairs"). Sources: [STOPS on TransitWiki](https://www.transitwiki.org/TransitWiki/index.php/STOPS_(Simplified_Trips-on-Project_Software)), [Sound Transit ST3 ridership forecasting methodology (draft, 2015)](https://www.wsdot.wa.gov/partners/erp/background/ST3%20Draft%20RidershipForecastingMethodologyReport_6March2015.pdf).
- **Wait model.** TAG M3.2 (May 2024) reportedly defines GC with access, wait, interchange and egress factors plus a boarding and a transfer penalty, gives indicative ranges for the weights, and sets wait to ½ headway up to a 15-minute headway and 7.5 min beyond (the model caps at 10). Source: [TAG unit M3.2](https://assets.publishing.service.gov.uk/media/666af32effd07973a043d110/tag-unit-m3.2-public-transport-assignment-modelling.pdf).
- **Israel.** The December 2012 edition of `נוהל פר"ת` is online ([PDF](https://www.infocenters.co.il/rsa/multimedia/Prat2012.pdf)); it covers value of time and project appraisal, but whether it gives walk, wait or transfer weights has not been checked, and a newer edition may exist. No public parameter report for the Israeli national model was found; the nearest published item is [Gur, Bekhor et al. (2009)](https://journals.sagepub.com/doi/abs/10.3141/2121-16) on national trip tables from cell-phone data. The model documentation must be requested (§8). The Ministry's 2024 validation guideline is cited in the repository (`docs/MOT_VALIDATION_PLAN.md`) but its text is not; if it gives ranges for other OVT parameters (transfer penalty, wait cap, walk speed), extract them in P1.

**Recalled references, not yet checked for existence or content:** Balcombe et al. (2004), *The demand for public transport: a practical guide* (TRL593); TCRP Report 95; TCQSM 3rd ed. (2013); Iseki & Taylor (2010) and Guo & Wilson (2011) on transfers; Guerra, Cervero & Tischler (2012), Daniels & Mulley (2013) and El-Geneidy et al. (2014) on walking catchments.

## 5. Method

**5.1 Protocol and search.** Fix inclusion criteria first: urban transit; weights reported relative to in-vehicle time or to the value of time; documented method and sample; 2000 onwards (older foundational studies allowed); bus, BRT, LRT, metro or rail; exclude walkability work that gives no time weights. Search TRID, Scopus / Web of Science / Google Scholar, the ITF, TRB / TCRP open reports, gov.uk, FTA and gov.il / Netivei Israel / the metropolitan transport authorities, in English and Hebrew (ערך זמן, זמן הליכה, זמן המתנה, קנס החלפה, מודל ארצי, פר"ת), then snowball from the meta-analyses.

**5.2 Extraction.** One row per estimate in a single evidence table (proposed `Output/ovt_research/evidence_table.csv`): id, parameter, stream, citation, year, country / city, mode(s), method (SP / RP / model calibration / guideline), sample, definition as reported, estimate, interval or range, unit (× IVT or min), context (headway band, purpose, interchange type, environment), normalised value, normalisation note, quality (1–3), applicability to Haifa (1–3), link.

**5.3 Normalisation rules.**

- **N1.** Express every weight as a multiplier on in-vehicle time. If a study reports relative to the value of time, convert with that study's own in-vehicle value.
- **N2.** For transfers record both the *pure penalty* (in-vehicle-equivalent minutes, excluding walk and wait) and the *total transfer cost* (including them). The model needs the pure penalty, because it counts walk and wait explicitly. Where only the total is reported, subtract walk × `w_walk` and wait × `w_wait` using the study's own times; if that is not possible, label it "total" and do not pool it with pure penalties.
- **N3.** Wait: separate initial from transfer wait; record the headway band (< 10, 10–15, > 15 min), random arrival versus timetable-aware, and real-time information. Keep reliability separate from the weight.
- **N4.** Walk: separate access, egress and transfer walk; record the environment (slope, crossings, shade), the distance band and the mode served (bus versus rail / LRT / BRT).
- **N5.** Vertical access: record the time and any penalty per level, escalator or lift separately, and whether it is in minutes or in-vehicle-equivalent minutes.
- **N6.** Keep empirical estimates (SP / RP) apart from practice conventions (guidance and calibrated models); report both medians.

**5.4 Synthesis.** Per parameter, tabulate and take the quality-weighted median and range by context; use a random-effects meta-regression only when there are at least 10 comparable estimates (covariates: mode, headway band, SP / RP, purpose, region). Apply the convergence rule of §1. Parameters with a screen swing under 5% (wait weight, bus transfer penalty) get S1 and S4 only, no primary-study search; S3 is capped at about one day.

**5.5 Israeli triangulation and the policy-versus-evidence rule.** Policy anchors are the Ministry guideline's out-of-vehicle ÷ in-vehicle range of 2–3 and, where they specify a value, `נוהל פר"ת` and the national model. Report them in their own columns next to the evidence median. They already disagree on walk and wait (2–3 against ≈ 1.5–1.7 in the first leads), so do not choose silently. **Proposed default:** keep the central case inside the policy range, so that it stays guideline-compliant, and carry the evidence range as the low-end sensitivity (screen, underground: walk weight 1.5 is +13%, 2.5 is −11%, 3.0 is −21%); the client decides. Internal check: the survey-reported bus door-to-door time is ×1.4, a fixed ≈ 9 min, above the timetable-based one (METHODOLOGY §6x addenda 2–3). Test whether literature-based walk and wait times close that gap.

**5.6 Translation into the model.**

- **Parameters.** `W_WALK` (with a new mode-specific LRT value if justified), `W_WAIT`, `TRANSFER_PEN`, `BRT_LRT_TRANSFER_PEN`, `WAIT_CAP`, `WALK_SPEED` / `DETOUR` (or slope-aware walk times from OSM plus a DEM, task E6), and a **new station-access term** per LRT station end (underground versus surface).
- **Rerun.** Set low / central / high, rerun steps 26 → 31 → 32 (about ten minutes per chain), add the OVT factors to the step-40 factorial, **re-estimate λ (step 33) on the new GC**, and report the capture band and any change in the alignment ranking.
- **Do not** use an unverified lead as an input.

**5.7 Documentation.** METHODOLOGY addendum (§6x / §6ac), the inventory row, tasks E4 and E7, and a revision note in the reports.

## 6. Deliverables, order and effort

| Stage | Work | Effort | Output | Blocked by |
|---|---|---|---|---|
| P0 | Protocol, parameter register, sensitivity screen | 0.5 d, **done** | this plan, `tools/ovt_sensitivity_screen.py` | none |
| P1 | S1 guidance and S4 model documentation; send the requests of §8 | 1.5–2 d | extracts, request letters | Israeli model documents (external) |
| P2 | S2 meta-analyses and S3 primary studies for RQ1–RQ4 | 1.5 d | evidence table | paywalls |
| P3 | S5 active-mode evidence; slope-aware walk times for Haifa | 1 d | walk-time method and test | OSM extract, DEM |
| P4 | Normalise, synthesise, write the parameter memo | 0.5 d | memo with central / low / high and status per parameter | P1–P3 |
| P5 | Model rerun, factorial, λ re-estimation, documentation | 1 d | updated outputs, METHODOLOGY addendum | P4, station design information |

About 5–6 working days, mostly parallel. The long pole is the Israeli model documentation and the station design information, not the literature.

**Acceptance.** Every parameter has a central value, a low–high range, a status (confirmed or range only) and its sources; the rerun capture band is reported next to the current one; no unverified lead is used as an input.

## 7. Risks and limits

- **Definitions differ across studies.** Normalisation (§5.3, above all N2) is the main work, not the search.
- **Transferability.** UK, US and Nordic values may not hold for Israel (income, car availability, climate, Haifa's slopes). Anchor on `נוהל פר"ת` and the national model, and record an applicability score per estimate.
- **Evidence, convention and policy.** Guidance and models often use 2.0, the meta-analyses report about 1.5–1.7 and the Ministry guideline expects 2–3. Keep the three apart (N6); a central value outside 2–3 would fail the Ministry's own check.
- **Thin evidence on vertical access and on BRT↔LRT interchanges**, and SP hypothetical bias. Expect ranges, not points, for RQ1 and RQ2, and ask the planning team for the design (§8).
- **Paywalls.** Prefer open versions; PDFs may need to be supplied.
- **The screen is screening grade** (paths held fixed): rerun the real chain before any decision.
- **Interactions.** The OVT research cannot settle the LRT premium or λ_T; report them with the new OVT values and do not let a lower walk penalty and the premium compensate for the same omitted attribute.

## 8. Inputs needed

1. **Israeli models.** Documentation of the national and metropolitan (Gush Dan, Haifa) models: OVT weights, boarding and transfer penalties, wait caps, walk speed and detour, station-specific access, calibration report; the current edition of `נוהל פר"ת` with any updates; and the full text of the Ministry's 2024 metropolitan-model validation guideline (draft 6 was uploaded to an earlier session but is not in the repository). Holders: Ministry of Transport, Netivei Israel, the metropolitan authorities.
2. **Station design from the planning team.** Depths and levels, escalators and lifts, gate layout, platform type, and the BRT↔LRT interchange layout (same platform, cross-platform, level change, walking distance). No public source replaces this.
3. **Decisions.** (a) For the walk and wait weights, which governs the central case: the guideline range (2–3) or the evidence median? Proposed default in §5.5: inside the guideline range, evidence as the sensitivity. (b) Go-ahead for the new model parameters (§5.6) and for the public-source work of P1–P2.
4. **For P3:** an OSM extract of the study area (task E6 is blocked on it) and a DEM.

## 9. Reproduction

```bash
python3 tools/ovt_sensitivity_screen.py [--csv results.csv]   # needs numpy; reads committed outputs only
```

It validates against `Output/skims/lrt_capture_scenarios.csv` first (and exits with an error if the replication is off by one trip or more), then prints every table of §2.
