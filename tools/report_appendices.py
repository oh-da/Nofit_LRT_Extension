"""Appendices A–D of the comprehensive report (reports/Nofit_LRT_Extension_Comprehensive_Report.docx):
   A. Calibration of the light-rail speed and time function (Tel Aviv Red Line, operator 22 → the Haifa extension, step 25)
   B. Out-of-vehicle time: what the research found and what the model uses (docs/OVT_WEIGHTS_PARAMETER_MEMO.md, §6al, step 45)
   C. The cost sensitivity λ: what it is, how it is used, with simple examples (steps 31, 33, 40, 45)
   D. The generalized cost function: why, and how we arrived at it (steps 26, 31, 44, 45)
Written for the report's readers rather than for the modellers: plain words first, the formula in a box, a worked example, then the limits.
Every number is taken from the files named in each appendix's "Sources" line; the figures are built here into Output/figures/appendix/.

Two ways to run:
   from tools/build_comprehensive_report.py (the hook before doc.save): add_appendices(doc, H, P, B, fig, table) — the appendices become part of every rebuild;
   standalone, python3 tools/report_appendices.py — opens the existing report, drops a previous appendix block if there is one, appends A–D, saves.
"""
import os, sys
import numpy as np, pandas as pd
while not os.path.exists('METHODOLOGY.md') and os.getcwd() != '/': os.chdir('..')
FIG = 'Output/figures/appendix'; os.makedirs(FIG, exist_ok=True)
REPORT = 'reports/Nofit_LRT_Extension_Comprehensive_Report.docx'

# ---------------- the numbers used in the appendices (source beside each) ----------------
UG_SEC, GR_SEC = 1.960792, 2.392690                                   # calibration report §6: min per Red Line section, underground / other
UG_FIT, GR_FIT = (0.8135, 1.3075, 0.9416), (1.2282, 1.9385, 1.0195)   # Output/lrt_v2/lrt_calibration_redline_spacing_check.csv: stop penalty (min), min/km, level factor
RL_SPACING = {'underground': 970, 'ground': 577}                      # same file: mean scheduled section length on the Red Line (m)
HAIFA_SPACING = 815                                                   # §6w: mean station spacing on hf_lrt_3 (354–1,396 m)
LAM, LAM_T = 0.03, 0.06                                               # steps 31 / 45
PREM_BUS, PREM_BRT = 5.0, 2.5                                         # step 45

def section_time(d_km, regime):
    """Calibrated stop-to-stop time (min) in the decomposed form of step 25 revision 2."""
    a, b, lvl = UG_FIT if regime == 'underground' else GR_FIT
    return lvl * (a + b * d_km)

def p_lrt(adv, lam_t=LAM_T):
    """Share of a pair's transit riders choosing the LRT when it is `adv` felt minutes cheaper than the bus path (premium included)."""
    return 1 / (1 + np.exp(-lam_t * adv))

def logsum_gain(d, lam_t=LAM_T):
    """Change in the transit bundle's composite cost when an LRT path d felt minutes dearer (d > 0) or cheaper (d < 0) than the bus path is added (step 45's `delta`)."""
    return -(1 / lam_t) * np.log1p(np.exp(-lam_t * d))

def car_shift(S, delta, lam=LAM):
    """New transit share from the base share S after a composite-cost change delta (step 45's `S_new`)."""
    f = np.exp(-lam * delta); return S * f / (S * f + 1 - S)

# ---------------- figures ----------------
def build_figures():
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})
    # A.1 — stop-to-stop time against station spacing, the two calibrated regimes
    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=200)
    km = np.linspace(0.3, 1.5, 100)
    for regime, col, lab in [('underground', '#2a78d6', 'segregated / underground (used for the Prioritized regime)'), ('ground', '#eb6834', 'street level (used for the Unprioritized regime)')]:
        ax.plot(km * 1000, section_time(km, regime), color=col, lw=2, label=lab)
        ax.plot([RL_SPACING[regime]], [section_time(RL_SPACING[regime] / 1000, regime)], 'o', color=col, ms=7)
        ax.annotate(f'Red Line mean spacing {RL_SPACING[regime]} m\n{section_time(RL_SPACING[regime] / 1000, regime):.2f} min (calibrated {UG_SEC if regime == "underground" else GR_SEC:.3f})', (RL_SPACING[regime], section_time(RL_SPACING[regime] / 1000, regime)),
                    xytext=(10, -30) if regime == 'underground' else (-182, 16), textcoords='offset points', fontsize=7.5, color=col)
    ax.axvline(HAIFA_SPACING, color='#7d8794', lw=1, ls='--'); ax.text(HAIFA_SPACING + 12, 0.45, f'Haifa extension\nmean spacing {HAIFA_SPACING} m', fontsize=7.5, color='#4b5665')
    ax.axvline(500, color='#c3c2b7', lw=1, ls=':'); ax.text(505, 0.45, "the report's\n500 m assumption", fontsize=7.5, color='#7d8794')
    ax.set_xlabel('distance between consecutive stations (m)'); ax.set_ylabel('time from one stop to the next (min)'); ax.set_ylim(0, 4.2); ax.grid(alpha=0.25)
    ax.legend(loc='upper left', fontsize=7.5, frameon=False); ax.set_title('Calibrated stop-to-stop time: running time plus a fixed stop penalty, by regime', fontsize=9)
    fig.tight_layout(); fig.savefig(f'{FIG}/appA_section_time_vs_spacing.png'); plt.close(fig)
    # C.1 — the two logit mechanisms
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.4, 3.4), dpi=200)
    adv = np.linspace(-30, 30, 200)
    for lt, col, lab in [(0.03, '#86b6ef', 'λ_T = 0.03 (λ 0.02)'), (0.06, '#2a78d6', 'λ_T = 0.06 (central)'), (0.10, '#184f95', 'λ_T = 0.10 (λ 0.05)')]:
        a1.plot(adv, 100 * p_lrt(adv, lt), color=col, lw=2, label=lab)
    for x in (10, 20): a1.plot([x], [100 * p_lrt(x)], 'o', color='#2a78d6', ms=6); a1.annotate(f'{100 * p_lrt(x):.0f} %', (x, 100 * p_lrt(x)), xytext=(6, -12), textcoords='offset points', fontsize=8)
    a1.axhline(50, color='#c3c2b7', lw=1); a1.axvline(0, color='#c3c2b7', lw=1)
    a1.set_xlabel('LRT advantage over the existing transit path (felt minutes)'); a1.set_ylabel('share of the pair\'s transit riders choosing the LRT (%)'); a1.set_ylim(0, 100); a1.grid(alpha=0.25); a1.legend(fontsize=7.5, frameon=False, loc='upper left')
    a1.set_title('Within transit: LRT against the existing path', fontsize=9)
    S = np.linspace(0.005, 0.6, 200)
    for d, col, lab in [(10, '#86b6ef', 'LRT 10 min dearer than the bus path'), (0, '#2a78d6', 'LRT equal to the bus path'), (-10, '#184f95', 'LRT 10 min cheaper')]:
        a2.plot(100 * S, 100 * (car_shift(S, logsum_gain(d)) - S), color=col, lw=2, label=f'{lab} (Δ = {logsum_gain(d):.1f} min)')
    a2.set_xlabel('transit share of the pair before the LRT (%)'); a2.set_ylabel('points added to the transit share (car → transit)'); a2.grid(alpha=0.25); a2.legend(fontsize=7.5, frameon=False, loc='upper left')
    a2.set_title('Between car and transit: the composite-cost gain, λ = 0.03', fontsize=9)
    fig.tight_layout(); fig.savefig(f'{FIG}/appC_logit_mechanisms.png'); plt.close(fig)
    # C.2 — what λ does to the 2022 central capture (step 31 / 40)
    fig, ax = plt.subplots(figsize=(6.4, 2.6), dpi=200)
    cases = [('λ 0.05 (least sensitive)', 3166), ('premium 0', 3410), ('central: λ 0.03, premium 5', 4254), ('premium 10', 5236), ('λ 0.02 (most sensitive)', 6031)]
    cols = ['#eb6834', '#eb6834', '#2a78d6', '#1baf7a', '#1baf7a']
    ax.barh([c[0] for c in cases], [c[1] for c in cases], color=cols, height=0.6)
    for i, (_, v) in enumerate(cases): ax.text(v + 60, i, f'{v:,} ({(v / 4254 - 1) * 100:+.0f} %)' if v != 4254 else f'{v:,}', va='center', fontsize=8)
    ax.set_xlim(0, 7400); ax.set_xlabel('LRT trips, 06:00–09:00, 2022, 25-area test (step 31, all underground)'); ax.invert_yaxis(); ax.grid(axis='x', alpha=0.25)
    ax.set_title('The cost sensitivity and the LRT premium move the capture by −26 % to +42 %', fontsize=9)
    fig.tight_layout(); fig.savefig(f'{FIG}/appC_lambda_range.png'); plt.close(fig)
    # D.1 — the worked example of section 2.4 as stacked felt minutes
    fig, ax = plt.subplots(figsize=(6.8, 3.2), dpi=200)
    comps = [('riding', 28, 20, '#184f95'), ('walking × 2', 20, 28, '#3987e5'), ('waiting × 2', 10, 5, '#86b6ef'), ('transfer penalty', 0, 0, '#c3c2b7'), ('LRT premium', 0, -5, '#1baf7a')]
    left = {'by bus': 0, 'by LRT': 0}
    for lab, b, l, col in comps:
        for mode, v in (('by bus', b), ('by LRT', l)):
            if v > 0: ax.barh(mode, v, left=left[mode], color=col, label=lab if mode == 'by bus' or lab == 'LRT premium' else None, height=0.55, edgecolor='white', linewidth=1.5); left[mode] += v
            elif v < 0: ax.barh(mode, v, left=left[mode], color=col, label=lab, height=0.55, edgecolor='white', linewidth=1.5, hatch='//'); left[mode] += v
    ax.text(58.8, 0, '58 felt minutes', va='center', fontsize=8.5, fontweight='bold'); ax.text(53.8, 1, '48 felt minutes (53 before the premium)', va='center', fontsize=8.5, fontweight='bold')
    ax.set_xlim(0, 80); ax.set_xlabel('generalized cost, felt minutes (Kiryat Haim → Bat Galim, the example of section 2.4)'); ax.invert_yaxis()
    h, l = ax.get_legend_handles_labels(); seen = {}; [seen.setdefault(ll, hh) for hh, ll in zip(h, l)]; ax.legend(seen.values(), seen.keys(), fontsize=7.5, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.28), ncol=5)
    ax.set_title('The LRT trip walks more but rides faster and comes more often: ten felt minutes cheaper', fontsize=9)
    fig.tight_layout(); fig.savefig(f'{FIG}/appD_gc_worked_example.png'); plt.close(fig)

# ---------------- the text ----------------
def add_appendices(doc, H, P, B, fig, table, build_figs=True):
    from docx.shared import Pt
    if build_figs: build_figures()
    def note(text):
        p = P(text); p.runs[0].font.size = Pt(8); p.runs[0].font.italic = True; return p
    def box(text):
        p = P(text); p.runs[0].font.bold = True; p.paragraph_format.left_indent = Pt(18); return p
    def sources(text): return note('Sources: ' + text)

    # ======================= A =======================
    H('Appendix A. Calibration of the light-rail speed and time function')
    P('What this appendix answers: where the running times of the planned line come from, why they were measured on the Tel Aviv Red Line, how the '
      'measurement was carried over to the Haifa alignment, and what the two operating regimes of the report (Prioritized and Unprioritized) mean in minutes.')
    H('A.1 Why a calibrated function', 2)
    P('The extension has no timetable yet, so the model needs a rule that turns the distance between two stations into minutes. The usual shortcut, a design speed, '
      'misses the part of a light-rail trip that is not running: slowing down, standing at the platform, accelerating again, and waiting at road junctions. '
      'Those minutes decide whether the LRT beats the bus on a given pair, so the study measured them on an operating Israeli light rail rather than assuming them.')
    P('The Tel Aviv Red Line (operator 22, lines 34447 and 34448) was chosen because its one line runs in both of the conditions the study needs: a segregated, '
      'underground core through Tel Aviv and street-level sections at its two ends. Measuring the same vehicles and the same operator in both conditions gives '
      'two consistent readings, one for a line that never waits at a junction and one for a line that runs with the street.')
    H('A.2 The data and how it was cleaned', 2)
    P('The operator\'s vehicle-location records give the time at which every tram reached every stop. The extract holds 1,078,845 stop records over 132 Thursdays '
      'between May 2023 and September 2026. A journey is kept only when it is complete (all 31 stops in order) and every stop-to-stop time is plausible '
      '(above zero and at most 10 minutes). That leaves 26,653 clean journeys and 799,590 stop-to-stop sections, of which 239,877 are underground and 559,713 at the surface.')
    P('A section counts as underground only when both of its stations are underground; a section with one surface station is counted as surface. That is the cautious '
      'choice, because the portal sections carry some of the street-level delay.')
    table(pd.DataFrame([['Source', 'Operator 22 vehicle-location records, lines 34447 / 34448'], ['Days', '132 Thursdays, 25 May 2023 to 10 September 2026 (in practice 2024–2026: no 2023 journey passes the completeness test)'],
                        ['Raw records', '1,078,845 stop records in 36,939 journeys'], ['Kept', '26,653 complete, clean journeys; 799,590 stop-to-stop sections'],
                        ['Underground rule', 'both stations of the section in the list of 11 underground stations'], ['Quality rule', 'every section time > 0 and ≤ 10 minutes']],
                       columns=['item', 'value']), font=8)
    note('Table A.1 — The calibration sample.')
    H('A.3 What was measured', 2)
    P('The calibration is a mean: how many minutes a tram takes, on average, from one stop to the next, in each regime. Because the mean is what the model needs '
      '(the expected time of many trips, not the typical one), it is used rather than the median.')
    box(f'Underground: {UG_SEC:.3f} minutes per section (95 % interval 1.958–1.963).   Surface: {GR_SEC:.3f} minutes per section (2.390–2.395).')
    fig(f'{FIG}/appA_redline_section_time_by_regime.png', 12, 'Figure A.1 — Mean stop-to-stop time by regime on the Red Line; the error bars (the 95 % intervals) are too small to see at this scale. Source: the calibration report, figure 1.')
    P('The check that the rule works: a complete Red Line journey has 9 underground and 21 surface sections, so the rule predicts 9 × 1.961 + 21 × 2.393 = 67.9 minutes. '
      'The observed mean is 67.9 minutes by construction; what matters is the spread around it: the typical error on a single journey is 3.7 minutes (5.5 %), '
      'and the two directions differ by about a minute (68.9 towards one end, 66.8 towards the other).')
    fig(f'{FIG}/appA_redline_trip_time_distribution.png', 12, 'Figure A.2 — Observed end-to-end times of the 26,653 clean journeys against the rule\'s 67.9 minutes. Source: the calibration report, figure 3.')
    table(pd.DataFrame([['2024', 2.007, 2.528, 9482], ['2025', 1.946, 2.365, 10752], ['2026', 1.919, 2.240, 6419], ['all years (used)', UG_SEC, GR_SEC, 26653]],
                       columns=['year', 'underground, min per section', 'surface, min per section', 'journeys']), {'underground, min per section': '{:.3f}', 'surface, min per section': '{:.3f}'}, font=8)
    note('Table A.2 — The same means by year. Operations have become faster each year; the study uses the pooled value, which is 2–6 % slower than 2026 alone and therefore slightly cautious.')
    H('A.4 From the Red Line to Haifa: the station-spacing correction', 2)
    P('A time per section is only useful if we know how long a section is. The calibration report converted its minutes to speeds by assuming 500 metres between stops '
      '(15.3 km/h underground, 12.5 km/h at the surface). The Red Line\'s own timetable, which records the distance at every stop, shows that its underground stations are '
      '970 metres apart on average and its surface stops 577 metres. So 1.961 minutes per underground section is a 30 km/h section, not a 15 km/h one, and applying the '
      '500 m reading to Haifa (the first revision of the study) made the underground case twice too slow.')
    P('The study therefore separated each section time into two parts, fitted on the Red Line\'s 14,477 scheduled sections: a running time that grows with distance, and a '
      'fixed stop penalty that covers braking, dwell and acceleration. Each regime is then scaled by the ratio of observed to scheduled time, so the rule still reproduces '
      'the measured means on the Red Line\'s own spacing.')
    box('Underground: time = 0.94 × (0.81 min + 1.31 min per km)   →   46 km/h between stops plus 49 seconds per stop.')
    box('Surface:       time = 1.02 × (1.23 min + 1.94 min per km)   →   31 km/h between stops plus 74 seconds per stop.')
    P(f'This form can be applied to any station spacing. On the Haifa extension the 24 stations are {HAIFA_SPACING} metres apart on average (354 to 1,396 m): a section takes '
      f'{section_time(HAIFA_SPACING / 1000, "underground"):.2f} minutes underground-style (27.6 km/h including stops) and {section_time(HAIFA_SPACING / 1000, "ground"):.2f} minutes at street level (17.1 km/h).')
    fig(f'{FIG}/appA_section_time_vs_spacing.png', 14, 'Figure A.3 — The calibrated rule as a function of station spacing: the Red Line\'s mean spacing (dots) reproduces the measured section times; the dashed line is the Haifa extension\'s mean spacing. Source: Output/lrt_v2/lrt_calibration_redline_spacing_check.csv.')
    P('A worked example. The first section of the extension, S01 to S02 in Tirat Carmel, is 1,247 metres long. Underground-style: 0.94 × (0.81 + 1.31 × 1.247) = 2.30 minutes. '
      'Street level: 1.02 × (1.23 + 1.94 × 1.247) = 3.72 minutes. Summing the 23 sections gives the end-to-end times of the report.')
    table(pd.DataFrame([['Decomposed form (running time + stop penalty, used)', 40.6, 27.7, 65.8, 17.1], ['Section form (one calibrated section per link, whatever its length)', 45.1, 24.9, 55.0, 20.4],
                        ['Nominal 500 m form (the report\'s speeds; superseded)', 73.5, 15.3, 89.7, 12.5]],
                       columns=['reading of the calibration', 'underground-style, min S01–S24', 'km/h', 'street level, min S01–S24', 'km/h ']), {'underground-style, min S01–S24': '{:.1f}', 'km/h': '{:.1f}', 'street level, min S01–S24': '{:.1f}', 'km/h ': '{:.1f}'}, font=8)
    note('Table A.3 — End-to-end time of the extension (18.7 km, 24 stations) under the three readings of the calibration. The decomposed form is the estimate (40.62 min, quoted as 40.7 elsewhere in the report); the other two are kept as bounds. Source: Output/lrt_v2/lrt_end_to_end_summary.csv.')
    fig('Output/figures/lrt_line_profile_hf_lrt_3.png', 16, 'Figure A.4 — Cumulative travel time along the extension under each reading and regime, and the stations on the alignment (step 25).')
    H('A.5 How the function enters the model', 2)
    for s in ['Prioritized regime: the extension runs with full priority at road junctions, so the model gives it the segregated (underground-calibrated) times: 40.7 minutes from Tirat Carmel to Hamifrats. No underground line is planned; the regimes differ in running time only (decision of 5 October 2026).',
              'Unprioritized regime: the extension runs at street level and waits at junctions with the traffic, so it gets the surface times: 65.8 minutes. The difference, 25 minutes on 18.7 km, is what "priority at the junctions" is worth in time, and the report shows it is worth about a quarter of the riders.',
              'Main route (Hamifrats to Nazareth): a different kind of line, mostly interurban with stations 2.1 km apart, for which the client specified 80 km/h between stops and 10 seconds per stop: 33.7 minutes. This is a specification, not a calibration, and is listed among the report\'s caveats (caveat 28).',
              'Checks on the calibrated regimes: a 50 km/h design speed with 10 s per stop would give 26.3 minutes on the extension; adding a 35-second allowance per stop for braking and acceleration brings it to 39.7 minutes, within 3 % of the calibrated 40.7. The calibrated rule is therefore a 46 km/h line that loses about 50 seconds at every stop, not a slow line.',
              'Headway: a tram every 5 minutes on the whole line, so the average wait is 2.5 minutes; the time on route does not include it.']: B(s)
    H('A.6 What to keep in mind', 2)
    for s in ['The rule was measured on Thursdays only and pooled over 2024–2026; 2026 alone is 2–6 % faster.',
              'The stop penalty embeds the Red Line\'s dwell times and acceleration. A Haifa operation with different vehicles or dwell rules would move the times by seconds per stop, tens of seconds end to end.',
              'The two regimes are the two pure cases. A line with priority at most but not all junctions sits between them; the mixed alignment tested in step 25 (the Haifa core segregated, the ends at street level) gives 56 minutes.',
              'The report\'s results are more sensitive to station access and transfers than to the running time itself (Appendix D), so the calibration decides the regime comparison more than the overall level of demand.']: B(s)
    sources('the calibration report (docs/Transit_Travel_Time_Calibration_Report_Operator22.md; the figures reproduced from its docx); METHODOLOGY.md §6w (step 25, revision 2 and addenda); Output/lrt_v2/lrt_calibration_redline_spacing_check.csv, lrt_end_to_end_summary.csv, lrt_line_profile.csv; Output/alternatives/time_on_route.csv.')

    # ======================= B =======================
    H('Appendix B. Out-of-vehicle time: what the research found and what the model uses')
    P('What this appendix answers: why the minutes spent walking, waiting and changing vehicles are weighted, what the literature and other models say those weights should be, '
      'what the study chose, and how much the choice moves the result. It condenses the research memo of 4 October 2026 (docs/OVT_WEIGHTS_PARAMETER_MEMO.md, 275 estimates from five evidence streams).')
    H('B.1 Why the weights matter here', 2)
    P('A trip by public transport is mostly not spent riding. Travellers find a minute of walking to the stop, standing at it or changing vehicles more tiresome than a minute '
      'in a moving vehicle, and every transport model counts those minutes more than once. The weight is the number of in-vehicle minutes one out-of-vehicle minute is worth.')
    P('For this study the weights are unusually important because of the geometry: the extension has 24 stations where the bus and Metronit network has thousands of stops. '
      'On the trunk pairs the walk to an LRT station is 13.9 minutes against 5.1 to a bus stop. With a walk weight of 2.0 that is an 18-minute handicap before the tram moves, '
      'which is why the LRT\'s in-vehicle advantage over the bus does not translate into a cost advantage on most pairs (Appendix D).')
    H('B.2 What was researched', 2)
    for s in ['Appraisal guidance of eleven countries and Israel (the UK TAG, Australia\'s ATAP, New Zealand, the Netherlands, Norway, Sweden, Denmark, the US FTA and TCQSM, the Israeli נוהל פר"ת and the Ministry of Transport\'s 2026 model-validation guideline).',
              'Meta-analyses and primary studies of how travellers value walking, waiting and interchange (Wardman and co-authors 2001–2026, TRL, the Dutch and Norwegian national value-of-time studies, London, Madrid, Sydney, Dublin, Copenhagen).',
              'The parameter files of ten calibrated regional models in the United States and Europe, read in full from their public repositories (ActivitySim for San Francisco, Detroit, Atlanta and Washington; San Diego; Seattle; Chicago; MATSim; OpenTripPlanner; R5).',
              'Walking evidence: speeds, detour factors, slopes, stairs and escalators, crossing delays, how far people walk to rail against bus.']: B(s)
    P('One limitation governs how the findings are read: the research session could not open the guidance and study documents themselves (the network policy blocked their hosts), '
      'so 255 of the 275 values come from published summaries and only the 20 model parameter files were read in full. By the research plan\'s own rule nothing is "confirmed"; '
      'the findings give the range each parameter lies in and where the study\'s value sits inside it.')
    H('B.3 The findings, parameter by parameter', 2)
    table(pd.DataFrame([
        ['Walk weight', '2.0', 'studies ≈ 1.5–1.7; guidance 1.5–2.0 (Israel MoT: out-of-vehicle 2–3); ten calibrated models: 2.0', '2.0: the practice median, the floor of the Israeli range, above the study median. Cautious for the LRT (it has the longer walks).'],
        ['Wait weight and rule', '2.0; wait = half the headway, capped at 10 min', 'studies ≈ 1.5; guidance 1.4–2.5; models 1.5 or 2.0; half the headway everywhere', '2.0 kept. At the LRT\'s 5-minute headway the 2.5-minute wait is if anything high: many riders time their arrival.'],
        ['Transfer penalty, bus ↔ LRT and bus ↔ bus', '8 felt minutes', 'studies 5–10 (up to 20 for bus–bus); guidance 5–10; models ≈ 10', '8 kept; inside every range; moves the capture by under 1 %.'],
        ['Transfer penalty, Metronit ↔ LRT', '4 felt minutes (was 0 until 5 October 2026)', 'same-platform or cross-platform interchange ≈ 4–5; with a level change ≈ 7; no study of a BRT–LRT interchange exists', 'A free transfer was below every value found; 4 adopted as the same-platform median. Each minute here matters: the Krayot market reaches the LRT by Metronit.'],
        ['Station access time', '0.5 min per station end (was 0)', 'physical 1–3 min per end for an underground station; practice 0.5 min per level (FTA STOPS), 2 min rail boarding (Sound Transit)', '0.5 adopted for surface stations (nothing underground is planned); the 1.5-minute underground test cost 23 % of the riders in the 2022 test.'],
        ['LRT-specific walk weight', 'none (same as bus)', 'one unverified summary suggests rail access walks are valued less; none of the ten models does this', 'Not used. The preference for rail is carried by the LRT premium instead.'],
        ['Walking speed and detour', '4.0 km/h, straight line × 1.3 (was 4.8 km/h)', 'level walking 1.2–1.4 m/s; models 4.5–4.8 km/h; Israeli national model reportedly 4 km/h', '4.0 km/h adopted on 5 October 2026 as the Israeli convention; slope-aware walk times remain an open item.'],
        ['LRT premium', '5 felt minutes over a bus path, 2.5 over a Metronit path', 'calibrated models value in-vehicle time on LRT at 0.80–0.85 of bus time and on BRT at 0.90–0.95', 'A 0.15 gap on the trunk\'s 14 minutes of riding ≈ 5 minutes; a 0.05–0.10 gap ≈ 1.7–3.3, taken as 2.5.']],
        columns=['parameter', 'in the model', 'what the evidence says', 'reading']), font=7)
    note('Table B.1 — The out-of-vehicle parameters: the study\'s values against the evidence. Full detail per parameter in Output/ovt_research/parameter_summary.csv.')
    H('B.4 How much the weights move the result', 2)
    P('The whole chain was rerun on nine parameter sets in the 2022 test case of step 31 (the extension alone, 25 areas, 4,254 LRT trips in the morning three hours with the weights of the time). '
      'The sets span from the evidence-side values, which favour the LRT, to the upper end of the Israeli guidance range with a deep underground station and a level-change interchange, which do not.')
    table(pd.DataFrame([
        ['Evidence medians (walk 1.5, wait 1.5)', 4935, '+16 %', 'lower weights shorten the LRT\'s felt walk more than the bus\'s'],
        ['Today\'s weights (walk 2, wait 2, transfer 8), no Metronit penalty, no station access', 4254, 'central of the test', 'the model before 5 October 2026'],
        ['… plus a 4-minute Metronit ↔ LRT penalty', 3837, '−10 %', 'the Metronit-fed trips pay for the change of vehicle'],
        ['… plus 1.5 min access per underground station end instead', 3257, '−23 %', 'the largest single item; the adopted 0.5 min at surface stations is a third of it'],
        ['… plus both terms', 2922, '−31 %', 'the "today\'s weights with the two missing terms" case'],
        ['Guidance upper range (walk 2.5, wait 2.5, transfer 10, Metronit 7, access 3)', 1456, '−66 %', 'the LRT-unfavourable bound']],
        columns=['parameter set', 'LRT trips, 2022 test', 'against 4,254', 'what drives it']), font=8)
    note('Table B.2 — The chain rerun on the out-of-vehicle parameter sets (step 31 chain, 2022, 25 areas, all-underground times). Source: Output/ovt_research/chain_results.csv. The report\'s reference case already carries the 4-minute Metronit penalty and the 0.5-minute access, so it sits between the second and the fifth row of this table.')
    fig('Output/figures/lrt_capture_tornado.png', 14, 'Figure B.1 — Which assumption moves the 2022 LRT number most (step 40): the out-of-vehicle set is the widest factor, ahead of the cost sensitivity and the running regime.')
    P('Two readings follow. The weights pull in both directions: the evidence favours lower weights, which help the LRT, and at the same time two terms the model had set to zero '
      '(the Metronit interchange and station access) are below every value found, which hurts it. And the cost sensitivity λ is robust to all of it: re-estimated on each set it stays '
      'at 0.030–0.036, so the weights change the cost differences themselves, not how travellers respond to them.')
    H('B.5 What the study decided, and what is still open', 2)
    for s in ['Central case: walk 2.0, wait 2.0, transfer 8, Metronit ↔ LRT 4, station access 0.5 per end, walking 4.0 km/h, premium 5 / 2.5. The weights are the practice median and inside every guidance range; the two new terms enter at their lower medians because no underground station is planned.',
              'Carried as sensitivities: the evidence-side weights (walk and wait 1.5) and the guidance-side weights (2.5, transfer 10); the station-access and interchange terms up to their upper values.',
              'Open, in order of value: reading the Israeli documents in full (an independent review attributes walk and wait 2.0, 4 km/h and transfer penalties of 12 bus–bus, 6 bus–rail and 3 rail–rail to the 2021 edition of נוהל פר"ת, unverified here); the station and interchange design (depth, escalators, whether the Metronit interchange is same-platform); slope-aware walking times for Haifa; and the policy decision of whether the guidance range or the evidence median governs the central case.']: B(s)
    sources('docs/OVT_WEIGHTS_PARAMETER_MEMO.md and docs/OVT_REPORTS_COMPARISON_2026-10-04.md; METHODOLOGY.md §6al and §6aq; Output/ovt_research/evidence_table.csv, parameter_summary.csv, parameter_sets.csv, chain_results.csv; Output/figures/lrt_capture_tornado.png (step 40).')

    # ======================= C =======================
    H('Appendix C. The cost sensitivity λ: what it is, how it is used, with simple examples')
    P('What this appendix answers: what the number λ ("lambda") does in the model, why there are two of them, how a cost difference becomes a number of riders, '
      'how λ was estimated from the survey, and why the result is reported as a range. Section 2.5 of the report gives the short version; this appendix walks through the arithmetic.')
    H('C.1 The idea in one sentence', 2)
    P('The model does not decide for each traveller. It turns a difference in felt minutes between two options into the share of travellers who pick each one, with a smooth curve: '
      'equal costs give an even split, a small advantage a small majority, a large advantage a large majority, never 100 %. λ is the steepness of that curve.')
    box('Share choosing option A = 1 / (1 + e^(λ × (cost of A − cost of B)))')
    P('With λ = 0.03 per felt minute, each minute of advantage changes the odds between the two options by about 3 %; ten minutes change them by about 35 %. '
      'A large λ means travellers react strongly to small cost differences; a small λ means habit, availability and things the cost does not capture dominate.')
    H('C.2 Why there are two λ\'s', 2)
    for s in ['λ_T = 0.06 inside public transport: on a pair of zones that already has a bus or Metronit path, the LRT path competes with it. The two options are alike (both are transit, same fare), so travellers are sensitive to the minutes between them.',
              'λ = 0.03 between the car and public transport: when the LRT is added, the public transport "bundle" as a whole gets better, and some car trips move to it. A car owner weighing a car against any transit option responds to cost about half as strongly as a transit rider choosing between two transit paths.',
              'The ratio λ_T = 2 λ is a standard nesting value, assumed rather than estimated on this corridor. The data support the size of the pooled λ (C.5); the ratio is a modelling convention.']: B(s)
    H('C.3 Example 1: the LRT against the bus on one pair', 2)
    P('Take the worked example of section 2.4: from Kiryat Haim to Bat Galim the bus trip feels like 58 minutes and the LRT trip like 48, a 10-minute advantage for the LRT (the 5-minute premium included). '
      'With λ_T = 0.06 the LRT takes 1 / (1 + e^(−0.06 × 10)) = 65 % of that pair\'s transit riders. If the pair has 100 transit trips in the morning peak, 65 ride the LRT and 35 stay on the bus.')
    advs = [-10, -5, 0, 5, 10, 20, 30]
    table(pd.DataFrame([[(f'{a:+d}' if a else '0').replace('-', '−')] + [f'{100 * p_lrt(a, lt):.0f} %' for lt in (0.03, 0.06, 0.10)] for a in advs],
                       columns=['LRT advantage, felt minutes (negative: the LRT is dearer)', 'λ_T = 0.03 (λ 0.02)', 'λ_T = 0.06 (central)', 'λ_T = 0.10 (λ 0.05)']), font=8)
    note('Table C.1 — Share of a pair\'s transit riders choosing the LRT, by its cost advantage and the sensitivity.')
    H('C.4 Example 2: the car', 2)
    P('For the car the model does not compare the car with the LRT directly. It asks how much better the whole public-transport offer became when the LRT path was added, '
      'and moves car trips in proportion to that improvement and to the pair\'s existing transit share. The improvement is the "composite cost" of the logit model:')
    box('Δ = −(1 / λ_T) × ln(1 + e^(−λ_T × d)),   with d = cost of the LRT path − premium − cost of the bus path')
    m = lambda v: f'{v:.1f}'.replace('-', '−')
    P(f'When the LRT path is 10 felt minutes cheaper (d = −10), Δ = {m(logsum_gain(-10))} minutes. When the two are equal, Δ = {m(logsum_gain(0))}. When the LRT path is 10 minutes dearer, Δ = {m(logsum_gain(10))}. '
      'The composite cost falls even when the LRT is no better than the bus: this is the standard property of the logit model, which values having two options, and it is one reason the car-to-transit shift is read as an order of magnitude rather than a point estimate.')
    P('The new transit share of the pair follows from the old one, S, and Δ:')
    box('S′ = S × e^(−λΔ) / (S × e^(−λΔ) + 1 − S)')
    rows = []
    for S in (0.02, 0.05, 0.20):
        rows.append([f'{100 * S:.0f} %'] + [f'{100 * car_shift(S, logsum_gain(d)):.1f} % ({100 * (car_shift(S, logsum_gain(d)) - S):+.1f} points)' for d in (10, 0, -10)])
    table(pd.DataFrame(rows, columns=['transit share of the pair before the LRT', 'LRT 10 min dearer than the bus path', 'LRT equal to the bus path', 'LRT 10 min cheaper']), font=8)
    note('Table C.2 — New transit share of a pair after the LRT, λ = 0.03. The shift is largest where transit already has a foothold; on the car-dominated pairs (2 % transit, the car-available segment of C.5) it is a fraction of a point. The corridor-wide result, 0.9 % of car trips, is the sum of such small shifts.')
    fig(f'{FIG}/appC_logit_mechanisms.png', 16, 'Figure C.1 — The two mechanisms. Left: the LRT\'s share of a pair\'s transit riders against its cost advantage, for the three sensitivities carried. Right: the points added to a pair\'s transit share by the car-to-transit shift, against its share before the LRT.')
    P('One more rule connects the two examples: the pair\'s observed 2022 share is smoothed towards the share of the wider area it belongs to before the pivot '
      '(weight k = 20 trips), so a pair with three surveyed trips does not swing the result. Because the model pivots on observed shares, removing the LRT returns the 2022 flows exactly.')
    H('C.5 How λ was estimated', 2)
    P('The obvious route failed. A fit of each area pair\'s 2022 transit share on the cost difference between bus and car (597 pairs, 70,000 trips) returns λ with the wrong sign: '
      'the pairs where transit is cheapest relative to the car are the pairs whose residents own few cars, so the share follows who lives there, not the minutes. A pair-level fit cannot separate the two.')
    P('The remedy was to go to the individual survey records (2,310 morning trips of 543 households within the corridor areas) and hold car availability constant: '
      'no car in the household, no licence, more licences than cars, or a car per driver; also the purpose of the trip, age, gender, sector and the distance band. '
      'Within a group of people with the same access to a car, those facing a smaller transit cost choose transit more often, and that slope is λ.')
    table(pd.read_csv('Output/mode_choice/lambda_summary.csv').rename(columns={'lambda': 'λ per felt minute', 'lo95': '95 % low', 'hi95': '95 % high', 'rows': 'trips', 'assumed (step 31)': 'assumed in the chain', 'assumed range': 'assumed range'}),
          {'λ per felt minute': '{:.3f}', '95 % low': '{:.3f}', '95 % high': '{:.3f}', 'assumed in the chain': '{:.3f}'}, font=7)
    note('Table C.3 — The person-level estimates (step 33). M1 is the central specification; M4 restricts the sample to licence holders in car-owning households. Source: Output/mode_choice/lambda_summary.csv.')
    fig('Output/figures/mode_choice_person_level_by_segment.png', 16, 'Figure C.2 — The observed transit share against the cost difference, by car-availability segment: four separate levels, and a visible slope only among the households without a car (step 33).')
    for s in ['The pooled estimate, 0.035 (interval 0.002–0.068), has the right sign and supports the assumed 0.03, which sits on its cautious side. On the May 2026 car network it is 0.040.',
              'By segment it is 0.083 for people in households without a car, and not different from zero (0.008 ± 0.017) for licence holders in car-owning households: the very travellers the LRT would have to win from the car. The survey has too few such people choosing transit on comparable pairs to measure their response.',
              'So the transit-side λ_T is supported by the data and the car-side λ is a judgement bounded by its range. The bus and Metronit shifts are the firmer part of every result; the car shift is an order of magnitude. A stated-preference survey of car owners on the corridor is the way to pin it down.']: B(s)
    H('C.6 What λ does to the result', 2)
    fig(f'{FIG}/appC_lambda_range.png', 14, 'Figure C.3 — The 2022 test capture (step 31, all underground, 25 areas) under the λ and premium cases carried through the chain.')
    P('The λ range alone spans −26 % to +42 % of the capture, the widest single factor after the out-of-vehicle set, which is why the report\'s planning range (5,532 to 10,537 morning riders around the reference 7,433) is built from it. '
      'The LRT premium (0 or 10 minutes instead of 5) gives a narrower band inside it, −20 % to +23 %. Doubling λ roughly doubles the car shift and pushes the LRT\'s share of transit away from an even split; halving it does the reverse.')
    sources('METHODOLOGY.md §6ac (step 31), §6ae (step 33), §6ak (step 40), §6aq (step 45); Output/mode_choice/lambda_summary.csv, coefficients_all_models.csv, sample_by_car_segment.csv; Output/skims/lrt_capture_scenarios.csv; the pivot code of notebooks/current/LRT_alternatives_demand.ipynb.')

    # ======================= D =======================
    H('Appendix D. The generalized cost function: why, and how we arrived at it')
    P('What this appendix answers: why the model reduces every trip to one number, what is in that number, where each ingredient comes from, and the sequence of decisions and corrections between the first draft of the formula in September 2026 and the one the report uses.')
    H('D.1 Why one number', 2)
    P('To ask whether a traveller would switch from a bus, a Metronit or a car to the LRT, the model has to compare trips that differ in every respect: one walks more, one waits less, '
      'one changes vehicles, one is faster but further from home. The generalized cost puts them on one scale, "how long the trip feels", in minutes. Minutes spent outside a vehicle '
      'count more than once (Appendix B), a change of vehicle carries a flat charge, and the preference for a rail vehicle enters as a bonus.')
    box('GC = in-vehicle time + 2 × walking + 2 × waiting + 8 per transfer (4 between Metronit and LRT) + 0.5 per LRT station end − LRT premium (5 over a bus path, 2.5 over a Metronit path)')
    table(pd.DataFrame([
        ['In-vehicle time', 'bus and Metronit: May 2026 timetable with the running times measured on the street network in May 2026 (the buses run 1.09 × the timetable in the peak); train: timetable; LRT: the calibrated function of Appendix A; car: the May 2026 measured network speeds between zone centroids, plus 3 minutes for parking and the walk at the ends', 'weight 1'],
        ['Walking', 'straight line × 1.3 for the street detour, at 4 km/h, from the zone to stops within 1 km and from stop to stop within 300 m for a transfer', 'weight 2'],
        ['Waiting', 'half the combined headway of the lines serving the pair in the peak hour, capped at 10 minutes; LRT 2.5 minutes (a tram every 5)', 'weight 2'],
        ['Transfer', 'a flat charge for the uncertainty and effort of changing vehicles, on top of the actual walking and waiting; the first boarding is not a transfer', '8 min; 4 min Metronit ↔ LRT'],
        ['Station access', 'the time inside a station from the entrance to the platform', '0.5 min per LRT end'],
        ['LRT premium', 'the preference for a rail-like vehicle at equal time, from the calibrated models\' in-vehicle multipliers', '−5 min against a bus path, −2.5 against a Metronit path'],
        ['Money', 'fare, parking, fuel', 'none, by decision (D.2, step 2)']],
        columns=['ingredient', 'where it comes from', 'how it counts']), font=7)
    note('Table D.1 — The ingredients of the generalized cost in the reference case.')
    H('D.2 How we got here, step by step', 2)
    for i, (h, s) in enumerate([
        ('The textbook starting point (LRT capture plan, 22 September 2026).', 'GC = in-vehicle time + 2 × walk + 2 × wait + 8 per transfer + (fare + parking) ÷ value of time, with a value of time of 30 ILS per hour as a placeholder. The weights 2 / 2 / 8 are the middle of the ranges in standard practice (1.5–2.5 for walking and waiting, 5–10 for a transfer).'),
        ('Money dropped (22 September 2026).', 'The transit fare in the area is flat and integrated, and a daily cap makes transfers and return trips free: the fare is the same for every bus, Metronit or LRT trip and for every pair, so it cannot change the choice between them. Against the car it is a constant per trip, which the model absorbs because it starts from the observed 2022 car-versus-transit split rather than predicting it from costs (C.4). Parking and car running costs were excluded on the same decision; no parking data exist for the area. The cost is in minutes only from here on.'),
        ('Placeholders replaced by measured data (22–23 September 2026).', 'The first fill used an 8-minute walk and a 10-minute headway for every bus pair. These gave way, in order, to the national timetable (walk to the actual stops, wait from the actual headways), then to the running times measured on the street network in May 2026, which are 1.1–1.4 times the timetable on the arterial hops where the demand is. The Metronit became a mode of its own. The LRT in-vehicle time was corrected for station spacing (Appendix A) and its headway set to 5 minutes. A check against the survey found that door-to-door bus times reported by travellers exceed the timetable-based ones by a fixed 7–9 minutes: the transfer, the wait for the line actually needed, and delay, which the transfer and wait terms stand in for.'),
        ('The LRT premium (22 September 2026) and the Metronit premium (5 October 2026).', 'Travellers prefer a rail vehicle at equal time. Calibrated models express this as an in-vehicle multiplier of 0.80–0.85 for LRT against 0.90–0.95 for BRT; on the trunk\'s 14 minutes of riding the gap is worth about 5 minutes against a bus path and about 2.5 against a Metronit path.'),
        ('The transfer structure (22 September and 5 October 2026).', 'A change between a bus and the LRT costs 8 minutes. The Metronit-to-LRT change was first set free, on the assumption of an integrated, same-platform interchange; the out-of-vehicle research found no study with a value below 4 minutes for even a cross-platform change, and 4 minutes was adopted (Appendix B).'),
        ('Station access and walking speed (5 October 2026).', 'Half a minute per station end for the way from the entrance to the platform, and walking at 4 km/h instead of 4.8 (the Israeli convention), both from the same research.'),
        ('From areas to zones (steps 44–45, October 2026).', 'The cost was first built between 25 corridor areas. An area-level skim pools the headways of every line serving the area and the walk to its nearest stop, which no single traveller gets: it understated the bus cost on the trunk by about a third (30 felt minutes against 45 at zone level). The reference case builds the cost per zone pair on the actual line graph of the timetable, with the LRT boarding at the cheapest-access station at each end.'),
        ('The checks.', 'The whole chain was rerun on nine out-of-vehicle parameter sets (Appendix B); the bus wait rule was tested with the busiest single line instead of the pooled headway (+14 % bus cost, +15 % LRT riders); the car times were compared with the survey\'s reported door-to-door times (0.90–0.95 of them, so no uplift); and the capture was run on a 2026 car network and on slower 2050 buses (section 4.9).')]):
        p = B(f'{h} {s}'); p.runs[0].font.bold = False
    H('D.3 A worked example', 2)
    P('From Kiryat Haim to Bat Galim by bus: walk 6 minutes to the stop, wait 5 (a bus every 10 minutes), ride 28, walk 4 at the end. By LRT: walk 9 to the station, wait 2.5, ride 20, walk 5. '
      'In felt minutes the bus trip is 28 + 2 × (6 + 4) + 2 × 5 = 58 and the LRT trip 20 + 2 × (9 + 5) + 2 × 2.5 = 53, less the 5-minute premium: 48. The LRT walks more and still wins by ten felt minutes because it is faster and comes more often; '
      'with λ_T = 0.06 that advantage gives it 65 % of the pair\'s transit riders (Appendix C).')
    fig(f'{FIG}/appD_gc_worked_example.png', 15, 'Figure D.1 — The worked example of section 2.4 as felt minutes: riding, walking and waiting (each weighted twice), and the premium; neither trip involves a transfer.')
    P('A second, illustrative case shows what the Metronit terms do. A trip from the Krayot to Bat Galim today rides the Metronit through: say 5 minutes of walking, 3 of waiting and 35 of riding, 35 + 2 × 5 + 2 × 3 = 51 felt minutes. '
      'The LRT path for the same trip takes the Metronit to Hamifrats (walk 5, wait 3, ride 18), changes there (4-minute penalty, 2.5-minute wait, 0.5-minute station access), rides the LRT 12 minutes to Bat Galim and walks 5 at the end, with the 2.5-minute premium: '
      f'18 + 12 + 2 × (5 + 5) + 2 × (3 + 2.5) + 4 + 0.5 + 0.5 − 2.5 = 63.5 felt minutes. The LRT path is dearer by 12.5 and takes {100 * p_lrt(-12.5):.0f} % of the pair\'s transit riders (the curve of Table C.1). '
      f'Set the interchange penalty to zero and the station access to zero, as the model did before 5 October, and the gap narrows to 7.5 and the share rises to {100 * p_lrt(-7.5):.0f} %: this is why those two terms, not the running speed, decide the Krayot market.')
    H('D.4 What the function does not capture', 2)
    for s in ['The weights are assumptions from the literature and from other calibrated models, not estimates on this corridor; the chain was rerun on nine sets to show the band they open (Appendix B).',
              'No money: a fare or parking policy that treats the modes differently cannot be tested with this function as it stands.',
              'No crowding, reliability or comfort beyond the LRT premium; no slopes in the walking times, in a city where they matter; no difference between a sheltered stop and an exposed one.',
              'The car\'s absolute cost does not reach the result: the model pivots on the observed 2022 split, so a slower car in 2050 changes nothing (caveat 25). Only the transit side of the cost moves the numbers.',
              'The walking terms are population- and employment-weighted averages per zone, not per address, and the LRT station access is a single figure per end.']: B(s)
    sources('docs/LRT_CAPTURE_PLAN.md; METHODOLOGY.md §6x (step 26 and its seven addenda), §6ac (step 31), §6ao (step 44), §6al, §6aq (step 45); Output/alternatives/skims_summary.csv; section 2.4 of this report.')

# ---------------- standalone: append to the existing report ----------------
def _drop_previous_appendices(doc):
    body = doc.element.body; kids = list(body); start = None
    for i, el in enumerate(kids):
        if el.tag.endswith('}p'):
            from docx.text.paragraph import Paragraph
            p = Paragraph(el, doc);
            if p.style.name.startswith('Heading 1') and p.text.startswith('Appendix A'): start = i; break
    if start is None: return 0
    n = 0
    for el in kids[start:]:
        if el.tag.endswith('}sectPr'): continue
        body.remove(el); n += 1
    return n

def main():
    """python3 tools/report_appendices.py            -> append / replace the appendices in the comprehensive report
       python3 tools/report_appendices.py --only     -> also write them as a document of their own, reports/Nofit_LRT_Extension_Report_Appendices.docx"""
    from docx import Document
    from docx.shared import Pt, Cm
    from docx.enum.section import WD_ORIENT
    only = '--only' in sys.argv
    if only:
        doc = Document(); st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(10)
        for s_ in doc.sections: s_.left_margin = s_.right_margin = Cm(2)
        doc.add_heading('Nofit LRT extension — demand study', 0); doc.add_paragraph('Appendices A–D of the comprehensive report (reports/Nofit_LRT_Extension_Comprehensive_Report.docx), as a document of their own.'); dropped = 0
    else:
        doc = Document(REPORT); dropped = _drop_previous_appendices(doc)
        sec = doc.add_section(); sec.orientation = WD_ORIENT.PORTRAIT; sec.page_width, sec.page_height = min(sec.page_width, sec.page_height), max(sec.page_width, sec.page_height); sec.left_margin = sec.right_margin = Cm(2)
    def P(text, style=None): return doc.add_paragraph(text, style=style)
    def B(text): return doc.add_paragraph(text, style='List Bullet')
    def H(text, lvl=1): return doc.add_heading(text, lvl)
    def fig(path, width=16, caption=None):
        if os.path.exists(path):
            doc.add_picture(path, width=Cm(width))
            if caption: c = doc.add_paragraph(caption); c.runs[0].font.size = Pt(8); c.runs[0].font.italic = True
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
    add_appendices(doc, H, P, B, fig, table)
    out = 'reports/Nofit_LRT_Extension_Report_Appendices.docx' if only else REPORT
    doc.save(out); print(f'{out}: appendices A–D {"written" if only else ("replaced" if dropped else "appended")}' + ('' if only else f' ({dropped} elements dropped)'))

if __name__ == '__main__': main()
