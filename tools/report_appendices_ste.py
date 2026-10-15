"""Appendices A–D of the comprehensive report in ASD-STE100 Simplified Technical English
(reports/Nofit_LRT_Extension_Comprehensive_Report_STE.docx) — the STE counterpart of tools/report_appendices.py:
   A. Calibration of the speed and time function of the light rail (Tel Aviv Red Line → the Haifa extension, step 25)
   B. Out-of-vehicle time: the findings of the research and the values in the model (docs/OVT_WEIGHTS_PARAMETER_MEMO.md, §6al, step 45)
   C. The cost sensitivity λ: what it is, how the model uses it, with simple examples (steps 31, 33, 40, 45)
   D. The generalized cost function: why, and how we got to it (steps 26, 31, 44, 45; the same content as docs/APPENDIX_D_GENERALIZED_COST_STE100.md)
Same numbers and same figures as the English appendices. The text obeys the ASD-STE100 writing rules (see the note at the top of the
STE report); the technical names of the appendices are in the report's technical-name table. The report builder's self-check runs on
every paragraph written here too (formulas and source lines are exempt).

Two ways to run (as the English module):
   from tools/build_comprehensive_report_ste.py (the hook before doc.save): add_appendices_ste(doc, H, P, B, fig, table, CAP)
   standalone, python3 tools/report_appendices_ste.py — opens the STE report, drops a previous appendix block, appends; --only writes
   reports/Nofit_LRT_Extension_Report_Appendices_STE.docx as a document of its own.
"""
import os, sys
import numpy as np, pandas as pd
while not os.path.exists('METHODOLOGY.md') and os.getcwd() != '/': os.chdir('..')
sys.path.insert(0, os.path.join(os.getcwd(), 'tools'))
from report_appendices import FIG, UG_SEC, GR_SEC, RL_SPACING, HAIFA_SPACING, section_time, p_lrt, logsum_gain, car_shift, build_figures
REPORT_STE = 'reports/Nofit_LRT_Extension_Comprehensive_Report_STE.docx'
def m(v, d=1): return f'{v:.{d}f}'.replace('-', '−')

def add_appendices_ste(doc, H, P, B, fig, table, CAP, build_figs=True):
    if build_figs: build_figures()
    def box(text): return P(text, bold=True, check=False)
    def sources(text): return CAP('Sources: ' + text)

    # ======================= A =======================
    H('Appendix A. Calibration of the speed and time function of the light rail')
    P('This appendix answers four questions. Where do the run times of the planned line come from? Why did we measure them on the Red Line in Tel Aviv? '
      'How did we move the measurement to the Haifa alignment? What do the two regimes of the report (Prioritized and Unprioritized) mean in minutes?')
    H('A.1 Why a calibrated function', 2)
    P('Because the extension has no timetable yet, the model needs a rule that changes the distance between two stations into minutes. The usual short cut is a design speed. '
      'This short cut misses the part of a light rail trip that is not a run. This part is the deceleration, the stop at the platform, the acceleration, and the wait at the road junctions. '
      'These minutes decide if the LRT is faster than the bus on a given pair. Thus the study measured them on a light rail in operation in Israel; it did not assume them.')
    P('We selected the Red Line in Tel Aviv (operator 22, lines 34447 and 34448). One line operates in the two conditions that the study needs. '
      'The first condition is a separated, underground core through Tel Aviv, and the second is a section at street level at each end. '
      'The same vehicles and the same operator in the two conditions give two consistent measurements. One is for a line that does not wait at junctions. The other is for a line that operates with the street.')
    H('A.2 The data and the cleaning', 2)
    P('The vehicle location records of the operator give the time when each tram got to each stop. The extract has 1,078,845 stop records on 132 Thursdays between May 2023 and September 2026. '
      'We keep a journey only when it is complete (all 31 stops in sequence). Each stop-to-stop time must be plausible: more than zero and not more than 10 minutes. '
      'The result is 26,653 clean journeys and 799,590 stop-to-stop sections: 239,877 underground and 559,713 at the surface.')
    P('A section is underground only when its two stations are underground. A section with one surface station counts as a surface section. This is the cautious choice, because the portal sections have a part of the street delay.')
    table(pd.DataFrame([['Source', 'Vehicle location records of operator 22, lines 34447 / 34448'], ['Days', '132 Thursdays, 25 May 2023 to 10 September 2026 (in practice 2024–2026: no journey of 2023 passes the completeness test)'],
                        ['Raw records', '1,078,845 stop records in 36,939 journeys'], ['Kept', '26,653 complete, clean journeys; 799,590 stop-to-stop sections'],
                        ['Underground rule', 'the two stations of the section are in the list of 11 underground stations'], ['Quality rule', 'each section time is more than 0 and not more than 10 minutes']],
                       columns=['Item', 'Value']), font=8)
    CAP('Table A.1 — The calibration sample.')
    H('A.3 The measurement', 2)
    P('The calibration is a mean: the minutes that a tram takes, on average, from one stop to the next stop, in each regime. The model needs the mean (the expected time of many trips), not the typical time. Thus we use the mean and not the median.')
    box(f'Underground: {UG_SEC:.3f} minutes for each section (95 % interval 1.958–1.963).   Surface: {GR_SEC:.3f} minutes for each section (2.390–2.395).')
    fig(f'{FIG}/appA_redline_section_time_by_regime.png', 12, 'Figure A.1 — Mean stop-to-stop time by regime on the Red Line. The error bars (the 95 % intervals) are too small to see at this scale. Source: the calibration report, figure 1.')
    P('The check that the rule is correct: a complete journey on the Red Line has 9 underground sections and 21 surface sections. Thus the rule gives 9 × 1.961 + 21 × 2.393 = 67.9 minutes. '
      'The observed mean is 67.9 minutes by construction. The important item is the spread around it. The typical error for one journey is 3.7 minutes (5.5 %). '
      'The two directions differ by approximately one minute (68.9 to one end, 66.8 to the other end).')
    fig(f'{FIG}/appA_redline_trip_time_distribution.png', 12, 'Figure A.2 — Observed end-to-end times of the 26,653 clean journeys against the 67.9 minutes of the rule. Source: the calibration report, figure 3.')
    table(pd.DataFrame([['2024', 2.007, 2.528, 9482], ['2025', 1.946, 2.365, 10752], ['2026', 1.919, 2.240, 6419], ['all years (used)', UG_SEC, GR_SEC, 26653]],
                       columns=['Year', 'Underground, min for each section', 'Surface, min for each section', 'Journeys']), {'Underground, min for each section': '{:.3f}', 'Surface, min for each section': '{:.3f}'}, font=8)
    CAP('Table A.2 — The same means by year. The operation became faster each year. The study uses the pooled value. This value is 2–6 % slower than 2026 alone, thus a little cautious.')
    H('A.4 From the Red Line to Haifa: the correction for the station spacing', 2)
    P('A time for each section is useful only if we know the length of a section. The calibration report changed its minutes into speeds with an assumption of 500 metres between stops (15.3 km/h underground, 12.5 km/h at the surface). '
      'The timetable of the Red Line gives the distance at each stop. It shows that the underground stations are 970 metres apart on average, and the surface stops 577 metres. '
      'Thus 1.961 minutes for an underground section is a section at 30 km/h, not at 15 km/h. The 500 m version applied to Haifa (the first revision of the study) made the underground case two times too slow.')
    P('Thus the study divided each section time into two parts, with a fit on the 14,477 scheduled sections of the Red Line. The first part is a run time that increases with the distance. '
      'The second part is a fixed stop penalty for the deceleration, the dwell and the acceleration. Then each regime gets a scale factor, the ratio of the observed time to the scheduled time. '
      'Thus the rule gives the measured means again on the spacing of the Red Line.')
    box('Underground: time = 0.94 × (0.81 min + 1.31 min for each km)   →   46 km/h between stops plus 49 seconds at each stop.')
    box('Surface:       time = 1.02 × (1.23 min + 1.94 min for each km)   →   31 km/h between stops plus 74 seconds at each stop.')
    P(f'This form applies to each station spacing. On the Haifa extension, the 24 stations are {HAIFA_SPACING} metres apart on average (354 to 1,396 m). '
      f'A section takes {section_time(HAIFA_SPACING / 1000, "underground"):.2f} minutes in the underground style (27.6 km/h with the stops) and {section_time(HAIFA_SPACING / 1000, "ground"):.2f} minutes at street level (17.1 km/h).')
    fig(f'{FIG}/appA_section_time_vs_spacing.png', 14, 'Figure A.3 — The calibrated rule as a function of the station spacing. The dots are the mean spacing of the Red Line; there the rule gives the measured section times. The dashed line is the mean spacing of the Haifa extension. Source: Output/lrt_v2/lrt_calibration_redline_spacing_check.csv.')
    P('An example. The first section of the extension, S01 to S02 in Tirat Carmel, is 1,247 metres long. Underground style: 0.94 × (0.81 + 1.31 × 1.247) = 2.30 minutes. '
      'Street level: 1.02 × (1.23 + 1.94 × 1.247) = 3.72 minutes. The sum of the 23 sections gives the end-to-end times of the report.')
    table(pd.DataFrame([['Divided form (run time + stop penalty, used)', 40.6, 27.7, 65.8, 17.1], ['Section form (one calibrated section for each link, for each length)', 45.1, 24.9, 55.0, 20.4],
                        ['Nominal 500 m form (the speeds of the calibration report; replaced)', 73.5, 15.3, 89.7, 12.5]],
                       columns=['Version of the calibration', 'Underground style, min S01–S24', 'km/h', 'Street level, min S01–S24', 'km/h ']), {'Underground style, min S01–S24': '{:.1f}', 'km/h': '{:.1f}', 'Street level, min S01–S24': '{:.1f}', 'km/h ': '{:.1f}'}, font=8)
    CAP('Table A.3 — End-to-end time of the extension (18.7 km, 24 stations) with the three versions of the calibration. The divided form is the estimate (40.62 min, given as 40.7 in the report). The other two forms are limits. Source: Output/lrt_v2/lrt_end_to_end_summary.csv.')
    fig('Output/figures/lrt_line_profile_hf_lrt_3.png', 16, 'Figure A.4 — Cumulative travel time along the extension for each version and regime, and the stations on the alignment (step 25).')
    H('A.5 How the function enters the model', 2)
    for s in ['Prioritized regime: the extension operates with full priority at the road junctions. Thus the model gives it the separated (underground-calibrated) times: 40.7 minutes from Tirat Carmel to Hamifrats. No underground line is planned. The regimes differ only in the run time (decision of 5 October 2026).',
              'Unprioritized regime: the extension operates at street level and waits at the junctions with the traffic. Thus it gets the surface times: 65.8 minutes. The difference, 25 minutes on 18.7 km, is the value of "priority at the junctions" in time. The report shows that it is worth approximately a quarter of the passengers.',
              'Main route (Hamifrats to Nazareth): a different type of line, mostly interurban, with stations 2.1 km apart. The client specified 80 km/h between stops and 10 seconds at each stop: 33.7 minutes. This is a specification, not a calibration. It is in the list of caveats of the report (caveat 28).',
              'Checks on the calibrated regimes: a design speed of 50 km/h with 10 s at each stop gives 26.3 minutes on the extension. An allowance of 35 seconds at each stop for the deceleration and the acceleration gives 39.7 minutes, within 3 % of the calibrated 40.7. Thus the calibrated rule is a line at 46 km/h that loses approximately 50 seconds at each stop. It is not a slow line.',
              'Headway: a tram each 5 minutes on all the line. Thus the mean wait is 2.5 minutes. The time on route does not include the wait.']: B(s)
    H('A.6 Points to remember', 2)
    for s in ['We measured the rule on Thursdays only and pooled the years 2024–2026. The year 2026 alone is 2–6 % faster.',
              'The stop penalty contains the dwell times and the acceleration of the Red Line. Different vehicles or dwell rules in Haifa change the times by seconds at each stop, and by tens of seconds on the full line.',
              'The two regimes are the two pure cases. A line with priority at most junctions, but not at all junctions, is between them. The mixed alignment of step 25 (the Haifa core separated, the ends at street level) gives 56 minutes.',
              'The results of the report are more sensitive to the station access and to the transfers than to the run time (Appendix D). Thus the calibration decides the comparison of the regimes more than the total level of demand.']: B(s)
    sources('the calibration report (docs/Transit_Travel_Time_Calibration_Report_Operator22.md; the figures are from its docx); METHODOLOGY.md §6w (step 25, revision 2 and addenda); Output/lrt_v2/lrt_calibration_redline_spacing_check.csv, lrt_end_to_end_summary.csv, lrt_line_profile.csv; Output/alternatives/time_on_route.csv.')

    # ======================= B =======================
    H('Appendix B. Out-of-vehicle time: the findings of the research and the values in the model')
    P('This appendix answers four questions. Why do the minutes of walk, wait and change of vehicle have a weight? What do the literature and other models say about these weights? '
      'What did the study select? How much does the selection change the result? It is a summary of the research memo of 4 October 2026 (docs/OVT_WEIGHTS_PARAMETER_MEMO.md, 275 estimates from five sources of evidence).')
    H('B.1 Why the weights are important here', 2)
    P('Most of a public transport trip is not in the vehicle. For travellers, a minute of walk, of wait or of change of vehicle is less comfortable than a minute in a vehicle that moves. '
      'Each transport model counts these minutes more than one time. The weight is the number of in-vehicle minutes that one out-of-vehicle minute is worth.')
    P('For this study, the weights are very important because of the geometry. The extension has 24 stations, but the bus and Metronit network has thousands of stops. '
      'On the trunk pairs, the walk to an LRT station is 13.9 minutes, against 5.1 minutes to a bus stop. With a walk weight of 2.0, this is a handicap of 18 minutes before the tram moves. '
      'Thus the in-vehicle advantage of the LRT against the bus does not become a cost advantage on most pairs (Appendix D).')
    H('B.2 The research', 2)
    for s in ['The appraisal guidance of eleven countries and Israel. The sources are the UK TAG, ATAP of Australia, New Zealand, the Netherlands, Norway, Sweden and Denmark. Also the US FTA and TCQSM, the Israeli Nohal Prat, and the model validation guideline of the Ministry of Transport (2026).',
              'Meta-analyses and primary studies of the values that travellers give to the walk, the wait and the transfer. The sources are Wardman and co-authors 2001–2026, TRL, the national value-of-time studies of the Netherlands and Norway, London, Madrid, Sydney, Dublin and Copenhagen.',
              'The parameter files of ten calibrated regional models in the United States and Europe, read in full from their public repositories. The models are ActivitySim for San Francisco, Detroit, Atlanta and Washington; San Diego; Seattle; Chicago; MATSim; OpenTripPlanner; R5.',
              'Evidence on the walk: speeds, detour factors, slopes, stairs and escalators, delays at crossings, and the distance that persons walk to rail and to bus.']: B(s)
    P('One limitation controls the interpretation of the findings. The research session could not open the guidance documents and the studies (the network policy blocked their hosts). '
      'Thus 255 of the 275 values come from published summaries, and only the 20 model parameter files were read in full. By the rule of the research plan, no value is "confirmed". '
      'The findings give the range of each parameter, and the position of the study value inside it.')
    H('B.3 The findings, parameter by parameter', 2)
    table(pd.DataFrame([
        ['Walk weight', '2.0', 'studies ≈ 1.5–1.7; guidance 1.5–2.0 (Israel MoT: out-of-vehicle 2–3); ten calibrated models: 2.0', '2.0: the median of practice, the bottom of the Israeli range, above the median of the studies. Cautious for the LRT (it has the longer walks).'],
        ['Wait weight and rule', '2.0; wait = half the headway, maximum 10 min', 'studies ≈ 1.5; guidance 1.4–2.5; models 1.5 or 2.0; half the headway in all sources', '2.0 kept. At the LRT headway of 5 minutes, the wait of 2.5 minutes is high if anything: many passengers plan their arrival.'],
        ['Transfer penalty, bus ↔ LRT and bus ↔ bus', '8 felt minutes', 'studies 5–10 (up to 20 for bus–bus); guidance 5–10; models ≈ 10', '8 kept; inside each range; moves the capture by less than 1 %.'],
        ['Transfer penalty, Metronit ↔ LRT', '4 felt minutes (0 until 5 October 2026)', 'same-platform or cross-platform interchange ≈ 4–5; with a change of level ≈ 7; there is no study of a BRT–LRT interchange', 'A free transfer was below each value found; 4 adopted as the same-platform median. Each minute here is important: the Krayot market gets to the LRT by Metronit.'],
        ['Station access time', '0.5 min for each station end (was 0)', 'physical 1–3 min for each end of an underground station; practice 0.5 min for each level (FTA STOPS), 2 min rail boarding (Sound Transit)', '0.5 adopted for surface stations (no underground station is planned); the test with 1.5 minutes underground cost 23 % of the passengers in the 2022 test.'],
        ['LRT-specific walk weight', 'none (the same as the bus)', 'one unverified summary says that rail access walks have a lower value; none of the ten models does this', 'Not used. The LRT premium carries the preference for rail.'],
        ['Walk speed and detour', '4.0 km/h, straight line × 1.3 (was 4.8 km/h)', 'level walk 1.2–1.4 m/s; models 4.5–4.8 km/h; the Israeli national model reportedly 4 km/h', '4.0 km/h adopted on 5 October 2026 as the Israeli convention; walk times with slopes are an open item.'],
        ['LRT premium', '5 felt minutes against a bus path, 2.5 against a Metronit path', 'calibrated models give in-vehicle time on the LRT a value of 0.80–0.85 of the bus time, and on the BRT 0.90–0.95', 'A gap of 0.15 on the 14 minutes of the trunk ≈ 5 minutes; a gap of 0.05–0.10 ≈ 1.7–3.3, taken as 2.5.']],
        columns=['Parameter', 'In the model', 'Evidence', 'Interpretation']), font=7)
    CAP('Table B.1 — The out-of-vehicle parameters: the values of the study against the evidence. Full detail for each parameter in Output/ovt_research/parameter_summary.csv.')
    H('B.4 How much the weights change the result', 2)
    P('We ran the full chain again on nine parameter sets in the 2022 test case of step 31. This test case is the extension alone, 25 areas, 4,254 LRT trips in the three AM hours with the weights of that time. '
      'The sets go from the evidence values, which help the LRT, to the upper end of the Israeli guidance range. The upper end has a deep underground station and an interchange with a change of level; it does not help the LRT.')
    table(pd.DataFrame([
        ['Evidence medians (walk 1.5, wait 1.5)', 4935, '+16 %', 'lower weights make the felt walk of the LRT shorter, more than the walk of the bus'],
        ['The weights of today (walk 2, wait 2, transfer 8), no Metronit penalty, no station access', 4254, 'central of the test', 'the model before 5 October 2026'],
        ['… plus a Metronit ↔ LRT penalty of 4 minutes', 3837, '−10 %', 'the trips with a Metronit feeder pay for the change of vehicle'],
        ['… plus 1.5 min of access for each underground station end instead', 3257, '−23 %', 'the largest single item; the adopted 0.5 min at surface stations is a third of it'],
        ['… plus the two terms', 2922, '−31 %', 'the case "the weights of today with the two terms that were missing"'],
        ['Guidance upper range (walk 2.5, wait 2.5, transfer 10, Metronit 7, access 3)', 1456, '−66 %', 'the limit that does not help the LRT']],
        columns=['Parameter set', 'LRT trips, 2022 test', 'Against 4,254', 'Cause']), font=8)
    CAP('Table B.2 — The chain on the out-of-vehicle parameter sets (chain of step 31, 2022, 25 areas, all underground times). Source: Output/ovt_research/chain_results.csv. The reference case of the report already has the 4-minute Metronit penalty and the 0.5-minute access. Thus it is between the second and the fifth row of this table.')
    fig('Output/figures/lrt_capture_tornado.png', 14, 'Figure B.1 — The assumption that changes the 2022 LRT number most (step 40). The out-of-vehicle set is the widest factor, before the cost sensitivity and the run regime.')
    P('Two conclusions follow. The weights pull in two directions: the evidence supports lower weights, which help the LRT. '
      'At the same time, the model had set two terms to zero: the Metronit interchange and the station access. The two are below each value found, which does not help the LRT. '
      'The cost sensitivity λ is robust to all of this: a new estimate on each set stays at 0.030–0.036. Thus the weights change the cost differences, not the reaction of the travellers to them.')
    H('B.5 The decision of the study, and the open items', 2)
    for s in ['Central case: walk 2.0, wait 2.0, transfer 8, Metronit ↔ LRT 4, station access 0.5 at each end, walk at 4.0 km/h, premium 5 / 2.5. The weights are the median of practice and inside each guidance range. The two new terms enter at their lower medians, because no underground station is planned.',
              'Sensitivities: the evidence weights (walk and wait 1.5) and the guidance weights (2.5, transfer 10). Also the station access and interchange terms up to their upper values.']: B(s)
    B('Open items, in the sequence of their value:')
    for s in ['Read the Israeli documents in full. An independent review gives these values for the 2021 Nohal Prat: walk and wait 2.0, 4 km/h, transfer penalties 12 bus–bus, 6 bus–rail, 3 rail–rail. This is not verified here.',
              'The design of the stations and of the interchange: depth, escalators, a Metronit interchange on the same platform or not.',
              'Walk times with slopes for Haifa.',
              'The policy decision: does the guidance range or the evidence median control the central case?']: B(s, 2)
    sources('docs/OVT_WEIGHTS_PARAMETER_MEMO.md and docs/OVT_REPORTS_COMPARISON_2026-10-04.md; METHODOLOGY.md §6al and §6aq; Output/ovt_research/evidence_table.csv, parameter_summary.csv, parameter_sets.csv, chain_results.csv; Output/figures/lrt_capture_tornado.png (step 40).')

    # ======================= C =======================
    H('Appendix C. The cost sensitivity λ: what it is, how the model uses it, with simple examples')
    P('This appendix answers five questions:')
    for s in ['What does the number λ ("lambda") do in the model?', 'Why are there two of them?', 'How does a cost difference become a number of passengers?', 'How did we estimate λ from the survey?', 'Why does the report give a range?']: B(s, 2)
    P('Section 2.5 of the report gives the short version. This appendix shows the arithmetic.')
    H('C.1 The idea', 2)
    P('The model does not decide for each traveller. It changes a difference in felt minutes between two options into the share of travellers who select each option, with a smooth curve. '
      'Equal costs give an equal split. A small advantage gives a small majority. A large advantage gives a large majority, never 100 %. λ is the slope of this curve.')
    box('Share that selects option A = 1 / (1 + e^(λ × (cost of A − cost of B)))')
    P('With λ = 0.03 for each felt minute, each minute of advantage changes the odds between the two options by approximately 3 %. Ten minutes change them by approximately 35 %. '
      'A large λ means that travellers react strongly to small cost differences. A small λ means that habit, availability and items that the cost does not contain have the control.')
    H('C.2 Why there are two λ', 2)
    for s in ['λ_T = 0.06 inside public transport. On a pair of zones that already has a bus or Metronit path, the LRT path competes with it. The two options are similar (the two are public transport, with the same fare). Thus the travellers are sensitive to the minutes between them.',
              'λ = 0.03 between the car and public transport. When the LRT is added, the public transport "bundle" as a whole becomes better, and some car trips move to it. A car owner compares the car with a public transport option. This car owner reacts to the cost approximately half as strongly as a passenger who selects between two public transport paths.',
              'The ratio λ_T = 2λ is a usual value for nested models. It is an assumption, not an estimate on this corridor. The data support the size of the pooled λ (C.5). The ratio is a convention of the models.']: B(s)
    H('C.3 Example 1: the LRT against the bus on one pair', 2)
    P('Take the example of section 2.4. From Kiryat Haim to Bat Galim, the bus trip feels like 58 minutes and the LRT trip like 48 minutes. This is an advantage of 10 minutes for the LRT (with the premium of 5 minutes). '
      'With λ_T = 0.06, the LRT takes 1 / (1 + e^(−0.06 × 10)) = 65 % of the public transport passengers of the pair. If the pair has 100 public transport trips in the AM peak, 65 use the LRT and 35 stay on the bus.')
    advs = [-10, -5, 0, 5, 10, 20, 30]
    table(pd.DataFrame([[(f'{a:+d}' if a else '0').replace('-', '−')] + [f'{100 * p_lrt(a, lt):.0f} %' for lt in (0.03, 0.06, 0.10)] for a in advs],
                       columns=['LRT advantage, felt minutes (negative: the LRT is more expensive)', 'λ_T = 0.03 (λ 0.02)', 'λ_T = 0.06 (central)', 'λ_T = 0.10 (λ 0.05)']), font=8)
    CAP('Table C.1 — Share of the public transport passengers of a pair that select the LRT, by its cost advantage and by the sensitivity.')
    H('C.4 Example 2: the car', 2)
    P('For the car, the model does not compare the car with the LRT directly. It asks how much the full public transport offer became better when the LRT path was added. '
      'Then it moves car trips in proportion to this improvement and to the public transport share of the pair. The improvement is the "composite cost" of the logit model:')
    box('Δ = −(1 / λ_T) × ln(1 + e^(−λ_T × d)),   with d = cost of the LRT path − premium − cost of the bus path')
    P(f'When the LRT path is 10 felt minutes cheaper (d = −10), Δ = {m(logsum_gain(-10))} minutes. When the two paths are equal, Δ = {m(logsum_gain(0))}. When the LRT path is 10 minutes more expensive, Δ = {m(logsum_gain(10))}. '
      'The composite cost decreases even when the LRT is not better than the bus. This is the standard property of the logit model, which gives a value to the presence of two options. '
      'This is one reason to read the shift from the car to public transport as an order of magnitude, not as a point estimate.')
    P('The new public transport share of the pair follows from the old share, S, and from Δ:')
    box('S′ = S × e^(−λΔ) / (S × e^(−λΔ) + 1 − S)')
    rows = []
    for S in (0.02, 0.05, 0.20):
        rows.append([f'{100 * S:.0f} %'] + [f'{100 * car_shift(S, logsum_gain(d)):.1f} % ({100 * (car_shift(S, logsum_gain(d)) - S):+.1f} points)' for d in (10, 0, -10)])
    table(pd.DataFrame(rows, columns=['Public transport share of the pair before the LRT', 'LRT 10 min more expensive than the bus path', 'LRT equal to the bus path', 'LRT 10 min cheaper']), font=8)
    CAP('Table C.2 — New public transport share of a pair after the LRT, λ = 0.03. The shift is largest where public transport already has a share. On the pairs where the car has most trips (2 % public transport, the car-available segment of C.5), the shift is a fraction of a point. The result for the corridor, 0.9 % of the car trips, is the sum of such small shifts.')
    fig(f'{FIG}/appC_logit_mechanisms.png', 16, 'Figure C.1 — The two mechanisms. Left: the LRT share of the public transport passengers of a pair against its cost advantage, for the three sensitivities. Right: the points added to the public transport share of a pair by the shift from the car, against its share before the LRT.')
    P('One more rule connects the two examples. Before the pivot, the model smooths the observed 2022 share of the pair to the share of its wider area (weight k = 20 trips). '
      'Thus a pair with three survey trips does not change the result. The model pivots on observed shares. Thus, if you remove the LRT, you get the 2022 flows again exactly.')
    H('C.5 How we estimated λ', 2)
    P('The obvious procedure failed. A fit of the public transport share of each pair of areas on the cost difference bus minus car gives λ with the wrong sign. The sample is 597 pairs and 70,000 trips. '
      'The pairs where public transport is cheapest against the car are the pairs where the residents have few cars. Thus the share follows who lives there, not the minutes. A fit at the pair level cannot separate the two effects.')
    P('The solution was to use the individual survey records (2,310 AM trips of 543 households inside the corridor areas). We kept the car availability constant. '
      'The car availability has four classes: no car in the household, no licence, more licences than cars, or a car for each driver. '
      'The purpose of the trip, the age, the gender, the sector and the distance band also stay constant. '
      'In a group of persons with the same access to a car, the persons with a smaller public transport cost select public transport more often. This slope is λ.')
    table(pd.read_csv('Output/mode_choice/lambda_summary.csv').rename(columns={'model': 'Model', 'lambda': 'λ for each felt minute', 'lo95': '95 % low', 'hi95': '95 % high', 'rows': 'Trips', 'households': 'Households', 'assumed (step 31)': 'Assumed in the chain', 'assumed range': 'Assumed range'}),
          {'λ for each felt minute': '{:.3f}', '95 % low': '{:.3f}', '95 % high': '{:.3f}', 'Assumed in the chain': '{:.3f}'}, font=7)
    CAP('Table C.3 — The estimates at the person level (step 33). M1 is the central specification. M4 limits the sample to licence holders in households with a car. Source: Output/mode_choice/lambda_summary.csv.')
    fig('Output/figures/mode_choice_person_level_by_segment.png', 16, 'Figure C.2 — The observed public transport share against the cost difference, by car availability segment (step 33). There are four separate levels, and a visible slope only for the households without a car.')
    for s in ['The pooled estimate, 0.035 (interval 0.002–0.068), has the correct sign and supports the assumed 0.03, which is on its cautious side. On the car network of May 2026, it is 0.040.',
              'By segment, it is 0.083 for persons in households without a car. For licence holders in households with a car, it is not different from zero (0.008 ± 0.017). These are the travellers that the LRT must get from the car. The survey has too few such persons who select public transport on comparable pairs to measure their reaction.',
              'Thus the data support λ_T on the public transport side, and λ on the car side is a judgement with a range. The shifts from the bus and from the Metronit are the more solid part of each result. The shift from the car is an order of magnitude. A stated preference survey of car owners on the corridor is the procedure to get it.']: B(s)
    H('C.6 What λ does to the result', 2)
    fig(f'{FIG}/appC_lambda_range.png', 14, 'Figure C.3 — The 2022 test capture (step 31, all underground, 25 areas) with the λ and premium cases that the chain carries.')
    P('The λ range alone is −26 % to +42 % of the capture, the widest single factor after the out-of-vehicle set. This is why the range for the plan in the report (5,532 to 10,537 AM passengers around the reference 7,433) comes from it. '
      'The LRT premium (0 or 10 minutes instead of 5) gives a narrower band inside it, −20 % to +23 %. If you double λ, the shift from the car approximately doubles, and the LRT share of public transport moves away from an equal split. If you halve λ, the opposite occurs.')
    sources('METHODOLOGY.md §6ac (step 31), §6ae (step 33), §6ak (step 40), §6aq (step 45); Output/mode_choice/lambda_summary.csv, coefficients_all_models.csv, sample_by_car_segment.csv; Output/skims/lrt_capture_scenarios.csv; the pivot code of notebooks/current/LRT_alternatives_demand.ipynb.')

    # ======================= D =======================
    H('Appendix D. The generalized cost function: why, and how we got to it')
    P('This appendix answers four questions. Why does the model change each trip into one number? What is in this number? Where does each component come from? '
      'Which decisions and corrections changed the formula between the first draft in September 2026 and the formula of the report?')
    H('D.1 Why one number', 2)
    P('The model must compare trips that are different in each part. One trip has more walk time. A different trip has less wait time. A third trip has a transfer. A fourth trip is faster, but the stop is far from the home. The model cannot compare these trips directly.')
    P('The generalized cost puts all these trips on one scale, the "felt" length of the trip, in minutes. The minutes outside a vehicle count more than one time (Appendix B). '
      'A change of vehicle has a fixed charge. The preference for a rail vehicle enters as a bonus.')
    box('GC = in-vehicle time + 2 × walk + 2 × wait + 8 for each transfer (4 between the Metronit and the LRT) + 0.5 for each LRT station end − LRT premium (5 against a bus path, 2.5 against a Metronit path)')
    table(pd.DataFrame([
        ['In-vehicle time', 'bus and Metronit: timetable of May 2026 with the run times measured on the street network in May 2026 (the buses operate at 1.09 × the timetable in the peak); train: timetable; LRT: the calibrated function of Appendix A; car: the measured network speeds of May 2026 between the zone centroids, plus 3 minutes for the parking and the walk at the ends', 'weight 1'],
        ['Walk', 'straight line × 1.3 for the street detour, at 4 km/h, from the zone to the stops within 1 km, and from stop to stop within 300 m for a transfer', 'weight 2'],
        ['Wait', 'half the combined headway of the lines that serve the pair in the peak hour, maximum 10 minutes; LRT 2.5 minutes (a tram each 5 minutes)', 'weight 2'],
        ['Transfer', 'a fixed charge for the uncertainty and the effort of a change of vehicle, in addition to the real walk and wait; the first boarding is not a transfer', '8 min; 4 min Metronit ↔ LRT'],
        ['Station access', 'the time inside a station from the entrance to the platform', '0.5 min for each LRT end'],
        ['LRT premium', 'the preference for a rail vehicle at equal time, from the in-vehicle multipliers of the calibrated models', '−5 min against a bus path, −2.5 against a Metronit path'],
        ['Money', 'fare, parking, fuel', 'none, by decision (D.2, step 2)']],
        columns=['Component', 'Source', 'Count']), font=7)
    CAP('Table D.1 — The components of the generalized cost in the reference case.')
    H('D.2 The sequence of decisions', 2)
    P('We changed the formula in seven steps between 22 September 2026 and October 2026. Then we did four checks on the full chain of the model.')
    H('Step 1. The first formula (LRT capture plan, 22 September 2026)', 3)
    box('GC = in-vehicle time + 2 × walk + 2 × wait + 8 for each transfer + (fare + parking) ÷ value of time')
    P('The value of time was 30 ILS for each hour, as a temporary value. The weights 2 / 2 / 8 are the middle of the ranges of standard practice: 1.5–2.5 for the walk and the wait, 5–10 for a transfer.')
    H('Step 2. We removed the money terms (22 September 2026)', 3)
    P('The public transport fare in the area is flat and integrated. A daily maximum makes transfers and return trips free. Thus the fare is the same for each bus, Metronit or LRT trip and for each pair. It cannot change the choice between them.')
    P('Against the car, the fare is a constant for each trip. The model starts from the observed 2022 split between car and public transport; it does not calculate the split from the costs (C.4). Thus a constant cost has no effect.')
    P('We also removed the parking and fuel costs by the same decision. There are no parking data for the area. From this step, the cost is in minutes only.')
    H('Step 3. We replaced the temporary values with measured data (22–23 September 2026)', 3)
    P('The first version used a walk of 8 minutes and a headway of 10 minutes for each bus pair. We replaced these values in three stages:')
    for s in ['The national timetable: the walk to the real stops, the wait from the real headways.', 'The run times measured on the street network in May 2026. On the arterial hops with the most demand, these times are 1.1–1.4 times the timetable.', 'The Metronit as a mode of its own.']: B(s, 2)
    P('We corrected the LRT in-vehicle time for the station spacing (Appendix A). We set the LRT headway to 5 minutes.')
    P('We compared the bus times with the door-to-door times that the travellers gave in the survey. The survey times are 7–9 minutes more than the timetable times. The transfer, the wait for the correct line and the delays cause this difference. The transfer and wait terms represent it.')
    H('Step 4. The LRT premium (22 September 2026) and the Metronit premium (5 October 2026)', 3)
    P('Travellers prefer a rail vehicle at equal time. Calibrated models show this as an in-vehicle multiplier of 0.80–0.85 for the LRT, against 0.90–0.95 for the BRT. '
      'On the 14 minutes of in-vehicle time on the trunk, the gap is approximately 5 minutes against a bus path. It is approximately 2.5 minutes against a Metronit path.')
    H('Step 5. The transfer structure (22 September and 5 October 2026)', 3)
    P('A change between a bus and the LRT costs 8 minutes. The change from the Metronit to the LRT was first free, with the assumption of an integrated interchange on the same platform. '
      'The out-of-vehicle research found no study with a value below 4 minutes, even for a cross-platform change. Thus we adopted 4 minutes (Appendix B).')
    H('Step 6. Station access and walk speed (5 October 2026)', 3)
    P('We added half a minute for each station end, for the way from the entrance to the platform. We changed the walk speed from 4.8 km/h to 4 km/h (the Israeli convention). The two values come from the same research.')
    H('Step 7. From areas to zones (steps 44–45, October 2026)', 3)
    P('We first made the cost between the 25 corridor areas. A matrix at the area level pools the headways of each line that serves the area and the walk to its nearest stop. No single traveller gets this combination. '
      'Thus the bus cost on the trunk was approximately a third too low: 30 felt minutes against 45 at the zone level.')
    P('The reference case makes the cost for each pair of zones on the real line graph of the timetable. The LRT boarding is at the station with the lowest access cost at each end.')
    H('The checks', 3)
    for s in ['We ran the full chain again on nine out-of-vehicle parameter sets (Appendix B).',
              'We tested the bus wait rule with the busiest single line instead of the pooled headway. The bus cost increased by 14 %, and the LRT capture increased by 15 %.',
              'We compared the car times with the door-to-door times in the survey. The car times are 0.90–0.95 of the survey times. Thus we did not increase them.',
              'We ran the capture on a car network of 2026 and on slower buses in 2050 (section 4.9).']: B(s, 2)
    H('D.3 Two examples', 2)
    P('Example 1: Kiryat Haim to Bat Galim. The trip by bus:')
    for s in ['Walk 6 minutes to the stop.', 'Wait 5 minutes (a bus each 10 minutes).', '28 minutes in the vehicle.', 'Walk 4 minutes at the end.']: B(s, 2)
    box('GC = 28 + 2 × (6 + 4) + 2 × 5 = 58 felt minutes')
    P('The same trip by LRT:')
    for s in ['Walk 9 minutes to the station.', 'Wait 2.5 minutes.', '20 minutes in the vehicle.', 'Walk 5 minutes at the end.']: B(s, 2)
    box('GC = 20 + 2 × (9 + 5) + 2 × 2.5 = 53 felt minutes.   Subtract the LRT premium of 5 minutes: 48 felt minutes')
    P('The LRT trip has more walk time. But its cost is 10 felt minutes lower, because the LRT is faster and operates more frequently. With λ_T = 0.06, this difference gives the LRT 65 % of the public transport passengers of the pair (Appendix C).')
    fig(f'{FIG}/appD_gc_worked_example.png', 15, 'Figure D.1 — Example 1 as felt minutes: in-vehicle time, walk time and wait time (each with a weight of 2), and the LRT premium. No trip in this example has a transfer.')
    P('Example 2: the Krayot to Bat Galim, with the Metronit terms. Today, this trip uses the Metronit for the full distance:')
    for s in ['Walk 5 minutes.', 'Wait 3 minutes.', '35 minutes in the vehicle.']: B(s, 2)
    box('GC = 35 + 2 × 5 + 2 × 3 = 51 felt minutes')
    P('The LRT path for the same trip has five parts:')
    for s in ['Metronit to Hamifrats: walk 5 minutes, wait 3 minutes, 18 minutes in the vehicle.',
              'Transfer at Hamifrats: transfer penalty 4 minutes, wait 2.5 minutes, station access 0.5 minutes.',
              'LRT to Bat Galim: 12 minutes in the vehicle, station access 0.5 minutes at the exit.',
              'Walk 5 minutes at the end.',
              'LRT premium against a Metronit path: −2.5 minutes.']: B(s, 2)
    box('GC = 18 + 12 + 2 × (5 + 5) + 2 × (3 + 2.5) + 4 + 0.5 + 0.5 − 2.5 = 63.5 felt minutes')
    P(f'The LRT path has a cost that is 12.5 felt minutes higher. It gets {100 * p_lrt(-12.5):.0f} % of the public transport passengers of the pair (the curve of Table C.1). '
      f'Before 5 October, the model used a transfer penalty of 0 minutes and a station access of 0 minutes for this transfer. With those values, the difference decreases to 7.5 felt minutes, and the LRT share increases to {100 * p_lrt(-7.5):.0f} %. '
      'Thus these two terms, and not the speed of the LRT, control the result for the Krayot market.')
    H('D.4 What the function does not include', 2)
    for s in ['The weights come from published studies and from other calibrated models. They are not calibrated on this corridor. We ran the chain again on nine sets to show the range that the weights open (Appendix B).',
              'The function has no money terms. Thus it cannot test a fare policy or a parking policy that gives different costs to different modes.',
              'The function has no terms for crowding, reliability or comfort, except the LRT premium. The walk times have no term for slopes, in a city where slopes are important. The function makes no difference between a stop with a shelter and a stop without a shelter.',
              'The absolute cost of the car has no effect on the result. The model starts from the split observed in 2022. Thus a slower car in 2050 changes nothing (caveat 25). Only the public transport side of the cost changes the numbers.',
              'The walk times are averages for each zone, weighted by population and by employment. They are not walk times for each address. The station access time is one value for each end.']: B(s)
    sources('docs/LRT_CAPTURE_PLAN.md; docs/APPENDIX_D_GENERALIZED_COST_STE100.md; METHODOLOGY.md §6x (step 26 and its seven addenda), §6ac (step 31), §6ao (step 44), §6al, §6aq (step 45); Output/alternatives/skims_summary.csv; section 2.4 of this report.')

# ---------------- standalone: append to the existing STE report ----------------
def main():
    """python3 tools/report_appendices_ste.py            -> append / replace the appendices in the STE report
       python3 tools/report_appendices_ste.py --only     -> write them as a document of their own, reports/Nofit_LRT_Extension_Report_Appendices_STE.docx"""
    from docx import Document
    from docx.shared import Pt, Cm
    from docx.enum.section import WD_ORIENT
    from report_appendices import _drop_previous_appendices
    only = '--only' in sys.argv
    if only:
        doc = Document(); st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(10)
        for s_ in doc.sections: s_.left_margin = s_.right_margin = Cm(2)
        doc.add_heading('Nofit LRT extension — demand study', 0); doc.add_paragraph('Appendices A–D of the comprehensive report in ASD-STE100 Simplified Technical English (reports/Nofit_LRT_Extension_Comprehensive_Report_STE.docx), as a document of their own.'); dropped = 0
    else:
        doc = Document(REPORT_STE); dropped = _drop_previous_appendices(doc)
        sec = doc.add_section(); sec.orientation = WD_ORIENT.PORTRAIT; sec.page_width, sec.page_height = min(sec.page_width, sec.page_height), max(sec.page_width, sec.page_height); sec.left_margin = sec.right_margin = Cm(2)
    def P(text, size=None, bold=None, italic=None, check=True):
        p = doc.add_paragraph(text)
        for r in p.runs:
            if size: r.font.size = Pt(size)
            if bold is not None: r.font.bold = bold
            if italic is not None: r.font.italic = italic
        return p
    def B(text, level=1): return doc.add_paragraph(text, style='List Bullet' if level == 1 else 'List Bullet 2')
    def H(text, lvl=1): return doc.add_heading(text, lvl)
    def CAP(text): return P(text, size=8, italic=True)
    def fig(path, width=16, caption=None):
        if os.path.exists(path):
            doc.add_picture(path, width=Cm(width))
            if caption: CAP(caption)
        else: P(f'[figure missing: {path}]')
    def table(df, fmt=None, font=8):
        fmt = fmt or {}
        t = doc.add_table(rows=1, cols=len(df.columns)); t.style = 'Light Grid Accent 1'
        for j, c in enumerate(df.columns):
            cell = t.rows[0].cells[j]; cell.text = str(c)
            for par in cell.paragraphs:
                for run in par.runs: run.font.size = Pt(font); run.font.bold = True
        for _, r in df.iterrows():
            cells = t.add_row().cells
            for j, (c, v) in enumerate(r.items()):
                f = fmt.get(c, '{:,.0f}')
                cells[j].text = (f.format(v) if isinstance(v, (float, int, np.floating, np.integer)) and not isinstance(v, bool) and np.isfinite(v) else ('' if isinstance(v, float) else str(v)))
                for par in cells[j].paragraphs:
                    for run in par.runs: run.font.size = Pt(font)
        return t
    add_appendices_ste(doc, H, P, B, fig, table, CAP)
    out = 'reports/Nofit_LRT_Extension_Report_Appendices_STE.docx' if only else REPORT_STE
    doc.save(out); print(f'{out}: appendices A–D {"written" if only else ("replaced" if dropped else "appended")}' + ('' if only else f' ({dropped} elements dropped)'))

if __name__ == '__main__': main()
