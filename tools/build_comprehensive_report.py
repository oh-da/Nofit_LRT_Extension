"""Build the comprehensive report of the Nofit LRT extension demand study:
   reports/Nofit_LRT_Extension_Comprehensive_Report.docx
   Output/figures/comprehensive/*.png   -- the report's own charts (flows per direction, mode split, shift)
Sections: 1 goal and objectives; 2 model structure, data (with vintages), approach; 3 calibration and base scenario
(results, charts, fitness for use and caveats); 4 results for BU 2040 / BU 2050 / HS 2040 / HS 2050 on the main route +
extension (with the extension part shown within it); 5 conclusions.
Run after notebooks/current/LRT_alternatives_demand.ipynb:  python3 tools/build_comprehensive_report.py"""
import os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.section import WD_ORIENT
while not os.path.exists('METHODOLOGY.md') and os.getcwd() != '/': os.chdir('..')
OUT = 'Output/alternatives'; FIG = 'Output/figures'; CFIG = f'{FIG}/comprehensive'; os.makedirs(CFIG, exist_ok=True)
SCEN = ['BU_2040', 'BU_2050', 'HS_2040', 'HS_2050']; SCEN_LAB = {'2022': '2022', 'BU_2040': '2040 BU', 'BU_2050': '2050 BU', 'HS_2040': '2040 HS', 'HS_2050': '2050 HS'}
ALT, REG = 'main_ext', 'prioritized'; REG_LAB = {'prioritized': 'Prioritized', 'unprioritized': 'Unprioritized'}
summary = pd.read_csv(f'{OUT}/demand_summary.csv'); route = pd.read_csv(f'{OUT}/time_on_route.csv'); skims = pd.read_csv(f'{OUT}/skims_summary.csv')
stations = pd.read_csv(f'{OUT}/stations_main_ext.csv')
xl = pd.ExcelFile('Input/Corridor_TAZ_Agg_V2.xlsx', engine='openpyxl'); names = xl.parse('AreaCodes').set_index('AggCode')['AggAreaName']
def srow(p, sc, reg=REG, alt='Main'):
    s = summary[(summary.period == p) & (summary.scenario == sc) & (summary.alternative.str.startswith(alt)) & (summary.regime.str.startswith(REG_LAB[reg]))]
    assert len(s) == 1, (p, sc, reg, alt); return s.iloc[0]
def loads(p, sc, kind, reg=REG):
    return pd.read_csv(f'{OUT}/{p}/{sc}/{ALT}_{reg}/{kind}_line_loads.csv')
# ---------------- the shift / demand table ----------------
def shift_table(p, reg=REG):
    rows = []
    for sc in ['2022'] + SCEN:
        r = srow(p, sc, reg)
        car0, tr0, brt0 = r['car before'], r['transit before'], r['BRT before']; bus0 = tr0 - brt0
        car1, bus1, brt1, lrt, tr1 = r['car'], r['bus'], r['BRT (Metronit)'], r['LRT'], r['total transit']
        d = f'{OUT}/{p}/{sc}/{ALT}_{reg}/'; from_car = r['LRT from car']
        from_brt = pd.read_csv(d + 'from_brt_area_v2.csv', index_col=0).values.sum(); from_bus = pd.read_csv(d + 'from_bus_area_v2.csv', index_col=0).values.sum()
        tot = car1 + tr1
        rows.append({'scenario': SCEN_LAB[sc],
                     'car before': car0, 'bus before': bus0, 'BRT before': brt0, 'transit before': tr0,
                     'car → transit': car0 - car1, 'car → LRT': from_car, 'BRT → LRT': from_brt, 'bus → LRT': from_bus,
                     'car after': car1, 'BRT after': brt1, 'LRT': lrt, 'bus after': bus1, 'total transit after': tr1,
                     'car share': car1 / tot, 'BRT share': brt1 / tot, 'LRT share': lrt / tot, 'bus share': bus1 / tot, 'transit share': tr1 / tot,
                     'LRT share of transit': lrt / tr1,
                     'LRT using the extension': r['LRT trips using the extension (at least one segment S01–S24)'],
                     'ext: from car': r['LRT from car using the extension'], 'ext: from BRT': r['LRT from BRT using the extension'], 'ext: from bus': r['LRT from bus using the extension'],
                     'LRT within the extension': r['LRT trips on the extension stations (both ends on S01–S24)'],
                     'busiest segment (3 h, one direction)': r['busiest segment load (3 h, one direction)']})
    return pd.DataFrame(rows)
tabs = {(p, reg): shift_table(p, reg) for p in ['AM', 'PM'] for reg in REG_LAB}
# ---------------- charts ----------------
seg_lab = (loads('AM', 'BU_2040', 'lrt')['from_station'] + '–' + loads('AM', 'BU_2040', 'lrt')['to_station']).tolist()
n_ext = int((loads('AM', 'BU_2040', 'lrt')['to_station'].str.startswith('S')).sum())   # 23 extension segments S01–S24 (S24 = M01 at Hamifrats)
st_area = stations.set_index('station_id')
def seg_names(ids):
    out = []
    for s in ids:
        a = st_area.loc[s, 'AggCode']; out.append(f"{s} {names[int(a)] if pd.notna(a) else ''}")
    return out
def flow_chart(p, kind, fname):
    """Line loads per segment, both directions, one panel per scenario (2022 + 4)."""
    scs = ['2022'] + SCEN; fig, axes = plt.subplots(len(scs), 1, figsize=(13, 2.6 * len(scs)), sharex=True)
    for ax, sc in zip(axes, scs):
        l = loads(p, sc, kind); x = np.arange(len(l))
        ax.bar(x - 0.2, l['dir1_towards_Nazareth_end'], 0.4, color='#1f77b4', label='towards Nazareth (S01 → M20)')
        ax.bar(x + 0.2, l['dir2_towards_TiratCarmel'], 0.4, color='#d62728', label='towards Tirat Carmel (M20 → S01)')
        ax.axvline(n_ext - 0.5, color='k', ls='--', lw=0.8); ax.text(n_ext - 0.3, ax.get_ylim()[1] * 0.9 if ax.get_ylim()[1] > 0 else 1, 'extension | main route', fontsize=7, va='top')
        ax.set_ylabel('passengers / 3 h'); ax.set_title(f'{SCEN_LAB[sc]} — {p}', fontsize=9, loc='left'); ax.grid(axis='y', alpha=0.3)
    axes[0].legend(fontsize=8, loc='upper right'); axes[-1].set_xticks(np.arange(len(l))); axes[-1].set_xticklabels(seg_lab, rotation=90, fontsize=6)
    fig.suptitle(f'{"LRT" if kind == "lrt" else "Total transit"} flow by segment and direction — main route + extension, Prioritized, {p} (three hours)', fontsize=11)
    fig.tight_layout(); fig.savefig(f'{CFIG}/{fname}', dpi=150); plt.close(fig)
def flow_chart_compact(p, kind, fname):
    """All four forecast scenarios on one pair of panels (one per direction)."""
    fig, axes = plt.subplots(2, 1, figsize=(13, 7), sharex=True); cols = {'BU_2040': '#9ecae1', 'BU_2050': '#3182bd', 'HS_2040': '#fdae6b', 'HS_2050': '#e6550d'}
    for ax, (d, lab) in zip(axes, [('dir1_towards_Nazareth_end', 'towards Nazareth (S01 → M20)'), ('dir2_towards_TiratCarmel', 'towards Tirat Carmel (M20 → S01)')]):
        for i, sc in enumerate(SCEN):
            l = loads(p, sc, kind); x = np.arange(len(l)); ax.bar(x + (i - 1.5) * 0.2, l[d], 0.2, color=cols[sc], label=SCEN_LAB[sc])
        ax.axvline(n_ext - 0.5, color='k', ls='--', lw=0.8); ax.set_ylabel('passengers / 3 h'); ax.set_title(lab, fontsize=9, loc='left'); ax.grid(axis='y', alpha=0.3)
    axes[0].legend(fontsize=8, ncol=4); axes[-1].set_xticks(np.arange(len(l))); axes[-1].set_xticklabels(seg_lab, rotation=90, fontsize=6)
    fig.suptitle(f'{"LRT" if kind == "lrt" else "Total transit"} flow by segment — the four scenarios, main route + extension, Prioritized, {p} (three hours)', fontsize=11)
    fig.tight_layout(); fig.savefig(f'{CFIG}/{fname}', dpi=150); plt.close(fig)
for p in ['AM', 'PM']:
    flow_chart(p, 'lrt', f'flow_lrt_{p}.png'); flow_chart(p, 'transit', f'flow_transit_{p}.png')
    flow_chart_compact(p, 'lrt', f'flow_lrt_scenarios_{p}.png'); flow_chart_compact(p, 'transit', f'flow_transit_scenarios_{p}.png')
def mode_split_chart(fname):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, p in zip(axes, ['AM', 'PM']):
        t = tabs[(p, REG)]; x = np.arange(len(t)); w = 0.6
        ax.bar(x, t['car share'] * 100, w, color='#7f7f7f', label='car')
        ax.bar(x, t['bus share'] * 100, w, bottom=t['car share'] * 100, color='#aec7e8', label='bus')
        ax.bar(x, t['BRT share'] * 100, w, bottom=(t['car share'] + t['bus share']) * 100, color='#1f77b4', label='BRT (Metronit)')
        ax.bar(x, t['LRT share'] * 100, w, bottom=(t['car share'] + t['bus share'] + t['BRT share']) * 100, color='#2ca02c', label='LRT')
        for i, r in t.iterrows():
            ax.text(i, 101, f"transit {r['transit share']*100:.1f} %\nLRT {r['LRT share']*100:.1f} %", ha='center', va='bottom', fontsize=7)
        ax.set_xticks(x); ax.set_xticklabels(t['scenario']); ax.set_ylim(0, 115); ax.set_ylabel('% of car + transit trips'); ax.set_title(f'{p} — mode split on the corridor (174 TAZs) after the LRT', fontsize=10); ax.grid(axis='y', alpha=0.3)
    axes[0].legend(loc='lower left', fontsize=8); fig.tight_layout(); fig.savefig(f'{CFIG}/{fname}', dpi=150); plt.close(fig)
mode_split_chart('mode_split.png')
def demand_bars(fname):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, p in zip(axes, ['AM', 'PM']):
        t = tabs[(p, REG)]; x = np.arange(len(t)); w = 0.2
        ax.bar(x - 1.5 * w, t['transit before'], w, color='#c7c7c7', label='transit before (no LRT)')
        ax.bar(x - 0.5 * w, t['total transit after'], w, color='#1f77b4', label='total transit after')
        ax.bar(x + 0.5 * w, t['LRT'], w, color='#2ca02c', label='LRT (main + extension)')
        ax.bar(x + 1.5 * w, t['LRT using the extension'], w, color='#98df8a', label='LRT using the extension')
        ax.set_xticks(x); ax.set_xticklabels(t['scenario']); ax.set_ylabel('trips / 3 h'); ax.set_title(f'{p} — transit demand on the corridor', fontsize=10); ax.grid(axis='y', alpha=0.3)
    axes[0].legend(fontsize=8); fig.tight_layout(); fig.savefig(f'{CFIG}/{fname}', dpi=150); plt.close(fig)
demand_bars('demand_by_scenario.png')
def shift_chart(fname):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, p in zip(axes, ['AM', 'PM']):
        t = tabs[(p, REG)]; x = np.arange(len(t)); w = 0.35
        ax.bar(x - w / 2, t['car → LRT'], w, color='#7f7f7f', label='from car (whole line)'); ax.bar(x - w / 2, t['BRT → LRT'], w, bottom=t['car → LRT'], color='#1f77b4', label='from BRT (Metronit)')
        ax.bar(x - w / 2, t['bus → LRT'], w, bottom=t['car → LRT'] + t['BRT → LRT'], color='#aec7e8', label='from bus')
        ax.bar(x + w / 2, t['ext: from car'], w, color='#7f7f7f', alpha=0.5, hatch='//', label='… of which using the extension'); ax.bar(x + w / 2, t['ext: from BRT'], w, bottom=t['ext: from car'], color='#1f77b4', alpha=0.5, hatch='//')
        ax.bar(x + w / 2, t['ext: from bus'], w, bottom=t['ext: from car'] + t['ext: from BRT'], color='#aec7e8', alpha=0.5, hatch='//')
        ax.set_xticks(x); ax.set_xticklabels(t['scenario']); ax.set_ylabel('LRT trips / 3 h'); ax.set_title(f'{p} — where the LRT trips come from', fontsize=10); ax.grid(axis='y', alpha=0.3)
    axes[0].legend(fontsize=8); fig.tight_layout(); fig.savefig(f'{CFIG}/{fname}', dpi=150); plt.close(fig)
shift_chart('shift_sources.png')
print('charts written')
# ---------------- Word report ----------------
doc = Document()
st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(10)
for s_ in doc.sections: s_.left_margin = s_.right_margin = Cm(2)
def P(text, style=None):
    return doc.add_paragraph(text, style=style)
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
def landscape():
    sec = doc.add_section(); sec.orientation = WD_ORIENT.LANDSCAPE; sec.page_width, sec.page_height = max(sec.page_width, sec.page_height), min(sec.page_width, sec.page_height); sec.left_margin = sec.right_margin = Cm(1.5)
def portrait():
    sec = doc.add_section(); sec.orientation = WD_ORIENT.PORTRAIT; sec.page_width, sec.page_height = min(sec.page_width, sec.page_height), max(sec.page_width, sec.page_height); sec.left_margin = sec.right_margin = Cm(2)

doc.add_heading('Nofit LRT extension — demand study', 0)
P('Comprehensive report: goal, model structure and data, calibration and base scenario, results for the 2040 / 2050 scenarios, conclusions. '
  'Produced 5 October 2026 from the repository Nofit_LRT_Extension (notebooks in notebooks/current/, technical record METHODOLOGY.md, plain-language record docs/PLAIN_ENGLISH_METHODOLOGY.md). '
  'Every number in this report can be traced to a file under Output/ named in the text.')

# ======================= 1 =======================
H('1. Goal and objectives')
P('The Nofit light-rail line (Hamifrats – Nazareth, the "main route") is under construction. The study asks what demand an extension of that line from Hamifrats through Haifa to Tirat Carmel '
  '(the "extension", 24 stations, 18.7 km along the Haifa seafront and the lower city) would carry, where that demand comes from, and how it depends on how the extension is operated and on how the metropolis grows.')
P('The objectives, in the order the work addressed them:')
for s_ in ['Build a base-year (2022) picture of the morning-peak travel market on the corridor — car, bus, Metronit BRT, rail — at the level of traffic analysis zones (TAZs), from the household travel survey and the ticketing, timetable and speed data available, and test it against independent counts.',
           'Grow that base to 2040 and 2050 under the two demographic scenarios of the metropolitan forecast (BU, business as usual; HS, high scenario), holding travel behaviour at 2022.',
           'Build the level of service (travel time, access, waiting, transfers) of the car and of every transit alternative — bus, Metronit, train and the planned LRT — on the same geography, from the May 2026 timetable and measured speeds.',
           'Estimate the demand the LRT would capture from bus, Metronit and car when it is added to that service, for the main route + extension run as one line, in two operating regimes of the extension (Prioritized: full priority at interchanges; Unprioritized: at grade), in the AM and PM peaks, by scenario.',
           'Report what the extension itself carries as a part of the through line: trips that use at least one segment between S01 and S24 (Tirat Carmel – Hamifrats).',
           'State what the chain can and cannot be used for, with every caveat found on the way.']:
    B(s_)
P('What the study is not: it is not a capacity, frequency or fare study, not an economic appraisal, and not a calibrated four-step regional model. It is a corridor demand screening built from observed data with a transparent, documented chain, intended to size and locate the market and to rank alternatives.')

# ======================= 2 =======================
H('2. The model — structure, data and approach')
H('2.1 Structure', 2)
P('The "model" is a chain of 45 documented, reproducible steps (Jupyter notebooks). It has four blocks:')
for s_ in ['Base-year matrices (steps 1–22). Person-journey trip matrices for the AM peak 06:00–09:00 (and, in a later wave, PM 16:00–19:00 and midday) by mode on 778 TAZs of the northern district, built from the 2017/18 household travel survey (THS) with household expansion weights, '
           'the bus layer calibrated to the May 2022 RavKav (smart-card) linked journeys with the on-board survey\'s destination pattern, rail from the national ridership series, and all layers moved from 2018 to a 2022 vintage. Product: Output/final_2022/ (car, transit, total TAZ matrices).',
           'Forecast matrices (step 23). The 2022 matrices moved to 2040 and 2050 under BU and HS by population and employment per TAZ (land-use indices fitted on 2022 demand, Furness balancing per layer), trip rates, destination choice and mode split held at 2022. Product: Output/forecast_taz/{BU_2040, BU_2050, HS_2040, HS_2050}/.',
           'Level of service (steps 25–30, 37, 43, 44). Travel-time, access, wait and transfer components for every mode on the 25 corridor areas and on the 781 TAZs: car routed over the May 2026 car-speed network; bus and Metronit from the Ministry of Transport GTFS of 22 May 2026 (services of Tuesday 2 June 2026) with running times taken from the May 2026 measured bus link speeds; '
           'the LRT from the calibrated stop-to-stop function (transferred from the Tel Aviv Red Line) on the planned alignment and stations; combined into a generalized cost GC = in-vehicle time + 2 × walk + 2 × wait + 8 min per transfer (the central set of the out-of-vehicle-weights research).',
           'LRT capture (steps 31–33, 39, 40, 45). An incremental-logit pivot on the observed 2022 mode shares per TAZ pair: within the transit nest the LRT path competes with the bus / Metronit path (binary logit, sensitivity λ_T = 0.06 per generalized minute, an LRT premium of 5 generalized minutes over a bus path and 2.5 over a Metronit path); '
           'the improvement of the transit nest\'s composite cost (logsum) shifts trips from the car (λ = 0.03). The shares are Empirical-Bayes smoothed towards the area pair (k = 20) before the pivot. Step 45 runs this per alternative, regime, period and scenario and loads the LRT trips onto the line between the cheapest-access stations at each end.']:
    B(s_)
fig(f'{FIG}/lrt_alternatives_lines.png', 15, 'Figure 2.1 — The main route (M01–M20, under construction) and the extension (S01–S24) with the corridor areas. Source: Output/figures/lrt_alternatives_lines.png (step 45).')
H('2.2 Data inputs and their dates', 2)
data = pd.DataFrame([
    ['Household travel survey (THS) 2017/18 — trips file, persons, households, activity diary', '2017–2018 (survey years)', 'Input/THS_2017-2018/', 'Base matrices by mode, trip rates, person-level λ (steps 1–22, 33)'],
    ['Cellular OD, average weekday, hourly, national 1270 zones', '2018–2019', 'Input/Matrices/AvgDayHourlyTrips201819_…', 'Validation of the survey matrices (step 1b, MoT T5)'],
    ['RavKav linked journeys (bus), May 2022', 'May 2022', 'Input/BusRavKav/May_2022/', 'Bus calibration and the destination pattern (steps 8–9, 15)'],
    ['RavKav 2025 boarding taps — Metronit, rail, national bus', '51–52 Tuesdays of 2025, 06:00–09:00', 'Input/BusRavKav/2025/', 'Boardings by stop and TAZ, Metronit and rail OD (steps 34, 41; MoT T7, T14)'],
    ['On-board bus survey destination probabilities by TAZ', '2022 (delivered with the RavKav 2022 work)', 'Input/6_9_BusProbability_ByTAZ.xlsx', 'Destination pattern below super-zone level (step 9)'],
    ['Zonal population and employment 2020, BU 2025; forecast files BU / HS 2040, 2050', '2020 base; forecast vintage of the metropolitan model', 'Input/Zonal_2020.csv, Input/Demographic_Forecast/', 'Vintage alignment to 2022 and the 2040 / 2050 growth (steps 11, 23)'],
    ['National rail ridership series', 'to 2022', 'public series (step 10)', 'Rail growth 2018 → 2022'],
    ['Emme highway network of the north with hourly traffic counts', 'counts 2017–2023 (station dates in the file; network of 23 Sep 2026)', 'Input/Network_with_Counts/', 'Car layer against road counts, all-or-nothing assignment (steps 36, 42; MoT T8, T11, T12)'],
    ['Ministry of Transport national GTFS feed', 'feed of 22 May 2026; services of Tuesday 2 June 2026', 'Input/GTFS/israel-public-transportation.zip', 'Bus, Metronit and train level of service, time on route (steps 29, 30, 44, 45)'],
    ['Bus link speeds on the street network (operator data)', 'May 2026, by weekday and hour', 'Input/BusSpeedData/ (Streets.shp, std_202605.csv)', 'Observed bus running times; the routing topology (steps 30, 37, 43)'],
    ['Car link speeds, whole country (GoogleSpeed)', 'May 2026, by hour (no weekday dimension)', 'Input/CarSpeedData/GoogleSpeed_202605/', 'Car skims by TAZ and area (steps 43, 37, 44)'],
    ['Planned LRT extension alignment and platforms (hf_lrt_3)', 'delivered 22 Sep 2026', 'Input/GeneralHalufa/', '24 stations, station-to-station times (step 25)'],
    ['Main Nofit route (under construction) and its 20 stop nodes', 'delivered 5 Oct 2026', 'Input/Main_Nofit/', 'Main-route stations and running time at 80 km/h (step 45)'],
    ['Corridor aggregation V2 — 25 areas, 174 TAZs, three route orders', 'delivered 22 Sep 2026', 'Input/Corridor_TAZ_Agg_V2.xlsx', 'Reporting geography, area skims, EB smoothing (steps 24–45)'],
    ['Transit travel-time calibration (Tel Aviv Red Line, operator 22)', '2024–2025 operating data (calibration report)', 'docs/Transit_Travel_Time_Calibration_Report_Operator22.md', 'Stop-to-stop LRT running-time function, underground / ground (step 25)'],
    ['Out-of-vehicle weights research (literature and the calibrated Israeli models)', 'executed 4 Oct 2026', 'docs/OVT_WEIGHTS_PARAMETER_MEMO.md', 'Walk / wait weights, transfer penalties, LRT premium (steps 44, 45)'],
], columns=['Input', 'Date / vintage', 'Where', 'Used for'])
table(data, font=7)
H('2.3 Approach', 2)
for s_ in ['Trips, not vehicles. Every matrix is person journeys of residents of the study area with both ends inside it, in the three-hour peak. Car occupancy (1.33 AM) and PCE factors enter only where the car layer is compared with counts.',
           'Two geographies. TAZs (781) for routing, access and the pivot; the 25 corridor areas for reporting, for the Empirical-Bayes prior and for the line profiles. The corridor market is the 174 TAZs of the V2 aggregation; demand is counted on pairs of TAZs in different areas.',
           'Level of service from measured data. Car and bus times are the May 2026 observed speeds (07:00 for AM, 17:00 for PM), not modelled congestion; the transit service is the actual timetable with wait = half the combined headway (capped at 10 min), access by walking at 4 km/h × 1.3 detour within 1 km, transfers within 300 m.',
           'The LRT as a new path inside the transit nest. For each TAZ pair the LRT path is the cheapest-access station at each end (gateway rule), its running time, a 2.5-min wait (5-min headway), 0.5 min station access per end, and a feeder leg by bus (8-min penalty) or Metronit (4-min penalty) where the stations are beyond walking distance. '
           'The LRT premium of 5 generalized minutes over a bus path and 2.5 over a Metronit path comes from the in-vehicle-time multipliers of the calibrated Israeli models (LRT 0.80–0.85 against BRT 0.90–0.95).',
           'Pivot, not re-estimation. The observed 2022 shares per TAZ pair are the anchor; the LRT changes them through P(LRT | transit) and the logsum change. The car\'s absolute cost cancels in the pivot (caveat 25), so the car-to-LRT shift rests on λ and the transit-side costs alone.',
           'Forecasts as demographic references. The 2040 / 2050 sets move the 2022 pattern with the people and jobs; they carry no service change, no change in car ownership, fares or telework. The PM forecast sets are the PM 2022 base grown at the AM growth per TAZ pair (caveat 28).',
           'Every step is a notebook with its inputs, outputs and checks recorded in METHODOLOGY.md; every result is reproducible from the repository (METHODOLOGY §9).']:
    B(s_)

# ======================= 3 =======================
H('3. Calibration and the base scenario')
H('3.1 Building the 2022 base', 2)
P('The base-year matrices come from the 2017/18 household travel survey (16,401 persons, 5,108 households, two survey days), weighted with the revised household weights, with the AM peak defined by the departure hour 06:00–08:59. '
  'The bus layer was calibrated to the May 2022 RavKav linked journeys under a segmented coverage rule: where the ticketing covers a super-zone pair well it sets the volume, elsewhere the survey keeps it, with the on-board survey\'s destination probabilities placing the trips below super-zone level. '
  'The rail layer is the survey\'s rail trips grown by the national ridership series. All layers were then moved from 2018 to 2022 by TAZ population and employment (geometric interpolation between the 2020 and BU-2025 zonal files).')
base = pd.DataFrame([['corridor → corridor', 72331, 10255, 313, 0], ['corridor → outside', 47011, 8947, 573, 292], ['outside → corridor', 89181, 19144, 1020, 2618], ['outside → outside', 1145275, 79615, 7545, 1141], ['all study area', 1353798, 117961, 9451, 4050]],
                    columns=['2022, AM 06:00–09:00', 'car', 'bus (+ Metronit)', 'taxi-type', 'rail'])
table(base); P('Table 3.1 — The 2022 base by corridor class (Output/ths2017/three_mode_2022/summary_2018_2022.csv). The corridor is the 28-sub-area definition of step 17; on the V2 corridor (25 areas, 174 TAZs) the off-diagonal market is 56,445 car / 14,133 transit / 720 taxi-type trips, transit share 0.20.').runs[0].font.size = Pt(8)
fig(f'{FIG}/three_mode_2022.png', 15, 'Figure 3.1 — The 2022 layers: car, bus, taxi-type and rail by super-zone (step 16).')
H('3.2 Tests against independent data', 2)
P('The base was tested against four independent sources. The outcome in one line each:')
for s_ in ['Bus against the RavKav ticketing on the corridor (step 28): on the Haifa trunk the calibrated survey profile is within 1–4 % of the ticketing profile in the direction towards Nazareth (1.01–1.04) and within −14 % / +12 % in the other direction; beyond Hamifrats the two frames differ by up to 1.5 × in one direction (Figure 3.2).',
           'Bus against RavKav by time of day (MoT T14): RavKav / survey bus trips 0.73 in the AM (education trips are 40 % of the survey\'s AM bus trips and are under-represented in the card data), 0.96 in the PM, 0.92 at midday.',
           'Car against road counts on closed cordons (step 36, Figure 3.3): survey car vehicles ÷ counted vehicles 0.58–0.90 on the outer cordons and 0.61–0.62 on the metropolitan core, the expected order for a residents\' personal-trip layer against all traffic (through, commercial and non-resident traffic are not in the survey). '
           'The survey\'s departure-time profile is peakier than the road\'s: 62 % of the three hours in the peak hour against 38–43 % on the counted links (caveat 18).',
           'Car assignment against link counts (step 42, MoT T11): all-or-nothing on the Emme network reproduces the counted volumes in total (assigned ÷ counted 0.93 on the 1,346 links counted 2021–2023) but not their pattern (R² 0.47 and RMSE 113 % against the guideline\'s 0.85 and 35 %) — a person-trip layer without commercial traffic or route choice does not pass a link-level test (caveat 23).',
           'Survey against cellular OD (step 1b, MoT T5): the super-zone matrices agree in structure; the one systematic divergence is intra-zone travel, which the survey holds above the cellular frame in every super-zone.',
           'Ministry of Transport validation guideline (2024 draft, tests T1–T19 on 226 items): 75 pass, 123 miss with a documented explanation, 10 findings, the rest not applicable or not run. The misses are concentrated in the tests written for a four-step assignment model (link volumes, trip-length distributions at TAZ level, intra-zonal shares); the trip rates (T3: 17 of 24 pass), mode split (T9: 15 of 21) and the car profile against counts (T8: 20 of 21) pass.']:
    B(s_)
fig(f'{FIG}/corridor_v2_survey_vs_ticketing.png', 16, 'Figure 3.2 — Transit profile on the corridor: calibrated survey against the RavKav ticketing, by route and direction (step 28).')
fig(f'{FIG}/car_cordon_counts.png', 16, 'Figure 3.3 — Car layer against the road counts on closed cordons (step 36).')
fig(f'{FIG}/mot_T9_modesplit.png', 15, 'Figure 3.4 — Mode split by super-zone against the guideline bands (MoT T9).')
H('3.3 Level of service and the cost sensitivity', 2)
P('The transit level of service was built from the timetable with the measured May 2026 running times: observed ÷ scheduled is 1.09 per bus trip (Metronit 0.87), 1.00 on hops under 500 m and 1.42 on hops over 2 km (Figure 3.5). '
  'The car times on the May 2026 network are 0.90 × the survey\'s reported door-to-door times on the trunk pairs and 0.95 × over all pairs, so there is no 2026 uplift of the car time (step 37). The May 2026 car speeds hardly move by hour (median 2.3 km/h across the day; caveat 24), so the "07:00" car skim is in effect an all-day May 2026 speed.')
fig(f'{FIG}/gtfs_bus_observed_vs_scheduled.png', 14, 'Figure 3.5 — Observed against scheduled bus running times, May 2026 (step 30).')
los = skims[(skims.period == 'AM')] if 'period' in skims.columns else skims
P('Generalized cost on the trunk pairs (trip-weighted, AM, generalized minutes; Output/alternatives/skims_summary.csv): car 13.8; bus / Metronit 44.8 at TAZ level (the area-level skim of step 31 had 27–30 because it pooled every direct line\'s headway and the nearest stop\'s walk — caveat 26); '
  'LRT through line 48.7 Prioritized / 57.2 Unprioritized including the 5-minute premium. The LRT\'s in-vehicle time on the trunk is below the bus\'s; its remaining disadvantage is station access and the transfer where a feeder is needed.')
P('The cost sensitivity λ could not be identified from the 2022 cross-section of pair shares (wrong sign, ρ² 0.002): the composition of the market by car availability hides it. At the person level (step 33, binary logit on the survey\'s AM trips within the corridor, car availability, purpose, person and distance held constant) λ = 0.035 per generalized minute (95 % interval 0.002–0.068; 0.040 on the 2026 car skim; 0.053 with area fixed effects), '
  'but it is 0.083 for no-car households, not significant for licence holders in car-owning households (0.008 ± 0.017) — the segment the LRT would draw from the car. The chain therefore uses an assumed λ = 0.03 (range 0.02–0.05) and λ_T = 2λ, and reports the range (Figure 3.6).')
fig(f'{FIG}/mode_choice_person_level_by_segment.png', 14, 'Figure 3.6 — λ by car-availability segment, person-level estimation (step 33).')
H('3.4 The base scenario with the LRT (2022)', 2)
r22 = srow('AM', '2022'); r22u = srow('AM', '2022', 'unprioritized'); r22p = srow('PM', '2022')
P(f'With the main route + extension added to the 2022 service, the AM three-hour LRT demand on the corridor market is {r22["LRT"]:,.0f} trips Prioritized ({r22u["LRT"]:,.0f} Unprioritized), {r22["LRT trips using the extension (at least one segment S01–S24)"]:,.0f} of them using the extension; '
  f'{r22["LRT from car"]:,.0f} come from the car and {r22["LRT from bus/BRT"]:,.0f} from bus and Metronit. The transit share of the corridor market moves from {r22["transit before"]/(r22["car before"]+r22["transit before"])*100:.1f} % to {r22["total transit"]/(r22["car"]+r22["total transit"])*100:.1f} %. The PM figure is {r22p["LRT"]:,.0f} ({r22p["LRT"]/r22["LRT"]*100:.0f} % of the AM).')
P('The uncertainty experiment (step 40) and the λ / premium ranges of step 31 put the 2022 capture between about 0.75 × and 1.4 × the central value: λ 0.02 → +40 %, λ 0.05 → −25 %; premium 0 → −20 %, premium 10 → +25 %. The regime (running time) is worth about −20 % (Unprioritized against Prioritized), of the same order as the λ range.')
fig(f'{FIG}/lrt_capture_tornado.png', 14, 'Figure 3.7 — Sensitivity of the 2022 LRT capture to the assumed factors (step 40).')
fig(f'{FIG}/alternatives/map_line_loads_AM_2022.png', 16, 'Figure 3.8 — LRT line loads and station boardings, 2022 AM, main route + extension, Prioritized (step 45).')
H('3.5 What the model is good for, and what it should not be used for', 2)
P('Good for:')
for s_ in ['Sizing the corridor market by mode and locating it (which areas and TAZs, which stations), at the three-hour peak and at the design-hour scale (≈ 1.8 × an average hour).',
           'Ranking alternatives and regimes against each other — through line against extension only, Prioritized against Unprioritized — and reading the order of magnitude of the LRT\'s draw from bus, Metronit and car.',
           'Showing how that market grows under the BU and HS demographics, with behaviour held constant.',
           'Relative statements about the line profile: where the load peaks, how the two directions differ, how much of the line\'s demand uses the extension.']:
    B(s_)
P('Not to be used for:')
for s_ in ['Passenger loads for capacity, fleet or frequency decisions, or for appraisal. The volumes are unvalidated externally at the link level; the loads are three-hour potential movements between the cheapest-access stations with no capacity constraint or crowding.',
           'Any statement that depends on the car\'s absolute travel time or on congestion in 2040 / 2050: the pivot cancels the car cost (caveat 25), the skims are May 2026 observed speeds, and the forecast carries no road or car-ownership change.',
           'The exact split between "from car" and "from transit": the induced car trips depend on the aggregation level the pivot is run at (TAZ gives 130 where the area level gives 414; caveat 27), and λ for choice riders is not identified (caveat 15).',
           'TAZ-level detail as such: below the area level the matrices are allocations of survey trips by weights, not observations; a single TAZ\'s number is not reliable.',
           'Operations of the main route: its stations, the 80 km/h at-grade running, the 5-minute headway and the through-running at Hamifrats without a transfer are assumptions (caveat 28); the PM forecast sets are grown at the AM rates.']:
    B(s_)
P('The full list of caveats (METHODOLOGY §8, 28 items) in brief:')
cav = [('1–3', 'Survey file version newer than the original run; coarse cellular zone mapping; intra-zone divergence survey vs cellular (72 % vs 34 %).'),
       ('4–6', 'Both survey days are the same households (cross-day validation is a lower bound); TAZ volumes scale hybrid probabilities; super-zone OD blocks of the TAZ hybrids are not conserved exactly.'),
       ('7–9', 'Units of the transit sources (OnBoard, RavKav) not reconciled; the segmented coverage rule is an assumption with a threshold (bus base 96,000–129,500 under the sweep); taxi-type codes carried as a separate layer.'),
       ('10–11', 'The forecast rests on demographic factors only; the 2022 vintage alignment is an interpolation assumption.'),
       ('12–13', 'Corridor profiles are potential movements between areas, not loads; the similarity tests are diagnostics, not acceptance criteria.'),
       ('14', 'The trips file\'s mode codes 4 and 5 (group taxi, Metronit) were swapped in early runs; corrected and the chain rerun — Metronit riders are in the transit layer.'),
       ('15', 'λ is estimated at the person level (0.035) but not identified for choice riders; the assumed 0.03 (0.02–0.05) is carried with its range.'),
       ('16–17', 'RavKav 2025 taps are boardings whose transfer tag is not the 2022 journey definition; the OnBoard destination pattern is what separates the ticketing products.'),
       ('18', 'The survey\'s departure-time profile is peakier than the road counts and the fare gates (0.62 vs 0.38–0.48 of the three hours in the peak hour).'),
       ('19', 'Two super-zone keys disagree on 142 TAZs; the keys table is used by decision.'),
       ('20', 'The RavKav shortfall against the survey is an AM, education-heavy phenomenon (0.74 AM, 0.96 PM).'),
       ('21–22', 'Car occupancy computed with the wrong hour in step 36 (1.33 stands within the band); the survey population is 5 % above the zonal population.'),
       ('23', 'The car layer does not reproduce the link counts\' pattern (all-or-nothing, no commercial traffic).'),
       ('24', 'The May 2026 car speeds are nearly the same in every hour — an all-day speed, not a peak one.'),
       ('25', 'The car skim\'s level does not reach the capture (the pivot cancels it).'),
       ('26', 'The area-level transit skim understates the TAZ traveller\'s cost by 1.5 ×; the alternatives are run at TAZ level for bus and LRT alike.'),
       ('27', 'The trips induced from the car depend on the aggregation level of the pivot.'),
       ('28', 'The main route\'s operation is assumed; PM forecast sets grown at AM rates.')]
table(pd.DataFrame(cav, columns=['Caveat', 'In brief']), font=7)

# ======================= 4 =======================
H('4. Results — the 2040 and 2050 scenarios')
P('All results in this section are for the main route + extension run as one through line (Tirat Carmel – Hamifrats – Nazareth) in the Prioritized regime of the extension, on the corridor market (TAZ pairs of the 174 corridor TAZs in different areas), three-hour periods. '
  'The extension part is reported within that run: trips that ride at least one segment between S01 and S24, and trips with both ends at extension stations. The Unprioritized regime is given as a sensitivity in 4.5. The 2022 row is the base with the LRT added to today\'s service. '
  'Source: Output/alternatives/demand_summary.csv and the per-run folders Output/alternatives/{AM,PM}/{scenario}/main_ext_prioritized/.')
H('4.1 Shift to the LRT and total demand by mode', 2)
landscape()
for p in ['AM', 'PM']:
    t = tabs[(p, REG)]
    P(f'Table 4.{1 if p == "AM" else 2} — {p} {"06:00–09:00" if p == "AM" else "16:00–19:00"}: the shift to the LRT and the demand by mode after the LRT, main route + extension, Prioritized (trips in three hours).').runs[0].font.bold = True
    a = t[['scenario', 'car before', 'bus before', 'BRT before', 'transit before', 'car → transit', 'car → LRT', 'BRT → LRT', 'bus → LRT']].copy()
    a['car → transit (% of car)'] = t['car → transit'] / t['car before'] * 100; a['BRT → LRT (% of BRT)'] = t['BRT → LRT'] / t['BRT before'] * 100; a['bus → LRT (% of bus)'] = t['bus → LRT'] / t['bus before'] * 100
    table(a, {'car → transit (% of car)': '{:.2f} %', 'BRT → LRT (% of BRT)': '{:.1f} %', 'bus → LRT (% of bus)': '{:.1f} %'}, font=7)
    P('Demand after the LRT and the share of each mode (of car + transit on the corridor market):').runs[0].font.italic = True
    b = t[['scenario', 'car after', 'BRT after', 'LRT', 'bus after', 'total transit after']].copy()
    for c in ['car share', 'BRT share', 'LRT share', 'bus share', 'transit share', 'LRT share of transit']: b[c] = t[c] * 100
    table(b, {c: '{:.1f} %' for c in ['car share', 'BRT share', 'LRT share', 'bus share', 'transit share', 'LRT share of transit']}, font=7)
    P('The extension part, as part of the through line:').runs[0].font.italic = True
    c = t[['scenario', 'LRT', 'LRT using the extension', 'ext: from car', 'ext: from BRT', 'ext: from bus', 'LRT within the extension', 'busiest segment (3 h, one direction)']].copy()
    c['extension share of LRT trips'] = t['LRT using the extension'] / t['LRT'] * 100
    table(c, {'extension share of LRT trips': '{:.1f} %'}, font=7)
    doc.add_paragraph()
portrait()
P('Reading the tables. "Before" is the scenario\'s no-build market (car, bus incl. rail, BRT = Metronit) on the corridor TAZ pairs; the three shift columns are the trips the pivot moves to the LRT from each; "after" is what remains plus the LRT. '
  '"car → transit" is the trips the logsum improvement moves out of the car; "car → LRT" is the part of them the LRT itself carries (the rest board the bus or Metronit path of their pair). "BRT → LRT" and "bus → LRT" are the LRT trips drawn from existing transit on the pairs whose transit path is Metronit-based or bus-based; the three LRT columns add up to the LRT total. Taxi-type trips (about 700) are carried unchanged and are outside the shares. '
  'The extension columns count the LRT trips of the same run that ride at least one segment between S01 and S24 (from either end of the line), and separately those with both ends at extension stations.')
P('A note on the car column. The AM shift from the car doubles between 2040 BU and 2050 BU (684 → 1,421) and between 2040 BU and 2040 HS (684 → 1,387) while the market grows by 16 % and 4 %. This is not a demand effect but the aggregation effect of caveat 27 seen across scenarios: '
  'the incremental shift of a TAZ pair is proportional to S·(1 − S) of its smoothed transit share, and the forecast sets of step 23 seed trips into TAZ pairs that are empty in 2022 (small-base and transforming TAZs receive the super-zone pattern), so the number of corridor pairs with both car and transit trips rises from 1,620 (2022) to 2,084 (2040 BU), 2,942 (2050 BU), 4,970 (2040 HS) and 5,688 (2050 HS) and the trip-weighted S·(1 − S) from 0.048 to 0.062. '
  'The PM sets, grown pair by pair from the PM base, keep the 2022 pair set and show a smooth car column (666 → 880). The car shift should therefore be read as an order of magnitude (300–1,300 trips, 0.4–1.5 % of the corridor car trips), not compared between scenarios (caveat 29).')
fig(f'{CFIG}/demand_by_scenario.png', 16, 'Figure 4.1 — Transit demand on the corridor by scenario: no-build transit, total transit after the LRT, LRT trips, and the LRT trips using the extension (AM and PM).')
fig(f'{CFIG}/shift_sources.png', 16, 'Figure 4.2 — Where the LRT trips come from (car, Metronit, bus), whole line and the part using the extension, by scenario.')
H('4.2 Flow on the line — LRT, both directions', 2)
P('Passengers on each segment of the line in the three hours, by direction: towards Nazareth (S01 → S24 → M20) and towards Tirat Carmel (M20 → M01 → S01). The dashed line marks the junction of the extension (S24) with the main route (M01, the same station at Hamifrats). '
  'Source: lrt_line_loads.csv in each run folder (the LRT trips between the cheapest-access stations of each TAZ pair).')
landscape()
fig(f'{CFIG}/flow_lrt_scenarios_AM.png', 25, 'Figure 4.3 — LRT flow by segment and direction, the four scenarios, AM.')
fig(f'{CFIG}/flow_lrt_scenarios_PM.png', 25, 'Figure 4.4 — LRT flow by segment and direction, the four scenarios, PM.')
fig(f'{CFIG}/flow_lrt_AM.png', 25, 'Figure 4.5 — LRT flow per scenario, both directions on one panel, AM (2022 and the four scenarios).')
fig(f'{CFIG}/flow_lrt_PM.png', 25, 'Figure 4.6 — LRT flow per scenario, both directions on one panel, PM.')
H('4.3 Flow on the line — total transit, both directions', 2)
P('The same profile for all transit trips of the corridor market (bus, Metronit and LRT after the LRT is added), loaded along the line between the LRT stations nearest their ends — the transit demand the line\'s corridor carries, of which the LRT takes the share shown in 4.1. '
  'Source: transit_line_loads.csv in each run folder.')
fig(f'{CFIG}/flow_transit_scenarios_AM.png', 25, 'Figure 4.7 — Total transit flow by segment and direction, the four scenarios, AM.')
fig(f'{CFIG}/flow_transit_scenarios_PM.png', 25, 'Figure 4.8 — Total transit flow by segment and direction, the four scenarios, PM.')
fig(f'{CFIG}/flow_transit_AM.png', 25, 'Figure 4.9 — Total transit flow per scenario, both directions, AM.')
fig(f'{CFIG}/flow_transit_PM.png', 25, 'Figure 4.10 — Total transit flow per scenario, both directions, PM.')
portrait()
H('4.4 Mode split on the route', 2)
P('The split of the corridor market between car and transit after the LRT, with the LRT shown within transit, by scenario and period.')
fig(f'{CFIG}/mode_split.png', 16, 'Figure 4.11 — Mode split on the corridor after the LRT: car, bus, Metronit and LRT, AM and PM.')
H('4.5 Sensitivity: the Unprioritized regime', 2)
rows = []
for p in ['AM', 'PM']:
    for sc in SCEN:
        a, b = srow(p, sc, 'prioritized'), srow(p, sc, 'unprioritized')
        rows.append({'period': p, 'scenario': SCEN_LAB[sc], 'LRT Prioritized': a['LRT'], 'LRT Unprioritized': b['LRT'], 'ratio': b['LRT'] / a['LRT'],
                     'using the extension, Prioritized': a['LRT trips using the extension (at least one segment S01–S24)'], 'using the extension, Unprioritized': b['LRT trips using the extension (at least one segment S01–S24)'],
                     'from car, Prioritized': a['LRT from car'], 'from car, Unprioritized': b['LRT from car']})
table(pd.DataFrame(rows), {'ratio': '{:.2f}'}, font=7)
P('Table 4.3 — LRT trips in the two regimes of the extension. The Unprioritized regime (at-grade running, 65.8 min end to end on the extension against 40.7) loses about a fifth of the LRT trips, most of it on the extension itself.').runs[0].font.size = Pt(8)
H('4.6 Time on route', 2)
rt = route[['mode', 'period', 'direction', 'from', 'to', 'scheduled_min (median)', 'observed_min (step 30 ratio)']].copy() if 'direction' in route.columns else route
rt.columns = [str(c) for c in rt.columns]; table(rt.head(40), {'scheduled_min (median)': '{:.0f}', 'observed_min (step 30 ratio)': '{:.0f}'}, font=7)
P('Table 4.4 — End-to-end times on the route by mode (Output/alternatives/time_on_route.csv). The LRT through line runs 74.3 min Prioritized / 99.6 min Unprioritized from Tirat Carmel to Nazareth (extension 40.7 / 65.8 min; main route 33.7 min at 80 km/h with 10 s dwell).').runs[0].font.size = Pt(8)
H('4.7 Maps', 2)
P('The map set of the alternatives report (Output/figures/alternatives/, 41 maps: line loads, origins and destinations of the LRT trips, LRT share, growth, shift sources and rates, travel-time maps) applies to these runs; four are reproduced here.')
fig(f'{FIG}/alternatives/map_line_loads_AM_HS_2050.png', 16, 'Figure 4.12 — LRT line loads and station boardings, HS 2050 AM.')
fig(f'{FIG}/alternatives/map_growth_by_scenario_AM.png', 16, 'Figure 4.13 — Growth of the LRT trips by TAZ, 2022 → each scenario, AM.')
fig(f'{FIG}/alternatives/map_shift_sources_AM_BU_2040.png', 16, 'Figure 4.14 — Sources of the LRT trips by TAZ (car, Metronit, bus), BU 2040 AM.')
fig(f'{FIG}/alternatives/map_time_lrt_vs_bus_AM.png', 16, 'Figure 4.15 — LRT against bus generalized cost by TAZ, AM.')

# ======================= 5 =======================
H('5. Conclusions')
tA = tabs[('AM', REG)].set_index('scenario'); tP = tabs[('PM', REG)].set_index('scenario')
lo, hi = tA.loc['2040 BU'], tA.loc['2050 HS']
peak1_lo = loads('AM', 'BU_2040', 'lrt')['dir1_towards_Nazareth_end'].max(); peak1_hi = loads('AM', 'HS_2050', 'lrt')['dir1_towards_Nazareth_end'].max()
for s_ in [f'Demand. The through line (main route + extension) carries {lo["LRT"]:,.0f} trips in the AM three hours in 2040 BU and {hi["LRT"]:,.0f} in 2050 HS ({tA.loc["2050 BU", "LRT"]:,.0f} in 2050 BU, {tA.loc["2040 HS", "LRT"]:,.0f} in 2040 HS); the PM is {tP.loc["2040 BU", "LRT"]/lo["LRT"]*100:.0f} % of the AM. '
           f'Of these, {lo["LRT using the extension"]:,.0f}–{hi["LRT using the extension"]:,.0f} ({lo["LRT using the extension"]/lo["LRT"]*100:.0f} %) use the extension and {lo["LRT within the extension"]:,.0f}–{hi["LRT within the extension"]:,.0f} travel between extension stations only: the extension is where most of the line\'s riders are, the main route feeds it rather than the reverse.',
           f'Sources. The LRT is first a transit reorganisation: {lo["BRT → LRT"]:,.0f}–{hi["BRT → LRT"]:,.0f} trips come from the Metronit ({lo["BRT → LRT"]/lo["BRT before"]*100:.0f} % of its corridor trips), {lo["bus → LRT"]:,.0f}–{hi["bus → LRT"]:,.0f} from the bus, and {lo["car → LRT"]:,.0f}–{hi["car → LRT"]:,.0f} from the car ({lo["car → LRT"]/lo["car before"]*100:.1f} % of the corridor car trips). '
           f'The transit share of the corridor market rises by about {(lo["transit share"] - srow("AM", "BU_2040")["transit share before"])*100:.1f} points; the LRT takes {lo["LRT share of transit"]*100:.0f} % of transit.',
           f'Profile. In the AM the busiest segment is the entry into Hamifrats from the main route (S24–M02) in the direction towards Tirat Carmel, {lo["busiest segment (3 h, one direction)"]:,.0f} (2040 BU) to {hi["busiest segment (3 h, one direction)"]:,.0f} (2050 HS) passengers in three hours (about 1,100–1,700 in the design hour at a 0.55–0.6 peak-hour factor); in the direction towards Nazareth the peak is on the Carmel coast (S14–S15, {peak1_lo:,.0f}–{peak1_hi:,.0f}). '
           f'In the PM the two directions nearly balance (S24–M02 towards Nazareth 1,300–1,400; S05–S06 or S11–S12 towards Tirat Carmel 1,100–1,700). The main route beyond Kiryat Ata (M06 onwards) carries a few hundred per direction; the extension carries 4 of 5 riders.',
           'Growth. Between 2040 BU and 2050 HS the LRT demand grows by about 45 %, in step with the corridor transit market (×1.3–1.5 on 2022), because the forecast holds behaviour at 2022; the HS scenario adds 15–25 % over BU in the same year.',
           'Regime. Priority at the interchanges is worth about 20–25 % of the LRT trips: at-grade running of the extension lengthens its end-to-end time from 41 to 66 minutes and loses a fifth of the riders, mostly on the extension.',
           'Robustness. The central figures sit within a range of about −25 % / +40 % from the cost sensitivity and the LRT premium alone (step 40); the car-to-LRT shift is the least certain component (caveats 15, 25, 27) and should be read as an order of magnitude; the bus and Metronit shifts rest on observed shares and measured service and are the firmer part.',
           'Fitness. The results support the sizing and location of the extension\'s market, the ranking of the regimes, and the design-hour scale of the trunk load. They do not support capacity, fleet or frequency decisions or an appraisal without a validated assignment and a full mode-choice model; the next steps are a purpose split of the survey, a PM-specific forecast, the main route\'s operating plan, and a choice-rider λ from a stated-preference or a revealed choice set with the car cost in it.']:
    B(s_)
P('Repository record: METHODOLOGY.md §6aq (step 45) and §8; docs/PLAIN_ENGLISH_METHODOLOGY.md Part 5; the alternatives report reports/LRT_Alternatives_Demand_Report.docx and its workbook Output/alternatives/LRT_alternatives_matrices.xlsx; this report\'s builder tools/build_comprehensive_report.py.')
os.makedirs('reports', exist_ok=True); doc.save('reports/Nofit_LRT_Extension_Comprehensive_Report.docx'); print('report written')
for (p, reg), t in tabs.items(): t.to_csv(f'{OUT}/shift_table_{p}_{reg}.csv', index=False)
print('shift tables written')
