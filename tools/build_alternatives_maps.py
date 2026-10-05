"""Maps for the LRT alternatives (step 45, METHODOLOGY §6aq): time, demand, line loads and differences, from Output/alternatives/.
All volumes (trips, line loads, boardings) are for the peak hour of the period (Output/alternatives/peak_hour_factors.csv); the time maps and the shift rates are unaffected.
Writes Output/figures/alternatives/*.png; run after notebooks/current/LRT_alternatives_demand.ipynb and before tools/build_alternatives_report.py:
    python3 tools/build_alternatives_maps.py"""
import os
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, TwoSlopeNorm
from matplotlib.cm import ScalarMappable
from shapely.geometry import LineString
while not os.path.exists('METHODOLOGY.md') and os.getcwd() != '/': os.chdir('..')
OUT = 'Output/alternatives'; FIG = 'Output/figures/alternatives'; os.makedirs(FIG, exist_ok=True)
BLUE, ORANGE, AQUA, PURPLE, INK, INK2, MUTED, GRID, AXIS = '#2a78d6', '#eb6834', '#1baf7a', '#7b5bd6', '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7'
ALTS = {'main_ext': 'Main route + extension', 'ext': 'Extension only'}; REGIMES = {'prioritized': 'Prioritized', 'unprioritized': 'Unprioritized'}
COMBOS = [(a, r) for a in ALTS for r in REGIMES]
tzg = gpd.read_file('Input/TAZ_North/TAZ_North.shp', engine='pyogrio'); tzg['TAZ'] = tzg['TAZ_NUMBER'].astype(int); tzg = tzg.drop_duplicates('TAZ').set_index('TAZ')
legend = pd.read_csv('Output/corridor_v2/area_legend_v2.csv'); legend.columns = [c.strip() for c in legend.columns]
name_col = [c for c in legend.columns if 'name' in c.lower()][0]; code_col = [c for c in legend.columns if 'code' in c.lower()][0]; NAMES = legend.set_index(code_col)[name_col].to_dict()
STN = {a: pd.read_csv(f'{OUT}/stations_{a}.csv') for a in ALTS}; MAIN = pd.read_csv(f'{OUT}/main_route_nodes.csv')
ext_line = LineString(STN['ext'][['x', 'y']].values); main_line = LineString(MAIN[['x', 'y']].values)
TAZS = sorted(set(pd.read_csv(f'{OUT}/AM/2022/ext_prioritized/t_lrt_area_v2.csv', index_col=0).index) | set())   # placeholder, replaced below
def rd(path):
    m = pd.read_csv(path, index_col=0); m.columns = m.columns.astype(int); m.index = m.index.astype(int); return m
# peak-hour factors (tools/peak_hour_factors_periods.py, step 27's method on the AM and PM windows): every volume map is drawn for the
# peak hour of its period — car and transit totals by the study-area factor of the layer, line loads by the network bus factor of the direction
PHF = pd.read_csv(f'{OUT}/peak_hour_factors.csv').set_index(['period', 'layer', 'direction'])['PHF3h']
def phf(p, layer, direction='all'): return float(PHF[(p, layer, direction)])
def loads_ph(p, sc, a, r):
    l = pd.read_csv(f'{OUT}/{p}/{sc}/{a}_{r}/lrt_line_loads.csv').copy(); l['dir1_towards_Nazareth_end'] *= phf(p, 'transit', 'up'); l['dir2_towards_TiratCarmel'] *= phf(p, 'transit', 'down'); return l
def boardings_ph(p, sc, a, r):
    b = pd.read_csv(f'{OUT}/{p}/{sc}/{a}_{r}/lrt_stations_boardings.csv').copy(); b[['boardings', 'alightings']] *= phf(p, 'transit'); return b
T_LRT = {}; T_TR = {}
def run(p, sc, a, r):
    k = (p, sc, a, r)
    if k not in T_LRT: T_LRT[k] = rd(f'{OUT}/{p}/{sc}/{a}_{r}/t_lrt_taz.csv.gz') * phf(p, 'transit'); T_TR[k] = rd(f'{OUT}/{p}/{sc}/{a}_{r}/t_tr_new_taz.csv.gz') * phf(p, 'transit')
    return T_LRT[k], T_TR[k]
TAZS = list(rd(f'{OUT}/AM/2022/ext_prioritized/t_lrt_taz.csv.gz').index); corr = tzg.loc[[t for t in TAZS if t in tzg.index]]
XMIN, XMAX, YMIN, YMAX = 188000, 236000, 727000, 752000
def base(ax, title):
    tzg.boundary.plot(ax=ax, color='#eeede8', lw=.25); corr.boundary.plot(ax=ax, color=AXIS, lw=.35)
    ax.set_xlim(XMIN, XMAX); ax.set_ylim(YMIN, YMAX); ax.set_axis_off(); ax.set_title(title, fontsize=9, loc='left')
def draw_lines(ax, alt, lw=1.2):
    ax.plot(*ext_line.xy, color=INK, lw=lw, alpha=.8)
    if alt == 'main_ext': ax.plot(*main_line.xy, color=INK, lw=lw, alpha=.8)
def choropleth(ax, series, title, cmap, norm, label, alt=None, fmt='{:,.0f}'):
    base(ax, title); g = corr.assign(v=series.reindex(corr.index).values)
    g.plot(ax=ax, column='v', cmap=cmap, norm=norm, edgecolor=AXIS, linewidth=.3, missing_kwds={'color': '#f4f3ef'})
    if alt: draw_lines(ax, alt)
    cb = plt.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax, shrink=.55, pad=.01); cb.set_label(label, fontsize=8); cb.ax.tick_params(labelsize=7)
def offset(seg, d):
    try: return seg.parallel_offset(d, 'left' if d > 0 else 'right')
    except Exception: return seg
def flow_map(ax, p, sc, a, r, wmax, title):
    base(ax, title); st = STN[a]; loads = loads_ph(p, sc, a, r); bo = boardings_ph(p, sc, a, r)
    xy = st.set_index('station_id')[['x', 'y']]
    for _, s in loads.iterrows():
        seg = LineString([xy.loc[s['from_station']].values, xy.loc[s['to_station']].values])
        for col, c, sign in (('dir1_towards_Nazareth_end', BLUE, 1), ('dir2_towards_TiratCarmel', ORANGE, -1)):
            w = s[col] / wmax * 9
            if w > 0.05:
                g = offset(seg, sign * 120); xs, ys = (g.xy if g.geom_type == 'LineString' else list(g.geoms)[0].xy); ax.plot(xs, ys, color=c, lw=max(w, .4), solid_capstyle='butt', alpha=.9)
    ax.scatter(st['x'], st['y'], s=4 + bo['boardings'].values / bo['boardings'].max() * 120, facecolor='white', edgecolor=INK, lw=.6, zorder=5)
def lrt_sum(p, sc, a, r, axis): T, _ = run(p, sc, a, r); return T.sum(axis=axis)
# ---------------- demand maps ----------------
for p, sc in (('AM', 'BU_2040'), ('PM', 'BU_2040'), ('AM', '2022'), ('AM', 'HS_2050')):
    wmax = max(loads_ph(p, sc, a, r)[['dir1_towards_Nazareth_end', 'dir2_towards_TiratCarmel']].values.max() for a, r in COMBOS)
    fig, axes = plt.subplots(2, 2, figsize=(16, 13))
    for ax, (a, r) in zip(axes.ravel(), COMBOS): flow_map(ax, p, sc, a, r, wmax, f'{ALTS[a]}, {REGIMES[r]} — {p} {sc}')
    axes[0, 0].plot([], [], color=BLUE, lw=4, label='towards Nazareth / Hamifrats end'); axes[0, 0].plot([], [], color=ORANGE, lw=4, label='towards Tirat Carmel'); axes[0, 0].scatter([], [], s=60, facecolor='white', edgecolor=INK, label='station (size = boardings)'); axes[0, 0].legend(loc='lower right', fontsize=8, frameon=False)
    fig.suptitle(f'LRT line loads by segment and direction (width ∝ trips, max {wmax:,.0f} in the peak hour) and station boardings — {p} {sc}', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_line_loads_{p}_{sc}.png', dpi=130); plt.close()
    for axis, lab in ((1, 'origins'), (0, 'destinations')):
        vals = {c: lrt_sum(p, sc, c[0], c[1], axis) for c in COMBOS}; vmax = max(v.max() for v in vals.values())
        fig, axes = plt.subplots(2, 2, figsize=(16, 13)); norm = Normalize(0, vmax)
        for ax, c in zip(axes.ravel(), COMBOS): choropleth(ax, vals[c], f'{ALTS[c[0]]}, {REGIMES[c[1]]}', 'YlGnBu', norm, f'LRT trip {lab} per TAZ, {p} peak hour', alt=c[0])
        fig.suptitle(f'LRT trip {lab} by TAZ — {p} {sc}', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_lrt_{lab}_{p}_{sc}.png', dpi=130); plt.close()
    # LRT share of transit by origin TAZ
    fig, axes = plt.subplots(2, 2, figsize=(16, 13)); norm = Normalize(0, 0.8)
    for ax, (a, r) in zip(axes.ravel(), COMBOS):
        T, TR = run(p, sc, a, r); sh = T.sum(1) / TR.sum(1).replace(0, np.nan); choropleth(ax, sh, f'{ALTS[a]}, {REGIMES[r]}', 'PuBuGn', norm, 'LRT share of transit trips from the TAZ', alt=a)
    fig.suptitle(f'LRT share of the transit trips by origin TAZ — {p} {sc}', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_lrt_share_{p}_{sc}.png', dpi=130); plt.close()
# ---------------- difference maps ----------------
p, sc = 'AM', 'BU_2040'
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
for ax, (axis, lab) in zip(axes, ((1, 'origins'), (0, 'destinations'))):
    d = lrt_sum(p, sc, 'main_ext', 'prioritized', axis) - lrt_sum(p, sc, 'ext', 'prioritized', axis); m = max(abs(d.min()), d.max())
    choropleth(ax, d, f'LRT trip {lab}: main route + extension minus extension only (Prioritized)', 'RdBu', TwoSlopeNorm(0, -m, m), f'difference in LRT {lab} per TAZ, {p} peak hour', alt='main_ext')
fig.suptitle(f'What the main route adds — {p} {sc}', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_diff_main_vs_ext_{p}_{sc}.png', dpi=130); plt.close()
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
for ax, a in zip(axes, ALTS):
    d = lrt_sum(p, sc, a, 'prioritized', 1) - lrt_sum(p, sc, a, 'unprioritized', 1); m = max(abs(d.min()), d.max(), 1)
    choropleth(ax, d, f'{ALTS[a]}: Prioritized minus Unprioritized, LRT trip origins', 'RdBu', TwoSlopeNorm(0, -m, m), f'difference in LRT origins per TAZ, {p} peak hour', alt=a)
fig.suptitle(f'What the underground extension adds — {p} {sc}', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_diff_prioritized_vs_unprioritized_{p}_{sc}.png', dpi=130); plt.close()
fig, axes = plt.subplots(1, 3, figsize=(22, 7)); v22 = lrt_sum('AM', '2022', 'main_ext', 'prioritized', 1); v50 = lrt_sum('AM', 'HS_2050', 'main_ext', 'prioritized', 1); vmax = max(v22.max(), v50.max())
choropleth(axes[0], v22, 'LRT trip origins, 2022', 'YlGnBu', Normalize(0, vmax), 'LRT origins per TAZ, AM peak hour', alt='main_ext'); choropleth(axes[1], v50, 'LRT trip origins, HS 2050', 'YlGnBu', Normalize(0, vmax), 'LRT origins per TAZ, AM peak hour', alt='main_ext')
d = v50 - v22; m = max(abs(d.min()), d.max()); choropleth(axes[2], d, 'HS 2050 minus 2022', 'RdBu', TwoSlopeNorm(0, -m, m), 'growth in LRT origins per TAZ', alt='main_ext')
fig.suptitle('Growth of the LRT demand, main route + extension, Prioritized, AM', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_growth_2022_to_HS2050_AM.png', dpi=130); plt.close()
fig, axes = plt.subplots(1, 2, figsize=(16, 7)); vam = lrt_sum('AM', 'BU_2040', 'main_ext', 'prioritized', 1); vpm = lrt_sum('PM', 'BU_2040', 'main_ext', 'prioritized', 1); vmax = max(vam.max(), vpm.max())
choropleth(axes[0], vam, 'AM 06:00–09:00', 'YlGnBu', Normalize(0, vmax), 'LRT origins per TAZ, peak hour', alt='main_ext'); choropleth(axes[1], vpm, 'PM 16:00–19:00', 'YlGnBu', Normalize(0, vmax), 'LRT origins per TAZ, peak hour', alt='main_ext')
fig.suptitle('LRT trip origins, AM against PM — main route + extension, Prioritized, BU 2040', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_lrt_origins_AM_vs_PM_BU_2040.png', dpi=130); plt.close()
# ---------------- time maps ----------------
bo = pd.read_csv(f'{OUT}/AM/BU_2040/main_ext_prioritized/lrt_stations_boardings.csv'); ref_station = bo.loc[bo['alightings'].idxmax()]; REF = int(ref_station['TAZ'])
ref_label = f"TAZ {REF} ({NAMES.get(int(ref_station['AggCode']), '')}, station {ref_station['station']})"
GC = {}
for p in ('AM', 'PM'):
    GC[(p, 'car')] = rd(f'{OUT}/{p}/car_gc_taz.csv.gz')
    for a in ALTS:
        GC[(p, 'bus', a)] = rd(f'{OUT}/{p}/transit_gc_no_lrt_taz_{a}.csv.gz')
        for r in REGIMES: GC[(p, 'lrt', a, r)] = rd(f'{OUT}/{p}/lrt_gc_taz_{a}_{r}.csv.gz')
for p in ('AM', 'PM'):
    fig, axes = plt.subplots(2, 2, figsize=(16, 13)); norm = Normalize(20, 120)
    for ax, (a, r) in zip(axes.ravel(), COMBOS): choropleth(ax, GC[(p, 'lrt', a, r)][REF], f'{ALTS[a]}, {REGIMES[r]}', 'RdYlGn_r', norm, f'LRT generalized minutes to {ref_label}', alt=a)
    fig.suptitle(f'Time by LRT (access + wait + ride + egress, generalized minutes) from every TAZ to {ref_label} — {p}', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_time_lrt_to_ref_{p}.png', dpi=130); plt.close()
    fig, axes = plt.subplots(1, 3, figsize=(22, 7)); bus = GC[(p, 'bus', 'main_ext')][REF]; lrt = GC[(p, 'lrt', 'main_ext', 'prioritized')][REF]
    choropleth(axes[0], bus, 'best bus / Metronit path, no LRT', 'RdYlGn_r', Normalize(20, 120), 'generalized minutes', alt=None)
    choropleth(axes[1], lrt, 'LRT, main route + extension, Prioritized', 'RdYlGn_r', Normalize(20, 120), 'generalized minutes', alt='main_ext')
    d = lrt - bus; choropleth(axes[2], d, 'LRT minus best bus (negative = LRT cheaper)', 'RdBu_r', TwoSlopeNorm(0, -40, 40), 'generalized minutes', alt='main_ext')
    fig.suptitle(f'Transit time to {ref_label}: today\'s best bus / Metronit path against the LRT — {p}', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_time_lrt_vs_bus_{p}.png', dpi=130); plt.close()
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
for ax, p in zip(axes, ('AM', 'PM')): choropleth(ax, GC[(p, 'car')][REF], f'car, {p} ({"07:00" if p == "AM" else "17:00"} speeds) + 3 min terminal', 'RdYlGn_r', Normalize(5, 70), 'minutes', alt='main_ext')
fig.suptitle(f'Car time to {ref_label}', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_time_car.png', dpi=130); plt.close()
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
for ax, (a, r) in zip(axes, (('main_ext', 'prioritized'), ('ext', 'prioritized'))):
    ratio = GC[('AM', 'lrt', a, r)][REF] / GC[('AM', 'car')][REF]; choropleth(ax, ratio, f'{ALTS[a]}, Prioritized: LRT ÷ car generalized time', 'RdYlGn_r', Normalize(1, 5), 'ratio', alt=a)
fig.suptitle(f'LRT against the car, generalized time to {ref_label} — AM', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_time_lrt_over_car_AM.png', dpi=130); plt.close()
# ---------------- volumes ----------------
def runmat(p, sc, a, r, k, scale=True): return rd(f'{OUT}/{p}/{sc}/{a}_{r}/{k}_taz.csv.gz') * (phf(p, 'car' if k.startswith('t_car') else 'transit') if scale else 1.0)
for p, sc in (('AM', 'BU_2040'), ('PM', 'BU_2040')):
    fig, axes = plt.subplots(2, 2, figsize=(16, 13)); bmax = max(boardings_ph(p, sc, a, r)[['boardings', 'alightings']].values.max() for a, r in COMBOS)
    for ax, (a, r) in zip(axes.ravel(), COMBOS):
        base(ax, f'{ALTS[a]}, {REGIMES[r]}'); draw_lines(ax, a); st = STN[a]; bo = boardings_ph(p, sc, a, r)
        ax.scatter(st['x'] - 150, st['y'], s=4 + bo['boardings'] / bmax * 700, facecolor=BLUE, edgecolor='white', lw=.4, alpha=.75, zorder=5)
        ax.scatter(st['x'] + 150, st['y'], s=4 + bo['alightings'] / bmax * 700, facecolor=ORANGE, edgecolor='white', lw=.4, alpha=.75, zorder=5)
        for _, s in bo.nlargest(6, 'boardings').iterrows(): ax.annotate(f"{s['station']} {s['boardings']:,.0f}", (st.loc[st['station_id'] == s['station'], 'x'].iloc[0], st.loc[st['station_id'] == s['station'], 'y'].iloc[0]), fontsize=6, color=INK2, xytext=(4, 4), textcoords='offset points')
    axes[0, 0].scatter([], [], s=200, color=BLUE, alpha=.75, label='boardings'); axes[0, 0].scatter([], [], s=200, color=ORANGE, alpha=.75, label='alightings'); axes[0, 0].legend(loc='lower right', frameon=False, fontsize=8)
    fig.suptitle(f'Station volumes: boardings and alightings in the peak hour (largest {bmax:,.0f}), six busiest labelled — {p} {sc}', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_station_volumes_{p}_{sc}.png', dpi=130); plt.close()
    fig, axes = plt.subplots(1, 3, figsize=(22, 7)); a, r = 'main_ext', 'prioritized'
    tr = runmat(p, sc, a, r, 't_tr_new').sum(1); car_ = runmat(p, sc, a, r, 't_car_new').sum(1); lrt = runmat(p, sc, a, r, 't_lrt').sum(1)
    choropleth(axes[0], car_, 'car trips from the TAZ (after the LRT)', 'YlOrBr', Normalize(0, car_.quantile(.98)), f'car trips, {p} peak hour', alt=a)
    choropleth(axes[1], tr, 'transit trips from the TAZ (bus + Metronit + LRT)', 'YlGnBu', Normalize(0, tr.quantile(.98)), f'transit trips, {p} peak hour', alt=a)
    choropleth(axes[2], lrt / tr.replace(0, np.nan), 'LRT share of the TAZ\'s transit trips', 'PuBuGn', Normalize(0, .8), 'share', alt=a)
    fig.suptitle(f'Trip volumes by origin TAZ — main route + extension, Prioritized, {p} {sc}', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_trip_volumes_{p}_{sc}.png', dpi=130); plt.close()
# ---------------- growth ----------------
a, r = 'main_ext', 'prioritized'; v22 = lrt_sum('AM', '2022', a, r, 1)
fig, axes = plt.subplots(2, 2, figsize=(16, 13)); vmax = max(abs(lrt_sum('AM', sc, a, r, 1) - v22).max() for sc in ('BU_2040', 'BU_2050', 'HS_2040', 'HS_2050'))
for ax, sc in zip(axes.ravel(), ('BU_2040', 'BU_2050', 'HS_2040', 'HS_2050')):
    d = lrt_sum('AM', sc, a, r, 1) - v22; choropleth(ax, d, f'{sc.replace("_", " ")} minus 2022: LRT trip origins (total {d.sum():+,.0f})', 'RdBu', TwoSlopeNorm(0, -vmax, vmax), 'change in LRT origins per TAZ, AM peak hour', alt=a)
fig.suptitle('Growth of the LRT demand by scenario-year — main route + extension, Prioritized, AM', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_growth_by_scenario_AM.png', dpi=130); plt.close()
fig, axes = plt.subplots(1, 2, figsize=(16, 7)); wmax = max(loads_ph('AM', sc, a, r)[['dir1_towards_Nazareth_end', 'dir2_towards_TiratCarmel']].values.max() for sc in ('2022', 'HS_2050'))
for ax, sc in zip(axes, ('2022', 'HS_2050')): flow_map(ax, 'AM', sc, a, r, wmax, f'line loads, AM {sc.replace("_", " ")} (max {wmax:,.0f})')
fig.suptitle('Growth of the line loads, 2022 against HS 2050 — main route + extension, Prioritized, AM (same width scale)', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_growth_line_loads_AM.png', dpi=130); plt.close()
# ---------------- shift to the LRT by source ----------------
for p, sc in (('AM', 'BU_2040'), ('PM', 'BU_2040'), ('AM', '2022')):
    fig, axes = plt.subplots(1, 3, figsize=(22, 7)); a, r = 'main_ext', 'prioritized'
    fc, fb, fm = (runmat(p, sc, a, r, k).sum(1) for k in ('from_car', 'from_bus', 'from_brt')); vmax = max(fb.max(), fm.max())
    choropleth(axes[0], fc, f'from the car ({fc.sum():,.0f} trips)', 'YlOrRd', Normalize(0, max(fc.max(), 1)), f'LRT trips drawn from the car, by origin TAZ, {p} peak hour', alt=a)
    choropleth(axes[1], fb, f'from the bus ({fb.sum():,.0f} trips)', 'YlGnBu', Normalize(0, vmax), f'LRT trips drawn from bus-based paths, {p} peak hour', alt=a)
    choropleth(axes[2], fm, f'from the Metronit ({fm.sum():,.0f} trips)', 'BuPu', Normalize(0, vmax), f'LRT trips drawn from Metronit-based paths, {p} peak hour', alt=a)
    fig.suptitle(f'Where the LRT trips come from, by origin TAZ — main route + extension, Prioritized, {p} {sc}', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_shift_sources_{p}_{sc}.png', dpi=130); plt.close()
    fig, axes = plt.subplots(2, 2, figsize=(16, 13)); vals = {c: runmat(p, sc, c[0], c[1], 'from_car').sum(1) for c in COMBOS}; vmax = max(v.max() for v in vals.values())
    for ax, c in zip(axes.ravel(), COMBOS): choropleth(ax, vals[c], f'{ALTS[c[0]]}, {REGIMES[c[1]]} ({vals[c].sum():,.0f} trips)', 'YlOrRd', Normalize(0, vmax), f'LRT trips drawn from the car, by origin TAZ, {p} peak hour', alt=c[0])
    fig.suptitle(f'Shift from the car to the LRT by origin TAZ — {p} {sc}', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_shift_from_car_{p}_{sc}.png', dpi=130); plt.close()
    fig, axes = plt.subplots(1, 2, figsize=(16, 7)); a, r = 'main_ext', 'prioritized'
    carb = runmat(p, sc, a, r, 't_car_base', False).sum(1); trb = runmat(p, sc, a, r, 't_tr_base', False).sum(1); fc = runmat(p, sc, a, r, 'from_car', False).sum(1); fo = (runmat(p, sc, a, r, 'from_bus', False) + runmat(p, sc, a, r, 'from_brt', False)).sum(1)
    choropleth(axes[0], fc / carb.replace(0, np.nan) * 100, 'car trips lost to the LRT, % of the TAZ\'s car trips', 'YlOrRd', Normalize(0, 3), '% of car trips', alt=a)
    choropleth(axes[1], fo / trb.replace(0, np.nan) * 100, 'bus and Metronit trips lost to the LRT, % of the TAZ\'s transit trips', 'YlGnBu', Normalize(0, 80), '% of transit trips', alt=a)
    fig.suptitle(f'Shift rates by origin TAZ — main route + extension, Prioritized, {p} {sc}', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_shift_rates_{p}_{sc}.png', dpi=130); plt.close()
print(f'maps written to {FIG}; reference destination {ref_label}'); print(len(os.listdir(FIG)), 'maps')
# ---------------- single-panel maps for the comprehensive report (one map per file, shared scales across scenario-years) ----------------
SFIG = f'{FIG}/single'; os.makedirs(SFIG, exist_ok=True); a, r = 'main_ext', 'prioritized'
SCS_ALL = ['2022', 'BU_2040', 'BU_2050', 'HS_2040', 'HS_2050']
import textwrap
def single(title, draw, fname, figsize=(12, 6.8)):
    fig_, ax_ = plt.subplots(figsize=figsize); draw(ax_); ax_.set_title(textwrap.fill(title, 120), fontsize=9, loc='left'); plt.tight_layout(); plt.savefig(f'{SFIG}/{fname}', dpi=150, bbox_inches='tight'); plt.close()
# line loads: one width scale and one boarding scale over every period and scenario-year
wmax_all = max(loads_ph(p, sc, a, r)[['dir1_towards_Nazareth_end', 'dir2_towards_TiratCarmel']].values.max() for p in ('AM', 'PM') for sc in SCS_ALL)
bmax_all = max(boardings_ph(p, sc, a, r)['boardings'].max() for p in ('AM', 'PM') for sc in SCS_ALL)
def flow_map_scaled(ax, p, sc, title):
    base(ax, title); st = STN[a]; ld = loads_ph(p, sc, a, r); bo = boardings_ph(p, sc, a, r); xy = st.set_index('station_id')[['x', 'y']]
    for _, s_ in ld.iterrows():
        seg = LineString([xy.loc[s_['from_station']].values, xy.loc[s_['to_station']].values])
        for col, c, sign in (('dir1_towards_Nazareth_end', BLUE, 1), ('dir2_towards_TiratCarmel', ORANGE, -1)):
            w = s_[col] / wmax_all * 9
            if w > 0.05:
                g = offset(seg, sign * 120); xs, ys = (g.xy if g.geom_type == 'LineString' else list(g.geoms)[0].xy); ax.plot(xs, ys, color=c, lw=max(w, .4), solid_capstyle='butt', alpha=.9)
    ax.scatter(st['x'], st['y'], s=4 + bo['boardings'].values / bmax_all * 120, facecolor='white', edgecolor=INK, lw=.6, zorder=5)
    ax.plot([], [], color=BLUE, lw=4, label='towards Nazareth'); ax.plot([], [], color=ORANGE, lw=4, label='towards Tirat Carmel'); ax.scatter([], [], s=60, facecolor='white', edgecolor=INK, label=f'station (size = boardings; largest {bmax_all:,.0f})'); ax.legend(loc='lower right', fontsize=8, frameon=False)
for p in ('AM', 'PM'):
    for sc in SCS_ALL:
        single(f'LRT line loads by segment and direction, {p} peak hour, {sc.replace("_", " ")} — main route + extension, Prioritized (width ∝ passengers; the same scale on every map, max {wmax_all:,.0f})', lambda ax_: flow_map_scaled(ax_, p, sc, ''), f'map_line_loads_{p}_{sc}.png')
# growth of the LRT origins 2022 -> each scenario-year, one colour scale
v22 = lrt_sum('AM', '2022', a, r, 1); vmax_g = max(abs(lrt_sum('AM', sc, a, r, 1) - v22).max() for sc in SCS_ALL[1:])
for sc in SCS_ALL[1:]:
    d_ = lrt_sum('AM', sc, a, r, 1) - v22
    single(f'{sc.replace("_", " ")} minus 2022: LRT trip origins by TAZ, AM peak hour (total {d_.sum():+,.0f}; one colour scale for the four maps)', lambda ax_, d_=d_: choropleth(ax_, d_, '', 'RdBu', TwoSlopeNorm(0, -vmax_g, vmax_g), 'change in LRT origins per TAZ, AM peak hour', alt=a), f'map_growth_AM_{sc}.png')
# shift sources in the reference case: bus and Metronit on one scale, the car on its own
sc = 'BU_2050'; fc, fb, fm = (runmat('AM', sc, a, r, k).sum(1) for k in ('from_car', 'from_bus', 'from_brt')); vmax_s = max(fb.max(), fm.max())
single(f'LRT trips drawn from the car, by origin TAZ — AM peak hour, {sc.replace("_", " ")} ({fc.sum():,.0f} trips; own colour scale)', lambda ax_: choropleth(ax_, fc, '', 'YlOrRd', Normalize(0, max(fc.max(), 1)), 'LRT trips from the car per TAZ', alt=a), f'map_shift_car_AM_{sc}.png')
single(f'LRT trips drawn from bus-based paths, by origin TAZ — AM peak hour, {sc.replace("_", " ")} ({fb.sum():,.0f} trips; scale shared with the Metronit map)', lambda ax_: choropleth(ax_, fb, '', 'YlGnBu', Normalize(0, vmax_s), 'LRT trips from bus-based paths per TAZ', alt=a), f'map_shift_bus_AM_{sc}.png')
single(f'LRT trips drawn from Metronit-based paths, by origin TAZ — AM peak hour, {sc.replace("_", " ")} ({fm.sum():,.0f} trips; scale shared with the bus map)', lambda ax_: choropleth(ax_, fm, '', 'BuPu', Normalize(0, vmax_s), 'LRT trips from Metronit-based paths per TAZ', alt=a), f'map_shift_brt_AM_{sc}.png')
# time to the reference destination: bus and LRT on one scale, then the difference
bus_t = GC[('AM', 'bus', a)][REF]; lrt_t = GC[('AM', 'lrt', a, r)][REF]
single(f'Generalized minutes to {ref_label} by the best bus / Metronit path (no LRT), AM — scale shared with the LRT map', lambda ax_: choropleth(ax_, bus_t, '', 'RdYlGn_r', Normalize(20, 120), 'generalized minutes', alt=None), 'map_time_bus_AM.png')
single(f'Generalized minutes to {ref_label} by the LRT (main route + extension, Prioritized), AM — scale shared with the bus map', lambda ax_: choropleth(ax_, lrt_t, '', 'RdYlGn_r', Normalize(20, 120), 'generalized minutes', alt=a), 'map_time_lrt_AM.png')
single(f'LRT minus best bus / Metronit, generalized minutes to {ref_label}, AM (negative = LRT cheaper)', lambda ax_: choropleth(ax_, lrt_t - bus_t, '', 'RdBu_r', TwoSlopeNorm(0, -40, 40), 'generalized minutes', alt=a), 'map_time_diff_AM.png')
print(len(os.listdir(SFIG)), 'single-panel maps in', SFIG)
