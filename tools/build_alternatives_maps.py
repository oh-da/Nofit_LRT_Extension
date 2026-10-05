"""Maps for the LRT alternatives (step 45, METHODOLOGY §6aq): time, demand, line loads and differences, from Output/alternatives/.
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
T_LRT = {}; T_TR = {}
def run(p, sc, a, r):
    k = (p, sc, a, r)
    if k not in T_LRT: T_LRT[k] = rd(f'{OUT}/{p}/{sc}/{a}_{r}/t_lrt_taz.csv.gz'); T_TR[k] = rd(f'{OUT}/{p}/{sc}/{a}_{r}/t_tr_new_taz.csv.gz')
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
    base(ax, title); st = STN[a]; loads = pd.read_csv(f'{OUT}/{p}/{sc}/{a}_{r}/lrt_line_loads.csv'); bo = pd.read_csv(f'{OUT}/{p}/{sc}/{a}_{r}/lrt_stations_boardings.csv')
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
    wmax = max(pd.read_csv(f'{OUT}/{p}/{sc}/{a}_{r}/lrt_line_loads.csv')[['dir1_towards_Nazareth_end', 'dir2_towards_TiratCarmel']].values.max() for a, r in COMBOS)
    fig, axes = plt.subplots(2, 2, figsize=(16, 13))
    for ax, (a, r) in zip(axes.ravel(), COMBOS): flow_map(ax, p, sc, a, r, wmax, f'{ALTS[a]}, {REGIMES[r]} — {p} {sc}')
    axes[0, 0].plot([], [], color=BLUE, lw=4, label='towards Nazareth / Hamifrats end'); axes[0, 0].plot([], [], color=ORANGE, lw=4, label='towards Tirat Carmel'); axes[0, 0].scatter([], [], s=60, facecolor='white', edgecolor=INK, label='station (size = boardings)'); axes[0, 0].legend(loc='lower right', fontsize=8, frameon=False)
    fig.suptitle(f'LRT line loads by segment and direction (width ∝ trips, max {wmax:,.0f} in the three hours) and station boardings — {p} {sc}', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_line_loads_{p}_{sc}.png', dpi=130); plt.close()
    for axis, lab in ((1, 'origins'), (0, 'destinations')):
        vals = {c: lrt_sum(p, sc, c[0], c[1], axis) for c in COMBOS}; vmax = max(v.max() for v in vals.values())
        fig, axes = plt.subplots(2, 2, figsize=(16, 13)); norm = Normalize(0, vmax)
        for ax, c in zip(axes.ravel(), COMBOS): choropleth(ax, vals[c], f'{ALTS[c[0]]}, {REGIMES[c[1]]}', 'YlGnBu', norm, f'LRT trip {lab} per TAZ, {p} 3 h', alt=c[0])
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
    choropleth(ax, d, f'LRT trip {lab}: main route + extension minus extension only (Prioritized)', 'RdBu', TwoSlopeNorm(0, -m, m), f'difference in LRT {lab} per TAZ, {p} 3 h', alt='main_ext')
fig.suptitle(f'What the main route adds — {p} {sc}', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_diff_main_vs_ext_{p}_{sc}.png', dpi=130); plt.close()
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
for ax, a in zip(axes, ALTS):
    d = lrt_sum(p, sc, a, 'prioritized', 1) - lrt_sum(p, sc, a, 'unprioritized', 1); m = max(abs(d.min()), d.max(), 1)
    choropleth(ax, d, f'{ALTS[a]}: Prioritized minus Unprioritized, LRT trip origins', 'RdBu', TwoSlopeNorm(0, -m, m), f'difference in LRT origins per TAZ, {p} 3 h', alt=a)
fig.suptitle(f'What the underground extension adds — {p} {sc}', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_diff_prioritized_vs_unprioritized_{p}_{sc}.png', dpi=130); plt.close()
fig, axes = plt.subplots(1, 3, figsize=(22, 7)); v22 = lrt_sum('AM', '2022', 'main_ext', 'prioritized', 1); v50 = lrt_sum('AM', 'HS_2050', 'main_ext', 'prioritized', 1); vmax = max(v22.max(), v50.max())
choropleth(axes[0], v22, 'LRT trip origins, 2022', 'YlGnBu', Normalize(0, vmax), 'LRT origins per TAZ, AM 3 h', alt='main_ext'); choropleth(axes[1], v50, 'LRT trip origins, HS 2050', 'YlGnBu', Normalize(0, vmax), 'LRT origins per TAZ, AM 3 h', alt='main_ext')
d = v50 - v22; m = max(abs(d.min()), d.max()); choropleth(axes[2], d, 'HS 2050 minus 2022', 'RdBu', TwoSlopeNorm(0, -m, m), 'growth in LRT origins per TAZ', alt='main_ext')
fig.suptitle('Growth of the LRT demand, main route + extension, Prioritized, AM', fontsize=11); plt.tight_layout(); plt.savefig(f'{FIG}/map_growth_2022_to_HS2050_AM.png', dpi=130); plt.close()
fig, axes = plt.subplots(1, 2, figsize=(16, 7)); vam = lrt_sum('AM', 'BU_2040', 'main_ext', 'prioritized', 1); vpm = lrt_sum('PM', 'BU_2040', 'main_ext', 'prioritized', 1); vmax = max(vam.max(), vpm.max())
choropleth(axes[0], vam, 'AM 06:00–09:00', 'YlGnBu', Normalize(0, vmax), 'LRT origins per TAZ, 3 h', alt='main_ext'); choropleth(axes[1], vpm, 'PM 16:00–19:00', 'YlGnBu', Normalize(0, vmax), 'LRT origins per TAZ, 3 h', alt='main_ext')
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
print(f'maps written to {FIG}; reference destination {ref_label}'); print(sorted(os.listdir(FIG)))
