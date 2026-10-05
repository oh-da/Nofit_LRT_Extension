# Two reports on the out-of-vehicle weights — a comparison

*4 October 2026. Compares `docs/OVT_WEIGHTS_PARAMETER_MEMO.md` (this repository's execution of `docs/OVT_WEIGHTS_RESEARCH_PLAN.md`, METHODOLOGY §6al; "the memo") with the independent report `OVT_WEIGHTS_RESEARCH_REPORT_Astra.md` of the same date ("the Astra report"), which was written against the same plan.*

## 1. Bottom line

The two reports agree on the direction of every parameter and disagree on three things: **how much of the evidence counts as verified, whether `נוהל פר"ת` has a 2021 edition that fixes the Israeli values, and what the central case should be now.**

- **Same conclusions.** Keep walk 2.0 and wait 2.0; a free BRT–LRT transfer and no underground station access are unsupported; a lower LRT-specific walk weight is not justified for the central case; the walk-distance shortcut should give way to OSM + DEM routing; λ must be re-estimated after any change; the LRT premium may double count the omitted access and interchange attributes; the station and interchange design is the missing input.
- **Different verification standard.** The memo could not read any document (the session's network policy blocked every host) and therefore, by the plan's own rule, confirms nothing and keeps every value, carrying the evidence as a run sensitivity. The Astra report treats its five sources as read and reaches "supported / retain" and "policy-supported" statuses on that basis, without an evidence table, per-estimate flags or section references.
- **The hinge is `נוהל פר"ת` 2021.** The Astra report's most consequential claim is that a 2021 edition exists on gov.il and specifies walk 2.0, wait 2.0, a 4 km/h walking speed and pure transfer penalties of 12 (bus–bus), 6 (bus–rail) and 3 (rail–rail) minutes. The memo's searches found only the 2012 edition and no transfer or walk-speed values; gov.il was unreachable. If the claim holds, four of the memo's "range only" rows become policy-supported and two recommendations change (walk speed, mode-pair-specific penalties). **It has to be checked by opening the PDF and citing the section**, which neither report has done.
- **Different coverage.** The Astra report stops at P4 ("P5 model rerun pending") and reasons from the screen; the memo ran the real chain (steps 31 → 33, then the step-40 factorial) on seven sets, and now on the Astra report's central set as well (§4 below).

## 2. Parameter by parameter

| Parameter | Model today | Astra central (range, status) | Memo proposed central (range, status) | Difference |
|---|---|---|---|---|
| Walk weight | 2.0 | 2.0 (1.5–2.5; "supported / retain") | 2.0 (1.5–2.5; "range only, unverified") | none in value; status only |
| Wait weight | 2.0 | 2.0 (1.5–2.5; supported) | 2.0 (1.5–2.5; range only) | none in value |
| LRT-specific walk weight | none | none; sensitivity only | none; one hypothesis run (1.65) reported, not proposed | none |
| Walk speed | 4.8 km/h (80 m/min) | **4.0 km/h** central, 4.8 as the fast sensitivity ("policy-supported change", from `פר"ת` 2021) | keep 80 m/min; × 0.85 / × 1.3 sensitivities; verified model configs use 3 mph (4.83 km/h) and 2.8 mph; Israeli national model reportedly 4 km/h + 2 min (unverified) | **substantive**: hinges on `פר"ת` 2021 |
| Detour factor | 1.3 | replace with OSM + DEM; interim 1.3–1.5 | same; the S5 extract §3 gives the method; blocked on data | none |
| Wait rule | ½ headway, cap 10 min | keep 2.5 min at 5-min headway; **replace the 10-min cap** with a frequency-sensitive rule | keep; the cap is inside practice (MTC / SEMCOG step the weight to 1.0 beyond 10 min; Emme advises a lower wait factor rather than a cap); 2.5 min at 5 min is if anything high (43 % timed arrivals at 5-min headways) | minor; affects only bus pairs with headways above 20 min |
| Bus–bus transfer penalty | 8 (shared) | **12** (7–16; "policy-supported central", `פר"ת` 2021) | 8 (5–10; confirm only, ≈ nil effect on capture) | value differs; model effect under 1 % either way (the bus–bus penalty sits in the *competitor's* GC on the 178 non-direct bus pairs, so 12 would raise LRT capture slightly) |
| Bus–LRT transfer penalty | 8 (shared) | **6** (5–10; policy-supported) | 8 (5–10) | value differs; small effect; needs the shared `TRANSFER_PEN` split in code |
| BRT–LRT transfer penalty | 0 | **6** (3–10; range only; `פר"ת` bus–rail 6 as the analogue) | **4** (0–7; range only; cross-platform proxies 3.6–5, level change 4.7–11) | both inside each other's range; 6 presumes a level-change-type interchange, 4 a same-platform one |
| LRT–LRT transfer penalty | 0 (unused, single line) | 3 (2–5; `פר"ת` rail–rail) | not addressed (unused until branches exist) | not yet material |
| Underground station access | none | **2.0 min per end** (1.5–3.0; range only; "actual internal access time, not an additional subjective penalty") | **1.5 UG / 0.5 surface** (0–3; range only; coded as walk-weighted minutes per end) | 2.0 vs 1.5, and a weighting question (§5) |
| Central-case status | — | 4,254 "likely optimistic"; proceed to P5 with a new central set | 4,254 unchanged until the documents are read and the design is known; the −31 % "today's weights plus the two terms" case shown next to it | **the decision the plan leaves to the client (§5.5, §8.3)** |

## 3. Where the reports agree, and why that matters

1. **The weights are not the issue.** Both find that 2.0 / 2.0 is defensible — the practice median (the memo verified this in ten calibrated model families), the floor of the Ministry's 2–3, inside TAG's 1.5–2.0 and 1.5–2.5 — and that the meta-analyses' lower values (≈ 1.5–1.7) belong in the low sensitivity. The Astra report's segment values for the 2026 meta-analysis (RP rail users ≈ 1.6, bus ≈ 1.9; SP 1.4 / 1.6) and the memo's pooled values (SP 1.50, RP 1.75) are the same paper read at different grain and are consistent.
2. **The zero-valued terms are the issue.** Both say a free BRT–LRT transfer and an access-less underground station are below every value found and are the largest single items. Both put the final values on the station and interchange design.
3. **No LRT-specific walk weight.** The Astra report says the evidence is insufficient; the memo adds the verified fact that none of ten calibrated models does it (rail preference is an in-vehicle multiplier of 0.85–0.9 or a boarding penalty).
4. **Process.** Both require λ re-estimated after the GC changes, a review of the 5-min premium for double counting, and OSM + DEM walk access as the real walk-time fix.

## 4. What the model says about the Astra central set

The Astra report did not rerun the model and warns, correctly, that the screen effects must not be added. The memo's chain can run its central set except for two items step 31 cannot set alone: the bus–bus / bus–LRT split (one shared `TRANSFER_PEN`) and the walking speed (a step-26 input). Set `astra_central_no_walkspeed` (walk / wait 2.0, transfer 6, BRT–LRT 6, 2.0 min per underground end, surface 0) is now in `Output/ovt_research/parameter_sets.csv` and `chain_results.csv`:

| Case | Underground (4,254) | Ground (3,206) | λ M1 |
|---|---|---|---|
| Astra central without the walk-speed change — real chain, steps 31 → 33 | **2,566 (−39.7 %)** | 2,760 (−13.9 %) | 0.037 (0.003–0.070) |
| … at the re-estimated λ | 2,068 | 2,257 | |
| Walking speed 4.0 km/h alone — screen (walk time × 1.2) | 3,871 (−9.0 %) | 2,914 (−9.1 %) | |
| Astra central in full — screen (× 1.2 walk, BRT–LRT 6, 2 min per end, transfer 6 or 12) | ≈ 2,240–2,280 (−47 %) | n/a | |
| Memo's nearest set, guideline_central_plus_access (2 / 2 / 8 / 4 / 1.5, 0.5) — real chain | 2,922 (−31.3 %) | 2,601 (−18.9 %) | 0.035 |

So the Astra report's "likely optimistic" is quantified: its own central set takes the underground case down by about 40 % through the chain, about 47 % with the slower walk, against the memo's −31 % for the same two terms at their lower medians. The ground alignment loses far less (−14 %) because it carries no station-access term — the Astra set gives the surface stations nothing, the memo's gives them 0.5 min. The bus–bus 12 the chain could not set would add roughly +50 trips (screen). Note that the Astra report's screen table quotes "around 4 km/h roughly −13 %"; the screen's × 1.2 row (4 km/h exactly) is −9 %, and −13 % is the × 1.3 row.

## 5. Where the reports differ, and what decides it

**5.1 Verification.** The memo's 275 estimates carry a verification flag each: 20 read in full (model configuration files on GitHub), 255 from search summaries, with the contradictions between summaries marked "CONFIRM" in the extracts. The Astra report lists five sources and cites none by section or table; its `פר"ת` 2021 values, its segment multipliers and its "UK and US practice" statements cannot be traced to a page. That is not a judgement on their accuracy — the memo's own numbers are mostly unread summaries too — but it means the Astra statuses ("supported", "policy-supported") are stronger than its documentation. Under the plan's §1 rule neither report has confirmed anything yet.

**5.2 `נוהל פר"ת` 2021.** The URL the Astra report gives (gov.il, `nohal_prat_21`) is plausible and was unreachable from this session; the memo's Hebrew searches returned only the 2012 PDF and fare-reform pages, and the one Hebrew snippet attributing "wait perceived 2–4×" to `פר"ת` is itself unresolved. Everything that separates the two reports' recommendations — walk speed 4.0, bus–bus 12, bus–LRT 6, rail–rail 3 — rests on this one document. **Open it, cite the section, and add the rows to the evidence table as "read in full".** If it says what the Astra report says, the memo's walk-speed and transfer-penalty rows change status and the model needs the small code change of §6.

**5.3 Station access: time or penalty.** The Astra report wants the 2 min "represented primarily as actual internal access time, not automatically as an additional subjective penalty on top of internal walk time". The memo codes the term as minutes added to the station walk, weighted by the walk weight (2.0), so 2 min per end is 8 generalized minutes per trip. Whether an escalator and gate minute deserves the walk weight, a lower one (Sound Transit factors all out-of-vehicle time by 2.0; STOPS adds unweighted minutes per level) or a boarding-penalty treatment is a real modelling choice the two reports resolve differently; halving the weight roughly halves the −23 % / −31 % effects. The design information settles the minutes; the weighting is a decision.

**5.4 Walking speed.** The memo saw no reason to move from 80 m/min: the verified model configurations use 3 mph (4.83 km/h), level walking speeds are 1.2–1.4 m/s, and the plan's own internal check (survey bus door-to-door times × 1.4 above the timetable, §5.5) argues for *more* out-of-vehicle time but does not say where. The Astra report's 4.0 km/h is a policy value, if `פר"ת` 2021 gives it, and it is what the Israeli national model reportedly uses. Both can be true: 4.0 km/h as the Israeli convention, 4.8 as the physical level speed. The chain cannot test it without step 26 (needs the bus-speed LFS file and the step-29 outputs); the screen says −9 % on its own.

**5.5 Wait cap.** The Astra report calls the 10-min cap "not a strong Israeli policy default" and wants a frequency-sensitive rule. The memo found the cap inside practice and the alternative mechanisms documented (weight step, lower wait factor). The difference is immaterial to the LRT (2.5 min either way) and small for the bus (it touches only headways above 20 min).

**5.6 The central case.** The Astra report moves it now (its §13 matrix); the memo keeps it and shows the band. The plan makes this a client decision (§5.5 "do not choose silently", §8.3). The memo's position is the plan's default; the Astra report's is a recommendation to change the default. The evidence both reports hold supports the direction of the change, not yet its size.

## 6. What each report has that the other lacks

| In the memo, not in the Astra report | In the Astra report, not in the memo |
|---|---|
| The evidence table (275 rows), five extracts with URLs, per-row verification and Haifa-applicability scores | The `נוהל פר"ת` 2021 edition and its values (to be verified) |
| The verified stream: ten calibrated model families' walk, wait, transfer and rail-IVT parameters read from source | A mode-pair-specific transfer structure (bus–bus / bus–LRT / BRT–LRT / LRT–LRT) as the recommended model form |
| The active-mode stream: slope functions, stairs and escalator multipliers, crossing delay, rail-vs-bus catchments, and a written method for Haifa | A walking-speed recommendation tied to Israeli policy |
| The Ministry guideline's published edition 1.0 (January 2026) and its ±20 % OVT sensitivity requirement | The open manuscript of the 2026 meta-analysis (White Rose eprint 239301) and the Sound Transit WSBLE technical appendix as sources |
| The chain reruns: seven (now eight) sets through steps 31 → 33, λ per set, the step-40 tornado | A recommendation to revise the wait cap |
| The parametrised notebooks and tools to rerun any set in 80 s | — |
| The fixed latent defect in step 31 (the Metronit penalty was not reaching the path cost) | — |

## 7. Reconciliation — what to do next

1. **Verify `נוהל פר"ת` 2021** from a session or machine that can reach gov.il: confirm the edition, quote the section for walk and wait weights, walking speed and the three transfer penalties, and add the rows to `evidence_table.csv` as read in full. This single step decides most of the disagreement.
2. **Adopt the Astra report's transfer structure in code** regardless: split `TRANSFER_PEN` into `BUS_BUS_TRANSFER_PEN` (the 178 non-direct bus pairs) and `BUS_LRT_TRANSFER_PEN` (the bus feeder legs), beside the existing `BRT_LRT_TRANSFER_PEN` and `LRT_LRT_TRANSFER_PEN`. A small change to step 31; defaults 8 / 8 reproduce today's outputs.
3. **Add the walking-speed sensitivity through step 26** (4.0 km/h; needs the bus-speed LFS file), then rerun 31 → 33 for the Astra central set in full.
4. **Decide the station-access weighting** (walk-weighted, unweighted, or boarding-penalty) before any central-case change; the design information decides the minutes.
5. **Put both central cases to the client** with the band: today's 4,254 / 3,206; the memo's "today's weights plus the two terms" 2,922 / 2,601; the Astra set 2,566 / 2,760 (≈ 2,250 underground with the slower walk). The ground alignment is the robust one in every reading.
6. Keep the rest of the plan's §8 inputs (station and interchange design, Israeli model documentation, OSM + DEM) as the critical path; both reports say so.
