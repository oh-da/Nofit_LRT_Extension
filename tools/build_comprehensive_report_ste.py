# -*- coding: utf-8 -*-
"""The comprehensive report in ASD-STE100 Simplified Technical English: reports/Nofit_LRT_Extension_Comprehensive_Report_STE.docx
Same structure and the same numbers as the Hebrew summary report (tools/build_comprehensive_report_he.py) and the English report
(tools/build_comprehensive_report.py); the charts are the English ones (Output/figures/comprehensive/, Output/figures/alternatives/).
The text obeys the writing rules of ASD-STE100 Issue 8: sentences of 25 words or fewer (20 in instructions), one topic for each sentence and
each paragraph, paragraphs of 6 sentences or fewer, the active voice, the simple present tense for facts, approved words with one meaning each,
no -ing verb forms, vertical lists for sequences. Technical names and technical verbs of transport modelling (permitted by the specification)
are listed in the table at the top of the report. The builder checks the three countable rules (sentence length, paragraph length, -ing forms)
on every paragraph, bullet and caption it writes and prints what it finds; formulas and source lines are exempt.
Run after tools/build_comprehensive_report.py:  python3 tools/build_comprehensive_report_ste.py"""
import os, re
import numpy as np, pandas as pd
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
while not os.path.exists('METHODOLOGY.md') and os.getcwd() != '/': os.chdir('..')
# the data, the helpers and the reference-case numbers of the English builder (everything before its Word report), so the three reports read the same files
_src = open('tools/build_comprehensive_report.py', encoding='utf-8').read()
_head, _rest = _src.split('# ======================= 0 =======================')
_head = _head.replace("doc = Document()", "doc = Document()  # the English builder's document object; not saved here")
exec(_head)   # noqa: defines summary, tabs, PHF, phf, loads, srow, ext_row, through_table, market_summary, market_tables, cross_hamifrats, busiest, ref, refE, refP, ref_unp, ref_slow, RANGE_LO/HI, mk_ref, SCEN, SCEN_LAB, REF, REG, OUT, CFIG, FIG, fA, fP, ref_brt_shift, ref_bus_shift

# ---------------- the STE self-check: the countable rules of ASD-STE100 on every paragraph written ----------------
ING_OK = {'boarding', 'boardings', 'parking', 'crowding', 'during', 'nothing', 'evening', 'morning', 'thing', 'things', 'spacing', 'meaning', 'everything', 'something', 'anything', 'according', 'bring', 'brings'}   # technical names and words that only end in -ing
_findings = []
def ste_check(text, where='text', procedural=False):
    if not text or text.startswith('[') or text.startswith('Sources:'): return
    sents = [s for s in re.split(r'(?<=[.!?])\s+(?=[A-Z"(λ0-9…])', text.strip()) if s.strip()]
    limit = 20 if procedural else 25
    if len(sents) > 6: _findings.append(f'{where}: paragraph of {len(sents)} sentences: "{text[:60]}…"')
    for s in sents:
        words = [w for w in re.split(r'\s+', s) if re.search(r'[A-Za-zλ0-9]', w)]
        if len(words) > limit: _findings.append(f'{where}: {len(words)} words: "{s[:90]}…"')
        for w in re.findall(r'\b[A-Za-z]+ing\b', s):
            if w.lower() not in ING_OK: _findings.append(f'{where}: -ing form "{w}" in "{s[:70]}…"')

# ---------------- Word helpers ----------------
doc = Document()
st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(10)
for sec in doc.sections: sec.left_margin = sec.right_margin = Cm(2)
def P(text, size=None, bold=None, italic=None, check=True):
    if check: ste_check(text, 'P')
    p = doc.add_paragraph(text)
    for r in p.runs:
        if size: r.font.size = Pt(size)
        if bold is not None: r.font.bold = bold
        if italic is not None: r.font.italic = italic
    return p
def B(text, level=1): ste_check(text, 'B'); return doc.add_paragraph(text, style='List Bullet' if level == 1 else 'List Bullet 2')
def H(text, lvl=1): return doc.add_heading(text, lvl)
def CAP(text): ste_check(text, 'CAP'); return P(text, size=8, italic=True, check=False)
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
def fig(path, width=16, caption=None):
    if os.path.exists(path):
        doc.add_picture(path, width=Cm(width)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        if caption: CAP(caption)
    else: P(f'[figure missing: {path}]', check=False)
def landscape():
    sec = doc.add_section(); sec.orientation = WD_ORIENT.LANDSCAPE; sec.page_width, sec.page_height = max(sec.page_width, sec.page_height), min(sec.page_width, sec.page_height); sec.left_margin = sec.right_margin = Cm(1.5)
def portrait():
    sec = doc.add_section(); sec.orientation = WD_ORIENT.PORTRAIT; sec.page_width, sec.page_height = min(sec.page_width, sec.page_height), max(sec.page_width, sec.page_height); sec.left_margin = sec.right_margin = Cm(2)
def n(x): return f'{x:,.0f}'
def pct(x, d=0): return f'{x:.{d}f} %'
def sgn(x): return f'{x:+.0f} %'
ext_use = ref['LRT trips using the extension (at least one segment S01–S24)']; ext_both = ref['LRT trips on the extension stations (both ends on S01–S24)']
cross = cross_hamifrats('AM', REF); peak_line = busiest('AM', REF, peak=True); peak_ext = busiest('AM', REF, ext_only_segments=True, peak=True)
EXT_COL = 'LRT trips using the extension (at least one segment S01–S24)'

# ======================= title =======================
doc.add_heading('Nofit LRT — extension of the line to Haifa and Tirat Carmel: the demand study', 0)
P('This is the ASD-STE100 (Simplified Technical English) version of the summary report. It has the same structure and the same numbers as the Hebrew summary report '
  '(Nofit_LRT_Extension_Comprehensive_Report_HE.docx) and as the full English report (Nofit_LRT_Extension_Comprehensive_Report.docx). '
  'The figures are the figures of the English report, with their English captions. The numbers of the study are of 5 October 2026. This version is of 15 October 2026.')
P('How this version applies ASD-STE100 Issue 8:', size=9, italic=True)
for s_ in ['Each sentence has 25 words or fewer (20 words in an instruction). Each sentence has one topic.',
           'Each paragraph has one topic and 6 sentences or fewer. Sequences are vertical lists.',
           'The text uses the active voice and the simple present tense for facts. Each word has one meaning. There are no -ing verb forms.',
           'The specification permits technical names and technical verbs. The table below gives the technical names of transport models that this report uses.']: B(s_)
tn = pd.DataFrame([
    ['LRT', 'Light rail transit. "The LRT" is the planned Nofit light rail line.'], ['Main route', 'The Nofit line in construction, Hamifrats – Nazareth, stations M01–M20.'], ['Extension', 'The planned continuation of the line from Hamifrats through Haifa to Tirat Carmel, stations S01–S24.'],
    ['Through line', 'The main route and the extension as one line, without a transfer at Hamifrats.'], ['Metronit', 'The bus rapid transit (BRT) system of the Haifa area.'], ['Public transport', 'Bus, Metronit, train and LRT together ("transit" in the English report).'],
    ['TAZ', 'Traffic analysis zone, the smallest geographic unit of the model (781 zones).'], ['Corridor area', 'One of the 25 groups of TAZs along the line, the geography of the report.'], ['Corridor market', 'The trips between the 174 TAZs of the corridor that start and end in different corridor areas.'],
    ['Pair', 'One origin zone and one destination zone.'], ['Path', 'The sequence of walks, waits and vehicles between the two zones of a pair.'], ['Generalized cost (GC)', 'One value, in felt minutes, that shows the total effort of a trip.'],
    ['Felt minute', 'A minute of trip time after the model applies the weights of the generalized cost.'], ['Transfer penalty', 'A fixed value that the model adds for each change of vehicle.'], ['LRT premium', 'A fixed value that the model subtracts from the cost of an LRT path.'],
    ['λ (lambda)', 'The cost sensitivity: the number that changes a difference in felt minutes into a difference in choices. λ_T is the value inside public transport.'], ['Logit model', 'The formula that changes a cost difference into a share of travellers.'], ['Pivot', 'A calculation that starts from the observed 2022 shares and changes them by the new cost difference; it does not estimate the shares again.'],
    ['Capture', 'The number of LRT trips that the model calculates.'], ['Shift', 'Trips that move from one mode to a different mode when the LRT is added.'], ['Scenario', 'A year and a demographic forecast: 2040 or 2050; BU (business as usual) or HS (high scenario).'],
    ['Reference case', 'The scenario 2050 BU, the through line, the Prioritized regime.'], ['Regime', 'How the extension operates: Prioritized (full priority at the road junctions) or Unprioritized (at street level, with the traffic).'], ['Peak hour', 'The busiest 60 minutes of a three-hour period (AM 06:00–09:00, PM 16:00–19:00).'],
    ['Load', 'The number of passengers on one segment of the line in one direction.'], ['Headway', 'The time between two vehicles of the same line.'], ['Feeder', 'A bus or Metronit leg that brings a traveller to an LRT station.'],
    ['Level of service', 'The travel time, access, wait and transfers of a mode between two zones.'], ['Matrix', 'A table of trips from each zone to each zone.'], ['Caveat', 'A documented limit of the model (chapter 8 of METHODOLOGY.md, 29 items).'],
    ['Step', 'One documented notebook of the chain of 45 steps (step 45 is the demand of the alternatives).']], columns=['Technical name', 'Meaning'])
table(tn, font=8)

# ======================= decision summary =======================
H('Summary for decision makers')
P('The question. The main route of the Nofit light rail (Hamifrats – Nazareth) is in construction. Must the line continue through Haifa to Tirat Carmel? '
  'If yes, must it operate as one line, or must the extension stop at Hamifrats?')
P('This report gives the quantity and the location of the demand for the extension. The base is the travel market that we measured in 2022, increased to 2040 and to 2050. '
  'The report also says what the evidence supports and what it does not support.')
P('Reference case. The main case for the plan is the year 2050 with the usual demographic scenario ("2050 BU"). The year 2040 and the high scenario ("HS") show the effect of growth. '
  'The reference alternative is the through line (main route + extension) with priority for the extension at the junctions ("Prioritized").', bold=True)
dec = pd.DataFrame([
    ['LRT passengers on the corridor, AM 06:00–09:00 / AM peak hour', f'{n(ref["LRT"])} / {n(ref["LRT"] * fA)}'],
    ['Of these: passengers who use the extension (S01–S24) / passengers who travel only between extension stations', f'{n(ext_use)} ({pct(ext_use / ref["LRT"] * 100)}) / {n(ext_both)}'],
    ['LRT passengers, PM 16:00–19:00 / PM peak hour', f'{n(refP["LRT"])} / {n(refP["LRT"] * fP)}'],
    ['Through line against a terminal at Hamifrats: extension passengers / all LRT passengers', f'{n(ext_use)} against {n(refE["LRT"])} ({sgn((ext_use / refE["LRT"] - 1) * 100)}) / {n(ref["LRT"])} against {n(refE["LRT"])} ({sgn((ref["LRT"] / refE["LRT"] - 1) * 100)})'],
    ['Source of the passengers (AM, 3 hours)', f'Metronit {n(ref_brt_shift)} ({pct(ref_brt_shift / ref["BRT before"] * 100)} of its corridor trips), bus {n(ref_bus_shift)}, car {n(ref["LRT from car"])} ({pct(ref["LRT from car"] / ref["car before"] * 100, 1)} of the corridor car trips)'],
    ['Maximum load, AM peak hour, one direction', f'{n(peak_line)} at the entry to Hamifrats (segment S24–M02, direction Tirat Carmel); on the extension itself {n(peak_ext)}'],
    ['Public transport share of the corridor market, before → after', f'{pct(ref["transit before"] / (ref["car before"] + ref["transit before"]) * 100, 1)} → {pct(ref["total transit"] / (ref["car"] + ref["total transit"]) * 100, 1)}; the LRT takes {pct(ref["LRT"] / ref["total transit"] * 100)} of public transport'],
    ['Largest markets (AM, 3 hours)', f'Tirat Carmel ↔ Haifa {n(mk_ref.iloc[1]["LRT trips (3 h)"])} ({pct(mk_ref.iloc[1]["share of all LRT trips"])}); inside Haifa {n(mk_ref.iloc[0]["LRT trips (3 h)"])} ({pct(mk_ref.iloc[0]["share of all LRT trips"])}); Krayot ↔ Haifa (with a feeder) {n(mk_ref.iloc[2]["LRT trips (3 h)"])} ({pct(mk_ref.iloc[2]["share of all LRT trips"])}); main route ↔ Haifa {n(mk_ref.iloc[3]["LRT trips (3 h)"])} ({pct(mk_ref.iloc[3]["share of all LRT trips"])})'],
    ['Extension without priority at the junctions (at street level)', f'{n(ref_unp["LRT"])} ({sgn((ref_unp["LRT"] / ref["LRT"] - 1) * 100)})'],
    ['Buses 20 % slower in 2050 (sensitivity)', f'{n(ref_slow["LRT"])} ({sgn((ref_slow["LRT"] / ref["LRT"] - 1) * 100)})' if ref_slow is not None else '—'],
], columns=['Reference case 2050 BU, main route + extension, Prioritized', 'Value'])
table(dec, font=8)
P('Range for the plan (LRT passengers, AM 06:00–09:00, reference case). The range comes from the cost sensitivity λ at the two ends of its range (0.05 and 0.02 around the central 0.03). '
  'This is the widest single factor of the uncertainty experiment (step 40). The LRT premium (0 or 10 minutes) gives a narrower band inside it. '
  'The regime is a design decision, not an uncertainty. Thus the table shows it separately.', bold=True)
pr = pd.DataFrame([['Central case for the plan (λ 0.03, premium 5 minutes, Prioritized)', ref['LRT'], ref['LRT'] * fA], ['Possible low case (λ 0.05: travellers with the lowest sensitivity to cost)', ref['LRT'] * RANGE_LO, ref['LRT'] * RANGE_LO * fA],
                   ['Possible high case (λ 0.02: the highest sensitivity)', ref['LRT'] * RANGE_HI, ref['LRT'] * RANGE_HI * fA], ['Design decision: extension without priority, central λ', ref_unp['LRT'], ref_unp['LRT'] * fA]],
                  columns=['Case', 'LRT passengers, 3 hours', 'LRT passengers, peak hour'])
table(pr, font=8)
P('What the evidence on the demand supports:', bold=True)
for s_ in [f'A market for the extension of approximately {ext_use * RANGE_LO / 1000:.0f},000 to {ext_use * RANGE_HI / 1000:.0f},000 passengers in the three AM hours in 2050 BU. Most of this market is on the Carmel coast and in the lower city. It has three parts of almost the same size: Tirat Carmel ↔ Haifa, trips inside Haifa, and the Krayot with a feeder.',
           f'The passengers of the extension do not depend on the through line: {n(ext_use)} on the through line, against {n(refE["LRT"])} if the extension stops at Hamifrats. The benefit of the through line is the transfer that it removes for the {n(cross)} trips ({pct(cross / ref["LRT"] * 100)}) that cross Hamifrats. Today these trips use the Metronit without a transfer. The +25 % on the full line is the market of the main route. This market travels in each case.',
           'Priority at the junctions: the regime at street level loses approximately a quarter of the passengers, most of them on the extension. This effect is larger than the growth between 2040 and 2050.',
           'A maximum load of approximately 1,000 to 1,400 passengers for each hour and direction at the entry to Hamifrats. This is the demand of a light rail, not of a metro.',
           'The rank of the alternatives and of the regimes. The order of magnitude of the shift from the Metronit, from the bus and from the car.']:
    B(s_)
P('What the evidence does not support:', bold=True)
for s_ in ['A passenger forecast for an economic appraisal, for the fleet or for the frequency. The loads are potential movements without a capacity limit. The service plan keeps each bus line and each Metronit line as it operates today. The base is validated at the corridor level, but not at the link level. The cost sensitivity has a range; it is not an estimate for the car owners that the line must attract.',
           'A statement about the car in 2040 / 2050. The shift from the car to the LRT is an order of magnitude only. It does not change with the road conditions in this model.',
           'A claim of a "new market". Most LRT passengers are the Metronit and bus passengers of today in a faster vehicle. The net addition to public transport is the shift from the car: some hundreds to approximately one thousand trips in three hours.',
           'Numbers for one station or one TAZ, and all items about the operation of the main route. The operation of the main route is an assumption.']:
    B(s_)
doc.add_page_break()

# ======================= 1 =======================
H('1. The goal and the objectives')
P('The main route of Nofit (Hamifrats – Nazareth) is in construction. The extension continues the line from Hamifrats through Haifa to Tirat Carmel: 24 stations, 18.7 km along the Haifa coast and the lower city. '
  'The study asks three questions about the extension:')
for s_ in ['How many passengers will the extension attract?', 'Where do these passengers come from?', 'How does the demand change with the operation of the extension and with the growth of the metropolis?']: B(s_)
P('The objectives, in the sequence of the work:')
for s_ in ['Make a picture of the travel market of the base year 2022 in the AM peak: car, bus, Metronit, rail. The level is the TAZ. The sources are the household travel survey, the ticket data, the timetables and the speed data. Compare this picture with independent counts.',
           'Increase the base to 2040 and to 2050 with the two demographic scenarios of the metropolitan forecast (BU, business as usual; HS, high scenario). Keep the travel behaviour of 2022.',
           'Make the level of service (travel time, access, wait, transfers) for the car and for each public transport mode: bus, Metronit, train and LRT. Use the same geography, the timetable of May 2026 and the measured speeds.',
           'Estimate the demand that the LRT gets from the bus, from the Metronit and from the car when the LRT is added to the service. Do this for the through line, in the two regimes of the extension, in the AM and PM peaks, for each scenario.',
           'Report what the extension carries as a part of the through line. These are the trips that use at least one segment between S01 and S24 (Tirat Carmel – Hamifrats).',
           'Say what the chain can do and what it cannot do, with each caveat that we found.']:
    B(s_)
P('What the study is not: it is not a study of capacity, frequency or fares. It is not an economic appraisal. It is not a calibrated four-step regional model. '
  'It is a demand estimate for a corridor, for a first selection between alternatives. We built it from measured data with a documented chain. Its purpose is to give the size and the location of the market, and to rank the alternatives.')

# ======================= 2 =======================
H('2. The "model": the structure, the data and the approach')
H('2.1 The structure', 2)
P('The "model" is a chain of 45 documented steps (Jupyter notebooks). Each step can be run again. The chain has four blocks:')
for s_ in ['Base-year matrices (steps 1–22). Person trip matrices for the AM peak 06:00–09:00 (and later also 16:00–19:00 and midday), by mode, on the 778 TAZs of the district. The source is the household travel survey of 2017/18 with expansion weights. The bus layer is calibrated to the RavKav (smart card) journeys of May 2022 with the destination pattern of the on-board survey. The rail layer uses the national series. All layers move from 2018 to 2022.',
           'Forecast matrices (step 23). The 2022 matrices move to 2040 and 2050 with the population and the employment of each TAZ. The trip rates, the destination choice and the mode split stay at 2022.',
           'Level of service (steps 25–30, 37, 43, 44). Travel time, access, wait and transfer for each mode on the 25 corridor areas and on the 781 TAZs. The car uses the car speed network of May 2026. The bus and the Metronit use the GTFS file of the Ministry of Transport (22 May 2026, service of Tuesday 2 June 2026). Their run times come from the bus speeds measured in May 2026. The LRT uses a stop-to-stop time function that we calibrated on the Red Line in Tel Aviv.',
           'LRT capture (steps 31–33, 39, 40, 45). A "pivot" on the mode shares that we observed in 2022 for each pair of TAZs. Inside public transport, the LRT path competes with the bus / Metronit path. The decrease in the cost of all public transport moves trips from the car. Step 45 does this for each alternative, regime, period and scenario.']:
    B(s_)
fig(f'{FIG}/lrt_alternatives_lines.png', 15, 'Figure 2.1 — The main route (M01–M20, in construction) and the extension (S01–S24) with the corridor areas.')
H('2.2 The data and their dates', 2)
data = pd.DataFrame([
    ['Household travel survey (THS) 2017/18', '2017–2018', 'Base matrices by mode, trip rates, estimate of λ'],
    ['Cellular OD trips, average weekday, by hour', '2018–2019', 'Check of the survey matrices'],
    ['RavKav — linked bus journeys', 'May 2022', 'Bus calibration and the destination pattern'],
    ['RavKav 2025 — boardings: Metronit, rail, national buses', '51–52 Tuesdays in 2025, 06:00–09:00', 'Boardings by stop and TAZ, Metronit and rail matrices'],
    ['On-board survey — destination probabilities by TAZ', '2022', 'Destination pattern below the super-zone level'],
    ['Population and employment 2020, 2025; forecasts BU / HS 2040, 2050', '2020 base; version of the metropolitan forecast', 'Move to 2022 and growth to 2040 / 2050'],
    ['Road network (Emme) with traffic counts by hour', 'counts 2017–2023', 'Check of the car layer against counts'],
    ['National GTFS of the Ministry of Transport', 'file of 22 May 2026; service of 2 June 2026', 'Level of service of bus, Metronit and train; time on route'],
    ['Bus speeds on the street network', 'May 2026, by day and hour', 'Observed bus run times; the network for the routes'],
    ['Car speeds, all the country (GoogleSpeed)', 'May 2026, by hour', 'Car time matrices'],
    ['Alignment and platforms of the extension (hf_lrt_3)', 'supplied 22 September 2026', '24 stations, times between stations'],
    ['Main Nofit route (in construction) and its 20 station nodes', 'supplied 5 October 2026', 'Stations of the main route and run time at 80 km/h'],
    ['Corridor aggregation V2 — 25 areas, 174 TAZs', 'supplied 22 September 2026', 'Geography of the report'],
    ['Calibration of LRT run times (Red Line, operator 22)', 'operation data 2024–2025', 'Stop-to-stop time function, with priority / at street level'],
    ['Research on the weights of out-of-vehicle time', 'done 4 October 2026', 'Walk / wait weights, transfer penalties, LRT premium'],
], columns=['Input', 'Date / version', 'Use'])
table(data, font=8)
H('2.3 The approach', 2)
for s_ in ['Trips of persons, not vehicles. Each matrix contains the trips of the residents of the study area with the two ends inside the area, in the three peak hours.',
           'Two geographies. The 781 TAZs for the routes, the access and the pivot; the 25 corridor areas for the report and for the profiles along the line. The corridor market is the 174 TAZs of the V2 aggregation. We count the demand on pairs of TAZs in different areas.',
           'Level of service from measured data. The car times and the bus times come from the speeds measured in May 2026 (07:00 for the AM, 17:00 for the PM). They are not a simulation of congestion. The service is the real timetable. The wait is half the headway (maximum 10 minutes). The access is a walk at 4 km/h × 1.3, up to 1 km, and transfers are possible up to 300 m.',
           'The level of service stays at May 2026 in each scenario year. The runs for 2040 / 2050 use the car times and the bus times of today, while the demand on the corridor increases by 30–60 %. The future network of the regional model is not available. A network of today with the demand of tomorrow, without the planned projects, is the worse assumption. Section 4.9 shows the effect of slower buses.',
           'Pivot, not a new estimate. The shares that we observed in 2022 for each pair are the anchor. The LRT changes them in two ways: the probability to select the LRT inside public transport, and the decrease of the total cost. The absolute cost of the car cancels in the pivot (caveat 25).',
           'The forecasts are "demographic references". They move the pattern of 2022 with the persons and the jobs. They have no change of service, car ownership, fares or work from home. The PM matrices for 2040 / 2050 are the PM base of 2022 increased with the AM growth (caveat 28).']:
    B(s_)
B('The LRT is a new path inside public transport. For each pair of TAZs, the path has five parts:')
for s_ in ['The station with the lowest access cost at each end.', 'The run time of the LRT between these stations.', 'A wait of 2.5 minutes (headway 5 minutes).', 'An access time of 0.5 minute at each station.',
           'A feeder leg where the stations are too far to walk: penalty 8 minutes by bus, or 4 minutes by Metronit.', 'The LRT premium: 5 minutes against a bus path, 2.5 minutes against a Metronit path.']: B(s_, 2)
H('2.4 The "generalized cost" in simple words', 2)
P('The generalized cost is the "felt" length of a trip, in minutes. A wait at a stop, a walk to the stop and a change of vehicle are less comfortable than a seat in a vehicle. '
  'Thus these minutes count more than one time. The result is one number for each trip. This number puts a bus trip, a Metronit trip, an LRT trip and a car trip on the same scale:')
P('Generalized cost = in-vehicle time + 2 × walk time + 2 × wait time + 8 minutes for each transfer (4 minutes between the Metronit and the LRT) − LRT premium (5 minutes against a bus, 2.5 minutes against the Metronit)', bold=True, check=False)
P('The wait is half the headway, with a maximum of 10 minutes. The walk is at 4 km/h on the straight line × 1.3 for the detour of the streets. '
  'The transfer penalty is a fixed charge for the uncertainty and the effort of a change of vehicle. It is added to the real time. The first boarding is not a transfer.')
P('The LRT premium shows the preference for a rail vehicle against a bus. The calibrated models in Israel found this preference. The car cost is the drive time at the measured speeds plus 3 minutes for the parking and the walk at the ends. '
  'Money is not in the calculation for all modes. The fare is flat and integrated, and there are no data on parking costs for the area.')
ex = pd.DataFrame([['Walk to the stop / station', '6 min × 2 = 12', '9 min × 2 = 18'], ['Wait: headway 10 min → 5 / headway 5 min → 2.5', '5 × 2 = 10', '2.5 × 2 = 5'], ['In-vehicle time', '28', '20'], ['Transfers', '0', '0'], ['Walk at the end', '4 min × 2 = 8', '5 min × 2 = 10'], ['LRT premium', '0', '−5'], ['Generalized cost', '58', '48']], columns=['Component (example: Kiryat Haim → Bat Galim)', 'By bus', 'By LRT'])
table(ex, font=8); CAP('Table 2.2 — A calculated example. The LRT trip is cheaper by ten felt minutes, although its walk is longer. The LRT is faster and operates more frequently.')
P('The model does not use the cost alone. It uses the difference between two options and a sensitivity coefficient λ. This coefficient changes felt minutes into a probability. '
  'Inside public transport (λ_T = 0.06 for each minute), an advantage of ten minutes gives the LRT approximately 65 % of the passengers of the pair. Twenty minutes give approximately 77 %. An equal cost gives 50 %.')
P('The shift from the car uses the decrease in the cost of all public transport with λ = 0.03, half the sensitivity. It starts from the public transport share that we observed in 2022 for the pair. '
  'Where the car has most of the trips, this share is small and the shift is small.')
H('2.5 The sensitivity coefficient λ: what it is, why it is necessary, how we estimated it', 2)
P('What it is. λ is the number that changes a difference in felt minutes into a difference in choices. In the logit model, the public transport cost changes by ΔGC minutes. Then the odds of public transport against the car change by the factor exp(−λ × ΔGC).')
P('With λ = 0.03, one minute moves the odds by 3 %, and ten minutes by approximately 35 %. A large λ means that travellers react strongly to small differences of cost. A small λ means that habit, availability and items outside the cost have the control.')
P('Why it is necessary. All the capture depends on it. The advantage of the LRT against the bus on a pair is a difference in felt minutes. λ_T decides how many public transport passengers of the pair move. λ decides how many car trips move. '
  'The λ range alone is −25 % to +40 % of the 2022 capture, more than the regime and the premium.')
P('Why we could not read it from the matrices. The simple estimate is a logit of the public transport share of each pair of areas on the cost difference bus minus car. The sample is 597 pairs and 70,000 trips. It gives λ with the wrong sign and without a fit.')
P('The cause is the composition of the population. The pairs with a cheap public transport are the pairs where the residents have few cars. Thus the share depends on who lives there, not on the minutes. A fit at the pair level cannot separate the two effects.')
P('How we estimated it (step 33). We used the persons in the survey: the AM trips inside the 25 corridor areas (2,310 trips, 543 households). The model is a logit of car against public transport with the cost difference as the explanatory variable. '
  'The survey weights apply, and the standard errors are clustered by household.')
P('The car availability, the purpose, the age, the gender, the sector, the student status and the distance stay constant. The car availability has four classes: no car in the household, no licence, more licences than cars, car available. '
  'The constant car availability makes λ identifiable. In a group of persons with the same access to a car, the persons with a lower public transport cost select public transport more often.')
lam = pd.read_csv('Output/mode_choice/lambda_summary.csv'); lam2 = pd.read_csv('Output/mode_choice/car_network/lambda_summary.csv') if os.path.exists('Output/mode_choice/car_network/lambda_summary.csv') else None
MODEL_STE = {'M1': 'M1: cost difference + car availability, purpose, person, distance (central)', 'M1b': 'M1b: as M1, with the cheaper of bus and Metronit', 'M3': 'M3: M1 + fixed effects for the origin and destination areas', 'M4': 'M4: only licence holders in households with a car (the segment that the LRT must get from the car)', 'M1u': 'M1u: M1 without weights'}
lt = pd.DataFrame({'Model (step 33)': [MODEL_STE[m.split(':')[0]] for m in lam['model']], 'λ for each felt minute': lam['lambda'], '95 % interval, low': lam['lo95'], 'High': lam['hi95'], 'Trips': lam['rows']})
if lam2 is not None: lt.loc[len(lt)] = ['M1 on the car matrix of May 2026 (step 37)', lam2['lambda'].iloc[0], lam2['lo95'].iloc[0], lam2['hi95'].iloc[0], lam2['rows'].iloc[0]]
lt.loc[len(lt)] = ['The assumption in the chain (step 31): λ, range 0.02–0.05; λ_T = 2λ = 0.06', 0.03, 0.02, 0.05, np.nan]
table(lt, {'λ for each felt minute': '{:.3f}', '95 % interval, low': '{:.3f}', 'High': '{:.3f}'}, font=8); CAP('Table 2.3 — The λ estimates (Output/mode_choice/lambda_summary.csv).')
P('The result. The pooled λ is 0.035 (0.002–0.068), with the correct sign, and 0.040 on the car matrix of 2026. By car availability segment:')
for s_ in ['Persons in households without a car: 0.083 (significant).', 'Persons without a licence: 0.027 (weak).', 'Persons with a car available: 0.053 (weak).', 'More licences than cars in the household: −0.006.',
           'Licence holders in households with a car: 0.008 ± 0.017, not different from zero.']: B(s_, 2)
P('The last segment is the segment that the LRT must get from the car. The survey does not have sufficient persons of this type who select public transport on comparable pairs.')
P('What the chain does with it. The chain keeps the assumption λ = 0.03 of step 31. This value is inside the interval of the pooled estimate, on its cautious side. The chain carries the range 0.02–0.05 in each capture run.')
P('It sets λ_T = 2λ inside public transport. The choice between two public transport paths is more sensitive to cost than the choice between car and public transport. The ratio 0.5 is a usual value for nested models; it is an assumption, not an estimate.')
P('The honest interpretation: the data support λ_T on the public transport side, and λ on the car side is a judgement with a range. Thus the shifts from the bus and from the Metronit are the more solid part of each result. The shift from the car is an order of magnitude.')

# ======================= 3 =======================
H('3. The calibration and the base scenario')
H('3.1 The base of 2022', 2)
P('The matrices of the base year come from the travel survey of 2017/18 (16,401 persons, 5,108 households, two survey days). The weights are the corrected household weights. The AM peak is the departure time 06:00–08:59. '
  'We calibrated the bus layer to the RavKav journeys of May 2022 with a segmented coverage rule. Where the ticket data cover a pair of super-zones well, they set the quantity. In the other pairs, the survey sets the quantity.')
P('The destination pattern of the on-board survey puts the trips below the super-zone level. The rail layer is the rail trips of the survey, increased with the national series. All layers move from 2018 to 2022 with the population and the employment of the TAZ.')
base = pd.DataFrame([['corridor → corridor', 72331, 10255, 313, 0], ['corridor → outside', 47011, 8947, 573, 292], ['outside → corridor', 89181, 19144, 1020, 2618], ['outside → outside', 1145275, 79615, 7545, 1141], ['all the study area', 1353798, 117961, 9451, 4050]],
                    columns=['2022, AM 06:00–09:00', 'Car', 'Bus (+ Metronit)', 'Taxi', 'Rail'])
table(base); CAP('Table 3.1 — The 2022 base by corridor class. On the V2 corridor (25 areas, 174 TAZs), the market between different areas is 56,445 car / 14,133 public transport / 720 taxi trips. The public transport share is 0.20.')
fig(f'{FIG}/three_mode_2022.png', 15, 'Figure 3.1 — The 2022 layers: car, bus, taxi and rail by super-zone (step 16).')
H('3.2 Tests against independent data', 2)
for s_ in ['Bus against the RavKav tickets on the corridor (step 28). On the Haifa trunk, the calibrated survey profile is within 1–4 % of the ticket profile in the direction Nazareth. In the other direction, it is within −14 % / +12 %. After Hamifrats, the two frames differ by up to 1.5 × in one direction (Figure 3.2).',
           'Bus against RavKav by time of day: RavKav / survey = 0.73 in the AM, 0.96 in the PM, 0.92 at midday. Trips to education are 40 % of the survey bus trips in the AM, and the card data under-represent them.',
           'Car against the traffic counts on closed cordons (step 36, Figure 3.3). Survey vehicles ÷ counted vehicles = 0.58–0.90 on the outer cordons and 0.61–0.62 in the metropolitan core. This is the expected order for a layer of personal trips of residents against all traffic. Through, commercial and non-resident traffic are not in the survey. The departure profile of the survey has a sharper peak than the road. The peak hour has 62 % of the three hours in the survey, against 38–43 % in the counts (caveat 18).',
           'Car assignment against the counts on links (step 42). The all-or-nothing assignment on the Emme network gives the correct total: 0.93 on 1,346 links. It does not give the correct pattern: R² 0.47 and RMSE 113 %, against 0.85 and 35 % in the guideline. A layer of person trips without commercial traffic and without route choice does not pass a test at the link level (caveat 23).',
           'Survey against the cellular trips (step 1b): the super-zone matrices agree in structure. The only systematic difference is the trips inside a zone, which are higher in the survey in each super-zone.',
           'Validation guideline of the Ministry of Transport (draft 2024, tests T1–T19, 226 items). 75 items pass, 123 fail with a documented explanation, and 10 are findings. The other items are not applicable or not run. The failures are in the tests for a four-step assignment model: link volumes, trip lengths at the TAZ level, trips inside a zone. The trip rates, the mode split and the car profile against the counts pass.']:
    B(s_)
fig(f'{FIG}/corridor_v2_survey_vs_ticketing.png', 16, 'Figure 3.2 — Public transport profile on the corridor: the calibrated survey against the RavKav tickets, by route and direction (step 28).')
fig(f'{FIG}/car_cordon_counts.png', 16, 'Figure 3.3 — The car layer against the traffic counts on closed cordons (step 36).')
H('3.3 The level of service and the cost sensitivity', 2)
P('We made the level of service of public transport from the timetable with the run times measured in May 2026. Observed ÷ scheduled is 1.09 for a bus trip (Metronit 0.87), 1.00 on hops shorter than 500 m and 1.42 on hops longer than 2 km. '
  'On the trunk pairs, the car times on the network of May 2026 are 0.90 × the door-to-door times in the survey. On all pairs, they are 0.95 ×. Thus there is no increase of the car time for 2026 (step 37).')
P('The car speeds of May 2026 almost do not change by hour (caveat 24). Thus the "07:00" matrix is in effect an all-day speed of May 2026.')
P('Generalized cost on the trunk pairs (weighted by trips, AM, felt minutes): car 13.8; bus / Metronit 44.8 at the TAZ level. The area matrix of step 31 gave 27–30. It pooled the headways of all direct lines and the walk to the nearest stop (caveat 26). '
  'The LRT on the through line is 48.7 with priority / 57.2 without, with the 5-minute premium. The in-vehicle time of the LRT on the trunk is lower than that of the bus. The disadvantage that remains for the LRT is the access to the station and the transfer where a feeder is necessary.')
fig(f'{FIG}/mode_choice_person_level_by_segment.png', 14, 'Figure 3.6 — λ by car availability segment, estimate at the person level (step 33).')
H('3.4 The base scenario with the LRT (2022)', 2)
r22 = srow('AM', '2022'); r22u = srow('AM', '2022', 'unprioritized'); r22p = srow('PM', '2022')
P(f'We add the main route + extension to the service of 2022. Then the LRT demand in the three AM hours on the corridor market is {n(r22["LRT"])} trips with priority ({n(r22u["LRT"])} without). {n(r22[EXT_COL])} of these trips use the extension. '
  f'{n(r22["LRT from car"])} come from the car and {n(r22["LRT from bus/BRT"])} from the bus and the Metronit. The public transport share of the corridor market increases from {pct(r22["transit before"] / (r22["car before"] + r22["transit before"]) * 100, 1)} to {pct(r22["total transit"] / (r22["car"] + r22["total transit"]) * 100, 1)}.')
P(f'PM: {n(r22p["LRT"])} ({pct(r22p["LRT"] / r22["LRT"] * 100)} of the AM). In the peak hour: {n(r22["LRT"] * fA)} AM and {n(r22p["LRT"] * fP)} PM.')
P('The uncertainty experiment (step 40) and the ranges of step 31 put the 2022 capture between 0.75 × and 1.4 × the central value. The effects are: λ 0.02 → +40 %, λ 0.05 → −25 %; premium 0 → −20 %, premium 10 → +25 %. '
  'The regime (run time) is worth approximately 20 % (without priority against with priority), the same order as the λ range.')
fig(f'{FIG}/lrt_capture_tornado.png', 14, 'Figure 3.7 — Sensitivity of the 2022 capture to the assumed factors (step 40).')
fig(f'{FIG}/alternatives/single/map_line_loads_AM_2022_zoom.png', 12, 'Figure 3.8z — The line loads of 2022, zoom on the extension (Tirat Carmel – Hamifrats).')
fig(f'{FIG}/alternatives/single/map_line_loads_AM_2022.png', 15, 'Figure 3.8 — Line loads and station boardings in the peak hour, AM 2022, main route + extension, Prioritized.')
H('3.5 What the model is good for, and what it must not be used for', 2)
P('Good for:', bold=True)
for s_ in ['The size and the location of the corridor market by mode (which areas, which stations), in the three peak hours and in the design hour.',
           'The rank of alternatives and regimes: through line against extension only, with priority against without priority. The order of magnitude of the shift from the bus, the Metronit and the car.',
           'The growth of the market in the demographic scenarios, with a constant behaviour.',
           'Relative statements about the line profile: where the load is maximum, how the directions differ, which part of the line demand uses the extension.']:
    B(s_)
P('Not for:', bold=True)
for s_ in ['Passenger loads for decisions on capacity, fleet or frequency, or for an economic appraisal. The quantities are not validated at the link level by an external source. The loads are potential movements in three hours between the stations with the lowest access cost, without a capacity limit or crowding.',
           'A statement that depends on the absolute car time or on the congestion in 2040 / 2050. The pivot cancels the car cost (caveat 25). The matrices use the speeds of May 2026 in each year. The forecast has no change of roads, service or car ownership. The sensitivity with slower buses (4.9) gives a limit for the public transport side (+2–5 %). The car side has no limit in this model.',
           'The exact split between "from the car" and "from public transport". The trips from the car depend on the aggregation level of the pivot (caveat 27). λ for car owners is not identified (caveat 15). Between the AM forecast scenarios, the car column is not comparable (caveat 29).',
           'Detail for one TAZ. Below the area level, the matrices are an allocation of the survey trips with weights, not observations.',
           'The operation of the main route. Its stations, the run at 80 km/h at street level and the headway of 5 minutes are assumptions (caveat 28). The continuation at Hamifrats without a transfer is also an assumption.']:
    B(s_)
P('The full list of caveats (29 items) is in chapter 8 of METHODOLOGY.md and in section 3.5 of the English report.')

# ======================= 4 =======================
H('4. The results: the scenarios of 2040 and 2050')
P('2050 BU is the main reference scenario: the plan year 2050 with the usual demographics. The year 2040 and the high scenario are growth sensitivities. '
  'The high scenario also changes the composition of the market (section 4.3). Thus the plan uses the reference scenario, and the high scenario is the upper value of the growth.', bold=True)
P('All results in this chapter are for the through line (Tirat Carmel – Hamifrats – Nazareth) in the "Prioritized" regime of the extension. '
  'The market is the corridor market (pairs of the 174 TAZs in different areas), in periods of three hours. The tables give the totals for three hours with the peak hour values beside them. All charts and maps show the peak hour.')
P('The peak hour factors are the share of the three hours in the busiest 60 minutes of the survey departures. The method is that of step 27, on the two windows. '
  'The line loads use the network bus factor of the direction (AM 0.55 direction Nazareth / 0.46 direction Tirat Carmel; PM 0.54 / 0.47). The totals use the factor of the study area (public transport AM 0.59 / PM 0.48). '
  'The factors observed in RavKav and in the counts are lower (0.38–0.48). Thus the peak hour values here are the upper value.')
H('4.1 Through line to Nazareth against a terminal of the extension at Hamifrats', 2)
P('We ran the two alternatives on the same matrices and the same base. The first alternative is the extension alone: 24 stations, terminal at Hamifrats. The second alternative is the through line: the extension plus the 20 stations of the main route, one line without a transfer at Hamifrats. '
  '"Extension passengers" are all the passengers of the extension-only line. On the through line, they are the passengers that use at least one segment between S01 and S24. The loads are for one direction in the AM peak hour.')
for p, lab in [('AM', 'AM'), ('PM', 'PM')]:
    tt = through_table(p, REF); tt.columns = ['Alternative', 'Extension passengers (3 h)', 'All LRT passengers (3 h)', 'All LRT passengers (peak hour)', 'Maximum load on the extension (peak hour, one direction)', 'Maximum load on the line (peak hour)', 'From the car (3 h)', 'Difference']
    tt['Alternative'] = ['Extension only (terminal at Hamifrats)', 'Through line (main route + extension)']; tt['Difference'] = ['–', tt['Difference'].iloc[1].replace('extension riders', 'extension passengers').replace('total LRT', 'all LRT')]
    table(tt, {'Difference': '{}'}, font=8); CAP(f'Table 4.{1 if p == "AM" else 2} — {lab}, 2050 BU: extension only against the through line, Prioritized.')
rows = []
for sc in ['2022'] + SCEN:
    m_, e_ = srow('AM', sc), ext_row('AM', sc)
    rows.append({'Scenario': SCEN_LAB[sc], 'Extension only: passengers': e_['LRT'], 'Through line: passengers who use the extension': m_[EXT_COL], 'Gain on the extension': (m_[EXT_COL] / e_['LRT'] - 1) * 100,
                 'Through line: all passengers': m_['LRT'], 'Gain on the line': (m_['LRT'] / e_['LRT'] - 1) * 100, 'Extension only: maximum load': busiest('AM', sc, 'ext', peak=True), 'Through line: maximum load on the extension': busiest('AM', sc, 'main_ext', ext_only_segments=True, peak=True), 'Through line: maximum load on the line': busiest('AM', sc, 'main_ext', peak=True)})
table(pd.DataFrame(rows), {'Gain on the extension': '{:+.0f} %', 'Gain on the line': '{:+.0f} %'}, font=8); CAP('Table 4.2a — The same comparison for each scenario year: AM three hours and AM peak hour loads.')
P(f'What this means. The through line does not add passengers to the extension in this model: {n(ext_use)} against {n(refE["LRT"])} ({sgn((ext_use / refE["LRT"] - 1) * 100)}) in 2050 BU. '
  f'The {n(cross)} trips that cross Hamifrats on the through line ({pct(cross / ref["LRT"] * 100)} of its passengers) also exist with a terminal at Hamifrats. '
  'In that case, they go to the Hamifrats station of the extension with a Metronit or bus feeder. There they get on the LRT at S24. The through line replaces the feeder leg with an LRT leg for the same trips.')
P(f'The +{(ref["LRT"] / refE["LRT"] - 1) * 100:.0f} % on the full line is the market of the main route (trips between its stations and Hamifrats, {n(ref["LRT"] - ext_use)} trips). '
  'A main route with a terminal at Hamifrats also carries this market. It is not a benefit of the through line.')
P('What the through line gives, in the terms of the model, is the transfer that it removes for the trips that cross Hamifrats. We did not run a main route with a terminal at Hamifrats beside an extension with a terminal there. '
  'That case puts the transfer penalty of 8 minutes (plus a second wait) on each trip that crosses. With λ_T = 0.06, this is approximately a third of the odds of the LRT path on these pairs against the Metronit. Today the Metronit operates through Hamifrats without a transfer.')
P('Thus the reference numbers depend on caveat 28: no transfer at Hamifrats, a headway of 5 minutes, 80 km/h on the main route. The passengers of the extension do not depend on it.')
H('4.2 The shift to the LRT and the demand by mode', 2)
landscape()
for p, lab in [('AM', 'AM 06:00–09:00'), ('PM', 'PM 16:00–19:00')]:
    t = tabs[(p, REG)]
    P(f'Table 4.{3 if p == "AM" else 4} — {lab}: the shift to the LRT and the demand by mode after the LRT, main route + extension, Prioritized (trips in three hours).', bold=True)
    a = pd.DataFrame({'Scenario': t['scenario'], 'Car before': t['car before'], 'Bus before': t['bus before'], 'Metronit before': t['BRT before'], 'Public transport before': t['transit before'], 'Car → public transport': t['car → transit'], 'Car → LRT': t['car → LRT'], 'Metronit → LRT': t['BRT → LRT'], 'Bus → LRT': t['bus → LRT'],
                      'Car → public transport (% of car)': t['car → transit'] / t['car before'] * 100, 'Metronit → LRT (% of Metronit)': t['BRT → LRT'] / t['BRT before'] * 100, 'Bus → LRT (% of bus)': t['bus → LRT'] / t['bus before'] * 100})
    table(a, {'Car → public transport (% of car)': '{:.2f} %', 'Metronit → LRT (% of Metronit)': '{:.1f} %', 'Bus → LRT (% of bus)': '{:.1f} %'}, font=7)
    P('Demand after the LRT and the share of each mode (of car + public transport on the corridor market):', italic=True)
    b = pd.DataFrame({'Scenario': t['scenario'], 'Car after': t['car after'], 'Metronit after': t['BRT after'], 'LRT': t['LRT'], 'LRT in the peak hour': t['LRT (peak hour)'], 'Bus after': t['bus after'], 'Public transport after': t['total transit after'],
                      'Car share': t['car share'] * 100, 'Metronit share': t['BRT share'] * 100, 'LRT share': t['LRT share'] * 100, 'Bus share': t['bus share'] * 100, 'Public transport share': t['transit share'] * 100, 'LRT share of public transport': t['LRT share of transit'] * 100})
    if summary_slow is not None: b['LRT, slower buses (sensitivity)'] = [srow(p, sc, REG, src=summary_slow)['LRT'] if sc in SLOW_FACTORS else np.nan for sc in ['2022'] + SCEN]
    table(b, {c: '{:.1f} %' for c in ['Car share', 'Metronit share', 'LRT share', 'Bus share', 'Public transport share', 'LRT share of public transport']}, font=7)
    P('The part of the extension, as a part of the through line:', italic=True)
    c = pd.DataFrame({'Scenario': t['scenario'], 'LRT': t['LRT'], 'Use the extension': t['LRT using the extension'], 'Use the extension, peak hour': t['LRT using the extension (peak hour)'], 'Of these: from the car': t['ext: from car'], 'From the Metronit': t['ext: from BRT'], 'From the bus': t['ext: from bus'], 'Only between extension stations': t['LRT within the extension'],
                      'Extension share of the LRT trips': t['LRT using the extension'] / t['LRT'] * 100, 'Busiest segment (3 h, one direction)': t['busiest segment (3 h, one direction)'], 'Busiest segment (peak hour)': t['busiest segment (peak hour, one direction)']})
    table(c, {'Extension share of the LRT trips': '{:.1f} %'}, font=7); doc.add_paragraph()
portrait()
P('How to read the tables. "Before" is the no-build market of the scenario (car, bus with rail, Metronit) on the pairs of corridor TAZs. "Car → public transport" is the trips that the decrease of the total cost moves out of the car. '
  '"Car → LRT" is the part of these trips that the LRT carries. The other trips move to the bus or Metronit path of the pair.')
P('"Metronit → LRT" and "Bus → LRT" are the LRT trips that come from the public transport of today. They come from the pairs with a Metronit path or a bus path. The three LRT columns add up to the LRT total. The taxi trips (approximately 700) do not change and are not in the shares.')
P('Note on the car column. The AM shift from the car doubles between 2040 BU and 2050 BU (684 → 1,421) and between 2040 BU and 2040 HS (684 → 1,387). The market increases by only 16 % and 4 %. This is not a demand effect but an aggregation effect (caveat 29).')
P('The shift in each pair is proportional to S·(1−S) of its public transport share. The forecast matrices put trips into pairs that are empty in 2022. Thus the number of pairs with both car trips and public transport trips increases from 1,620 to 5,688.')
P('The PM matrices increase pair by pair from the PM base. They keep the pairs of 2022 and show a smooth car column. Read the shift from the car as an order of magnitude (300–1,300 trips, 0.4–1.5 % of the car trips on the corridor). Do not compare it between scenarios.')
fig(f'{CFIG}/demand_by_scenario_AM.png', 12, 'Figure 4.1a — Public transport demand on the corridor by scenario, AM peak hour. The bars: public transport without the LRT, public transport after the LRT, the LRT trips, the LRT trips that use the extension. Same scale as 4.1b.')
fig(f'{CFIG}/demand_by_scenario_PM.png', 12, 'Figure 4.1b — The same for the PM peak hour.')
fig(f'{CFIG}/shift_sources_AM.png', 12, 'Figure 4.2a — The source of the LRT passengers (car, Metronit, bus) by scenario, AM peak hour: the full line, the part that uses the extension. Same scale as 4.2b.')
fig(f'{CFIG}/shift_sources_PM.png', 12, 'Figure 4.2b — The same for the PM peak hour.')
H('4.3 The source of the demand: the markets', 2)
P('The tables group the LRT trips of the reference scenario by the corridor areas of their two ends (the two directions together). Table 4.7 gives the ten largest pairs of areas. "Haifa" is Matam to Hamifrats (areas 202–210). '
  'The Krayot (101–104, 301–304) are not on the line; they reach the line with a bus or Metronit feeder. The main route is Bazan-Hutsot to Nazareth (211–217). '
  '"Cross Hamifrats" is the load on segment S24–M02 in the two directions: each trip from one side of the junction to the other side.')
MK_STE = {'Haifa internal (both ends Matam – Hamifrats)': 'Inside Haifa (the two ends between Matam and Hamifrats)', 'Tirat Carmel ↔ Haifa': 'Tirat Carmel ↔ Haifa', 'Krayot ↔ Haifa (Krayot by feeder)': 'Krayot ↔ Haifa (the Krayot with a feeder)', 'Main route (Kiryat Ata – Nazareth) ↔ Haifa': 'Main route (Kiryat Ata – Nazareth) ↔ Haifa',
          'Main route ↔ Krayot / Tirat Carmel': 'Main route ↔ Krayot / Tirat Carmel', 'within the main route': 'Inside the main route', 'Krayot ↔ Tirat Carmel': 'Krayot ↔ Tirat Carmel', 'crossing Hamifrats (ride the S24–M02 segment)': 'Cross Hamifrats (use segment S24–M02)', 'purely extension to extension (both ends at S01–S24)': 'Only between extension stations (the two ends at S01–S24)', 'using the extension at all': 'Use the extension (at least one segment)'}
for sc in [REF, 'HS_2050']:
    ms, tot = market_summary('AM', sc); ms = pd.DataFrame({'Market': [MK_STE[m] for m in ms['market']], 'LRT trips (3 h)': ms['LRT trips (3 h)'], 'Share of all LRT trips': ms['share of all LRT trips']})
    table(ms, {'Share of all LRT trips': '{:.0f} %'}, font=8); CAP(f'Table 4.{5 if sc == REF else 6} — The markets of the LRT trips, AM three hours, {SCEN_LAB[sc]} (total {n(tot)}).')
sym, tot, top_df = market_tables('AM', REF); top_df.columns = ['Rank', 'Pair of areas (the two directions)', 'LRT trips (3 h)', 'Share of all LRT trips']
table(top_df, {'Share of all LRT trips': '{:.1f} %'}, font=8); CAP('Table 4.7 — The ten largest pairs of areas of the LRT trips, AM three hours, 2050 BU. The area names are the English names of the aggregation file.')
P(f'What this means. In 2050 BU, the market has three parts of almost the same size. They are Tirat Carmel ↔ Haifa ({pct(mk_ref.iloc[1]["share of all LRT trips"])}), inside Haifa ({pct(mk_ref.iloc[0]["share of all LRT trips"])}) and the Krayot with a feeder to Haifa ({pct(mk_ref.iloc[2]["share of all LRT trips"])}). '
  f'The areas of the main route add {pct(mk_ref.iloc[3]["share of all LRT trips"])} with Haifa, and some percent between them. {pct(mk_ref.iloc[7]["share of all LRT trips"])} of the trips cross Hamifrats, and {pct(mk_ref.iloc[8]["share of all LRT trips"])} stay between extension stations. Tirat Carmel – Bat Galim is the largest pair.')
P('The scenario 2050 HS reads differently: inside Haifa a third, Tirat Carmel a tenth. The high scenario moves population and jobs to the Haifa areas, and it puts trips into pairs that are empty today (caveat 29). '
  'Thus the composition, not only the total, depends on the scenario. This is one more reason to plan with the BU reference scenario.')
H('4.4 What occurs to the Metronit', 2)
P('The model keeps each bus line and each Metronit line as it operates today (timetable of June 2026) in each scenario year. It adds the LRT as a new path. No line is removed.')
P(f'In 2050 BU, {n(ref_brt_shift)} trips move from the Metronit ({pct(ref_brt_shift / ref["BRT before"] * 100)} of the Metronit trips on the corridor). '
  'These are passengers on pairs where the best public transport path today is the Metronit, and where the LRT path has a lower generalized cost. '
  f'The cause is a faster run on the trunk, a station nearer to the ends, or both. They select the LRT, while the Metronit continues to operate beside it. The other {n(ref["BRT (Metronit)"])} Metronit trips stay, because their path is still the cheaper one.')
P('Four conclusions for the numbers:')
for s_ in ['The LRT and the Metronit operate together in the model on all the trunk from Hof HaCarmel to the Krayot. Most LRT passengers are the public transport passengers of today in a better vehicle. The public transport market increases only by the shift from the car: some hundreds to approximately one thousand trips in three hours. The LRT replaces current public transport capacity on the trunk much more than it makes a new market.',
           f'A part of the shift "from the Metronit" and "from the bus" is only a change of vehicle on one leg of the trip. It is not a new public transport trip. The LRT path can start or end with a Metronit or bus feeder (penalty 4 / 8 minutes). Such a trip counts as an LRT trip. The Krayot market ({n(mk_ref.iloc[2]["LRT trips (3 h)"])} trips) is almost all of this type: Metronit passengers who transfer to the LRT at Hamifrats or on the trunk. Thus a passenger count for the LRT is a count of boardings, not a count of trips that exist only because of the LRT.',
           f'The Metronit service can decrease on the common section after the line opens. Then the passengers that the Metronit keeps in the model (the pairs where it is cheaper) must move to the LRT or to the bus. The LRT loads on the trunk increase, up to a maximum: the Metronit trips on the corridor before the LRT ({n(ref["BRT before"])} in 2050 BU, AM). The opposite case, a new feeder structure that brings the Metronit lines to the LRT stations, improves the access quality and the attraction. We did not model these two cases. The numbers of the report are for the case where the two operate together, the conservative case for the LRT.',
           'The decision that the LRT and the Metronit operate together on the trunk is a decision of the network plan, outside this study. It changes the LRT loads by up to the Metronit volume on the trunk. This is more than each demand uncertainty in this report. Make this decision before you use the numbers for capacity.']:
    B(s_)
H('4.5 The flow along the line: LRT, the two directions', 2)
P('Passengers on each segment of the line in the peak hour, by direction: direction Nazareth (S01 → S24 → M20) and direction Tirat Carmel (M20 → M01 → S01). The dashed line shows the junction of the extension (S24) with the main route (M01, the same station at Hamifrats).')
landscape()
P('All charts in this section use the same vertical scale (' + f'{YMAX["lrt"]:,.0f}' + ' passengers in the peak hour). Thus you can compare the scenarios by eye. There is one chart for each scenario and period with the two directions. Then there is one chart for each direction with the four forecast scenarios side by side.')
k_ = 3
DIR_STE = {'dir1': 'direction Nazareth', 'dir2': 'direction Tirat Carmel'}
for p in ['AM', 'PM']:
    for sc in SCS:
        fig(f'{CFIG}/flow_lrt_{p}_{sc}.png', 25, f'Figure 4.{k_} — LRT flow by segment and direction, {SCEN_LAB[sc]}, {p} peak hour.'); k_ += 1
    for (col, lab2, _), tag in zip(DIRS, ('dir1', 'dir2')):
        fig(f'{CFIG}/flow_lrt_{p}_scenarios_{tag}.png', 25, f'Figure 4.{k_} — LRT flow by segment, {DIR_STE[tag]}, the four scenarios, {p} peak hour.'); k_ += 1
P('The same flows between the corridor areas along the line. Each bar is the load on the segment from one area to the next area (Tirat Carmel → Matam … Hamovil → Nazareth), in the peak hour. One vertical scale (' + f'{AYMAX["lrt"]:,.0f}' + ') applies to all area charts in the section. The area names are the English names of the aggregation file.')
for p in ['AM', 'PM']:
    for sc in SCS:
        fig(f'{CFIG}/areaflow_lrt_{p}_{sc}.png', 25, f'Figure 4.{k_} — LRT flow between the corridor areas, {SCEN_LAB[sc]}, {p} peak hour.'); k_ += 1
    for (col, lab2, _), tag in zip(DIRS, ('dir1', 'dir2')):
        fig(f'{CFIG}/areaflow_lrt_{p}_scenarios_{tag}.png', 25, f'Figure 4.{k_} — LRT flow between the corridor areas, {DIR_STE[tag]}, the four scenarios, {p} peak hour.'); k_ += 1
H('4.6 The flow along the line: all public transport, the two directions', 2)
P('The same profile for all public transport trips of the corridor market: bus, Metronit and LRT after the LRT is added. The trips are loaded along the line between the LRT stations nearest to their ends. '
  'This is the public transport demand that the corridor of the line carries. The LRT takes the share of it that section 4.2 shows.')
P('Same structure and same rule: one vertical scale (' + f'{YMAX["transit"]:,.0f}' + ' passengers in the peak hour) for all charts in the section.')
for p in ['AM', 'PM']:
    for sc in SCS:
        fig(f'{CFIG}/flow_transit_{p}_{sc}.png', 25, f'Figure 4.{k_} — All public transport flow by segment and direction, {SCEN_LAB[sc]}, {p} peak hour.'); k_ += 1
    for (col, lab2, _), tag in zip(DIRS, ('dir1', 'dir2')):
        fig(f'{CFIG}/flow_transit_{p}_scenarios_{tag}.png', 25, f'Figure 4.{k_} — All public transport flow by segment, {DIR_STE[tag]}, the four scenarios, {p} peak hour.'); k_ += 1
P('The same between the corridor areas (one vertical scale, ' + f'{AYMAX["transit"]:,.0f}' + ', for all area charts in the section).')
for p in ['AM', 'PM']:
    for sc in SCS:
        fig(f'{CFIG}/areaflow_transit_{p}_{sc}.png', 25, f'Figure 4.{k_} — All public transport flow between the corridor areas, {SCEN_LAB[sc]}, {p} peak hour.'); k_ += 1
    for (col, lab2, _), tag in zip(DIRS, ('dir1', 'dir2')):
        fig(f'{CFIG}/areaflow_transit_{p}_scenarios_{tag}.png', 25, f'Figure 4.{k_} — All public transport flow between the corridor areas, {DIR_STE[tag]}, the four scenarios, {p} peak hour.'); k_ += 1
portrait()
H('4.7 The mode split on the route', 2)
P('The split of the corridor market between the car and public transport after the LRT, by scenario and period. The LRT is shown inside public transport.')
fig(f'{CFIG}/mode_split_AM.png', 12, 'Figure 4.11a — The mode split on the corridor after the LRT: car, bus, Metronit and LRT, AM.')
fig(f'{CFIG}/mode_split_PM.png', 12, 'Figure 4.11b — The same for the PM.')
H('4.8 Sensitivity: the regime without priority', 2)
rows = []
for p in ['AM', 'PM']:
    for sc in SCEN:
        a_, b_ = srow(p, sc, 'prioritized'), srow(p, sc, 'unprioritized')
        rows.append({'Period': p, 'Scenario': SCEN_LAB[sc], 'LRT with priority': a_['LRT'], 'LRT without priority': b_['LRT'], 'Ratio': b_['LRT'] / a_['LRT'], 'Use the extension, with': a_[EXT_COL], 'Use the extension, without': b_[EXT_COL], 'From the car, with': a_['LRT from car'], 'From the car, without': b_['LRT from car']})
table(pd.DataFrame(rows), {'Ratio': '{:.2f}'}, font=8); CAP('Table 4.8 — LRT trips in the two regimes of the extension. The regime without priority (run at street level) loses approximately a fifth to a quarter of the trips, most of them on the extension. Its end-to-end time on the extension is 65.8 minutes against 40.7.')
H('4.9 Sensitivity: slower buses in 2040 and 2050', 2)
P('Each scenario year runs on the level of service of May 2026. Two conclusions follow. First, a slower car does not change the result in this model. The pivot moves trips only with the change of the public transport "bundle". The car level enters with the shares observed in 2022 (caveat 25).')
P('Second, slower buses do count. A bus in mixed traffic that becomes slower with the road increases the bus cost. The Metronit on its lanes and the LRT with priority keep their times. Thus the central assumption is conservative for the LRT.')
P('The sensitivity: we ran step 45 again with slower buses. We multiply the run time of each bus trip, except the Metronit, by 1.10 in 2040 and by 1.20 in 2050 (BU and HS). The Metronit and the LRT do not change. The bus feeder legs of the LRT paths become slower with the buses. '
  'The factors come from a usual volume-delay curve for a road demand that increases by 1.3–1.6 × from approximately 80 % of capacity. They are not calibrated values.')
if summary_slow is not None:
    rows = []
    for p in ['AM', 'PM']:
        for sc in SCEN:
            a_, b_ = srow(p, sc, REG), srow(p, sc, REG, src=summary_slow)
            rows.append({'Period': p, 'Scenario': SCEN_LAB[sc], 'Bus factor': SLOW_FACTORS[sc], 'LRT central': a_['LRT'], 'LRT, slower buses': b_['LRT'], 'Ratio': b_['LRT'] / a_['LRT'], 'From the car, central': a_['LRT from car'], 'From the car, slower': b_['LRT from car'], 'Use the extension, central': a_[EXT_COL], 'Use the extension, slower': b_[EXT_COL]})
    sens = pd.DataFrame(rows); table(sens, {'Bus factor': '{:.2f}', 'Ratio': '{:.2f}'}, font=8); sA = sens[sens['Period'] == 'AM']
    CAP(f'Table 4.9 — LRT trips with slower buses against the central case. AM: the LRT gains {sgn((sA["Ratio"].min() - 1) * 100)} to {sgn((sA["Ratio"].max() - 1) * 100)}. The gain is small, because the in-vehicle time of a bus is much less than half of its generalized cost. The walk and the wait have weight 2, and there is the transfer penalty. Also the feeders of the LRT become slower.')
H('4.10 Time on the route', 2)
P('The through line operates in 74.3 minutes with priority and 99.6 minutes without priority, from Tirat Carmel to Nazareth. The extension takes 40.7 / 65.8 minutes. The main route takes 33.7 minutes at 80 km/h with a stop of 10 seconds. '
  'Metronit line 1, end to end: 65 minutes in the timetable, 57 minutes in operation. Train: Hof HaCarmel – Kiryat Motzkin, 30–31 minutes. Car between the corridor areas: the speeds of May 2026 plus 3 minutes (the full table is in the English report, Table 4.10).')
H('4.11 Maps', 2)
P('The full set of maps (41 maps: line loads, origins and destinations, LRT share, growth, sources of the shift, travel times) is in Output/figures/alternatives/. Four types of map are here.')
P('One map for each scenario. All maps have the same width scale (the maximum of 2050 HS) and the same scale for the boarding circles. After each map, there is a zoom on the extension (Tirat Carmel – Hamifrats), with the same scale.')
k_ = 12
for sc in SCEN:
    fig(f'{FIG}/alternatives/single/map_line_loads_AM_{sc}.png', 15, f'Figure 4.{k_} — LRT line loads and station boardings in the AM peak hour, {SCEN_LAB[sc]}, main route + extension, Prioritized.'); fig(f'{FIG}/alternatives/single/map_line_loads_AM_{sc}_zoom.png', 12, f'Figure 4.{k_}z — The same map, zoom on the extension.'); k_ += 1
fig(f'{FIG}/alternatives/single/map_line_loads_PM_BU_2050.png', 15, f'Figure 4.{k_} — The same for the PM peak hour, 2050 BU.'); fig(f'{FIG}/alternatives/single/map_line_loads_PM_BU_2050_zoom.png', 12, f'Figure 4.{k_}z — The same map, zoom on the extension.'); k_ += 1
P('The growth of the origins of the LRT trips by TAZ, from 2022 to each scenario: one map for each scenario, with one colour scale.')
for sc in SCEN:
    fig(f'{FIG}/alternatives/single/map_growth_AM_{sc}.png', 15, f'Figure 4.{k_} — Growth of the origins of the LRT trips by TAZ, 2022 → {SCEN_LAB[sc]}, AM peak hour.'); fig(f'{FIG}/alternatives/single/map_growth_AM_{sc}_zoom.png', 12, f'Figure 4.{k_}z — The same map, zoom on the extension.'); k_ += 1
P('The sources of the LRT trips by origin TAZ in the reference scenario, one map for each source. The bus map and the Metronit map have one colour scale. The car map has its own scale (its values are an order of magnitude smaller).')
for src_, lab_ in [('car', 'from the car'), ('bus', 'from bus paths'), ('brt', 'from Metronit paths')]:
    fig(f'{FIG}/alternatives/single/map_shift_{src_}_AM_{REF}.png', 15, f'Figure 4.{k_} — LRT trips {lab_} by origin TAZ, 2050 BU, AM peak hour.'); fig(f'{FIG}/alternatives/single/map_shift_{src_}_AM_{REF}_zoom.png', 12, f'Figure 4.{k_}z — The same map, zoom on the extension.'); k_ += 1
P('The generalized cost to the reference destination, the TAZ of the busiest LRT exit station. The maps show the best bus or Metronit path today and the LRT, with one colour scale, then their difference.')
for m_, lab_ in [('bus', 'The best bus or Metronit path, without the LRT'), ('lrt', 'The LRT, main route + extension, Prioritized'), ('diff', 'The LRT minus the bus (negative = the LRT is cheaper)')]:
    fig(f'{FIG}/alternatives/single/map_time_{m_}_AM.png', 15, f'Figure 4.{k_} — {lab_}: felt minutes from each TAZ, AM.'); fig(f'{FIG}/alternatives/single/map_time_{m_}_AM_zoom.png', 12, f'Figure 4.{k_}z — The same map, zoom on the extension.'); k_ += 1

# ======================= 5 =======================
H('5. Conclusions')
tA = tabs[('AM', REG)].set_index('scenario'); lo, hi = tA.loc['2040 BU'], tA.loc['2050 HS']
for s_ in [f'Reference case. 2050 BU: {n(ref["LRT"])} LRT passengers in the three AM hours ({n(ref["LRT"] * fA)} in the peak hour). The range for the plan is {n(ref["LRT"] * RANGE_LO)}–{n(ref["LRT"] * RANGE_HI)} with the cost sensitivity. {n(ext_use)} passengers use the extension, against {n(refE["LRT"])} if the extension stops at Hamifrats. Three markets have almost the same size (Tirat Carmel ↔ Haifa, inside Haifa, the Krayot with a feeder). The maximum load is {n(peak_line)} for each hour and direction at the entry to Hamifrats.',
           f'Demand. The through line carries {n(lo["LRT"])} trips in the three AM hours in 2040 BU and {n(hi["LRT"])} in 2050 HS. The PM is approximately 85 % of the AM. {pct(ext_use / ref["LRT"] * 100)} of the trips use the extension. The extension is where most passengers of the line are. The main route feeds the extension, not the opposite.',
           f'Sources. The LRT is first a new organisation of public transport. {n(lo["BRT → LRT"])}–{n(hi["BRT → LRT"])} trips come from the Metronit (approximately a third of its corridor trips). {n(lo["bus → LRT"])}–{n(hi["bus → LRT"])} come from the bus, and {n(lo["car → LRT"])}–{n(hi["car → LRT"])} from the car (approximately one percent of the car trips on the corridor). The public transport share of the corridor market increases by approximately one point. The LRT takes approximately a third to two fifths of public transport.',
           'Profile. In the AM, the busiest segment is the entry to Hamifrats from the main route (S24–M02), direction Tirat Carmel. It carries approximately 1,000 to 1,400 passengers in the peak hour. In the direction Nazareth, the maximum is on the Carmel coast (S14–S15, 770–1,050). In the PM, the two directions are almost in balance. The main route after Kiryat Ata carries some hundreds in each direction, and the extension carries four of each five passengers.',
           'Growth. Between 2040 BU and 2050 HS, the LRT demand increases by approximately 45 %. This is the rate of the public transport market on the corridor, because the forecast keeps the behaviour of 2022. The high scenario adds 15–25 % to the BU scenario in the same year.',
           'Regime. Priority at the junctions is worth approximately 20–25 % of the LRT trips. A run at street level increases the time on the extension from 41 to 66 minutes. It loses approximately a quarter of the passengers, most of them on the extension.',
           'Robustness. The central numbers are in a range of approximately −25 % / +40 % from the cost sensitivity and the LRT premium alone. The level of service stays at May 2026 in each year, and slower buses give the LRT 2–5 % more in the AM. Thus the central case is conservative for the LRT. The shift from the car is the least certain part (caveats 15, 25, 27, 29); read it as an order of magnitude. The shifts from the bus and from the Metronit depend on observed shares and measured service; they are the solid part.',
           'Use. The results support the size and the location of the extension market, the rank of the regimes and the scale of the trunk load. They do not support decisions on capacity, fleet or frequency, or an economic appraisal, without a validated assignment and a full mode choice model. The next steps are:']:
    B(s_)
for s_ in ['A split of the survey by purpose.', 'A specific forecast for the PM.', 'The operation plan of the main route.', 'A decision about the future of the Metronit.', 'A λ for car owners from a source that has the car cost.']: B(s_, 2)
P('Documentation: METHODOLOGY.md chapter 6aq (step 45) and chapter 8; docs/PLAIN_ENGLISH_METHODOLOGY.md part 5; the full English report reports/Nofit_LRT_Extension_Comprehensive_Report.docx; the builder of this report tools/build_comprehensive_report_ste.py.', check=False)
# ======================= appendices A–D =======================
import sys; sys.path.insert(0, os.path.join(os.getcwd(), 'tools')); from report_appendices_ste import add_appendices_ste
portrait(); add_appendices_ste(doc, H, P, B, fig, table, CAP)   # tools/report_appendices_ste.py: the LRT time function, out-of-vehicle time, λ, the generalized cost
doc.save('reports/Nofit_LRT_Extension_Comprehensive_Report_STE.docx'); print('STE report written')
print(f'STE self-check: {len(_findings)} finding(s) on the countable rules (25 words per sentence, 6 sentences per paragraph, no -ing forms)')
for f_ in _findings: print('  ' + f_)
