"""Peak-hour factors for the alternatives' charts (step 45 / the comprehensive report): step 27's method (Corridor_peak_hour_V2_routes.ipynb,
the busiest sliding 60-minute window of the survey's departures, trips allocated to the V2 areas, link-crossing weights by direction on the
tree network) run on the PM window 16:00-19:00, beside the AM values of step 27 (Output/corridor_v2/peak_hour_factors_v2.csv).
Writes Output/corridor_v2/peak_hour_factors_v2_pm.csv (the PM table, same layout as step 27's) and Output/alternatives/peak_hour_factors.csv
(period x layer {car, transit} x direction {up, down, all}: network factors by direction, study-area factor for the totals; transit = bus).
Needs the LFS inputs of step 27 (trips file, TAZ_2636 keys, Corridor_TAZ_Agg_V2). Run:  python3 tools/peak_hour_factors_periods.py  (about 2 minutes)"""
import os, sys
while not os.path.exists('METHODOLOGY.md') and os.getcwd() != '/': os.chdir('..')
H0 = 16
# All paths in this notebook are relative to the repository root; anchor the working directory there
import os
while not os.path.exists('METHODOLOGY.md') and os.getcwd() != '/': os.chdir('..')
assert os.path.exists('METHODOLOGY.md'), 'run from inside the Nofit_LRT_Extension repository'



import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BLUE, ORANGE, AQUA, PURPLE, INK, INK2, MUTED, GRID, AXIS = '#2a78d6', '#eb6834', '#1baf7a', '#7b5bd6', '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7'
OUT = 'Output/corridor_v2'; os.makedirs(OUT, exist_ok=True); os.makedirs('Output/figures', exist_ok=True)
def style_ax(ax, title=None, xlabel=None, ylabel=None):
    ax.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
    for s in ax.spines.values(): s.set_color(AXIS)
    ax.tick_params(colors=INK2, labelsize=9)
    if title: ax.set_title(title, color=INK, fontsize=11)
    if xlabel: ax.set_xlabel(xlabel, color=INK2, fontsize=10)
    if ylabel: ax.set_ylabel(ylabel, color=INK2, fontsize=10)

# ---- survey trips with minute-level departure time (same extraction as steps 15 / 20) ----
df = pd.read_excel('Input/THS_2017-2018/trips_ths_2017.xlsx')
d = df.sort_values(['PerID3', 'SurveyDay', 'placeno']).copy(); g = d.groupby(['PerID3', 'SurveyDay'])
d['origin'] = g['actTaz'].shift(1); d['trip_dep_h'] = g['Dep_h'].shift(1); d['dep'] = g['STDep'].shift(1)
trips = d.dropna(subset=['origin', 'actTaz', 'trip_dep_h']); trips = trips[trips['trip_dep_h'].isin([H0, H0 + 1, H0 + 2])].copy()
NB = 12; trips['bin'] = ((trips['dep'] - float(H0)) * 4).astype(int).clip(0, NB - 1)
COMP = {'CAR': [10, 11], 'BUS': [3, 5], 'TAXI': [4, 8], 'RAIL': [7]}   # codes confirmed against the activities file, step 33 (23 Sep 2026): 3 Public Bus, 5 Matronit; 4 group taxi, 8 special taxi
trips['comp'] = trips['mainmode'].map(lambda m: next((k for k, v in COMP.items() if m in v), 'OTHER'))
k26 = pd.read_excel('Input/TAZ_2636_Keys.xlsx').drop_duplicates('TAZ_2636'); map_2636_1250 = k26.set_index('TAZ_2636')['TAZ_1250']
trips['o1250'] = trips['origin'].map(map_2636_1250); trips['d1250'] = trips['actTaz'].map(map_2636_1250)
KEYS_LFS = 'Input/Matrices/1270_02_09_2021_TAZ_North_keys.csv'
keys_raw = pd.read_csv('Input/taz_keys_from_shapefile.csv') if open(KEYS_LFS, 'rb').read(40).startswith(b'version https://git-lfs') else pd.read_csv(KEYS_LFS, encoding='windows-1255')
kd = keys_raw[['TAZ_1270', 'TAZ_NUMBER', 'SZ_NEW']].dropna(subset=['TAZ_NUMBER']).astype({'TAZ_NUMBER': int, 'SZ_NEW': int}).drop_duplicates('TAZ_NUMBER')
TAZ = np.array(sorted(kd['TAZ_NUMBER'])); N = len(TAZ); taz_pos = {t: i for i, t in enumerate(TAZ)}
children = kd.groupby('TAZ_1270')['TAZ_NUMBER'].apply(list); north_1250 = sorted(children.index); z_idx = {z: i for i, z in enumerate(north_1250)}
tm = trips[trips['o1250'].isin(z_idx) & trips['d1250'].isin(z_idx)].copy(); tm['oi'] = tm['o1250'].map(z_idx); tm['di'] = tm['d1250'].map(z_idx)
zon = pd.read_csv('Input/Zonal_2020.csv', encoding='windows-1255').set_index('TAZ_ID').reindex(TAZ)
pop, emp = zon['POPULATION'].fillna(0).values, zon['EMPL_TOT'].fillna(0).values
def alloc(primary, secondary):
    S = np.zeros((len(north_1250), N))
    for z, kids in children.items():
        idx = [taz_pos[t] for t in kids]
        for v in (primary[idx], secondary[idx], np.ones(len(idx))):
            if v.sum() > 0: S[z_idx[z], idx] = v / v.sum(); break
    return S
S_o, S_d = alloc(pop, emp), alloc(emp, pop)
# ---- V2 areas, routes and the tree ----
xl = pd.ExcelFile('Input/Corridor_TAZ_Agg_V2.xlsx'); areas = xl.parse('AreaCodes').set_index('AggCode'); key = xl.parse('TazAgg')
area_of = key.set_index('TAZ')['AggCode']; AREAS = list(areas.index); apos = {a: i for i, a in enumerate(AREAS)}; names = areas['AggAreaName']
ROUTES = {r: list(areas[areas[f'Order_{r}'] > 0].sort_values(f'Order_{r}').index) for r in ['T1', 'T2', 'T3']}
TRUNK = [a for a in ROUTES['T1'] if all(a in ROUTES[r] for r in ROUTES)]; BRANCH = {r: [a for a in seq if a not in TRUNK] for r, seq in ROUTES.items()}
M_area = np.zeros((N, len(AREAS)))
for i, t in enumerate(TAZ):
    if t in area_of.index: M_area[i, apos[area_of[t]]] = 1
SA_o, SA_d = S_o @ M_area, S_d @ M_area
# tree path: number of links crossed in each direction between two areas
def to_root(a):
    if a in TRUNK: return list(reversed(TRUNK[:TRUNK.index(a) + 1]))
    r = next(r for r in ROUTES if a in BRANCH[r]); i = BRANCH[r].index(a)
    return list(reversed(BRANCH[r][:i + 1])) + list(reversed(TRUNK))
def dir_links(o, d_):
    if o == d_: return 0, 0
    po, pd_ = to_root(o), to_root(d_); common = next(a for a in po if a in set(pd_))
    return pd_.index(common), po.index(common)          # (links up, links down)
UPL = np.array([[dir_links(o, d_)[0] for d_ in AREAS] for o in AREAS]); DNL = np.array([[dir_links(o, d_)[1] for d_ in AREAS] for o in AREAS])
print(f"AM trips in the study area: {len(tm):,} sampled; V2: {len(AREAS)} areas, routes " + ', '.join(f'{r} {len(s)} areas' for r, s in ROUTES.items()))



def pair_table(sub):
    """Long table: sampled trip row, origin area, destination area, allocation share (product of the two shares)."""
    So, Sd = SA_o[sub['oi'].values], SA_d[sub['di'].values]; rows = []
    for r_, (so, sd) in enumerate(zip(So, Sd)):
        nzo, nzd = np.nonzero(so)[0], np.nonzero(sd)[0]
        for co in nzo:
            for cd in nzd:
                if co != cd: rows.append((r_, co, cd, so[co] * sd[cd]))
    return pd.DataFrame(rows, columns=['row', 'o', 'd', 'share'])
def window_stats(s):
    s = np.asarray(s, float); tot = s.sum()
    if tot <= 0: return dict(PHF3h=np.nan, start=np.nan, PHF60=np.nan)
    p = s / tot; win = np.array([p[i:i + 4].sum() for i in range(NB - 3)]); k = int(np.argmax(win))
    return dict(PHF3h=win[k], start=H0 + k / 4, PHF60=win[k] / (4 * p[k:k + 4].max()))
LAYERS = ['CAR', 'BUS', 'TAXI']; rng = np.random.default_rng(7); B = 50
prof = {}; rows = []
for comp in LAYERS:
    sub = tm[tm['comp'] == comp].reset_index(drop=True); pt = pair_table(sub)
    pt['wf'] = sub['new_wf'].values[pt['row']]; pt['bin'] = sub['bin'].values[pt['row']]; pt['hh'] = sub['HHID3'].values[pt['row']]
    for scope in ['T1', 'T2', 'T3', 'network']:
        seq = ROUTES.get(scope); t = pt.copy()
        if seq is not None:
            spos = {apos[a]: i for i, a in enumerate(seq)}; t = t[t['o'].isin(spos) & t['d'].isin(spos)].copy()
            t['up'] = np.clip(t['d'].map(spos) - t['o'].map(spos), 0, None); t['down'] = np.clip(t['o'].map(spos) - t['d'].map(spos), 0, None)
        else:
            t['up'] = UPL[t['o'].values, t['d'].values]; t['down'] = DNL[t['o'].values, t['d'].values]
        for dname in ['up', 'down']:
            td = t[t[dname] > 0].copy(); td['w'] = td['share'] * td['wf'] * td[dname]           # link-crossing weight in this direction
            prof[(comp, scope, dname)] = td
            s = np.bincount(td['bin'].values, weights=td['w'].values, minlength=NB); st = window_stats(s)
            hh_ids = np.unique(td['hh'].values); hpos = {h: i for i, h in enumerate(hh_ids)}; hidx = np.array([hpos[h] for h in td['hh'].values], dtype=int); b3, b60 = [], []   # dtype fixed 23 Sep 2026: a layer-direction with no sampled trips (taxi-type under the corrected codes) gave an empty float index
            for _ in range(B):
                mult = np.bincount(rng.integers(0, len(hh_ids), len(hh_ids)), minlength=len(hh_ids))
                sb = np.bincount(td['bin'].values, weights=td['w'].values * mult[hidx], minlength=NB); sbst = window_stats(sb); b3.append(sbst['PHF3h']); b60.append(sbst['PHF60'])
            rows.append({'scope': scope, 'layer': comp, 'direction': dname, 'n sampled': int(td['row'].nunique()), **st, 'PHF3h p5': np.nanpercentile(b3, 5), 'PHF3h p95': np.nanpercentile(b3, 95), 'PHF60 p5': np.nanpercentile(b60, 5), 'PHF60 p95': np.nanpercentile(b60, 95)})
for comp in LAYERS + ['RAIL']:
    sub = tm[tm['comp'] == comp]; st = window_stats(sub.groupby('bin')['new_wf'].sum().reindex(range(NB)).fillna(0).values)
    rows.append({'scope': 'study area', 'layer': comp, 'direction': '—', 'n sampled': len(sub), **st})
phf = pd.DataFrame(rows)
phf['peak hour'] = phf['start'].map(lambda s: f"{int(s):02d}:{int((s % 1) * 60):02d}–{int(s + 1):02d}:{int((s % 1) * 60):02d}" if pd.notna(s) else '')

phf['window'] = f'{H0:02d}:00–{H0+3:02d}:00'
phf.to_csv('Output/corridor_v2/peak_hour_factors_v2_pm.csv', index=False, float_format='%.4f')
am = pd.read_csv('Output/corridor_v2/peak_hour_factors_v2.csv')
rows = []
for period, tab in (('AM', am), ('PM', phf)):
    for layer, lay in (('car', 'CAR'), ('transit', 'BUS')):
        for direction in ('up', 'down'):
            r = tab[(tab.scope == 'network') & (tab.layer == lay) & (tab.direction == direction)].iloc[0]
            rows.append({'period': period, 'layer': layer, 'direction': direction, 'PHF3h': r['PHF3h'], 'peak hour': r['peak hour'], 'n sampled': int(r['n sampled']),
                         'basis': f"step 27's method, network scope, {lay} trips crossing links in this direction" + ('' if period == 'AM' else ', PM window 16:00–19:00')})
        r = tab[(tab.scope == 'study area') & (tab.layer == lay)].iloc[0]
        rows.append({'period': period, 'layer': layer, 'direction': 'all', 'PHF3h': r['PHF3h'], 'peak hour': r['peak hour'], 'n sampled': int(r['n sampled']),
                     'basis': f"step 27's method, study area, all {lay} trips" + ('' if period == 'AM' else ', PM window 16:00–19:00')})
out = pd.DataFrame(rows); out.to_csv('Output/alternatives/peak_hour_factors.csv', index=False, float_format='%.4f'); print(out.to_string(index=False))
