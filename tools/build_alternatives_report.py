"""Build the LRT-alternatives report (step 45, METHODOLOGY §6aq) from Output/alternatives/:
   Output/alternatives/LRT_alternatives_matrices.xlsx  -- the car and transit (and LRT) trip matrices on the 25 corridor areas, one sheet per run, plus the summary tables
   reports/LRT_Alternatives_Demand_Report.docx          -- the report: matrices (where they are, the central ones shown), time on route, total demand AM / PM
Run after notebooks/current/LRT_alternatives_demand.ipynb:  python3 tools/build_alternatives_report.py"""
import os, glob
import numpy as np, pandas as pd
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
while not os.path.exists('METHODOLOGY.md') and os.getcwd() != '/': os.chdir('..')
OUT = 'Output/alternatives'; FIG = 'Output/figures'
PERIODS = ['AM', 'PM']; SCEN = ['2022', 'BU_2040', 'BU_2050', 'HS_2040', 'HS_2050']
ALTS = {'main_ext': 'Main route + extension', 'ext': 'Extension only'}; REGIMES = {'prioritized': 'Prioritized', 'unprioritized': 'Unprioritized'}
summary = pd.read_csv(f'{OUT}/demand_summary.csv'); route = pd.read_csv(f'{OUT}/time_on_route.csv'); skims = pd.read_csv(f'{OUT}/skims_summary.csv')
xl = pd.ExcelFile('Input/Corridor_TAZ_Agg_V2.xlsx', engine='openpyxl'); areas = xl.parse('AreaCodes').set_index('AggCode'); names = areas['AggAreaName']
def area_mat(p, sc, alt, reg, k):
    m = pd.read_csv(f'{OUT}/{p}/{sc}/{alt}_{reg}/{k}_area_v2.csv', index_col=0); m.columns = m.columns.astype(int); return m
# ---------------- workbook ----------------
with pd.ExcelWriter(f'{OUT}/LRT_alternatives_matrices.xlsx', engine='openpyxl') as xw:
    s = summary.copy(); s.to_excel(xw, sheet_name='Summary', index=False, float_format='%.0f')
    route.to_excel(xw, sheet_name='TimeOnRoute', index=False, float_format='%.1f'); skims.to_excel(xw, sheet_name='Skims', index=False, float_format='%.1f')
    legend = pd.DataFrame({'AggCode': areas.index, 'name': names.values}); legend.to_excel(xw, sheet_name='Areas', index=False)
    for p in PERIODS:
        for sc in SCEN:
            for alt in ALTS:
                for reg in REGIMES:
                    sheet = f'{p}_{sc}_{alt}_{reg[:5]}'[:31]; row = 0
                    for k, lab in [('t_car_new', 'CAR trips (after the LRT), origin area x destination area'), ('t_tr_new', 'TRANSIT trips (bus + Metronit + LRT), after the LRT'), ('t_lrt', 'LRT trips'), ('t_brt', 'Metronit trips after the LRT'), ('t_bus', 'bus trips after the LRT')]:
                        m = area_mat(p, sc, alt, reg, k); m.index = [f'{a} {names[a]}' for a in m.index]; m.columns = [str(c) for c in m.columns]
                        pd.DataFrame({lab: []}).to_excel(xw, sheet_name=sheet, startrow=row, index=False); m.round(1).to_excel(xw, sheet_name=sheet, startrow=row + 1); row += len(m) + 4
print('workbook written')
# ---------------- Word report ----------------
doc = Document()
st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(10)
def table(df, float_fmt='{:,.0f}', font=8, col_widths=None):
    t = doc.add_table(rows=1, cols=len(df.columns)); t.style = 'Light Grid Accent 1'
    for j, c in enumerate(df.columns):
        cell = t.rows[0].cells[j]; cell.text = str(c)
        for par in cell.paragraphs:
            for run in par.runs: run.font.size = Pt(font); run.font.bold = True
    for _, r in df.iterrows():
        cells = t.add_row().cells
        for j, v in enumerate(r):
            cells[j].text = (float_fmt.format(v) if isinstance(v, (float, np.floating)) and np.isfinite(v) else ('' if isinstance(v, float) else str(v)))
            for par in cells[j].paragraphs:
                for run in par.runs: run.font.size = Pt(font)
    if col_widths:
        for j, w in enumerate(col_widths):
            for row in t.rows: row.cells[j].width = Cm(w)
    return t
doc.add_heading('Nofit LRT — demand for the main route and the extension', 0)
doc.add_paragraph('Alternatives: (1) main route + extension as one through line; (2) extension only. Extension regimes: Prioritized (underground, step 25 calibrated times) and Unprioritized (at grade). '
                  'Main route at its 80 km/h design speed. Scenario-years 2022, BU 2040, BU 2050, HS 2040, HS 2050; periods AM 06:00–09:00 and PM 16:00–19:00; TAZ level (174 corridor TAZs) aggregated to the 25 corridor areas; both directions of the line. '
                  'Source: notebooks/current/LRT_alternatives_demand.ipynb (METHODOLOGY §6aq); produced 5 October 2026.')
doc.add_heading('Assumptions stated', 1)
for s_ in ['Out-of-vehicle parameters: the central set of the OVT research — walk 2.0 × and wait 2.0 × in-vehicle time, bus ↔ LRT transfer 8 min, Metronit ↔ LRT 4 min, station access 1.5 min per underground end and 0.5 per surface end; wait = half the headway, capped at 10 min; walking 4.8 km/h on the straight line × 1.3.',
           'LRT premium: 5 generalized minutes over a bus-based alternative and 2.5 over a Metronit-based one (estimated from the calibrated models\' in-vehicle multipliers, LRT 0.80–0.85 against BRT 0.90–0.95; range 1.5–3.5). Cost sensitivity λ = 0.03 per generalized minute, λ_T = 0.06 within the transit nest (step 31\'s central values).',
           'Main route stations: not in the delivery — taken at the route\'s network nodes at least 1 km apart (27 stations, 1.6 km mean spacing); to be replaced by the planned station list. Running time 80 km/h between stops + 10 s dwell per stop, at grade. One line through-runs at a 5-minute headway.',
           'Transit level of service: the GTFS bus and Metronit services of Tuesday 2 June 2026 in each period, with step 30\'s observed running times (May 2026 speeds); the car on the May 2026 speeds (07:00 / 17:00). Demand: step 31\'s incremental-logit pivot per TAZ pair on the observed 2022 shares.',
           'Base and forecast matrices: AM 2022 from step 22, PM 2022 from the wave-1b PM layers; forecast AM sets from step 23; forecast PM sets = the PM base grown at step 23\'s AM rates per TAZ pair (an approximation). Totals are for the three-hour periods on the corridor-internal TAZ pairs in different areas; taxi is carried unchanged; rail is inside the bus figure.']:
    doc.add_paragraph(s_, style='List Bullet')
doc.add_heading('1. Matrices — car and transit', 1)
doc.add_paragraph('Every run\'s trip matrices are in Output/alternatives/: at TAZ level (174 × 174, *_taz.csv.gz) and on the 25 corridor areas (*_area_v2.csv), for the car, total transit, LRT, Metronit and bus after the LRT. '
                  'The workbook Output/alternatives/LRT_alternatives_matrices.xlsx holds the 25 × 25 car and transit matrices of all 40 runs, one sheet per period × scenario × alternative × regime. The two matrices below are the central combination (main route + extension, Prioritized, BU 2040, AM), trips in the three hours, rows = origin area, columns = destination area (codes; names in the Areas sheet).')
sec = doc.sections[-1]; sec.orientation = WD_ORIENT.LANDSCAPE; sec.page_width, sec.page_height = sec.page_height, sec.page_width; sec.left_margin = sec.right_margin = Cm(1.2)
for k, lab in [('t_car_new', 'Car trips, BU 2040 AM, main route + extension, Prioritized'), ('t_tr_new', 'Transit trips (bus + Metronit + LRT), BU 2040 AM, main route + extension, Prioritized'), ('t_lrt', 'of which LRT trips')]:
    doc.add_paragraph(lab).runs[0].font.bold = True
    m = area_mat('AM', 'BU_2040', 'main_ext', 'prioritized', k); df = m.round(0).astype(int).reset_index().rename(columns={'index': 'o \\ d'}); df.columns = [str(c) for c in df.columns]
    table(df, '{:,.0f}', font=6)
doc.add_paragraph('Area totals of the same run (origins), all four alternative × regime combinations, AM and PM:')
rows = []
for p in PERIODS:
    for alt in ALTS:
        for reg in REGIMES:
            m = area_mat(p, 'BU_2040', alt, reg, 't_lrt'); rows.append(pd.Series(m.sum(1).values, index=[f'{a} {names[a]}' for a in m.index], name=f'{p} {ALTS[alt]} {REGIMES[reg]}'))
tot = pd.concat(rows, axis=1).round(0); tot.insert(0, 'area', tot.index); table(tot.reset_index(drop=True), '{:,.0f}', font=7)
doc.add_heading('2. Time on route — LRT, Metronit, train, car', 1)
doc.add_paragraph('End-to-end and segment times. LRT from the station time matrices (symmetric); Metronit line 1 from its scheduled trips of the period, first to last study-area stop, with step 30\'s observed ÷ scheduled ratio; train from the day\'s Israel Railways trips; car on the May 2026 speeds between the corridor areas\' points plus a 3-minute terminal.')
rt = route.copy(); rt['scheduled_min (median)'] = rt['scheduled_min (median)'].round(1); rt['observed_min (step 30 ratio)'] = rt['observed_min (step 30 ratio)'].round(1)
rt = rt[['mode', 'period', 'direction', 'from', 'to', 'stops', 'scheduled_min (median)', 'observed_min (step 30 ratio)']].rename(columns={'scheduled_min (median)': 'minutes (scheduled / design)', 'observed_min (step 30 ratio)': 'observed (min)'})
table(rt, '{:,.1f}', font=7)
doc.add_heading('3. Total demand — car, Metronit, LRT, total transit, AM and PM', 1)
doc.add_paragraph('Trips in the three-hour period on the corridor-internal TAZ pairs (TAZs in different corridor areas), after the LRT. Total transit = bus + Metronit + LRT (rail inside the bus figure). "Busiest segment" is the largest three-hour load on one station-to-station segment in one direction.')
for p in PERIODS:
    doc.add_paragraph(f'{p} ({"06:00–09:00" if p == "AM" else "16:00–19:00"})').runs[0].font.bold = True
    s_ = summary[summary['period'] == p][['scenario', 'alternative', 'regime', 'car', 'bus', 'BRT (Metronit)', 'LRT', 'total transit', 'LRT from car', 'busiest segment load (3 h, one direction)']].copy()
    s_['regime'] = s_['regime'].str.split(' (', regex=False).str[0]; s_ = s_.rename(columns={'BRT (Metronit)': 'Metronit', 'busiest segment load (3 h, one direction)': 'busiest segment'}); table(s_, '{:,.0f}', font=7)
doc.add_heading('Figures', 1)
for f, cap in [('lrt_alternatives_lines.png', 'The two lines and their stations.'), ('lrt_alternatives_demand.png', 'LRT trips by scenario-year, alternative and regime, AM and PM.'), ('lrt_alternatives_line_loads.png', 'Line loads by segment and direction, main route + extension, Prioritized, BU 2040, AM.')]:
    if os.path.exists(f'{FIG}/{f}'): doc.add_picture(f'{FIG}/{f}', width=Cm(24)); doc.add_paragraph(cap).alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_heading('4. Maps — time, demand, loads and differences', 1)
doc.add_paragraph('Produced by tools/build_alternatives_maps.py from the same runs (Output/figures/alternatives/). Reference destination for the time maps: the TAZ of the station with the most LRT alightings (BU 2040 AM, main route + extension, Prioritized).')
MAPS = [('map_time_lrt_vs_bus_AM.png', 'Transit time to the reference TAZ, AM: today\'s best bus / Metronit path, the LRT (main route + extension, Prioritized), and the difference (blue = LRT cheaper).'),
        ('map_time_lrt_to_ref_AM.png', 'Time by LRT to the reference TAZ (access + wait + ride + egress, generalized minutes), AM, the four alternative × regime combinations.'),
        ('map_time_car.png', 'Car time to the reference TAZ, AM (07:00 speeds) and PM (17:00 speeds), plus the 3-minute terminal.'),
        ('map_time_lrt_over_car_AM.png', 'LRT ÷ car generalized time to the reference TAZ, AM, main route + extension and extension only (Prioritized).'),
        ('map_line_loads_AM_BU_2040.png', 'LRT line loads by segment and direction (width ∝ trips) and station boardings (circle size), AM BU 2040, the four combinations.'),
        ('map_line_loads_PM_BU_2040.png', 'The same for the PM BU 2040.'),
        ('map_line_loads_AM_HS_2050.png', 'The same for the AM HS 2050, the largest loads.'),
        ('map_lrt_origins_AM_BU_2040.png', 'LRT trip origins by TAZ, AM BU 2040, the four combinations.'),
        ('map_lrt_destinations_AM_BU_2040.png', 'LRT trip destinations by TAZ, AM BU 2040.'),
        ('map_lrt_share_AM_BU_2040.png', 'LRT share of the transit trips by origin TAZ, AM BU 2040.'),
        ('map_diff_main_vs_ext_AM_BU_2040.png', 'What the main route adds: LRT origins and destinations, main route + extension minus extension only (Prioritized), AM BU 2040.'),
        ('map_diff_prioritized_vs_unprioritized_AM_BU_2040.png', 'What the underground extension adds: LRT origins, Prioritized minus Unprioritized, AM BU 2040.'),
        ('map_growth_2022_to_HS2050_AM.png', 'Growth of the LRT demand, 2022 to HS 2050, main route + extension, Prioritized, AM.'),
        ('map_lrt_origins_AM_vs_PM_BU_2040.png', 'LRT trip origins, AM against PM, main route + extension, Prioritized, BU 2040.')]
for f, cap in MAPS:
    pth = f'{FIG}/alternatives/{f}'
    if os.path.exists(pth): doc.add_picture(pth, width=Cm(24)); doc.add_paragraph(cap).alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_heading('Limits', 1)
doc.add_paragraph('The main route\'s stations are assumed; its demand moves with the real station list and with any feeder restructuring in Kiryat Ata and Nazareth. The forecast PM sets are grown at the AM rates. The LRT premium over the Metronit is an estimate, not an estimated parameter. '
                  'The pivot\'s induced car trips depend on the aggregation level (METHODOLOGY caveat 27). No capacity, no route choice against parallel bus services, no fare, no park-and-ride. The level of service is a single best path per TAZ pair at the line\'s own headway (caveat 26).')
os.makedirs('reports', exist_ok=True); doc.save('reports/LRT_Alternatives_Demand_Report.docx'); print('report written')
