"""Level of service for the scenario workbook: step 45's AM transit graph rebuilt with the Metronit as today,
cut back to Hamifrats, or removed.

The scenario workbook (`tools/build_scenario_workbook.py`, `exports/Nofit_LRT_Scenario_Model.xlsx`) runs step 45's pivot
in Excel formulas, so every parameter that enters the pivot after the network (λ, λ_T, the LRT premiums, the smoothing
weight k, the LRT headway, station access and running time) can be changed in the workbook. A change of the transit
network cannot: it changes the shortest paths. This script therefore precomputes, for each Metronit network variant, the
zone-to-zone costs the pivot needs, with the code of `notebooks/current/LRT_alternatives_demand.ipynb` (cells 2, 4, 8),
AM period only:

  M0  Metronit as today (all five lines: 83001, 67002, 67003, 62004, 52005) - reproduces step 45 exactly
  M1  Metronit cut back to Hamifrats: every Metronit ride edge with a stop in Haifa south / west of Hamifrats is removed
      (corridor areas 202-209 and the off-corridor Haifa zones 1300-1899: Hadar, downtown, Bat Galim, Carmel, Matam);
      the lines keep running between Hamifrats and the Krayot / Kiryat Ata and feed the LRT there
  M2  Metronit removed everywhere (its riders take the regular buses)

The bus network is kept as it runs today in every variant (step 45's convention); only Metronit ride edges are dropped.

Outputs (`Output/scenario_tool/`), 174 x 174 corridor TAZ matrices, gzip CSV:
  transit_gc_no_lrt_{v}_{alt}.csv.gz       best bus / Metronit path without the LRT (generalized minutes)
  metronit_based_{v}_{alt}.csv.gz          1 where that path rides the Metronit for at least half its in-vehicle time
  lrt_gc_{v}_{alt}_{reg}.csv.gz            LRT path (access + boarding penalty + wait + station access + line + egress)
  lrt_board_{v}_{alt}_{reg}.csv.gz         boarding station (order in stations_{alt}.csv, 1-based; 0 = no LRT path)
  lrt_alight_{v}_{alt}_{reg}.csv.gz        alighting station (same coding)
  metronit_edges_removed.csv               the ride edges each variant removes
  variants.csv                             variant codes and descriptions
Run time about 1.5 minutes. Inputs: the committed step-30 / step-45 GTFS products under Output/gtfs/, Output/lrt_v2/,
Input/Main_Nofit/ (plain git), Input/TAZ_North/ (plain git), Input/Zonal_2020.csv and, from LFS,
Input/Corridor_TAZ_Agg_V2.xlsx and Input/Main_Nofit/Main_Nofit_StopsID.csv (python3 tools/lfs_pull.py <file>).
"""
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

import geopandas as gpd  # noqa: E402
from scipy.sparse import csr_matrix  # noqa: E402
from scipy.sparse.csgraph import dijkstra  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402

OUT = 'Output/scenario_tool'
os.makedirs(OUT, exist_ok=True)

# --- parameters: step 45 (cell 2), unchanged ---
W_WALK, W_WAIT, TRANSFER_PEN, BRT_LRT_PEN = 2.0, 2.0, 8.0, 4.0
ACC_STATION = 0.5
WALK_SPEED, DETOUR, WAIT_CAP = 4.0 * 1000 / 60, 1.3, 10.0
LRT_HEADWAY = 5.0
LRT_WAIT = LRT_HEADWAY / 2
MAIN_SPEED_KMH, MAIN_DWELL_S = 80.0, 10.0
ACCESS_M, TRANSFER_M, STATION_STOP_M = 1000.0, 300.0, 400.0
PERIOD = {'hours': (6, 9), 'peak': (7, 8)}
ALTS = {'main_ext': 'Main route + extension', 'ext': 'Extension only'}
REGIMES = {'prioritized': 'Prioritized', 'unprioritized': 'Unprioritized'}

METRONIT_ROUTES = (83001, 67002, 67003, 62004, 52005)
HAIFA_SOUTH_AREAS = set(range(202, 210))          # corridor areas Matam ... Namal-Giborim (south / west of Hamifrats)
HAIFA_SOUTH_TAZ = (1300, 1899)                    # off-corridor Haifa zones (Hadar, downtown, Carmel, Neve Shaanan ...)
VARIANTS = {
    'M0': 'Metronit as today (all five lines)',
    'M1': 'Metronit cut back to Hamifrats (removed in Haifa south/west of Hamifrats; kept Hamifrats - Krayot / Kiryat Ata)',
    'M2': 'Metronit removed everywhere (riders use the regular buses)',
}

# --- zones (cell 2) ---
xl = pd.ExcelFile('Input/Corridor_TAZ_Agg_V2.xlsx')
areas = xl.parse('AreaCodes').set_index('AggCode')
key = xl.parse('TazAgg')
AREAS = list(areas.index)
tzg = gpd.read_file('Input/TAZ_North/TAZ_North.shp', engine='pyogrio')
TAZC = pd.DataFrame({'TAZ': tzg['TAZ_NUMBER'].astype(int), 'cx': tzg.geometry.centroid.x,
                     'cy': tzg.geometry.centroid.y}).drop_duplicates('TAZ').set_index('TAZ')
TAZS = sorted(key['TAZ'].astype(int))
NT = len(TAZS)
ta = key.set_index('TAZ')['AggCode'].reindex(TAZS).astype(int).values
TC = TAZC.loc[TAZS, ['cx', 'cy']].values.astype(float)
INTER = ta[:, None] != ta[None, :]
taz_area = key.set_index('TAZ')['AggCode'].astype(int).to_dict()

# --- stations and line times (cell 4) ---
st_ext = pd.read_csv('Output/lrt_v2/lrt_stations_hf_lrt_3.csv')[['station_id', 'chainage_m', 'x', 'y', 'TAZ', 'AggCode']].copy()
T_EXT = {r: pd.read_csv(f'Output/lrt_v2/lrt_station_times_{f}.csv', index_col=0)
         for r, f in (('prioritized', 'all_underground'), ('unprioritized', 'all_ground'))}
m = gpd.read_file('Input/Main_Nofit/Main_Nofit 2026-10-05.shp', engine='pyogrio').to_crs(2039)
adj = {}
for r in m.itertuples():
    adj.setdefault(r.AB_INODE, []).append((r.AB_JNODE, r.Index))
    adj.setdefault(r.AB_JNODE, []).append((r.AB_INODE, r.Index))
path, used, cur = [34000], set(), 34000
while True:
    nxt = [(n, i) for n, i in adj[cur] if i not in used]
    if not nxt:
        break
    n, i = nxt[0]
    used.add(i)
    path.append(n)
    cur = n
coords = {}
for r in m.itertuples():
    coords[r.AB_INODE] = r.geometry.coords[0]
    coords[r.AB_JNODE] = r.geometry.coords[-1]
ch = [0.0]
for a, b in zip(path[:-1], path[1:]):
    ch.append(ch[-1] + m.geometry.iloc[[i for n, i in adj[a] if n == b][0]].length)
main_nodes = pd.DataFrame({'node': path, 'x': [coords[n][0] for n in path], 'y': [coords[n][1] for n in path], 'chainage_m': ch})
stop_set = set(pd.read_csv('Input/Main_Nofit/Main_Nofit_StopsID.csv')['Node'].astype(int))
keep = [i for i, n in enumerate(path) if n in stop_set]
if 0 not in keep:
    keep = [0] + keep
st_main = main_nodes.loc[keep].reset_index(drop=True)
st_main['station_id'] = [f'M{k + 1:02d}' for k in range(len(st_main))]
seg_km = np.diff(st_main['chainage_m'].values) / 1000
sec_min = seg_km / MAIN_SPEED_KMH * 60 + MAIN_DWELL_S / 60
cum = np.concatenate([[0], np.cumsum(sec_min)])
T_MAIN = pd.DataFrame(np.abs(cum[:, None] - cum[None, :]), index=st_main['station_id'], columns=st_main['station_id'])
st_main_rest = st_main.iloc[1:].copy()
STATIONS, T_LINE = {}, {}
for alt in ALTS:
    if alt == 'main_ext':
        s = pd.concat([st_ext.assign(line='extension'), st_main_rest.assign(line='main')[['station_id', 'chainage_m', 'x', 'y', 'line']]])
    else:
        s = st_ext.assign(line='extension')
    s = s.reset_index(drop=True)
    STATIONS[alt] = s
    for reg in REGIMES:
        ids = list(s['station_id'])
        T = pd.DataFrame(0.0, index=ids, columns=ids)
        te = T_EXT[reg].reindex(index=st_ext['station_id'], columns=st_ext['station_id'])
        T.loc[te.index, te.columns] = te.values
        if alt == 'main_ext':
            tm = T_MAIN.reindex(index=st_main['station_id'], columns=st_main['station_id'])
            mids = list(st_main_rest['station_id'])
            T.loc[mids, mids] = tm.loc[mids, mids].values
            via = te.loc[:, 'S24'].values[:, None] + tm.loc['M01', mids].values[None, :]
            T.loc[te.index, mids] = via
            T.loc[mids, te.index] = via.T
        T_LINE[(alt, reg)] = T

# --- transit graph (cell 8), with the Metronit variant ---
stops_sa = pd.read_csv('Output/gtfs/stops_study_area.csv').set_index('stop_id')
ST = pd.read_csv('Output/gtfs/stop_times_study_area_am_trips_v45.csv.gz')
seg_obs = pd.read_csv('Output/gtfs/bus_segments_observed.csv')
seg_obs = seg_obs[seg_obs['flag'].isin(['ok', 'ok_undirected']) & (seg_obs['observed_min'] > 0)].set_index(['stop_a', 'stop_b'])['observed_min']
stop_taz = stops_sa['TAZ'].to_dict()


def haifa_south(stop_id):
    t = stop_taz.get(stop_id)
    if t is None or pd.isna(t):
        return False
    t = int(t)
    if t in taz_area:
        return taz_area[t] in HAIFA_SOUTH_AREAS
    return HAIFA_SOUTH_TAZ[0] <= t <= HAIFA_SOUTH_TAZ[1]


def build_transit(variant):
    cfg = PERIOD
    st = ST.copy()
    st['line'] = st['route_code'].astype(int).astype(str) + '_' + st['direction_id'].astype(int).astype(str)
    st = st.sort_values(['trip_id', 'stop_sequence'])
    g = st.groupby('trip_id')
    st['next_stop'] = g['stop_id'].shift(-1)
    st['next_arr'] = g['arr'].shift(-1)
    st['dt_min'] = (st['next_arr'] - st['dep']) / 60
    rides = st.dropna(subset=['next_stop'])
    rides = rides[rides['dt_min'] > 0].copy()
    rides['next_stop'] = rides['next_stop'].astype(int)
    rt = rides.groupby(['line', 'stop_id', 'next_stop']).agg(sched_min=('dt_min', 'median'), is_brt=('is_brt', 'max')).reset_index()
    rt['obs_min'] = [seg_obs.get((a, b), np.nan) for a, b in zip(rt['stop_id'], rt['next_stop'])]
    rt['ride_min'] = rt['obs_min'].where(rt['obs_min'].notna(), rt['sched_min'])
    # the variant: drop Metronit ride edges
    brt = rt['is_brt'].astype(bool)
    if variant == 'M1':
        drop = brt & np.array([haifa_south(a) or haifa_south(b) for a, b in zip(rt['stop_id'], rt['next_stop'])])
    elif variant == 'M2':
        drop = brt
    else:
        drop = pd.Series(False, index=rt.index)
    removed = rt[drop].assign(variant=variant)
    rt = rt[~drop].copy()
    dep = st.groupby(['line', 'stop_id']).agg(n_peak=('peak', 'sum'), n_win=('trip_id', 'nunique')).reset_index()
    dep['per_hour'] = np.where(dep['n_peak'] > 0, dep['n_peak'], dep['n_win'] / (cfg['hours'][1] - cfg['hours'][0]))
    dep['wait_min'] = np.minimum(60 / dep['per_hour'] / 2, WAIT_CAP)
    STOPS = sorted(set(rt['stop_id']) | set(rt['next_stop']))
    spos = {s: i for i, s in enumerate(STOPS)}
    NS = len(STOPS)
    ln_keys = sorted(set(zip(rt['line'], rt['stop_id'])) | set(zip(rt['line'], rt['next_stop'])))
    lpos = {k: NS + i for i, k in enumerate(ln_keys)}
    NL = len(ln_keys)
    Eg = {k: [] for k in ('u', 'v', 'gc', 'ivt', 'walk', 'wait', 'board', 'brt')}

    def add(u, v, gc, ivt=0.0, walk=0.0, wait=0.0, board=0.0, brt=0.0):
        Eg['u'].append(u); Eg['v'].append(v); Eg['gc'].append(gc); Eg['ivt'].append(ivt)
        Eg['walk'].append(walk); Eg['wait'].append(wait); Eg['board'].append(board); Eg['brt'].append(brt)
    for r in rt.itertuples():
        add(lpos[(r.line, r.stop_id)], lpos[(r.line, r.next_stop)], r.ride_min, ivt=r.ride_min, brt=r.ride_min if r.is_brt else 0.0)
    wait_of = dep.set_index(['line', 'stop_id'])['wait_min']
    for (line, s), ln in lpos.items():
        w = wait_of.get((line, s), WAIT_CAP)
        add(spos[s], ln, W_WAIT * w + TRANSFER_PEN, wait=w, board=1.0)
        add(ln, spos[s], 0.0)
    sxy = stops_sa.loc[STOPS, ['x', 'y']].values
    kd = cKDTree(sxy)
    for i, j in kd.query_pairs(TRANSFER_M):
        wk = np.hypot(*(sxy[i] - sxy[j])) * DETOUR / WALK_SPEED
        add(i, j, W_WALK * wk, walk=wk); add(j, i, W_WALK * wk, walk=wk)
    return {'E': Eg, 'add': add, 'NS': NS, 'NL': NL, 'sxy': sxy, 'kd': kd, 'removed': removed, 'lines': rt['line'].nunique()}


def finish_graph(T, stations_xy):
    NS, NL, add, kd, sxy = T['NS'], T['NL'], T['add'], T['kd'], T['sxy']
    O0 = NS + NL; D0 = O0 + NT; K0 = D0 + NT; NK = len(stations_xy); N = K0 + NK
    for ti in range(NT):
        c = TC[ti]
        near = kd.query_ball_point(c, ACCESS_M) or [kd.query(c)[1]]
        for i in near:
            wk = np.hypot(*(sxy[i] - c)) * DETOUR / WALK_SPEED
            add(O0 + ti, i, W_WALK * wk, walk=wk); add(i, D0 + ti, W_WALK * wk, walk=wk)
    for k, (x, y) in enumerate(stations_xy):
        for i in kd.query_ball_point((x, y), STATION_STOP_M):
            wk = np.hypot(sxy[i][0] - x, sxy[i][1] - y) * DETOUR / WALK_SPEED
            add(i, K0 + k, W_WALK * wk, walk=wk); add(K0 + k, i, W_WALK * wk, walk=wk)
    kds = cKDTree(stations_xy)
    for ti in range(NT):
        c = TC[ti]
        near = kds.query_ball_point(c, ACCESS_M) or [kds.query(c)[1]]
        for k in near:
            wk = np.hypot(stations_xy[k][0] - c[0], stations_xy[k][1] - c[1]) * DETOUR / WALK_SPEED
            add(O0 + ti, K0 + k, W_WALK * wk, walk=wk); add(K0 + k, D0 + ti, W_WALK * wk, walk=wk)
    Eg = T['E']
    G = csr_matrix((Eg['gc'], (Eg['u'], Eg['v'])), shape=(N, N))
    G.data = np.maximum(G.data, 1e-6)
    mats = {k: csr_matrix((Eg[k], (Eg['u'], Eg['v'])), shape=(N, N)) for k in ('ivt', 'walk', 'wait', 'board', 'brt')}
    return G, mats, O0, D0, K0, NK


def path_sums(pred, mats, N):
    valid = pred >= 0
    idx_ = np.where(valid)[0]
    acc = {}
    for k, M in mats.items():
        e = np.zeros(N)
        e[idx_] = np.asarray(M[pred[idx_], idx_]).ravel()
        acc[k] = e
    jump = np.where(valid, pred, np.arange(N))
    for _ in range(40):
        for k in acc:
            acc[k] = acc[k] + acc[k][jump]
        nj = jump[jump]
        if np.array_equal(nj, jump):
            break
        jump = nj
    return acc


def skim_sources(G, mats, src, dst, chunk=40):
    N = G.shape[0]
    res = {'gc': np.full((len(src), len(dst)), np.nan)}
    res.update({k: np.full_like(res['gc'], np.nan) for k in mats})
    for s0 in range(0, len(src), chunk):
        srcs = src[s0:s0 + chunk]
        D, P = dijkstra(G, indices=srcs, directed=True, return_predecessors=True)
        for i in range(len(srcs)):
            res['gc'][s0 + i] = D[i, dst]
            sums = path_sums(P[i], mats, N)
            for k in mats:
                res[k][s0 + i] = sums[k][dst]
    for k in res:
        res[k][~np.isfinite(res['gc'])] = np.nan
    return res


def lrt_skim(S, alt, reg):
    acc, egr = S['acc'], S['egr']
    T = T_LINE[(alt, reg)].values
    NK = S['NK']
    acc_term = np.full(NK, ACC_STATION)

    def pen(R):
        brt_leg = (R['brt'] >= 0.5 * np.maximum(R['ivt'], 1e-9)) & (R['ivt'] > 0)
        return np.where(R['board'] >= 1, np.where(brt_leg, BRT_LRT_PEN, TRANSFER_PEN), 0.0)
    A_ = acc['gc'] + pen(acc) + (W_WAIT * LRT_WAIT + acc_term)[None, :]
    B_ = egr['gc'] + pen(egr) + acc_term[None, :]
    Ainf = np.where(np.isfinite(A_), A_, np.inf)
    Binf = np.where(np.isfinite(B_), B_, np.inf)
    a_o = Ainf.argmin(1); b_d = Binf.argmin(1)
    a_ok = np.isfinite(Ainf.min(1)); b_ok = np.isfinite(Binf.min(1))
    gc = Ainf[np.arange(NT), a_o][:, None] + T[a_o][:, b_d] + Binf[np.arange(NT), b_d][None, :]
    valid = a_ok[:, None] & b_ok[None, :] & (a_o[:, None] != b_d[None, :]) & INTER
    np.fill_diagonal(valid, False)
    gc = np.where(valid, gc, np.nan)
    a_best = np.where(valid, a_o[:, None], -1)
    b_best = np.where(valid, b_d[None, :], -1)
    return gc, a_best, b_best


def save(M, name, fmt='%.4f'):
    pd.DataFrame(M, index=TAZS, columns=TAZS).to_csv(f'{OUT}/{name}.csv.gz', float_format=fmt, compression='gzip')


def main(variants):
    removed_all = []
    for v in variants:
        for alt in ALTS:
            t0 = time.time()
            T = build_transit(v)
            if alt == 'main_ext':
                removed_all.append(T['removed'])
            sxy_st = STATIONS[alt][['x', 'y']].values.astype(float)
            G, mats, O0, D0, K0, NK = finish_graph(T, sxy_st)
            orig = np.arange(O0, O0 + NT); dest = np.arange(D0, D0 + NT); stn = np.arange(K0, K0 + NK)
            bus = skim_sources(G, mats, orig, dest)
            acc = skim_sources(G, mats, orig, stn)
            Gt = G.T.tocsr()
            mats_t = {k: M.T.tocsr() for k, M in mats.items()}
            egr = skim_sources(Gt, mats_t, dest, stn)
            for R in (bus, acc, egr):
                R['gc'] = R['gc'] - TRANSFER_PEN * (R['board'] >= 1)
            bus_gc = bus['gc'].copy()
            np.fill_diagonal(bus_gc, np.nan)
            brt_based = (bus['brt'] >= 0.5 * np.maximum(bus['ivt'], 1e-9)) & (bus['ivt'] > 0)
            S = {'acc': acc, 'egr': egr, 'NK': NK}
            save(bus_gc, f'transit_gc_no_lrt_{v}_{alt}')
            save(brt_based.astype(int), f'metronit_based_{v}_{alt}', fmt='%d')
            for reg in REGIMES:
                gc, a_b, b_b = lrt_skim(S, alt, reg)
                save(gc, f'lrt_gc_{v}_{alt}_{reg}')
                save(a_b + 1, f'lrt_board_{v}_{alt}_{reg}', fmt='%d')
                save(b_b + 1, f'lrt_alight_{v}_{alt}_{reg}', fmt='%d')
            print(f'{v} / {alt}: {T["NS"]:,} stops, {T["lines"]} line-directions, {len(T["removed"])} Metronit ride edges removed; '
                  f'no-LRT paths {np.isfinite(bus_gc).sum():,}, Metronit-based {int((brt_based & np.isfinite(bus_gc)).sum()):,}; {time.time() - t0:.0f} s', flush=True)
    pd.concat(removed_all)[['variant', 'line', 'stop_id', 'next_stop', 'ride_min']].to_csv(f'{OUT}/metronit_edges_removed.csv', index=False, float_format='%.2f')
    pd.DataFrame({'variant': list(VARIANTS), 'description': list(VARIANTS.values())}).to_csv(f'{OUT}/variants.csv', index=False)
    for alt in ALTS:
        s = STATIONS[alt].copy()
        s['order'] = np.arange(1, len(s) + 1)
        for reg in REGIMES:
            s[f'time_from_S01_{reg}'] = T_LINE[(alt, reg)].iloc[0].values
        s.to_csv(f'{OUT}/stations_{alt}.csv', index=False, float_format='%.2f')


if __name__ == '__main__':
    main(sys.argv[1:] or list(VARIANTS))
