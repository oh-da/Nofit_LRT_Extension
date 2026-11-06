"""The Metronit scenario against the central case: tables, charts and a Markdown note.

The scenario (step 45 with METRONIT_CUT="BU_2040,BU_2050,HS_2040,HS_2050", ALT_OUT=Output/alternatives_metronit_krayot;
pipeline step v45_metro; METHODOLOGY §6aq addendum 5): once the LRT runs, the Metronit serves the Krayot only, up to
Merkazit Hamifrats; in Haifa and Tirat Carmel the LRT is the one mass-transit mode beside the train and the buses.

Reads   Output/alternatives/demand_summary.csv (central) and Output/alternatives_metronit_krayot/demand_summary.csv,
        the per-run area matrices, line loads and station boardings of both, Output/alternatives/peak_hour_factors.csv.
Writes  Output/alternatives_metronit_krayot/comparison_vs_central.csv            every run of both folders side by side
        Output/alternatives_metronit_krayot/markets_vs_central_AM.csv            the LRT trips by market group (through line, Prioritized)
        Output/alternatives_metronit_krayot/line_loads_vs_central_{AM,PM}.csv    loads by segment and direction, three hours and peak hour
        Output/alternatives_metronit_krayot/station_boardings_vs_central_AM.csv  boardings and alightings by station
        Output/alternatives_metronit_krayot/figures/*.png                        the charts (one chart per file, one scale per set)
        docs/METRONIT_KRAYOT_SCENARIO_2026-11-05.md                               the note, every number read from the files above
Run     python3 tools/metronit_scenario_summary.py        (after v45_metro; seconds)
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

while not os.path.exists('METHODOLOGY.md') and os.getcwd() != '/': os.chdir('..')
assert os.path.exists('METHODOLOGY.md'), 'run from inside the Nofit_LRT_Extension repository'

CEN, SCN = 'Output/alternatives', 'Output/alternatives_metronit_krayot'; FIG = f'{SCN}/figures'; os.makedirs(FIG, exist_ok=True)
NOTE = 'docs/METRONIT_KRAYOT_SCENARIO_2026-11-05.md'
BLUE, ORANGE, AQUA, PURPLE, INK, INK2, MUTED, GRID = '#2a78d6', '#eb6834', '#1baf7a', '#7b5bd6', '#0b0b0b', '#52514e', '#898781', '#e1e0d9'
SCEN = ['BU_2040', 'BU_2050', 'HS_2040', 'HS_2050']; SCEN_LAB = {'2022': '2022', 'BU_2040': '2040 BU', 'BU_2050': '2050 BU', 'HS_2040': '2040 HS', 'HS_2050': '2050 HS'}
ALT, REG = 'main_ext', 'prioritized'; REF = 'BU_2050'
ALT_LAB = {'main_ext': 'Main route + extension', 'ext': 'Extension only'}; REG_LAB = {'prioritized': 'Prioritized', 'unprioritized': 'Unprioritized'}
KEEP = ['car', 'bus', 'BRT (Metronit)', 'LRT', 'total transit', 'LRT from bus/BRT', 'LRT from car', 'car before', 'transit before', 'BRT before', 'transit share after', 'LRT share of transit',
        'LRT trips on the extension stations (both ends on S01–S24)', 'LRT trips using the extension (at least one segment S01–S24)', 'LRT from car using the extension', 'LRT from bus using the extension',
        'LRT from BRT using the extension', 'busiest segment load (3 h, one direction)']
SHORT = {'LRT trips on the extension stations (both ends on S01–S24)': 'LRT both ends on extension', 'LRT trips using the extension (at least one segment S01–S24)': 'LRT using the extension',
         'busiest segment load (3 h, one direction)': 'busiest segment (3 h)'}

cen = pd.read_csv(f'{CEN}/demand_summary.csv'); scn = pd.read_csv(f'{SCN}/demand_summary.csv')
PHF = pd.read_csv(f'{CEN}/peak_hour_factors.csv').set_index(['period', 'layer', 'direction'])['PHF3h']
xl = pd.ExcelFile('Input/Corridor_TAZ_Agg_V2.xlsx', engine='openpyxl'); names = xl.parse('AreaCodes').set_index('AggCode')['AggAreaName']
KEYS = ['period', 'scenario', 'alternative', 'regime']
for d in (cen, scn): d['regime'] = d['regime'].str.split(' (', regex=False).str[0]

# ---- 1. every run side by side --------------------------------------------------------------------------------------------
m = cen[KEYS + KEEP].merge(scn[KEYS + KEEP + ['TAZ pairs with transit dearer than today', 'transit trips on those pairs before', 'transit lost to the car on those pairs', 'LRT trips on those pairs']], on=KEYS, suffixes=(' central', ' scenario'))
m['LRT ratio'] = m['LRT scenario'] / m['LRT central']; m['car change central'] = m['car before central'] - m['car central']; m['car change scenario'] = m['car before scenario'] - m['car scenario']
m.to_csv(f'{SCN}/comparison_vs_central.csv', index=False, float_format='%.1f')
base_eq = m[m.scenario == '2022']; max_dev = float((base_eq[[k + ' scenario' for k in KEEP]].values - base_eq[[k + ' central' for k in KEEP]].values).__abs__().max())
print(f'2022 rows (no cut): largest absolute difference from the central run over {len(KEEP)} columns × {len(base_eq)} runs = {max_dev:.3f}')

def row(d, p, sc, alt=ALT, reg=REG):
    s = d[(d.period == p) & (d.scenario == sc) & (d.alternative == ALT_LAB[alt]) & (d.regime == REG_LAB[reg])]; assert len(s) == 1; return s.iloc[0]

# ---- 2. markets of the LRT trips (AM, through line, Prioritized) -------------------------------------------------------------
GRP = {**{201: 'Tirat Carmel'}, **{a: 'Haifa (Matam – Hamifrats)' for a in range(202, 211)}, **{a: 'Main route (Kiryat Ata – Nazareth)' for a in range(211, 218)}, **{a: 'Krayot (off the line, by feeder)' for a in [101, 102, 103, 104, 301, 302, 303, 304]}}
ORDER = ['Tirat Carmel', 'Haifa (Matam – Hamifrats)', 'Krayot (off the line, by feeder)', 'Main route (Kiryat Ata – Nazareth)']
def area_mat(root, p, sc, kind, alt=ALT, reg=REG):
    a = pd.read_csv(f'{root}/{p}/{sc}/{alt}_{reg}/{kind}_area_v2.csv', index_col=0); a.columns = a.columns.astype(int); return a
def markets(root, p, sc, kind='t_lrt'):
    a = area_mat(root, p, sc, kind); G = a.copy(); G.index = [GRP[x] for x in G.index]; G.columns = [GRP[x] for x in G.columns]
    GG = G.groupby(level=0).sum().T.groupby(level=0).sum().T.reindex(index=ORDER, columns=ORDER); sym = (GG + GG.T).values.copy(); np.fill_diagonal(sym, np.diag(GG.values))
    sym = pd.DataFrame(sym, index=ORDER, columns=ORDER); T_, H_, K_, M_ = ORDER
    return {'Tirat Carmel ↔ Haifa': sym.loc[T_, H_], 'Haifa internal': sym.loc[H_, H_], 'Krayot ↔ Haifa (by feeder)': sym.loc[K_, H_], 'Main route ↔ Haifa': sym.loc[M_, H_],
            'Main route ↔ Krayot / Tirat Carmel': sym.loc[M_, K_] + sym.loc[M_, T_], 'within the main route': sym.loc[M_, M_], 'Krayot ↔ Tirat Carmel': sym.loc[K_, T_], 'total': float(a.values.sum())}
mk_rows = []
for sc in SCEN:
    c, s = markets(CEN, 'AM', sc), markets(SCN, 'AM', sc)
    for k in c: mk_rows.append({'scenario': SCEN_LAB[sc], 'market': k, 'LRT central (3 h)': c[k], 'LRT scenario (3 h)': s[k], 'difference': s[k] - c[k], 'ratio': s[k] / c[k] if c[k] else np.nan})
mk = pd.DataFrame(mk_rows); mk.to_csv(f'{SCN}/markets_vs_central_AM.csv', index=False, float_format='%.1f')
# where the Metronit trips of today go in the scenario: by area group of the pair (AM, REF)
def source_split(root, p, sc):
    out = {}
    for kind in ('from_brt', 'from_bus', 'from_car', 't_brt', 't_bus', 't_car_new', 't_tr_new'):
        a = area_mat(root, p, sc, kind); G = a.copy(); G.index = [GRP[x] for x in G.index]; G.columns = [GRP[x] for x in G.columns]
        GG = G.groupby(level=0).sum().T.groupby(level=0).sum().T.reindex(index=ORDER, columns=ORDER); out[kind] = GG
    return out

# ---- 3. line loads and boardings (through line, Prioritized) -------------------------------------------------------------------
ll_rows = {}
for p in ('AM', 'PM'):
    fu, fd = float(PHF[(p, 'transit', 'up')]), float(PHF[(p, 'transit', 'down')]); parts = []
    for sc in SCEN:
        c = pd.read_csv(f'{CEN}/{p}/{sc}/{ALT}_{REG}/lrt_line_loads.csv'); s = pd.read_csv(f'{SCN}/{p}/{sc}/{ALT}_{REG}/lrt_line_loads.csv')
        d = c[['from_station', 'to_station']].copy(); d['scenario'] = SCEN_LAB[sc]
        d['to Nazareth central (3 h)'] = c['dir1_towards_Nazareth_end']; d['to Nazareth scenario (3 h)'] = s['dir1_towards_Nazareth_end']
        d['to Tirat Carmel central (3 h)'] = c['dir2_towards_TiratCarmel']; d['to Tirat Carmel scenario (3 h)'] = s['dir2_towards_TiratCarmel']
        d['to Nazareth central (peak hour)'] = c['dir1_towards_Nazareth_end'] * fu; d['to Nazareth scenario (peak hour)'] = s['dir1_towards_Nazareth_end'] * fu
        d['to Tirat Carmel central (peak hour)'] = c['dir2_towards_TiratCarmel'] * fd; d['to Tirat Carmel scenario (peak hour)'] = s['dir2_towards_TiratCarmel'] * fd
        parts.append(d)
    ll_rows[p] = pd.concat(parts); ll_rows[p].to_csv(f'{SCN}/line_loads_vs_central_{p}.csv', index=False, float_format='%.1f')
bd_parts = []
for sc in SCEN:
    c = pd.read_csv(f'{CEN}/AM/{sc}/{ALT}_{REG}/lrt_stations_boardings.csv'); s = pd.read_csv(f'{SCN}/AM/{sc}/{ALT}_{REG}/lrt_stations_boardings.csv')
    d = c[['station', 'line', 'TAZ', 'AggCode']].copy(); d['scenario'] = SCEN_LAB[sc]; d['area'] = d['AggCode'].map(lambda a: names.get(int(a), '') if pd.notna(a) else '')
    d['boardings central'] = c['boardings']; d['boardings scenario'] = s['boardings']; d['alightings central'] = c['alightings']; d['alightings scenario'] = s['alightings']; bd_parts.append(d)
bd = pd.concat(bd_parts); bd.to_csv(f'{SCN}/station_boardings_vs_central_AM.csv', index=False, float_format='%.1f')

# ---- 4. charts: one chart per file, one scale per set ------------------------------------------------------------------------
def style(ax):
    ax.grid(axis='y', color=GRID, lw=.6); ax.set_axisbelow(True)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
ymax = max(cen[cen.scenario.isin(SCEN) & (cen.alternative == ALT_LAB[ALT]) & (cen.regime == 'Prioritized')]['LRT'].max(), scn[scn.scenario.isin(SCEN) & (scn.alternative == ALT_LAB[ALT]) & (scn.regime == 'Prioritized')]['LRT'].max()) * 1.15
for p in ('AM', 'PM'):
    fig, ax = plt.subplots(figsize=(8, 4.2)); xs = np.arange(len(SCEN))
    cv = [row(cen, p, sc)['LRT'] for sc in SCEN]; sv = [row(scn, p, sc)['LRT'] for sc in SCEN]
    ax.bar(xs - .2, cv, .4, color=BLUE, label='central case (every Metronit line as today)'); ax.bar(xs + .2, sv, .4, color=ORANGE, label='Metronit on the Krayot side of Hamifrats only')
    for x, a, b in zip(xs, cv, sv): ax.text(x - .2, a, f'{a:,.0f}', ha='center', va='bottom', fontsize=8, color=INK2); ax.text(x + .2, b, f'{b:,.0f}\n({(b / a - 1) * 100:+.0f} %)', ha='center', va='bottom', fontsize=8, color=INK)
    ax.set_xticks(xs); ax.set_xticklabels([SCEN_LAB[sc] for sc in SCEN]); ax.set_ylim(0, ymax); ax.set_ylabel(f'LRT trips, {p} three hours'); style(ax)
    ax.set_title(f'LRT trips by scenario-year, {p} — main route + extension, Prioritized', fontsize=10); ax.legend(frameon=False, fontsize=8, loc='upper left')
    plt.tight_layout(); plt.savefig(f'{FIG}/lrt_trips_vs_central_{p}.png', dpi=150); plt.close()
lmax = max(ll_rows['AM'][[c for c in ll_rows['AM'].columns if 'peak hour' in c]].values.max(), ll_rows['PM'][[c for c in ll_rows['PM'].columns if 'peak hour' in c]].values.max()) * 1.1
for p in ('AM', 'PM'):
    for dirn, lab in (('to Tirat Carmel', 'towards Tirat Carmel'), ('to Nazareth', 'towards Nazareth')):
        d = ll_rows[p][ll_rows[p].scenario == SCEN_LAB[REF]]; xs = np.arange(len(d)); fig, ax = plt.subplots(figsize=(13, 4.2))
        ax.bar(xs - .2, d[f'{dirn} central (peak hour)'], .4, color=BLUE, label='central case'); ax.bar(xs + .2, d[f'{dirn} scenario (peak hour)'], .4, color=ORANGE, label='Metronit on the Krayot side only')
        ax.set_xticks(xs[::2]); ax.set_xticklabels(d['from_station'].iloc[::2], rotation=90, fontsize=7); ax.set_ylim(0, lmax); ax.set_ylabel('LRT trips on the segment, peak hour'); style(ax)
        ax.set_title(f'LRT flow by segment {lab}, {SCEN_LAB[REF]}, {p} peak hour — main route + extension, Prioritized', fontsize=10); ax.legend(frameon=False, fontsize=8)
        plt.tight_layout(); plt.savefig(f'{FIG}/line_loads_vs_central_{p}_{REF}_{dirn.replace(" ", "_")}.png', dpi=150); plt.close()
fig, ax = plt.subplots(figsize=(9, 4.2)); xs = np.arange(len(SCEN)); w = .2
for i, (col, lab, color) in enumerate((('car', 'car', MUTED), ('bus', 'bus', AQUA), ('BRT (Metronit)', 'Metronit', PURPLE), ('LRT', 'LRT', ORANGE))):
    ax.bar(xs + (i - 1.5) * w, [row(scn, 'AM', sc)[col] - row(cen, 'AM', sc)[col] for sc in SCEN], w, color=color, label=lab)
ax.axhline(0, color=INK, lw=.8); ax.set_xticks(xs); ax.set_xticklabels([SCEN_LAB[sc] for sc in SCEN]); ax.set_ylabel('trips, scenario − central (AM 3 h)'); style(ax)
ax.set_title('Corridor trips by mode after the LRT: the Metronit scenario minus the central case, AM — main route + extension, Prioritized', fontsize=10); ax.legend(frameon=False, fontsize=8)
plt.tight_layout(); plt.savefig(f'{FIG}/mode_change_vs_central_AM.png', dpi=150); plt.close()
print('charts written to', FIG)

# ---- 5. the note ---------------------------------------------------------------------------------------------------------------
def f0(x): return f'{x:,.0f}'
def pct(a, b): return f'{(a / b - 1) * 100:+.0f} %'
def md_table(df, fmt=None):
    fmt = fmt or {}; cols = list(df.columns); out = ['| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)]
    for _, r in df.iterrows(): out.append('| ' + ' | '.join(fmt.get(c, lambda v: f'{v:,.0f}' if isinstance(v, (int, float, np.floating, np.integer)) and pd.notna(v) else str(v))(r[c]) for c in cols) + ' |')
    return '\n'.join(out)
L = []
A = {sc: (row(cen, 'AM', sc), row(scn, 'AM', sc)) for sc in SCEN}; Pm = {sc: (row(cen, 'PM', sc), row(scn, 'PM', sc)) for sc in SCEN}
cR, sR = A[REF]
L.append('# The Metronit scenario: the Metronit kept on the Krayot side of Merkazit Hamifrats only — 2040 / 2050 × BU / HS\n')
L.append('**5 November 2026.** Step 45 rerun with `METRONIT_CUT="BU_2040,BU_2050,HS_2040,HS_2050"` (pipeline step `v45_metro`, METHODOLOGY §6aq addendum 5), '
         'output `Output/alternatives_metronit_krayot/`. Every number here is read from that folder and from the central run (`Output/alternatives/`) by '
         '`tools/metronit_scenario_summary.py`, which also writes the comparison tables and the charts named below. Three-hour periods unless the peak hour is named.\n')
L.append('## 1. The scenario\n')
L.append('Once the LRT runs, the Metronit serves the Krayot only, up to Merkazit Hamifrats; in Haifa and Tirat Carmel the LRT is the one mass-transit mode beside the '
         'train and the buses. In the model: every Metronit ride edge with a stop in Haifa proper or Tirat Carmel (the zonal superzones 13–17 and 24 — the Carmel coast and '
         'Hof HaCarmel, Bat Galim and Kiryat Eliezer, the lower city, Hadar, the Check Post / Gesher Paz, Tirat Carmel) is removed from the transit graph of the four '
         'forecast sets; the edges between the Krayot, Kiryat Haim, the Hamifrats bay zone (Merkazit Hamifrats, Lev Hamifrats, the refineries, Tsomet Kiryat Ata), Nesher and '
         'Yagur stay. Lines 1 and its limited-stop twin run Merkazit Hamifrats ↔ Merkazit HaKrayot, line 3 Merkazit Hamifrats ↔ Kiryat Ata, line 2 keeps its Krayot ↔ Hamifrats '
         'legs and loses its Hadar loop, the Yagur – Nesher line ends at Nesher. Of the 170 Metronit stops 97 stay and 73 go. The buses (every line as it runs today), the train, '
         'the car and the LRT (through line, main route + extension, 5-minute headway) are as in the central case; the 2022 base keeps today\'s network.\n')
L.append('The pivot measures the transit nest\'s change from **today\'s** network: a pair that gains the LRT moves trips from the car as before; a pair that loses its Metronit '
         'without an LRT worth the change loses transit share to the car. The LRT\'s share within transit is taken against the scenario\'s best no-LRT path, so where the Metronit '
         'is gone the LRT competes with the bus alone and carries the bus premium (5 generalized minutes) rather than the Metronit\'s (2.5). Without a cut the formula is step 31\'s '
         f'exactly: the 2022 rows of the scenario run reproduce the central run to {max_dev:.1f} trips.\n')
L.append('## 2. The headline: LRT trips, main route + extension, Prioritized\n')
rows = []
for p, D in (('AM', A), ('PM', Pm)):
    for sc in SCEN:
        c, s = D[sc]; rows.append({'period': p, 'scenario-year': SCEN_LAB[sc], 'LRT central': c['LRT'], 'LRT scenario': s['LRT'], 'change': pct(s['LRT'], c['LRT']),
                                   'using the extension, central': c['LRT trips using the extension (at least one segment S01–S24)'], 'using the extension, scenario': s['LRT trips using the extension (at least one segment S01–S24)'],
                                   'from car, central': c['LRT from car'], 'from car, scenario': s['LRT from car'], 'busiest segment (3 h), central': c['busiest segment load (3 h, one direction)'], 'busiest segment (3 h), scenario': s['busiest segment load (3 h, one direction)']})
L.append(md_table(pd.DataFrame(rows), {'change': str}))
L.append('')
fA, fP = float(PHF[('AM', 'transit', 'all')]), float(PHF[('PM', 'transit', 'all')])
L.append(f'Peak hour (the survey\'s factors, AM {fA:.2f} / PM {fP:.2f} of the three hours; the upper reading, caveat 18): {SCEN_LAB[REF]} AM {f0(sR["LRT"] * fA)} LRT trips against {f0(cR["LRT"] * fA)} in the central case; '
         f'PM {f0(Pm[REF][1]["LRT"] * fP)} against {f0(Pm[REF][0]["LRT"] * fP)}.\n')
L.append('## 3. Where the trips come from and where the Metronit riders go\n')
rows = []
for sc in SCEN:
    c, s = A[sc]
    rows.append({'scenario-year': SCEN_LAB[sc], 'corridor Metronit riders today': c['BRT before'], 'Metronit riders after, central': c['BRT (Metronit)'], 'Metronit riders after, scenario': s['BRT (Metronit)'],
                 'bus riders after, central': c['bus'], 'bus riders after, scenario': s['bus'], 'car → transit, central': c['car before'] - c['car'], 'car → transit, scenario': s['car before'] - s['car'],
                 'pairs with transit dearer than today': s['TAZ pairs with transit dearer than today'], 'their transit trips today': s['transit trips on those pairs before'], 'of which lost to the car': s['transit lost to the car on those pairs'], 'of which on the LRT': s['LRT trips on those pairs']})
tab = pd.DataFrame(rows)
L.append(md_table(tab)); L.append('')
sp_c, sp_s = source_split(CEN, 'AM', REF), source_split(SCN, 'AM', REF)
L.append(f'Sources of the LRT trips, AM {SCEN_LAB[REF]} (the source is the pair\'s path type today: Metronit-based, bus-based, or the car):\n')
rows = []
for kind, lab in (('from_brt', 'from Metronit-based pairs'), ('from_bus', 'from bus-based pairs'), ('from_car', 'from the car')):
    rows.append({'source': lab, 'central': float(sp_c[kind].values.sum()), 'scenario': float(sp_s[kind].values.sum()), 'difference': float(sp_s[kind].values.sum() - sp_c[kind].values.sum())})
L.append(md_table(pd.DataFrame(rows))); L.append('')
L.append('## 4. The markets of the LRT trips, AM\n')
L.append(md_table(mk[mk.scenario.isin([SCEN_LAB[REF], SCEN_LAB['HS_2050']])].rename(columns={'scenario': 'scenario-year', 'LRT central (3 h)': 'LRT central', 'LRT scenario (3 h)': 'LRT scenario'}), {'ratio': lambda v: f'{v:.2f}'}))
L.append(f'\nThe full table for the four scenario-years is `markets_vs_central_AM.csv`.\n')
L.append('## 5. Line loads and stations\n')
rows = []
for p in ('AM', 'PM'):
    d = ll_rows[p]
    for sc in SCEN:
        e = d[d.scenario == SCEN_LAB[sc]]
        for dirn in ('to Tirat Carmel', 'to Nazareth'):
            ic, is_ = e[f'{dirn} central (peak hour)'].idxmax(), e[f'{dirn} scenario (peak hour)'].idxmax()
            rows.append({'period': p, 'scenario-year': SCEN_LAB[sc], 'direction': dirn, 'busiest segment, central': f"{e.loc[ic, 'from_station']}–{e.loc[ic, 'to_station']}", 'peak-hour load, central': e.loc[ic, f'{dirn} central (peak hour)'],
                         'busiest segment, scenario': f"{e.loc[is_, 'from_station']}–{e.loc[is_, 'to_station']}", 'peak-hour load, scenario': e.loc[is_, f'{dirn} scenario (peak hour)'],
                         'busiest extension segment, scenario': (lambda ee: f"{ee.loc[ee[f'{dirn} scenario (peak hour)'].idxmax(), 'from_station']}–{ee.loc[ee[f'{dirn} scenario (peak hour)'].idxmax(), 'to_station']}")(e[e.to_station.str.startswith('S')]),
                         'its peak-hour load': e[e.to_station.str.startswith('S')][f'{dirn} scenario (peak hour)'].max()})
L.append(md_table(pd.DataFrame(rows), {'busiest segment, central': str, 'busiest segment, scenario': str, 'busiest extension segment, scenario': str})); L.append('')
b = bd[bd.scenario == SCEN_LAB[REF]].copy(); b['gain'] = b['boardings scenario'] + b['alightings scenario'] - b['boardings central'] - b['alightings central']
top = b.sort_values('gain', ascending=False).head(8)[['station', 'area', 'boardings central', 'boardings scenario', 'alightings central', 'alightings scenario', 'gain']]
L.append(f'Stations with the largest gain of boardings + alightings, AM {SCEN_LAB[REF]}:\n'); L.append(md_table(top)); L.append('')
L.append('## 6. The other alternative and regime\n')
rows = []
for p in ('AM', 'PM'):
    for sc in SCEN:
        for alt in ('main_ext', 'ext'):
            for reg in ('prioritized', 'unprioritized'):
                c, s = row(cen, p, sc, alt, reg), row(scn, p, sc, alt, reg); rows.append({'period': p, 'scenario-year': SCEN_LAB[sc], 'alternative': ALT_LAB[alt], 'regime': REG_LAB[reg], 'LRT central': c['LRT'], 'LRT scenario': s['LRT'], 'change': pct(s['LRT'], c['LRT'])})
L.append(md_table(pd.DataFrame(rows), {'change': str})); L.append('')
L.append('## 7. Charts\n')
for f_ in sorted(os.listdir(FIG)): L.append(f'- `{FIG}/{f_}`')
L.append('\n## 8. How to read it\n')
L.append('- The scenario is a **network decision**, not a demand uncertainty: the comprehensive report\'s section 4.4 anticipated that a reduced Metronit would raise the LRT\'s '
         'trunk loads by up to the Metronit\'s corridor volume. This run puts a number on it with the model\'s own choice mechanism; the comprehensive report carries it as section 4.10.')
L.append('- The cut reads the superzone of each stop\'s TAZ from `Zonal_2020.csv` (`SZ_NEW`). Caveat 19 notes that this column disagrees with the chain\'s key table in 142 TAZs; 18 of the 60 TAZs with a '
         'Metronit stop are among them, every one on the same side of the cut under either key, so the partition of the 170 stops is the same.')
L.append('- What is not modelled: no bus restructuring beside the cut (the buses parallel to the Metronit\'s former Haifa section keep running, so the no-LRT alternative in Haifa is the bus, '
         'not nothing), no capacity on the LRT or at Merkazit Hamifrats, no change of Metronit frequencies, no fare, no park-and-ride. The λ, the out-of-vehicle weights, the peak-hour factor and the '
         'aggregation dependence of the pivot (caveats 15, 18, 27, 33) apply as in the central case; the planning range of the central case (λ 0.02–0.05) scales this scenario the same way.')
L.append('- The transit lost to the car is the pivot\'s reading of the pairs whose Metronit is gone and whose LRT path is dearer than today\'s Metronit path (long walks to a station, a '
         'feeder transfer); it is small against the market and is an upper reading, since those riders would in practice also find restructured buses.')
open(NOTE, 'w').write('\n'.join(L) + '\n'); print('note written:', NOTE)
print(pd.DataFrame([{'period': p, 'scenario': SCEN_LAB[sc], 'LRT central': D[sc][0]['LRT'], 'LRT scenario': D[sc][1]['LRT'], 'change': pct(D[sc][1]['LRT'], D[sc][0]['LRT'])} for p, D in (('AM', A), ('PM', Pm)) for sc in SCEN]).round(0).to_string(index=False))
