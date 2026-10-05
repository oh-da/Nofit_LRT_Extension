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
# the bus-slowdown sensitivity (step 45 rerun with BUS_SLOWDOWN, ALT_OUT=Output/alternatives_bus_slow): mixed-traffic buses 10 % slower in 2040, 20 % in 2050
SLOW_OUT = 'Output/alternatives_bus_slow'; SLOW_FACTORS = {'BU_2040': 1.10, 'BU_2050': 1.20, 'HS_2040': 1.10, 'HS_2050': 1.20}
summary_slow = pd.read_csv(f'{SLOW_OUT}/demand_summary.csv') if os.path.exists(f'{SLOW_OUT}/demand_summary.csv') else None
stations = pd.read_csv(f'{OUT}/stations_main_ext.csv')
xl = pd.ExcelFile('Input/Corridor_TAZ_Agg_V2.xlsx', engine='openpyxl'); names = xl.parse('AreaCodes').set_index('AggCode')['AggAreaName']
def srow(p, sc, reg=REG, alt='Main', src=None):
    src = summary if src is None else src
    s = src[(src.period == p) & (src.scenario == sc) & (src.alternative.str.startswith(alt)) & (src.regime.str.startswith(REG_LAB[reg]))]
    assert len(s) == 1, (p, sc, reg, alt); return s.iloc[0]
# peak-hour factors (tools/peak_hour_factors_periods.py: step 27's method on the AM and PM windows). Every chart is drawn for the peak hour
# of its period: line loads by the network bus factor of the direction (the LRT and total transit alike, the chain's convention since step 31),
# totals by the study-area factor of the layer (transit for the LRT and transit quantities, car for the car).
PHF = pd.read_csv(f'{OUT}/peak_hour_factors.csv'); PHFI = PHF.set_index(['period', 'layer', 'direction'])['PHF3h']
def phf(p, layer, direction='all'): return float(PHFI[(p, layer, direction)])
def loads(p, sc, kind, reg=REG, peak=True):
    l = pd.read_csv(f'{OUT}/{p}/{sc}/{ALT}_{reg}/{kind}_line_loads.csv').copy()
    if peak: l['dir1_towards_Nazareth_end'] *= phf(p, 'transit', 'up'); l['dir2_towards_TiratCarmel'] *= phf(p, 'transit', 'down')
    return l
def peak_busiest(p, sc, reg=REG):
    l = loads(p, sc, 'lrt', reg); return float(max(l['dir1_towards_Nazareth_end'].max(), l['dir2_towards_TiratCarmel'].max()))
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
                     'busiest segment (3 h, one direction)': r['busiest segment load (3 h, one direction)'],
                     'LRT (peak hour)': lrt * phf(p, 'transit'), 'LRT using the extension (peak hour)': r['LRT trips using the extension (at least one segment S01–S24)'] * phf(p, 'transit'),
                     'busiest segment (peak hour, one direction)': peak_busiest(p, sc, reg)})
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
        ax.set_ylabel('passengers / peak hour'); ax.set_title(f'{SCEN_LAB[sc]} — {p}', fontsize=9, loc='left'); ax.grid(axis='y', alpha=0.3)
    axes[0].legend(fontsize=8, loc='upper right'); axes[-1].set_xticks(np.arange(len(l))); axes[-1].set_xticklabels(seg_lab, rotation=90, fontsize=6)
    fig.suptitle(f'{"LRT" if kind == "lrt" else "Total transit"} flow by segment and direction — main route + extension, Prioritized, {p} peak hour (factors {phf(p, "transit", "up"):.2f} / {phf(p, "transit", "down"):.2f} of the three hours)', fontsize=11)
    fig.tight_layout(); fig.savefig(f'{CFIG}/{fname}', dpi=150); plt.close(fig)
def flow_chart_compact(p, kind, fname):
    """All four forecast scenarios on one pair of panels (one per direction)."""
    fig, axes = plt.subplots(2, 1, figsize=(13, 7), sharex=True); cols = {'BU_2040': '#9ecae1', 'BU_2050': '#3182bd', 'HS_2040': '#fdae6b', 'HS_2050': '#e6550d'}
    for ax, (d, lab) in zip(axes, [('dir1_towards_Nazareth_end', 'towards Nazareth (S01 → M20)'), ('dir2_towards_TiratCarmel', 'towards Tirat Carmel (M20 → S01)')]):
        for i, sc in enumerate(SCEN):
            l = loads(p, sc, kind); x = np.arange(len(l)); ax.bar(x + (i - 1.5) * 0.2, l[d], 0.2, color=cols[sc], label=SCEN_LAB[sc])
        ax.axvline(n_ext - 0.5, color='k', ls='--', lw=0.8); ax.set_ylabel('passengers / peak hour'); ax.set_title(lab, fontsize=9, loc='left'); ax.grid(axis='y', alpha=0.3)
    axes[0].legend(fontsize=8, ncol=4); axes[-1].set_xticks(np.arange(len(l))); axes[-1].set_xticklabels(seg_lab, rotation=90, fontsize=6)
    fig.suptitle(f'{"LRT" if kind == "lrt" else "Total transit"} flow by segment — the four scenarios, main route + extension, Prioritized, {p} peak hour (factors {phf(p, "transit", "up"):.2f} / {phf(p, "transit", "down"):.2f} of the three hours)', fontsize=11)
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
        t = tabs[(p, REG)]; x = np.arange(len(t)); w = 0.2; f = phf(p, 'transit')
        ax.bar(x - 1.5 * w, t['transit before'] * f, w, color='#c7c7c7', label='transit before (no LRT)')
        ax.bar(x - 0.5 * w, t['total transit after'] * f, w, color='#1f77b4', label='total transit after')
        ax.bar(x + 0.5 * w, t['LRT'] * f, w, color='#2ca02c', label='LRT (main + extension)')
        ax.bar(x + 1.5 * w, t['LRT using the extension'] * f, w, color='#98df8a', label='LRT using the extension')
        ax.set_xticks(x); ax.set_xticklabels(t['scenario']); ax.set_ylabel('trips / peak hour'); ax.set_title(f'{p} — transit demand on the corridor, peak hour ({f:.2f} of the three hours)', fontsize=10); ax.grid(axis='y', alpha=0.3)
    axes[0].legend(fontsize=8); fig.tight_layout(); fig.savefig(f'{CFIG}/{fname}', dpi=150); plt.close(fig)
demand_bars('demand_by_scenario.png')
def shift_chart(fname):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, p in zip(axes, ['AM', 'PM']):
        t = tabs[(p, REG)].copy(); x = np.arange(len(t)); w = 0.35; f = phf(p, 'transit')
        for c in ['car → LRT', 'BRT → LRT', 'bus → LRT', 'ext: from car', 'ext: from BRT', 'ext: from bus']: t[c] = t[c] * f
        ax.bar(x - w / 2, t['car → LRT'], w, color='#7f7f7f', label='from car (whole line)'); ax.bar(x - w / 2, t['BRT → LRT'], w, bottom=t['car → LRT'], color='#1f77b4', label='from BRT (Metronit)')
        ax.bar(x - w / 2, t['bus → LRT'], w, bottom=t['car → LRT'] + t['BRT → LRT'], color='#aec7e8', label='from bus')
        ax.bar(x + w / 2, t['ext: from car'], w, color='#7f7f7f', alpha=0.5, hatch='//', label='… of which using the extension'); ax.bar(x + w / 2, t['ext: from BRT'], w, bottom=t['ext: from car'], color='#1f77b4', alpha=0.5, hatch='//')
        ax.bar(x + w / 2, t['ext: from bus'], w, bottom=t['ext: from car'] + t['ext: from BRT'], color='#aec7e8', alpha=0.5, hatch='//')
        ax.set_xticks(x); ax.set_xticklabels(t['scenario']); ax.set_ylabel('LRT trips / peak hour'); ax.set_title(f'{p} — where the LRT trips come from, peak hour ({f:.2f} of the three hours)', fontsize=10); ax.grid(axis='y', alpha=0.3)
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

# ---------- the reference case and the decision numbers (computed once, used by the summary, section 4 and the conclusions) ----------
REF = 'BU_2050'; REF_LAB = SCEN_LAB[REF]
def ext_row(p, sc, reg=REG): return srow(p, sc, reg, alt='Ext')
def cross_hamifrats(p, sc, reg=REG):
    l = loads(p, sc, 'lrt', reg, peak=False); r = l[(l.from_station == 'S24') & (l.to_station == 'M02')].iloc[0]; return float(r['dir1_towards_Nazareth_end'] + r['dir2_towards_TiratCarmel'])
def busiest(p, sc, alt='main_ext', reg=REG, ext_only_segments=False, peak=False):
    l = pd.read_csv(f'{OUT}/{p}/{sc}/{alt}_{reg}/lrt_line_loads.csv').copy()
    if peak: l['dir1_towards_Nazareth_end'] *= phf(p, 'transit', 'up'); l['dir2_towards_TiratCarmel'] *= phf(p, 'transit', 'down')
    if ext_only_segments: l = l[l.to_station.str.startswith('S')]
    return float(max(l['dir1_towards_Nazareth_end'].max(), l['dir2_towards_TiratCarmel'].max()))
def through_table(p, sc, reg=REG):
    m, e = srow(p, sc, reg), ext_row(p, sc, reg); fp = phf(p, 'transit')
    rows = [{'alternative': 'Extension only (terminating at Hamifrats)', 'extension riders (3 h)': e['LRT'], 'total LRT riders (3 h)': e['LRT'], 'total LRT riders (peak hour)': e['LRT'] * fp,
             'peak load on the extension (peak hour, one direction)': busiest(p, sc, 'ext', reg, peak=True), 'peak load on the line (peak hour)': busiest(p, sc, 'ext', reg, peak=True), 'from car (3 h)': e['LRT from car'], 'difference': '–'},
            {'alternative': 'Through-running (main route + extension)', 'extension riders (3 h)': m['LRT trips using the extension (at least one segment S01–S24)'], 'total LRT riders (3 h)': m['LRT'], 'total LRT riders (peak hour)': m['LRT'] * fp,
             'peak load on the extension (peak hour, one direction)': busiest(p, sc, 'main_ext', reg, ext_only_segments=True, peak=True), 'peak load on the line (peak hour)': busiest(p, sc, 'main_ext', reg, peak=True), 'from car (3 h)': m['LRT from car'],
             'difference': f"extension riders {(m['LRT trips using the extension (at least one segment S01–S24)'] / e['LRT'] - 1) * 100:+.0f} %; total LRT {(m['LRT'] / e['LRT'] - 1) * 100:+.0f} %"}]
    return pd.DataFrame(rows)
GRP = {**{201: 'Tirat Carmel'}, **{a: 'Haifa (Matam – Hamifrats)' for a in range(202, 211)}, **{a: 'Main route (Kiryat Ata – Nazareth)' for a in range(211, 218)}, **{a: 'Krayot (off the line, by feeder)' for a in [101, 102, 103, 104, 301, 302, 303, 304]}}
GRP_ORDER = ['Tirat Carmel', 'Haifa (Matam – Hamifrats)', 'Krayot (off the line, by feeder)', 'Main route (Kiryat Ata – Nazareth)']
def market_tables(p, sc, reg=REG):
    m = pd.read_csv(f'{OUT}/{p}/{sc}/{ALT}_{reg}/t_lrt_area_v2.csv', index_col=0); m.columns = m.columns.astype(int); tot = m.values.sum()
    G = m.copy(); G.index = [GRP[a] for a in G.index]; G.columns = [GRP[a] for a in G.columns]; GG = G.groupby(level=0).sum().T.groupby(level=0).sum().T.reindex(index=GRP_ORDER, columns=GRP_ORDER)
    sym = (GG + GG.T).values.copy(); np.fill_diagonal(sym, np.diag(GG.values)); sym = pd.DataFrame(sym, index=GRP_ORDER, columns=GRP_ORDER)
    pairs = m.stack().reset_index(); pairs.columns = ['o', 'd', 't']; pairs['key'] = [tuple(sorted((a, b))) for a, b in zip(pairs.o, pairs.d)]
    top = pairs.groupby('key')['t'].sum().sort_values(ascending=False).head(10)
    top_df = pd.DataFrame({'rank': range(1, len(top) + 1), 'area pair (both directions)': [f'{names[a]} – {names[b]}' for a, b in top.index], 'LRT trips (3 h)': top.values, 'share of all LRT trips': top.values / tot * 100})
    return sym, tot, top_df
def market_summary(p, sc, reg=REG):
    sym, tot, _ = market_tables(p, sc, reg); r = srow(p, sc, reg); H_, T_, K_, M_ = GRP_ORDER[1], GRP_ORDER[0], GRP_ORDER[2], GRP_ORDER[3]
    out = {'Haifa internal (both ends Matam – Hamifrats)': sym.loc[H_, H_], 'Tirat Carmel ↔ Haifa': sym.loc[T_, H_], 'Krayot ↔ Haifa (Krayot by feeder)': sym.loc[K_, H_], 'Main route (Kiryat Ata – Nazareth) ↔ Haifa': sym.loc[M_, H_],
           'Main route ↔ Krayot / Tirat Carmel': sym.loc[M_, K_] + sym.loc[M_, T_], 'within the main route': sym.loc[M_, M_], 'Krayot ↔ Tirat Carmel': sym.loc[K_, T_],
           'crossing Hamifrats (ride the S24–M02 segment)': cross_hamifrats(p, sc, reg), 'purely extension to extension (both ends at S01–S24)': r['LRT trips on the extension stations (both ends on S01–S24)'], 'using the extension at all': r['LRT trips using the extension (at least one segment S01–S24)']}
    return pd.DataFrame({'market': list(out.keys()), 'LRT trips (3 h)': list(out.values()), 'share of all LRT trips': [v / tot * 100 for v in out.values()]}), tot
ref = srow('AM', REF); refP = srow('PM', REF); refE = ext_row('AM', REF); fA = phf('AM', 'transit'); fP = phf('PM', 'transit')
ref_brt_shift = pd.read_csv(f'{OUT}/AM/{REF}/{ALT}_{REG}/from_brt_area_v2.csv', index_col=0).values.sum(); ref_bus_shift = pd.read_csv(f'{OUT}/AM/{REF}/{ALT}_{REG}/from_bus_area_v2.csv', index_col=0).values.sum()
ref_unp = srow('AM', REF, 'unprioritized'); ref_slow = srow('AM', REF, REG, src=summary_slow) if summary_slow is not None else None
RANGE_LO, RANGE_HI = 3166 / 4254, 6031 / 4254   # step 40: λ 0.05 / 0.02 around the central 0.03 (the widest single factor; premium 0 / 10 gives 0.80 / 1.23)
mk_ref, mk_tot = market_summary('AM', REF)

# ======================= 0 =======================
H('Executive decision summary')
P(f'The question. The Nofit light-rail main route (Hamifrats – Nazareth) is under construction. Should it be extended through Haifa to Tirat Carmel, and if so, run through as one line or terminate at Hamifrats? This report sizes and locates the demand for the extension, from the observed 2022 travel market grown to 2040 and 2050, and states what that evidence does and does not support.')
P(f'Reference case. {REF_LAB} is the principal planning year and scenario; 2040 and the high (HS) scenario illustrate growth sensitivity. The through line in the Prioritized regime (priority at the interchanges) is the reference alternative.').runs[0].font.bold = True
dec = pd.DataFrame([
    ['LRT riders on the corridor, AM 06:00–09:00 / AM peak hour', f'{ref["LRT"]:,.0f} / {ref["LRT"] * fA:,.0f}'],
    ['… of which use the extension (S01–S24) / travel only between extension stations', f'{ref["LRT trips using the extension (at least one segment S01–S24)"]:,.0f} ({ref["LRT trips using the extension (at least one segment S01–S24)"] / ref["LRT"] * 100:.0f} %) / {ref["LRT trips on the extension stations (both ends on S01–S24)"]:,.0f}'],
    ['LRT riders, PM 16:00–19:00 / PM peak hour', f'{refP["LRT"]:,.0f} / {refP["LRT"] * fP:,.0f}'],
    ['Through-running against terminating at Hamifrats: extension riders / total LRT riders', f'{ref["LRT trips using the extension (at least one segment S01–S24)"]:,.0f} vs {refE["LRT"]:,.0f} ({(ref["LRT trips using the extension (at least one segment S01–S24)"] / refE["LRT"] - 1) * 100:+.0f} %) / {ref["LRT"]:,.0f} vs {refE["LRT"]:,.0f} ({(ref["LRT"] / refE["LRT"] - 1) * 100:+.0f} %)'],
    ['Where the riders come from (AM 3 h)', f'Metronit {ref_brt_shift:,.0f} ({ref_brt_shift / ref["BRT before"] * 100:.0f} % of its corridor trips), bus {ref_bus_shift:,.0f}, car {ref["LRT from car"]:,.0f} ({ref["LRT from car"] / ref["car before"] * 100:.1f} % of corridor car trips)'],
    ['Peak load, AM peak hour, one direction', f'{busiest("AM", REF, peak=True):,.0f} at the entry into Hamifrats (S24–M02, towards Tirat Carmel); on the extension itself {busiest("AM", REF, ext_only_segments=True, peak=True):,.0f}'],
    ['Transit share of the corridor market, before → after', f'{ref["transit before"] / (ref["car before"] + ref["transit before"]) * 100:.1f} % → {ref["total transit"] / (ref["car"] + ref["total transit"]) * 100:.1f} %; the LRT takes {ref["LRT"] / ref["total transit"] * 100:.0f} % of transit'],
    ['Largest markets (AM 3 h)', '; '.join(f'{r["market"]} {r["LRT trips (3 h)"]:,.0f} ({r["share of all LRT trips"]:.0f} %)' for _, r in mk_ref.iloc[[0, 1, 2, 3]].iterrows())],
    ['Unprioritized extension (at grade through the interchanges)', f'{ref_unp["LRT"]:,.0f} ({(ref_unp["LRT"] / ref["LRT"] - 1) * 100:+.0f} %)'],
    ['Slower buses in 2050 (× 1.20 in mixed traffic)', f'{ref_slow["LRT"]:,.0f} ({(ref_slow["LRT"] / ref["LRT"] - 1) * 100:+.0f} %)' if ref_slow is not None else 'n/a'],
], columns=[f'Reference case {REF_LAB}, main route + extension, Prioritized', 'value'])
table(dec, font=8)
P('Planning range (AM 06:00–09:00 LRT riders, reference case). The range is the cost sensitivity λ at the ends of its carried range (0.05 / 0.02 around the central 0.03), the widest single factor of the uncertainty experiment (step 40); the LRT premium (0 / 10 minutes) gives a narrower band inside it. The regime is a design choice, not an uncertainty, and is shown separately.').runs[0].font.bold = True
pr = pd.DataFrame([['Central planning case (λ 0.03, premium 5, Prioritized)', ref['LRT'], ref['LRT'] * fA], ['Plausible lower case (λ 0.05: travellers least sensitive to cost)', ref['LRT'] * RANGE_LO, ref['LRT'] * RANGE_LO * fA], ['Plausible upper case (λ 0.02: most sensitive)', ref['LRT'] * RANGE_HI, ref['LRT'] * RANGE_HI * fA],
                   ['Design choice: Unprioritized extension, central λ', ref_unp['LRT'], ref_unp['LRT'] * fA]], columns=['case', 'LRT riders, 3 h', 'LRT riders, peak hour'])
table(pr, font=8)
P('What the demand evidence supports:').runs[0].font.bold = True
for s_ in [f'An extension market of the order of {ref["LRT trips using the extension (at least one segment S01–S24)"] * RANGE_LO / 1000:.0f},000–{ref["LRT trips using the extension (at least one segment S01–S24)"] * RANGE_HI / 1000:.0f},000 AM three-hour riders in {REF_LAB}, located on the Carmel coast and the lower city, with Tirat Carmel ↔ Haifa, Haifa internal and the Krayot feeder market as its three legs.',
           f'That the extension\'s riders do not depend on through-running: {ref["LRT trips using the extension (at least one segment S01–S24)"]:,.0f} on the through line against {refE["LRT"]:,.0f} if it terminates at Hamifrats. Through-running\'s benefit is the transfer it spares the {cross_hamifrats("AM", REF):,.0f} trips ({cross_hamifrats("AM", REF) / ref["LRT"] * 100:.0f} %) that cross Hamifrats, which today ride the Metronit through; the +25 % on the line is the main route\'s own market, carried either way.',
           'Priority at the interchanges: the at-grade regime loses about a quarter of the riders, mostly on the extension, a larger effect than the growth between 2040 and 2050.',
           'A peak load in the low thousands per hour and direction at the Hamifrats entry, which is a light-rail scale of demand, not a metro one.',
           'The ranking of these alternatives and regimes, and the order of magnitude of the draw from the Metronit, the bus and the car.']:
    B(s_)
P('What it does not support:').runs[0].font.bold = True
for s_ in ['A ridership forecast for appraisal, fleet or frequency decisions: the loads are unconstrained potential movements on a service plan that keeps every bus and Metronit line as it runs today, from a base validated at corridor level but not at link level, with the cost sensitivity bounded by a range rather than estimated for the car-owning riders the line must win.',
           'Any statement about the car in 2040 / 2050: the car-to-LRT shift is an order of magnitude and does not respond to road conditions in this model.',
           'A new-market claim: most LRT riders are today\'s Metronit and bus riders on a faster vehicle; the net addition to transit is the car shift, a few hundred to a thousand trips in three hours.',
           'Station-level or TAZ-level numbers as such, or anything about the main route\'s own operation, which is assumed.']:
    B(s_)
doc.add_page_break()

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
           'Level of service held at May 2026 in every scenario-year. The 2040 / 2050 runs use today\'s car and bus times while the corridor demand grows by 30–60 %: the regional model\'s future network is not available, and degrading today\'s network with tomorrow\'s demand while leaving out every planned road and transit scheme would be the worse assumption. '
           'What slower buses would do is tested in section 4.9 (+2 % of LRT trips in 2040, +4–5 % in 2050); a slower car cannot register in the pivot at all (see below).',
           'The LRT as a new path inside the transit nest. For each TAZ pair the LRT path is the cheapest-access station at each end (gateway rule), its running time, a 2.5-min wait (5-min headway), 0.5 min station access per end, and a feeder leg by bus (8-min penalty) or Metronit (4-min penalty) where the stations are beyond walking distance. '
           'The LRT premium of 5 generalized minutes over a bus path and 2.5 over a Metronit path comes from the in-vehicle-time multipliers of the calibrated Israeli models (LRT 0.80–0.85 against BRT 0.90–0.95).',
           'Pivot, not re-estimation. The observed 2022 shares per TAZ pair are the anchor; the LRT changes them through P(LRT | transit) and the logsum change. The car\'s absolute cost cancels in the pivot (caveat 25), so the car-to-LRT shift rests on λ and the transit-side costs alone.',
           'Forecasts as demographic references. The 2040 / 2050 sets move the 2022 pattern with the people and jobs; they carry no service change, no change in car ownership, fares or telework. The PM forecast sets are the PM 2022 base grown at the AM growth per TAZ pair (caveat 28).',
           'Every step is a notebook with its inputs, outputs and checks recorded in METHODOLOGY.md; every result is reproducible from the repository (METHODOLOGY §9).']:
    B(s_)

H('2.4 The generalized cost, in plain terms', 2)
P('The generalized cost is "how long the trip feels", in minutes. Standing at a stop, walking to it and changing vehicles are more irksome than sitting in a moving vehicle, so those minutes count more than once. The result is one number per trip that puts a bus trip, a Metronit trip, an LRT trip and a car trip on the same scale:')
P('GC = in-vehicle time + 2 × walking time + 2 × waiting time + 8 min per transfer (4 min between Metronit and LRT) − LRT premium (5 min over a bus path, 2.5 over a Metronit path)')
P('Waiting is half the headway, capped at 10 minutes. Walking is at 4 km/h on the straight line × 1.3 for the street detour. The transfer penalty is a flat charge for the uncertainty and the hassle of changing vehicles, on top of the actual time; the first boarding is not a transfer. The LRT premium reflects the preference for rail-like vehicles over buses found in the calibrated Israeli models. The car is the drive time on the measured speeds plus 3 minutes for parking and the walk at the ends. Money is out of every mode by decision: the fare is flat and integrated, and no parking-cost data exist for the area.')
ex = pd.DataFrame([['walk to the stop / station', '6 min × 2 = 12', '9 min × 2 = 18'], ['wait: 10-min headway → 5 / 5-min headway → 2.5', '5 × 2 = 10', '2.5 × 2 = 5'], ['in-vehicle time', '28', '20'], ['transfers', '0', '0'], ['walk at the end', '4 min × 2 = 8', '5 min × 2 = 10'], ['LRT premium', '0', '−5'], ['generalized cost', '58', '48']], columns=['component (example: Kiryat Haim → Bat Galim)', 'by bus', 'by LRT'])
table(ex, font=8); P('Table 2.2 — A worked example. The LRT trip is ten felt minutes cheaper although its walking is longer, because it is faster and comes more often.').runs[0].font.size = Pt(8)
P('The model never uses the cost alone; it uses the difference between two options and a sensitivity λ that turns felt minutes into a probability. Within the transit nest (λ_T = 0.06 per generalized minute) a ten-minute advantage gives the LRT about 65 % of a pair\'s transit riders, twenty minutes about 77 %, equal cost 50 %. '
  'The shift from the car works on the improvement of the whole transit bundle with λ = 0.03, half as sensitive, and starts from the pair\'s observed 2022 transit share: where the car is dominant that share is small and the shift is small. The car\'s own cost never enters the pivot, only the observed balance it produced in 2022 (caveat 25); a car that worsens by 2040 would therefore have to be modelled as a change of the no-build shares first (handover item D-11).')
P('Three things follow for reading the results. The weights are assumptions from the literature and the calibrated models, not estimates on this corridor (the out-of-vehicle research memo lists the alternatives and the chain was rerun on seven sets). At TAZ level the bus cost on the trunk is about 45 felt minutes, not the 30 an area-level skim suggested, because an area skim pools every line\'s headway and the nearest stop\'s walk, which no single traveller gets (caveat 26). And the LRT\'s remaining disadvantage against the Metronit on the trunk is station access and the feeder transfer, not the ride, so anything that shortens the walk or removes a transfer moves the capture more than a faster vehicle does.')

H('2.5 The cost sensitivity λ: what it is, why it is needed, how it was estimated', 2)
P('What it is. λ is the number that turns a difference in felt minutes into a difference in choices. In the logit model the odds of choosing transit over the car change by a factor exp(−λ × ΔGC) when the transit cost changes by ΔGC generalized minutes. With λ = 0.03 one generalized minute moves the odds by 3 %, ten minutes by about 35 %; with λ_T = 0.06 inside the transit nest, ten minutes of advantage give the LRT about 65 % of a pair\'s transit riders. A large λ means travellers react strongly to small cost differences; a small λ means habit, availability and things outside the cost dominate.')
P('Why it is needed. The whole capture rests on it. The LRT\'s advantage over the bus on a pair is a cost difference in felt minutes; λ_T decides how many of that pair\'s transit riders move, and λ how many car trips the improved transit bundle attracts. Halving λ roughly halves the car shift and raises the LRT\'s share of transit towards an even split; doubling it does the reverse. The λ range alone spans −25 % to +40 % of the 2022 capture (step 40), more than the regime or the premium.')
P('Why it could not be read off the matrices. The obvious estimate, a logit of each area pair\'s 2022 transit share on the bus-minus-car cost difference (597 pairs, 70,000 trips), returns λ with the wrong sign (−0.010) and no fit; with constants per distance band, +0.008 and still nothing. The reason is composition: the pairs with cheap transit are the pairs whose residents own few cars, so the share is driven by who lives there, not by the minutes. A pair-level fit cannot separate the two.')
P('How it was estimated (step 33). At the person level, on the survey\'s AM trips within the 25 corridor areas (2,310 trips, 543 households), a binary logit of car against transit with the cost difference ΔGC as the explanatory variable and car availability (no car in the household, no licence, more licences than cars, a car available), purpose, age, gender, sector, student status and a distance band held constant. Weighted by the survey\'s expansion weights, standard errors clustered by household. Holding car availability constant is what makes λ identifiable: within a group of people with the same access to a car, those facing a smaller transit cost choose transit more often.')
lam = pd.read_csv('Output/mode_choice/lambda_summary.csv'); lam2 = pd.read_csv('Output/mode_choice/car_network/lambda_summary.csv') if os.path.exists('Output/mode_choice/car_network/lambda_summary.csv') else None
lt = lam[['model', 'lambda', 'lo95', 'hi95', 'rows', 'households']].copy(); lt.columns = ['model (step 33, survey car skim)', 'λ per generalized minute', '95 % low', '95 % high', 'trips', 'households']
if lam2 is not None: lt.loc[len(lt)] = ['M1 on the May 2026 car network skim (step 37)', lam2['lambda'].iloc[0], lam2['lo95'].iloc[0], lam2['hi95'].iloc[0], lam2['rows'].iloc[0], lam2['households'].iloc[0]]
lt.loc[len(lt)] = ['assumed in the chain (step 31): λ, range 0.02–0.05; λ_T = 2λ = 0.06', 0.03, 0.02, 0.05, np.nan, np.nan]
table(lt, {'λ per generalized minute': '{:.3f}', '95 % low': '{:.3f}', '95 % high': '{:.3f}'}, font=7)
P('Table 2.3 — λ estimates (Output/mode_choice/lambda_summary.csv). M1 is the central specification; M1b uses the cheaper of the bus and the Metronit as the transit cost; M3 adds origin and destination area effects; M4 restricts the sample to licence holders in car-owning households; M1u is unweighted.').runs[0].font.size = Pt(8)
P('What came out. The pooled λ is 0.035 (0.002–0.068), the right sign, ρ² 0.43, and 0.040 on the 2026 car skim. By car-availability segment it is 0.083 for people in households without a car (significant), 0.027 for people without a licence and 0.053 for people with a car available (both weak), and −0.006 where licences outnumber cars. For licence holders in car-owning households alone, the segment the LRT would have to win from the car, λ is 0.008 ± 0.017: not different from zero. The survey has too few such people choosing transit on comparable pairs to pin it down (Figure 3.6).')
P('What the chain does with it. It keeps the assumed λ = 0.03 of step 31, inside the pooled estimate\'s interval and on its cautious side, carries the range 0.02–0.05 through every capture run, and sets λ_T = 2λ within the transit nest: the choice between two transit paths is more cost-sensitive than the choice between car and transit, and the ratio 0.5 is a standard nesting value, assumed rather than estimated. The honest reading is that the transit-side λ_T is supported by the data and the car-side λ is a judgement bounded by its range; that is why the bus and Metronit shifts are the firmer part of every result and the car shift an order of magnitude.')

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
  f'{r22["LRT from car"]:,.0f} come from the car and {r22["LRT from bus/BRT"]:,.0f} from bus and Metronit. The transit share of the corridor market moves from {r22["transit before"]/(r22["car before"]+r22["transit before"])*100:.1f} % to {r22["total transit"]/(r22["car"]+r22["total transit"])*100:.1f} %. The PM figure is {r22p["LRT"]:,.0f} ({r22p["LRT"]/r22["LRT"]*100:.0f} % of the AM). In the peak hour: {r22["LRT"]*phf("AM", "transit"):,.0f} AM and {r22p["LRT"]*phf("PM", "transit"):,.0f} PM (factors {phf("AM", "transit"):.2f} / {phf("PM", "transit"):.2f}).')
P('The uncertainty experiment (step 40) and the λ / premium ranges of step 31 put the 2022 capture between about 0.75 × and 1.4 × the central value: λ 0.02 → +40 %, λ 0.05 → −25 %; premium 0 → −20 %, premium 10 → +25 %. The regime (running time) is worth about −20 % (Unprioritized against Prioritized), of the same order as the λ range.')
fig(f'{FIG}/lrt_capture_tornado.png', 14, 'Figure 3.7 — Sensitivity of the 2022 LRT capture to the assumed factors (step 40).')
fig(f'{FIG}/alternatives/map_line_loads_AM_2022.png', 16, 'Figure 3.8 — LRT line loads and station boardings in the peak hour, 2022 AM, main route + extension, Prioritized (step 45).')
H('3.5 What the model is good for, and what it should not be used for', 2)
P('Good for:')
for s_ in ['Sizing the corridor market by mode and locating it (which areas and TAZs, which stations), at the three-hour peak and at the design-hour scale (≈ 1.8 × an average hour).',
           'Ranking alternatives and regimes against each other — through line against extension only, Prioritized against Unprioritized — and reading the order of magnitude of the LRT\'s draw from bus, Metronit and car.',
           'Showing how that market grows under the BU and HS demographics, with behaviour held constant.',
           'Relative statements about the line profile: where the load peaks, how the two directions differ, how much of the line\'s demand uses the extension.']:
    B(s_)
P('Not to be used for:')
for s_ in ['Passenger loads for capacity, fleet or frequency decisions, or for appraisal. The volumes are unvalidated externally at the link level; the loads are three-hour potential movements between the cheapest-access stations with no capacity constraint or crowding.',
           'Any statement that depends on the car\'s absolute travel time or on congestion in 2040 / 2050: the pivot cancels the car cost (caveat 25), the skims are May 2026 observed speeds in every year, and the forecast carries no road, service or car-ownership change. The slower-bus sensitivity of 4.9 bounds the transit side of this (+2–5 % of LRT trips); the car side is unbounded in this model.',
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
P(f'{REF_LAB} is the principal reference case: the planning year 2050 with the business-as-usual demographics; 2040 and the high scenario (HS) are shown as growth sensitivities. The HS sets also move the market\'s composition (section 4.3), so the reference case is the one to plan on and the HS figures the upper growth reading.').runs[0].font.bold = True
P('All results in this section are for the main route + extension run as one through line (Tirat Carmel – Hamifrats – Nazareth) in the Prioritized regime of the extension, on the corridor market (TAZ pairs of the 174 corridor TAZs in different areas), three-hour periods. '
  'The extension part is reported within that run: trips that ride at least one segment between S01 and S24, and trips with both ends at extension stations. The Unprioritized regime is given as a sensitivity in 4.8. The 2022 row is the base with the LRT added to today\'s service. '
  'Source: Output/alternatives/demand_summary.csv and the per-run folders Output/alternatives/{AM,PM}/{scenario}/main_ext_prioritized/.')
P('Periods and the peak hour. The matrices are three-hour periods (AM 06:00–09:00, PM 16:00–19:00); the tables give the three-hour totals with the peak-hour values beside them, and every chart and map is drawn for the peak hour. '
  'The peak-hour factors are the share of the three hours in the busiest sliding 60-minute window of the survey\'s departures (step 27\'s method, run on both windows; Output/alternatives/peak_hour_factors.csv): '
  'line loads use the network bus factor of the direction (the chain\'s convention for LRT loads since step 31, the LRT and total transit alike); totals use the study-area factor of the layer. '
  'The observed design-hour factors are lower (RavKav boardings 0.43–0.48, road counts 0.38–0.43 in the AM; caveat 18), so the peak-hour values here are the survey\'s, the upper reading.')
pf = PHF.copy(); pf['PHF3h'] = pf['PHF3h'].round(3); table(pf[['period', 'layer', 'direction', 'PHF3h', 'peak hour', 'basis']], {'PHF3h': '{:.3f}'}, font=7)
P('Table 4.0 — Peak-hour factors applied (share of the three-hour period in the peak hour).').runs[0].font.size = Pt(8)
H('4.1 Through-running to Nazareth against terminating the extension at Hamifrats', 2)
P('Both alternatives were run on the same skims and base: the extension alone (24 stations, terminating at Hamifrats) and the through line (the extension plus the main route\'s 20 stations, one line without a transfer at Hamifrats). "Extension riders" are all the riders of the extension-only line, and the through line\'s riders who ride at least one segment between S01 and S24. Peak loads are per direction in the AM peak hour.')
for p in ['AM', 'PM']:
    tt = through_table(p, REF); table(tt, {'difference': '{}'}, font=7)
    P(f'Table 4.{1 if p == "AM" else 2} — {p}, {REF_LAB}: extension only against through-running, Prioritized.').runs[0].font.size = Pt(8)
rows = []
for sc in ['2022'] + SCEN:
    m, e = srow('AM', sc), ext_row('AM', sc)
    rows.append({'scenario': SCEN_LAB[sc], 'extension only: LRT riders': e['LRT'], 'through line: riders using the extension': m['LRT trips using the extension (at least one segment S01–S24)'], 'gain on the extension': (m['LRT trips using the extension (at least one segment S01–S24)'] / e['LRT'] - 1) * 100,
                 'through line: total LRT riders': m['LRT'], 'gain on the line': (m['LRT'] / e['LRT'] - 1) * 100, 'extension only: peak load (peak h)': busiest('AM', sc, 'ext', peak=True), 'through line: peak load on the extension (peak h)': busiest('AM', sc, 'main_ext', ext_only_segments=True, peak=True), 'through line: peak load on the line (peak h)': busiest('AM', sc, 'main_ext', peak=True)})
table(pd.DataFrame(rows), {'gain on the extension': '{:+.0f} %', 'gain on the line': '{:+.0f} %'}, font=7)
P('Table 4.2a — The same comparison for every scenario-year, AM three hours and AM peak-hour loads.').runs[0].font.size = Pt(8)
P(f'Reading. Through-running does not add riders to the extension in this model: {ref["LRT trips using the extension (at least one segment S01–S24)"]:,.0f} against {refE["LRT"]:,.0f} ({(ref["LRT trips using the extension (at least one segment S01–S24)"] / refE["LRT"] - 1) * 100:+.0f} %) in {REF_LAB}, and {(srow("AM", "BU_2040")["LRT trips using the extension (at least one segment S01–S24)"] / ext_row("AM", "BU_2040")["LRT"] - 1) * 100:+.0f} % in 2040 BU. '
  f'The {cross_hamifrats("AM", REF):,.0f} trips that cross Hamifrats on the through line ({cross_hamifrats("AM", REF) / ref["LRT"] * 100:.0f} % of its riders) exist in the terminating case too: there they reach the extension\'s Hamifrats station by Metronit or bus feeder and board the LRT at S24. Through-running replaces that feeder leg by an LRT leg for the same trips. '
  f'The +{(ref["LRT"] / refE["LRT"] - 1) * 100:.0f} % on the line as a whole is the main route\'s own market (trips between its stations and Hamifrats, {ref["LRT"] - ref["LRT trips using the extension (at least one segment S01–S24)"]:,.0f} trips), which a main line terminating at Hamifrats would carry as well; it is not a benefit of through-running. '
  'What through-running buys, in the model\'s terms, is the transfer it spares those crossing trips: a main line terminating at Hamifrats beside a terminating extension was not run, but it would put the 8-minute transfer penalty (plus a second wait) on every crossing trip, and with λ_T = 0.06 that is worth about a third of the odds of the LRT path on those pairs against the Metronit, which runs through without a transfer today. '
  'The reference figures therefore rest on caveat 28 (through-running without a transfer, a 5-minute headway on the whole line, 80 km/h at grade on the main route); the extension\'s own riders do not.')
H('4.2 Shift to the LRT and total demand by mode', 2)
landscape()
for p in ['AM', 'PM']:
    t = tabs[(p, REG)]
    P(f'Table 4.{3 if p == "AM" else 4} — {p} {"06:00–09:00" if p == "AM" else "16:00–19:00"}: the shift to the LRT and the demand by mode after the LRT, main route + extension, Prioritized (trips in three hours).').runs[0].font.bold = True
    a = t[['scenario', 'car before', 'bus before', 'BRT before', 'transit before', 'car → transit', 'car → LRT', 'BRT → LRT', 'bus → LRT']].copy()
    a['car → transit (% of car)'] = t['car → transit'] / t['car before'] * 100; a['BRT → LRT (% of BRT)'] = t['BRT → LRT'] / t['BRT before'] * 100; a['bus → LRT (% of bus)'] = t['bus → LRT'] / t['bus before'] * 100
    table(a, {'car → transit (% of car)': '{:.2f} %', 'BRT → LRT (% of BRT)': '{:.1f} %', 'bus → LRT (% of bus)': '{:.1f} %'}, font=7)
    P('Demand after the LRT and the share of each mode (of car + transit on the corridor market):').runs[0].font.italic = True
    b = t[['scenario', 'car after', 'BRT after', 'LRT', 'bus after', 'total transit after']].copy()
    for c in ['car share', 'BRT share', 'LRT share', 'bus share', 'transit share', 'LRT share of transit']: b[c] = t[c] * 100
    if summary_slow is not None:
        b['LRT, buses slower (sensitivity)'] = [srow(p, sc, REG, src=summary_slow)['LRT'] if sc in SLOW_FACTORS else np.nan for sc in ['2022'] + SCEN]
        b['LRT share of transit, buses slower'] = [srow(p, sc, REG, src=summary_slow)['LRT'] / srow(p, sc, REG, src=summary_slow)['total transit'] * 100 if sc in SLOW_FACTORS else np.nan for sc in ['2022'] + SCEN]
    table(b, {**{c: '{:.1f} %' for c in ['car share', 'BRT share', 'LRT share', 'bus share', 'transit share', 'LRT share of transit']}, 'LRT share of transit, buses slower': '{:.1f} %'}, font=7)
    P('The extension part, as part of the through line:').runs[0].font.italic = True
    c = t[['scenario', 'LRT', 'LRT (peak hour)', 'LRT using the extension', 'LRT using the extension (peak hour)', 'ext: from car', 'ext: from BRT', 'ext: from bus', 'LRT within the extension', 'busiest segment (3 h, one direction)', 'busiest segment (peak hour, one direction)']].copy()
    c['extension share of LRT trips'] = t['LRT using the extension'] / t['LRT'] * 100
    table(c, {'extension share of LRT trips': '{:.1f} %'}, font=7)
    doc.add_paragraph()
portrait()
P('Reading the tables. "Before" is the scenario\'s no-build market (car, bus incl. rail, BRT = Metronit) on the corridor TAZ pairs; the three shift columns are the trips the pivot moves to the LRT from each; "after" is what remains plus the LRT. '
  '"car → transit" is the trips the logsum improvement moves out of the car; "car → LRT" is the part of them the LRT itself carries (the rest board the bus or Metronit path of their pair). "BRT → LRT" and "bus → LRT" are the LRT trips drawn from existing transit on the pairs whose transit path is Metronit-based or bus-based; the three LRT columns add up to the LRT total. Taxi-type trips (about 700) are carried unchanged and are outside the shares. '
  'The extension columns count the LRT trips of the same run that ride at least one segment between S01 and S24 (from either end of the line), and separately those with both ends at extension stations. '
  'The last two columns of the demand table are the bus-slowdown sensitivity of 4.9 (mixed-traffic buses 10 % slower in 2040 and 20 % in 2050, Metronit and LRT unchanged); the 2022 row has no such case.')
P('A note on the car column. The AM shift from the car doubles between 2040 BU and 2050 BU (684 → 1,421) and between 2040 BU and 2040 HS (684 → 1,387) while the market grows by 16 % and 4 %. This is not a demand effect but the aggregation effect of caveat 27 seen across scenarios: '
  'the incremental shift of a TAZ pair is proportional to S·(1 − S) of its smoothed transit share, and the forecast sets of step 23 seed trips into TAZ pairs that are empty in 2022 (small-base and transforming TAZs receive the super-zone pattern), so the number of corridor pairs with both car and transit trips rises from 1,620 (2022) to 2,084 (2040 BU), 2,942 (2050 BU), 4,970 (2040 HS) and 5,688 (2050 HS) and the trip-weighted S·(1 − S) from 0.048 to 0.062. '
  'The PM sets, grown pair by pair from the PM base, keep the 2022 pair set and show a smooth car column (666 → 880). The car shift should therefore be read as an order of magnitude (300–1,300 trips, 0.4–1.5 % of the corridor car trips), not compared between scenarios (caveat 29).')
fig(f'{CFIG}/demand_by_scenario.png', 16, 'Figure 4.1 — Transit demand on the corridor by scenario, peak hour: no-build transit, total transit after the LRT, LRT trips, and the LRT trips using the extension (AM and PM).')
fig(f'{CFIG}/shift_sources.png', 16, 'Figure 4.2 — Where the LRT trips come from (car, Metronit, bus), whole line and the part using the extension, by scenario, peak hour.')
H('4.3 Where the demand comes from — markets', 2)
P(f'The LRT trips of the reference case grouped by the corridor areas of their two ends (Output/alternatives/AM/{REF}/main_ext_prioritized/t_lrt_area_v2.csv; both directions added), and the ten largest area pairs. "Haifa" is Matam to Hamifrats (areas 202–210); the Krayot (areas 101–104, 301–304) are off the line and reach it by bus or Metronit feeder; the main route is Bazan-Hutsot to Nazareth (211–217). "Crossing Hamifrats" is the load on the S24–M02 segment in both directions, i.e. every trip that rides from one side of the junction to the other.')
for sc in [REF, 'HS_2050']:
    ms, tot = market_summary('AM', sc); table(ms, {'share of all LRT trips': '{:.0f} %'}, font=7)
    P(f'Table 4.{5 if sc == REF else 6} — Markets of the LRT trips, AM three hours, {SCEN_LAB[sc]} (total {tot:,.0f}).').runs[0].font.size = Pt(8)
sym, tot, top_df = market_tables('AM', REF); table(top_df, {'share of all LRT trips': '{:.1f} %'}, font=7)
P(f'Table 4.7 — The ten largest area pairs of the LRT trips, AM three hours, {REF_LAB}.').runs[0].font.size = Pt(8)
P(f'Reading. In {REF_LAB} the market has three legs of similar size: Tirat Carmel ↔ Haifa ({mk_ref.iloc[1]["share of all LRT trips"]:.0f} %), Haifa internal ({mk_ref.iloc[0]["share of all LRT trips"]:.0f} %) and the Krayot reaching Haifa by feeder ({mk_ref.iloc[2]["share of all LRT trips"]:.0f} %); the main route\'s own areas add {mk_ref.iloc[3]["share of all LRT trips"]:.0f} % to Haifa and a few percent among themselves. '
  f'{mk_ref.iloc[7]["share of all LRT trips"]:.0f} % of the trips cross Hamifrats and {mk_ref.iloc[8]["share of all LRT trips"]:.0f} % stay between extension stations. Tirat Carmel ↔ Bat Galim is the single largest pair. The HS 2050 set reads differently — Haifa internal a third, Tirat Carmel a tenth — because the high scenario moves population and jobs into Haifa\'s TAZs and seeds trips into pairs empty today (caveat 29); the composition, not only the total, is scenario-dependent, which is one reason to plan on the BU reference.')
H('4.4 What happens to the Metronit', 2)
P(f'The model keeps every bus and Metronit line as it runs today (the June 2026 timetable) in every scenario-year and adds the LRT as a new path. Nothing is cut. The {ref_brt_shift:,.0f} trips shown as moving from the Metronit in {REF_LAB} ({ref_brt_shift / ref["BRT before"] * 100:.0f} % of the corridor Metronit trips) are travellers on pairs whose best transit path today is the Metronit and for whom the LRT path is cheaper in generalized cost: a faster ride on the trunk, a station nearer their ends, or both. They choose the LRT while the Metronit still runs beside it. The remaining {ref["BRT (Metronit)"]:,.0f} Metronit trips stay because their path is still the cheaper one.')
P('Four consequences for reading the numbers:')
for s_ in ['The LRT and the Metronit coexist in the model on the whole trunk from Hof HaCarmel to the Krayot. The LRT\'s riders are, for the most part, today\'s transit riders on a better vehicle: the transit market itself grows only by the car shift, a few hundred to about a thousand trips in three hours. The LRT replaces existing transit capacity on the trunk far more than it creates a market.',
           f'Part of the "Metronit" and "bus" shift is a change of technology for one leg of the trip, not a new transit trip: the LRT path may begin or end with a Metronit or bus feeder (penalty 4 / 8 minutes), and such a trip is counted as an LRT trip. The Krayot market ({mk_ref.iloc[2]["LRT trips (3 h)"]:,.0f} trips) is almost entirely of this kind: Metronit riders who transfer to the LRT at Hamifrats or on the trunk. A rider count for the LRT is therefore a boarding count, not a count of trips that exist only because of the LRT.',
           'If the Metronit were reduced on the overlap after opening, the riders it keeps in the model (the pairs where it is still cheaper) would have to move to the LRT or to the bus: the LRT loads on the trunk would rise, bounded by the Metronit\'s corridor trips before the LRT (' + f'{ref["BRT before"]:,.0f} in {REF_LAB} AM). The reverse, a feeder reorganisation that brings Metronit lines to the LRT stations, would raise the LRT\'s access quality and its draw. Neither is modelled; the report\'s figures are for the coexistence case, which is the conservative one for the LRT.',
           'Whether the LRT and the Metronit are intended to coexist on the trunk is a network-planning decision outside this study. It changes the LRT\'s loads by up to the Metronit\'s trunk volume, more than any demand uncertainty in this report, and it should be settled before the figures are used for capacity.']:
    B(s_)
H('4.5 Flow on the line — LRT, both directions', 2)
P('Passengers on each segment of the line in the peak hour, by direction: towards Nazareth (S01 → S24 → M20) and towards Tirat Carmel (M20 → M01 → S01). The dashed line marks the junction of the extension (S24) with the main route (M01, the same station at Hamifrats). '
  'Source: lrt_line_loads.csv in each run folder (the LRT trips between the cheapest-access stations of each TAZ pair), scaled to the peak hour by the network bus factor of the direction.')
landscape()
fig(f'{CFIG}/flow_lrt_scenarios_AM.png', 25, 'Figure 4.3 — LRT flow by segment and direction, the four scenarios, AM.')
fig(f'{CFIG}/flow_lrt_scenarios_PM.png', 25, 'Figure 4.4 — LRT flow by segment and direction, the four scenarios, PM.')
fig(f'{CFIG}/flow_lrt_AM.png', 25, 'Figure 4.5 — LRT flow per scenario, both directions on one panel, AM (2022 and the four scenarios).')
fig(f'{CFIG}/flow_lrt_PM.png', 25, 'Figure 4.6 — LRT flow per scenario, both directions on one panel, PM.')
H('4.6 Flow on the line — total transit, both directions', 2)
P('The same profile for all transit trips of the corridor market (bus, Metronit and LRT after the LRT is added), loaded along the line between the LRT stations nearest their ends — the transit demand the line\'s corridor carries, of which the LRT takes the share shown in 4.2. '
  'Source: transit_line_loads.csv in each run folder, scaled to the peak hour as above.')
fig(f'{CFIG}/flow_transit_scenarios_AM.png', 25, 'Figure 4.7 — Total transit flow by segment and direction, the four scenarios, AM.')
fig(f'{CFIG}/flow_transit_scenarios_PM.png', 25, 'Figure 4.8 — Total transit flow by segment and direction, the four scenarios, PM.')
fig(f'{CFIG}/flow_transit_AM.png', 25, 'Figure 4.9 — Total transit flow per scenario, both directions, AM.')
fig(f'{CFIG}/flow_transit_PM.png', 25, 'Figure 4.10 — Total transit flow per scenario, both directions, PM.')
portrait()
H('4.7 Mode split on the route', 2)
P('The split of the corridor market between car and transit after the LRT, with the LRT shown within transit, by scenario and period.')
fig(f'{CFIG}/mode_split.png', 16, 'Figure 4.11 — Mode split on the corridor after the LRT: car, bus, Metronit and LRT, AM and PM.')
H('4.8 Sensitivity: the Unprioritized regime', 2)
rows = []
for p in ['AM', 'PM']:
    for sc in SCEN:
        a, b = srow(p, sc, 'prioritized'), srow(p, sc, 'unprioritized')
        rows.append({'period': p, 'scenario': SCEN_LAB[sc], 'LRT Prioritized': a['LRT'], 'LRT Unprioritized': b['LRT'], 'ratio': b['LRT'] / a['LRT'],
                     'using the extension, Prioritized': a['LRT trips using the extension (at least one segment S01–S24)'], 'using the extension, Unprioritized': b['LRT trips using the extension (at least one segment S01–S24)'],
                     'from car, Prioritized': a['LRT from car'], 'from car, Unprioritized': b['LRT from car']})
table(pd.DataFrame(rows), {'ratio': '{:.2f}'}, font=7)
P('Table 4.8 — LRT trips in the two regimes of the extension. The Unprioritized regime (at-grade running, 65.8 min end to end on the extension against 40.7) loses about a fifth of the LRT trips, most of it on the extension itself.').runs[0].font.size = Pt(8)
H('4.9 Sensitivity: slower buses in 2040 and 2050', 2)
P('Every scenario year runs on the May 2026 level of service: the car and the buses are as fast in 2050 as today while the corridor demand grows by 30–60 %. This is the "do-minimum network" convention, kept because the 2040 road and transit network of the regional model is not available and degrading today\'s network with tomorrow\'s demand while leaving out every planned scheme would be the worse assumption. '
  'Two things follow. First, a slower car would change nothing in this model: the pivot moves trips on the change of the transit bundle only, and the car\'s level enters through the observed 2022 shares (caveat 25); making the car count needs a no-build mode-choice step (handover item D-11). '
  'Second, slower buses do count: a bus in mixed traffic that slows with the road raises the bus generalized cost, while the Metronit on its lanes and a Prioritized LRT keep their times, so both the LRT share within transit and the draw from the car rise. The central assumption is therefore conservative for the LRT.')
P('The sensitivity: step 45 rerun with the running time of every bus ride that is not the Metronit multiplied by 1.10 in 2040 and 1.20 in 2050 (both BU and HS), the Metronit and the LRT unchanged, the bus feeder legs of the LRT paths slowed with the buses. '
  'The factors are a reading of a standard volume–delay curve for a road demand growing by 1.3–1.6 × from about 80 % of capacity, not a calibrated value: the May 2026 car speeds hardly move by hour (caveat 24) and cannot calibrate one. Source: Output/alternatives_bus_slow/demand_summary.csv.')
if summary_slow is not None:
    rows = []
    for p in ['AM', 'PM']:
        for sc in SCEN:
            a, b = srow(p, sc, REG), srow(p, sc, REG, src=summary_slow)
            rows.append({'period': p, 'scenario': SCEN_LAB[sc], 'bus factor': SLOW_FACTORS[sc], 'LRT central': a['LRT'], 'LRT, buses slower': b['LRT'], 'ratio': b['LRT'] / a['LRT'],
                         'from car, central': a['LRT from car'], 'from car, buses slower': b['LRT from car'], 'from bus/BRT, central': a['LRT from bus/BRT'], 'from bus/BRT, buses slower': b['LRT from bus/BRT'],
                         'using the extension, central': a['LRT trips using the extension (at least one segment S01–S24)'], 'using the extension, buses slower': b['LRT trips using the extension (at least one segment S01–S24)'],
                         'transit share after, central': a['total transit'] / (a['car'] + a['total transit']) * 100, 'transit share after, buses slower': b['total transit'] / (b['car'] + b['total transit']) * 100})
    sens = pd.DataFrame(rows); table(sens, {'bus factor': '{:.2f}', 'ratio': '{:.2f}', 'transit share after, central': '{:.1f} %', 'transit share after, buses slower': '{:.1f} %'}, font=7)
    sA = sens[sens.period == 'AM']
    P(f'Table 4.9 — LRT trips with slower buses against the central case, main route + extension, Prioritized (three hours). AM: the LRT gains {(sA["ratio"].min() - 1) * 100:+.0f} % to {(sA["ratio"].max() - 1) * 100:+.0f} %, from {sA["LRT central"].min():,.0f}–{sA["LRT central"].max():,.0f} to {sA["LRT, buses slower"].min():,.0f}–{sA["LRT, buses slower"].max():,.0f}.').runs[0].font.size = Pt(8)
else: P('[sensitivity run not found: Output/alternatives_bus_slow/]')
H('4.10 Time on route', 2)
rt = route[['mode', 'period', 'direction', 'from', 'to', 'scheduled_min (median)', 'observed_min (step 30 ratio)']].copy() if 'direction' in route.columns else route
rt.columns = [str(c) for c in rt.columns]; table(rt.head(40), {'scheduled_min (median)': '{:.0f}', 'observed_min (step 30 ratio)': '{:.0f}'}, font=7)
P('Table 4.10 — End-to-end times on the route by mode (Output/alternatives/time_on_route.csv). The LRT through line runs 74.3 min Prioritized / 99.6 min Unprioritized from Tirat Carmel to Nazareth (extension 40.7 / 65.8 min; main route 33.7 min at 80 km/h with 10 s dwell).').runs[0].font.size = Pt(8)
H('4.11 Maps', 2)
P('The map set of the alternatives report (Output/figures/alternatives/, 41 maps: line loads, origins and destinations of the LRT trips, LRT share, growth, shift sources and rates, travel-time maps) applies to these runs; four are reproduced here.')
fig(f'{FIG}/alternatives/map_line_loads_AM_HS_2050.png', 16, 'Figure 4.12 — LRT line loads and station boardings in the peak hour, HS 2050 AM.')
fig(f'{FIG}/alternatives/map_growth_by_scenario_AM.png', 16, 'Figure 4.13 — Growth of the LRT trips by TAZ, 2022 → each scenario, AM peak hour.')
fig(f'{FIG}/alternatives/map_shift_sources_AM_BU_2040.png', 16, 'Figure 4.14 — Sources of the LRT trips by TAZ (car, Metronit, bus), BU 2040 AM peak hour.')
fig(f'{FIG}/alternatives/map_time_lrt_vs_bus_AM.png', 16, 'Figure 4.15 — LRT against bus generalized cost by TAZ, AM.')

# ======================= 5 =======================
H('5. Conclusions')
tA = tabs[('AM', REG)].set_index('scenario'); tP = tabs[('PM', REG)].set_index('scenario')
lo, hi = tA.loc['2040 BU'], tA.loc['2050 HS']; fA = phf('AM', 'transit')
peak1_lo = loads('AM', 'BU_2040', 'lrt')['dir1_towards_Nazareth_end'].max(); peak1_hi = loads('AM', 'HS_2050', 'lrt')['dir1_towards_Nazareth_end'].max()
_pm = [loads('PM', sc, 'lrt') for sc in SCEN]; pm_d1_lo, pm_d1_hi = min(l['dir1_towards_Nazareth_end'].max() for l in _pm), max(l['dir1_towards_Nazareth_end'].max() for l in _pm); pm_d2_lo, pm_d2_hi = min(l['dir2_towards_TiratCarmel'].max() for l in _pm), max(l['dir2_towards_TiratCarmel'].max() for l in _pm)
for s_ in [f'Reference case. {REF_LAB}: {ref["LRT"]:,.0f} LRT riders in the AM three hours ({ref["LRT"] * fA:,.0f} in the peak hour), planning range {ref["LRT"] * RANGE_LO:,.0f}–{ref["LRT"] * RANGE_HI:,.0f} on the cost sensitivity; {ref["LRT trips using the extension (at least one segment S01–S24)"]:,.0f} use the extension against {refE["LRT"]:,.0f} if the extension terminated at Hamifrats; three markets of similar size (Tirat Carmel ↔ Haifa, Haifa internal, the Krayot by feeder); peak load {busiest("AM", REF, peak=True):,.0f} per hour and direction at the Hamifrats entry.',
           f'Demand. The through line (main route + extension) carries {lo["LRT"]:,.0f} trips in the AM three hours in 2040 BU and {hi["LRT"]:,.0f} in 2050 HS ({tA.loc["2050 BU", "LRT"]:,.0f} in 2050 BU, {tA.loc["2040 HS", "LRT"]:,.0f} in 2040 HS), that is {lo["LRT"]*fA:,.0f}–{hi["LRT"]*fA:,.0f} in the AM peak hour; the PM is {tP.loc["2040 BU", "LRT"]/lo["LRT"]*100:.0f} % of the AM. '
           f'Of these, {lo["LRT using the extension"]:,.0f}–{hi["LRT using the extension"]:,.0f} ({lo["LRT using the extension"]/lo["LRT"]*100:.0f} %) use the extension and {lo["LRT within the extension"]:,.0f}–{hi["LRT within the extension"]:,.0f} travel between extension stations only: the extension is where most of the line\'s riders are, the main route feeds it rather than the reverse.',
           f'Sources. The LRT is first a transit reorganisation: {lo["BRT → LRT"]:,.0f}–{hi["BRT → LRT"]:,.0f} trips come from the Metronit ({lo["BRT → LRT"]/lo["BRT before"]*100:.0f} % of its corridor trips), {lo["bus → LRT"]:,.0f}–{hi["bus → LRT"]:,.0f} from the bus, and {lo["car → LRT"]:,.0f}–{hi["car → LRT"]:,.0f} from the car ({lo["car → LRT"]/lo["car before"]*100:.1f} % of the corridor car trips). '
           f'The transit share of the corridor market rises by about {(lo["transit share"] - srow("AM", "BU_2040")["transit share before"])*100:.1f} points; the LRT takes {lo["LRT share of transit"]*100:.0f} % of transit.',
           f'Profile. In the AM the busiest segment is the entry into Hamifrats from the main route (S24–M02) in the direction towards Tirat Carmel, {lo["busiest segment (3 h, one direction)"]:,.0f} (2040 BU) to {hi["busiest segment (3 h, one direction)"]:,.0f} (2050 HS) passengers in three hours, {lo["busiest segment (peak hour, one direction)"]:,.0f}–{hi["busiest segment (peak hour, one direction)"]:,.0f} in the peak hour; in the direction towards Nazareth the peak is on the Carmel coast (S14–S15, {peak1_lo:,.0f}–{peak1_hi:,.0f} in the peak hour). '
           f'In the PM the two directions nearly balance (S24–M02 towards Nazareth {pm_d1_lo:,.0f}–{pm_d1_hi:,.0f} in the peak hour; S05–S06 or S11–S12 towards Tirat Carmel {pm_d2_lo:,.0f}–{pm_d2_hi:,.0f}). The main route beyond Kiryat Ata (M06 onwards) carries a few hundred per direction; the extension carries 4 of 5 riders.',
           'Growth. Between 2040 BU and 2050 HS the LRT demand grows by about 45 %, in step with the corridor transit market (×1.3–1.5 on 2022), because the forecast holds behaviour at 2022; the HS scenario adds 15–25 % over BU in the same year.',
           'Regime. Priority at the interchanges is worth about 20–25 % of the LRT trips: at-grade running of the extension lengthens its end-to-end time from 41 to 66 minutes and loses a fifth of the riders, mostly on the extension.',
           'Robustness. The central figures sit within a range of about −25 % / +40 % from the cost sensitivity and the LRT premium alone (step 40); the level of service is held at May 2026 in every year, and if the buses slow with the road (10 % in 2040, 20 % in 2050) the LRT gains ' + (f'{(sA["ratio"].min() - 1) * 100:.0f}–{(sA["ratio"].max() - 1) * 100:.0f} % in the AM' if summary_slow is not None else 'a few percent') + ' (section 4.9), so the constant-LOS central case is conservative for the LRT; the car-to-LRT shift is the least certain component (caveats 15, 25, 27) and should be read as an order of magnitude; the bus and Metronit shifts rest on observed shares and measured service and are the firmer part.',
           'Fitness. The results support the sizing and location of the extension\'s market, the ranking of the regimes, and the design-hour scale of the trunk load. They do not support capacity, fleet or frequency decisions or an appraisal without a validated assignment and a full mode-choice model; the next steps are a purpose split of the survey, a PM-specific forecast, the main route\'s operating plan, and a choice-rider λ from a stated-preference or a revealed choice set with the car cost in it.']:
    B(s_)
P('Repository record: METHODOLOGY.md §6aq (step 45) and §8; docs/PLAIN_ENGLISH_METHODOLOGY.md Part 5; the alternatives report reports/LRT_Alternatives_Demand_Report.docx and its workbook Output/alternatives/LRT_alternatives_matrices.xlsx; this report\'s builder tools/build_comprehensive_report.py.')
os.makedirs('reports', exist_ok=True); doc.save('reports/Nofit_LRT_Extension_Comprehensive_Report.docx'); print('report written')
for (p, reg), t in tabs.items(): t.to_csv(f'{OUT}/shift_table_{p}_{reg}.csv', index=False)
print('shift tables written')
