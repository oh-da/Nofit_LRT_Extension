# Out-of-vehicle weights and times — parameter memo

*4 October 2026. Outcome of `docs/OVT_WEIGHTS_RESEARCH_PLAN.md` (P1–P5). Evidence in `Output/ovt_research/` (`evidence_table.csv`, 275 estimates; `extracts/*.md`, five stream reports; `parameter_summary.csv`; `parameter_sets.csv`; `chain_results.csv`). Model side in METHODOLOGY §6al.*

## 1. Outcome

**No parameter is confirmed; every parameter keeps its current value, and the evidence range is carried as a sensitivity.** This is the plan's own rule (§1: "confirmed" needs three independent sources read and normalised; §5.6: "do not use an unverified lead as an input"), applied to what the session could actually do: the cloud environment's network policy blocked every document host (gov.uk, gov.il, infocenters.co.il, ScienceDirect, ResearchGate, ITF, TRB, FTA, WSDOT, the university repositories), so **no study, appraisal guideline or Israeli document was read in full**. The 275 estimates in the evidence table come from search-engine summaries of those documents, except the 20 rows of stream S4 (model configuration files on GitHub), which were read and are verified. The two Israeli anchors — `נוהל פר"ת` 2012 and the Ministry's metropolitan-model validation guideline, of which the search found the published **edition 1.0 of 13 January 2026** on gov.il — remain unread.

What the evidence does establish, even at search-summary grade, is the shape of the problem:

| Parameter | In the model | Empirical SP / RP (unverified) | Guidance (unverified) | Calibrated models (verified) | Israeli policy | Status |
|---|---|---|---|---|---|---|
| Walk weight (× IVT) | 2.0 | median ≈ 1.6, range 1.3–2.0 | TAG 1.5–2.0, ATAP / TfNSW 1.5, Sweden 2, FTA ≈ 2 | **2.0** (10 model families, 1.0–2.5) | OVT ÷ IVT 2–3 | range only; 2.0 = practice median, floor of the policy range, above the evidence median |
| Walk weight, LRT vs bus | one value | one summary of Wardman 2004: bus 2.15 / rail 1.65, contradicted in the same summary | none give a mode-specific value | **none of 10 models** does; rail preference is an IVT multiplier (LRT 0.85–0.9) or a boarding penalty | — | not supported; kept as a hypothesis run |
| Walk speed / detour | 80 m/min, × 1.3, no slope | 1.2–1.4 m/s level; 10 % grade ≈ −25 % speed; stairs ≈ 2× time | — | **3 mph** (MTC, ARC, MWCOG, SANDAG), 2.8 mph (SEMCOG) | — | range only; slope-aware times (task E6) are the real item |
| Wait weight (× IVT); wait rule | 2.0; ½ headway, cap 10 min | median ≈ 1.5, range 1.0–2.0; ½ headway universal; random-arrival threshold 5–11 min | TAG 1.5–2.5, ATAP 1.4 / 1.5, TCQSM 2 | **1.5 or 2.0** (bimodal), transfer wait ≥ initial; weight step rather than a cap at 10 min | OVT ÷ IVT 2–3; `פר"ת` reportedly "wait perceived 2–4×" (snippet) | range only; 2.0 inside every range |
| Bus ↔ LRT, bus–bus transfer penalty (pure, min) | 8 | ≈ 5–10 (London RP 5.0, Madrid SP 10.9); bus–bus SP 16–21 | TAG 5–10, ATAP 5 / 7 / 10, STOPS 5 | **≈ 10** (0–27) | — | range only; 8 inside every guidance range; ≈ nil effect on capture |
| BRT ↔ LRT transfer penalty (pure, min) | 0 | cross-platform ≈ 4–5 (3.6–5), level change ≈ 7 (4.7–11) | ATAP between-mode 7 / 10 | not distinguished | — | range only; **zero is below every reported value**; no BRT–LRT study exists |
| Underground station access (min per end) | none | physical 1–3 min per direction; level change ≈ 1 min or 20–25 % of the interchange penalty | STOPS 0.5 min per level; Sound Transit rail boarding 2 min + 0.5 per escalator, OVT × 2 | TM2 LRT boarding 4.5 min; DaySim 8 min per boarding | — | range only; **none is below every reported value** |

Full detail per parameter, with the proposed central / low / high and the sources behind each, is in `Output/ovt_research/parameter_summary.csv`.

## 2. What was done, and what was not

| Stage | Done | Not done, and why |
|---|---|---|
| P0 screen | done earlier (plan §2) | — |
| P1 guidance (S1) and model documentation (S4) | S1 from search summaries: TAG M3.2, PDFH, ATAP M1, TfNSW 2025, NZ MBCM, KiM 2022, TØI 2020, ASEK, TERESA, FTA / STOPS, TCQSM, `פר"ת` 2012, MOT guideline ed. 1.0 (Jan 2026). S4 **read in full** from GitHub: ActivitySim prototype_mtc / production_semcog / prototype_arc / prototype_mwcog, SANDAG ABM3, SimOR, PSRC ActivitySim, SoundCast / SeaCast / PierceCast / BKRCast DaySim and Emme, MTC TM1 skims and TM2 (2023 dev), CMAP, MATSim scenarios, OpenTripPlanner and R5 defaults | S1 texts unread (egress blocked). Request letters of plan §8 not sent (external). Israeli national / metropolitan model parameters: nothing public found |
| P2 meta-analyses (S2) and primary studies (S3) | 118 rows across RQ1–RQ4: Wardman 2001 / 2004 / 2016 / 2026, Abrantes & Wardman 2011, TRL593, Kouwenhoven 2014, Wardman & Hine 2000, Guo & Wilson 2004 / 2011, Garcia-Martinez 2018, Schakenbos 2016, Yap, Wong & Cats 2024, Douglas & Jones 2013, Nielsen 2021, NTA Ireland 2024, TfL 2016, Fan & Machemehl 2009, Luethi 2007, Ingvardson 2018, Psarros 2011, Watkins 2011, Brakewood 2014 | all from summaries; several snippets contradict each other (flagged "CONFIRM" in the extracts) |
| P3 active-mode (S5) | 40 rows: slope functions (Tobler, Naismith, Irmischer & Clarke, Campbell), level speeds, crossing delay (HCM), circuity, rail-vs-bus catchments (Calgary, Sydney, Brisbane, Montreal, Melbourne), stairs / escalator multipliers, shade; the r5, OpenTripPlanner, OSMnx and r5py slope code read in full; a method for Haifa written up in the S5 extract §3 | slope-aware walk times not computed: Overpass and the DEM hosts are blocked (task E6 stays blocked) |
| P4 synthesis | this memo; `parameter_summary.csv`; `evidence_table.csv` with the N1 / N2 / N5 normalisation where the unit allowed it | quality-weighted medians are by stream and by eye, not a meta-regression (fewer than 10 comparable *verified* estimates per parameter) |
| P5 model rerun | **done**: steps 31 → 33 for seven parameter sets, λ re-estimated on each set's generalized cost; the OVT sets added to the step-40 factorial and tornado | step 32 (forecast years) not rerun: skims are held fixed there and the 2022 ranking is what the decision needs; step 26 not rerun (walk speed / detour / wait cap unchanged, see §4) |

## 3. The evidence, by research question

All values below are from search summaries unless marked *(verified)*. The extracts list every number with its source URL and a "CONFIRM" flag where summaries disagreed.

**RQ3 — walk weight.** The meta-analyses sit below the convention: Wardman 2001 / 2004 walk 1.66 ± 0.12; Wardman, Chintakayala & de Jong 2016 1.45 urban / 1.70 inter-urban; a 2026 worldwide meta-analysis by Wardman and co-authors recommends 1.50 (SP-weighted) to 1.75 (RP-weighted) and says so explicitly against the "rule of two"; TRL593 1.4–2.0; the Dutch national study 2014 ≈ 1.5 (2022 ≈ 1.5–2.0, and in one summary "not significantly different from 1"); Norway 2020 ≈ 1.3. Guidance: TAG M3.2 1.5–2.0, ATAP and TfNSW 1.5 ("normal effort, uncongested"), Sweden 2, FTA practice ≈ 2 (0.25–16 observed). Calibrated models *(verified)*: 2.0 in MTC, SEMCOG, SANDAG, SimOR, DaySim Seattle; 1.8–2.0 MWCOG; 2.0 / 2.5 (short / long) ARC; 1.97 PSRC; transfer walk 2.5 in SANDAG and SimOR, 3 in CMAP's assignment. **No model uses a lower walk weight for rail access than for bus** *(verified across all ten)*; the rail preference is an in-vehicle multiplier (LRT 0.85–0.9, heavy rail 0.8, commuter rail 0.7) or a boarding penalty. The observed longer walks to rail (medians ≈ 1.75–2.4× bus in Sydney, Brisbane, Montreal, Calgary; not in Melbourne for a street tram) are a supply / catchment effect, not a weight.

**RQ4 — wait.** Wardman 2004 1.47 ± 0.18 (headway 0.80 ± 0.08); Abrantes & Wardman 2011 ≈ 2.0; Wardman 2016 urban 1.50; TfL 2016 London bus 2.0, falling to 1.7 / 1.0 / 0.8 for users of real-time information; ATAP 1.4 platform / 1.5 transfer wait; TCQSM 2; older WebTAG 2.5; Netherlands 2022 ≈ 1.0. Models *(verified)*: initial wait 1.5 (SANDAG, SimOR, PSRC, MWCOG, TM2) or 2.0 (MTC, SEMCOG, ARC, DaySim); transfer wait 2.0 (2.5 PierceCast, 3–3.5 in TM2's assignment); half-headway everywhere an assignment file was readable; MTC and SEMCOG drop the weight to 1.0 beyond a 10-minute initial wait rather than capping the time; Emme's guidance advises a lower wait factor rather than a cap. Empirical random-arrival threshold 5–11 min (2–3 min on the London Underground; 43 % timed arrivals at a 5-min headway in Copenhagen), so 2.5 min at the LRT's 5-min headway is if anything high. Reliability is handled outside the weight in every source; real-time information lowers both perceived wait and the weight.

**RQ5 — bus transfer penalty.** Pure (net of walk and wait): London RP 5.03; Madrid SP 10.9 (15.2–17.7 in another summary, probably total); Wardman, Hine & Stradling 4.5 bus–bus (3.6 guaranteed), 8 rail–rail; Dublin SP 16–21; Douglas & Jones Sydney 21 bus–bus, 17 bus–rail; literature span 4–20. Guidance TAG 5–10, ATAP 5 / 7 / 10, STOPS 5 (to 10), VTPI 5–15. Models *(verified)*: MTC / SEMCOG 10 per transfer (5 at trip level), PSRC 22–27, SANDAG ≈ 26 for the first transfer (convex), MWCOG 0, DaySim 8 per boarding, TM2 2.5–4.5 per boarding by mode, CMAP 25 at assignment. The model's 8 is inside every guidance range; the screen already showed the parameter moves capture by under 1 %.

**RQ2 — BRT ↔ LRT.** No study values a BRT–LRT interchange (Currie 2005 says so explicitly). Proxies for a same-platform or cross-platform interchange: London RP 3.6 (cross-platform metro), Sydney 5 (no platform change), NL tram–bus 4.8, ATAP same-facility 5 (within mode) / 7 (between modes); with a level change London 4.7, Sydney 7–11, ATAP 7–10. A free transfer is below every value found.

**RQ1 — station access.** No valuation study of vertical access was found. Practice: STOPS adds 0.5 min per level (0.5 / 1.0 / 1.5) plus an optional station penalty and, from v1.50, explicit vertical profiles; Sound Transit codes rail stations with pedestrian and escalator links (0.5 min per escalator link), a 2-min rail boarding penalty against 5 for bus, and factors all out-of-vehicle time by 2.0; TM2 (2023) uses a 4.5-min LRT boarding penalty *(verified)*; DaySim Seattle 8 min per boarding *(verified)*. Behaviourally, a level change is worth ≈ 1 min or 20–25 % of the interchange penalty (London RP) and a platform change +2 min (Sydney SP); stairs ≈ 1.86× and escalators ≈ 1.28× level walking time in Dutch station route choice. Physically, a mid-depth escalator ride is ≈ 1.5 min and a deep one 2.5–3 min; fare gates are 1–2 s per passenger unless queuing. A Haifa underground end of 1–3 min before weighting is consistent with all of this.

**Israel.** `פר"ת` 2012: the summaries confirm it defines door-to-door time as walk + wait + in-vehicle + transfer and gives values of time by purpose; one Hebrew snippet attributes "wait perceived 2–4 times in-vehicle time" to it, unresolved. No newer edition was found. The Ministry guideline: edition 1.0 published 13 January 2026 (URL in the RQ4 extract §4), "out-of-vehicle value 2–3 relative to in-vehicle", OVT reported for three periods, ±20 % sensitivity on the OVT coefficients; nothing on transfer penalties, wait rules or walk speed. The national model: the Bank of Israel discussion paper 2023.12 (Amedi) reportedly describes its walk access as 4 km/h plus a 2-min constant up to 1 km, with distance-banded effective speeds in the same summary — to be read. No parameter report of the national or metropolitan models is public.

## 4. The model reruns (steps 31 → 33, headway 5, full bus competition, 25 V2 areas, 06:00–09:00)

Parameter sets in `Output/ovt_research/parameter_sets.csv`; results in `chain_results.csv`. Capture at the assumed λ 0.03 / λ_T 0.06 / premium 5; λ re-estimated by step 33 (M1, car vs transit on the set's bus and car GC) and the capture at that λ (λ_T = 2λ) alongside.

| Set | walk / LRT walk / wait | transfer / BRT–LRT / access UG, GR (min) | Underground (4,254) | Ground (3,206) | λ M1 (95 %) | Underground at λ M1 |
|---|---|---|---|---|---|---|
| empirical_low | 1.5 / 1.5 / 1.5 | 8 / 0 / 0, 0 | 4,935 (+16.0 %) | 3,765 (+17.4 %) | 0.030 (−0.004–0.064) | 4,935 |
| lrt_walk_weight (hypothesis) | 2.0 / 1.65 / 2.0 | 8 / 0 / 0, 0 | 4,867 (+14.4 %) | 3,686 (+15.0 %) | 0.035 (0.002–0.068) | 4,591 |
| default (today) | 2.0 / 2.0 / 2.0 | 8 / 0 / 0, 0 | 4,254 | 3,206 | 0.035 (0.002–0.068) | 3,910 |
| brt_lrt_penalty_only | 2.0 / 2.0 / 2.0 | 8 / 4 / 0, 0 | 3,837 (−9.8 %) | 2,861 (−10.8 %) | 0.035 | 3,491 |
| empirical_central | 1.66 / 1.66 / 1.5 | 8 / 4 / 1.5, 0.5 | 3,465 (−18.5 %) | 3,011 (−6.1 %) | 0.032 (−0.003–0.066) | 3,339 |
| station_access_only | 2.0 / 2.0 / 2.0 | 8 / 0 / 1.5, 0.5 | 3,257 (−23.4 %) | 2,920 (−8.9 %) | 0.035 | 2,858 |
| guideline_central_plus_access | 2.0 / 2.0 / 2.0 | 8 / 4 / 1.5, 0.5 | 2,922 (−31.3 %) | 2,601 (−18.9 %) | 0.035 | 2,533 |
| guideline_high | 2.5 / 2.5 / 2.5 | 10 / 7 / 3, 0.5 | 1,456 (−65.8 %) | 1,970 (−38.6 %) | 0.036 (0.006–0.067) | 1,053 |

**Reading.**

1. **The band is 1,456–4,935 underground (−66 % to +16 %), 1,970–3,765 ground.** In the step-40 tornado the OVT set is now the widest factor (range 3,479 trips), ahead of λ / premium (2,865) and the LRT regime (1,889). The screen's bounds (2,900–5,165 without vertical access, 1,777 with) are confirmed in direction and roughly in size; the chain re-optimises the feeder paths, so the penalty effects are a little softer per minute but the sets stack more terms.
2. **The two terms the model sets to zero dominate the downside.** A 4-min pure BRT–LRT penalty alone costs 10 %; station access of 1.5 min per underground end alone costs 23 % (9 % at the surface). Together on today's weights, −31 % underground. Neither is below the evidence; both depend on the station and interchange design the planning team has not yet supplied (plan §8).
3. **The weights pull the other way.** The empirical medians (walk 1.5–1.66, wait 1.5) raise capture by 16 % on their own, and the "empirical_central" set that combines them with the two new terms lands at −18 % underground but −6 % at the surface. The walk weight matters because of the LRT's 13.9-min trunk walk against 5.1 for the bus (plan §2); the ground alignment is less exposed to the access term and more to the weights.
4. **λ is robust to the weights.** The person-level estimate moves from 0.035 to 0.030–0.036 across the sets (M3 with area fixed effects 0.049–0.053; M4 for licence holders still not identified, 0.002–0.011). The assumed 0.03 stands under every set; the capture at the re-estimated λ is 5–10 % below the assumed-λ figure for the sets where λ_M1 > 0.03 and equal where it is 0.030. The weights do not rescue or undermine the λ story; they change the GC differences themselves.
5. **The LRT-side walk weight is not a free parameter.** The hypothesis run (LRT station walk 1.65, bus 2.0) adds 14 %, nearly the whole empirical-low effect, from one unverified table in one summary; no calibrated model does this. It is reported, not proposed.
6. **The premium interaction (plan §1).** The calibrated models express the rail preference as an in-vehicle multiplier of 0.85–0.9 for LRT *(verified)*. On the trunk's 13.8 min of LRT in-vehicle time that is worth 1.4–2.1 generalized minutes, against the model's 5-min premium. If a station-access term is adopted, the premium should be re-examined with it (the premium may already be absorbing what a lower walk weight or a boarding bonus would otherwise carry), not added on top.

## 5. The policy-versus-evidence rule (plan §5.5) — proposed default, pending the client's decision

Keep the central case at walk 2.0 / wait 2.0 / transfer 8: it is the calibrated-model median *(verified)*, inside TAG, at the floor of the Ministry's 2–3 and inside every guidance range found. Carry **walk 1.5 / wait 1.5** (evidence side, +16 %) and **walk 2.5 / wait 2.5 / transfer 10** (policy side) as the weight sensitivities. Treat the **BRT–LRT penalty (0 → 4, up to 7) and the station-access term (0 → 1.5 UG / 0.5 surface, up to 3)** as the open design-dependent items: on the evidence a free, access-less underground LRT is the optimistic end, and the capture band reported to the client should show the −31 % "today's weights plus the two terms" case next to the 4,254. Both the Ministry's ±20 % OVT sensitivity (guideline ed. 1.0) and the plan's convergence rule can be met once the three Israeli documents and the top five international ones are read.

## 6. What is needed to confirm (in order of value)

1. **Read in full** (all blocked from the session, URLs in the extracts §3–4): TAG M3.2 May 2024 Table 1; ATAP M1 technical report (Douglas & Jones 2013 table); Yap, Wong & Cats 2024 (open access); Guo & Wilson 2011 (open PDF at brt.cl); Wardman et al. 2016 (open) and the 2026 worldwide meta-analysis; `נוהל פר"ת` 2012; the Ministry guideline ed. 1.0 (January 2026); Bank of Israel DP 2023.12 for the national model's walk assumptions; the Sound Transit 2015 methodology and STOPS user guide v2.53 for RQ1. A session whose network policy allows these hosts (or the PDFs placed in `Input/`) turns most "range only" rows into "confirmed" or "rejected" within a day.
2. **Station and interchange design** from the planning team (plan §8.2): depth and levels per underground station, escalators and lifts, gate layout, and whether the Metronit–LRT interchange is same-platform, cross-platform or a level change. This decides RQ1 and RQ2 — the two largest items — and no literature replaces it.
3. **Israeli model documentation** (plan §8.1): the national and Haifa metropolitan models' OVT weights, boarding and transfer penalties, wait rule and walk speed.
4. **OSM extract and DEM** for the slope-aware walk times (task E6; the S5 extract §3 gives the method: OSMnx + Copernicus GLO-30 or the Survey of Israel DTM, Tobler normalised to 1.3 m/s on the flat with the downhill bonus capped, stairs at Fruin speeds, 25–30 s per signalised crossing).
5. **Decision (plan §8.3):** which governs the central case, the guideline range or the evidence median; and whether the two new terms enter the central case now at their evidence medians or wait for the design.

## 7. Reproduction

```bash
pip install numpy pandas scipy matplotlib openpyxl statsmodels nbformat nbclient ipykernel
python3 tools/lfs_pull.py Input/Corridor_TAZ_Agg_V2.xlsx Input/TAZ_2636_Keys.xlsx Input/THS_2017-2018/trips_ths_2017.xlsx \
        Input/THS_2017-2018/ACTIVITIES_DEC18_corrected.csv Input/THS_2017-2018/HHfinal.csv Input/THS_2017-2018/PersonsFin2.csv
python3 tools/ovt_run_chain.py            # steps 31 -> 33 for every set in Output/ovt_research/parameter_sets.csv (≈ 80 s per set)
python3 tools/ovt_chain_summary.py        # Output/ovt_research/chain_results.csv (validates each set's capture formula to < 1 trip)
python3 tools/ovt_build_evidence_table.py # Output/ovt_research/evidence_table.csv from extracts/*.md
python3 tools/ovt_sensitivity_screen.py   # the P0 screen, unchanged
git checkout -- Input/ && git clean -fdq Input/   # restore the LFS pointers before committing
```

Step 31 reads `OVT_TAG`, `W_WALK`, `W_WALK_LRT`, `W_WAIT`, `TRANSFER_PEN`, `BRT_LRT_TRANSFER_PEN`, `STATION_ACCESS_UG`, `STATION_ACCESS_GR` from the environment (defaults = today's values; a non-default set must carry a tag and writes to `Output/skims/ovt_<tag>/`); step 33 reads `SKIM_DIR`. The default run reproduces the committed `Output/skims/` to the trip.
