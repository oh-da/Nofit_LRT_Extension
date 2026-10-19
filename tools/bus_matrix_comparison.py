"""Bus 2022 layer vs RavKav 2022 journeys vs the raw survey bus matrix, AM / PM / midday.
Output: Output/validation_mot/bus_layer_vs_ravkav_vs_survey.xlsx (+ the three tables as csv)."""
import numpy as np, pandas as pd

PER = {'AM 06:00-09:00': ('', 'Output/bus/bus_od_taz_avg.csv'),
       'PM 16:00-19:00': ('_pm', 'Output/bus/periods/bus_od_taz_avg_PM.csv'),
       'midday 10:00-14:00': ('_md', 'Output/bus/periods/bus_od_taz_avg_MD.csv')}
keys = pd.read_csv('Input/Matrices/1270_02_09_2021_TAZ_North_keys.csv', encoding='windows-1255')
sz_of = keys[['TAZ_NUMBER', 'SZ_NEW']].dropna().astype(int).drop_duplicates('TAZ_NUMBER').set_index('TAZ_NUMBER')['SZ_NEW']

def load(path, ix):
    m = pd.read_csv(path, index_col=0); m.index = m.index.astype(int); m.columns = m.columns.astype(int)
    return m.reindex(index=ix, columns=ix, fill_value=0).fillna(0)
def fit(x, y):                                   # y on x through the cells: R2 of the correlation, slope of y = a + b x
    x, y = np.asarray(x, float).ravel(), np.asarray(y, float).ravel()
    return np.corrcoef(x, y)[0, 1] ** 2, np.polyfit(x, y, 1)[0]
def r(a, b): return a / b if b else np.nan

tot, orig_rows, od_rows = [], [], []
for per, (suf, rk_path) in PER.items():
    L = pd.read_csv(f'Output/ths2017/three_mode_2022{suf}/bus_2022_taz.csv', index_col=0); L.index = L.index.astype(int); L.columns = L.columns.astype(int)
    ix = L.index; K = load(rk_path, ix); S = load(f'Output/ths2017/two_mode{suf}/bus_survey_taz.csv', ix)
    sz = sz_of.reindex(ix).astype(int).values
    M = {'layer': L, 'ravkav': K, 'survey': S}
    SZ = {k: m.groupby(sz).sum().T.groupby(sz).sum().T for k, m in M.items()}          # 36 x 36 super-zone OD
    n = len(ix); off = ~np.eye(n, dtype=bool); szoff = ~np.eye(SZ['layer'].shape[0], dtype=bool)
    v = {k: m.values.sum() for k, m in M.items()}; intra = {k: np.trace(m.values) for k, m in M.items()}
    s = {'window': per, 'bus 2022 layer': v['layer'], 'RavKav 2022 journeys': v['ravkav'], 'raw survey 2017/18 (expanded)': v['survey'],
         'layer / RavKav': r(v['layer'], v['ravkav']), 'layer / survey': r(v['layer'], v['survey']), 'RavKav / survey': r(v['ravkav'], v['survey']),
         'intra-TAZ share: layer': intra['layer'] / v['layer'], 'intra-TAZ share: RavKav': intra['ravkav'] / v['ravkav'], 'intra-TAZ share: survey': intra['survey'] / v['survey'],
         'layer / RavKav, between TAZs': r(v['layer'] - intra['layer'], v['ravkav'] - intra['ravkav']), 'layer / survey, between TAZs': r(v['layer'] - intra['layer'], v['survey'] - intra['survey'])}
    for ref, lab in (('ravkav', 'RavKav'), ('survey', 'survey')):
        r2, sl = fit(SZ[ref].values[szoff], SZ['layer'].values[szoff]); s[f'super-zone OD, layer vs {lab}: R2'] = r2; s[f'super-zone OD, layer vs {lab}: slope'] = sl
        o_l, o_r = SZ['layer'].sum(axis=1), SZ[ref].sum(axis=1)
        s[f'origin super-zones within ±15 %, layer vs {lab}'] = int((((o_l / o_r) - 1).abs() <= 0.15).sum())
    tot.append(s)
    for z in SZ['layer'].index:
        orig_rows.append({'window': per, 'origin super-zone': z, 'bus 2022 layer': SZ['layer'].loc[z].sum(), 'RavKav 2022': SZ['ravkav'].loc[z].sum(), 'survey': SZ['survey'].loc[z].sum(),
                          'layer / RavKav': r(SZ['layer'].loc[z].sum(), SZ['ravkav'].loc[z].sum()), 'layer / survey': r(SZ['layer'].loc[z].sum(), SZ['survey'].loc[z].sum()),
                          'RavKav / survey': r(SZ['ravkav'].loc[z].sum(), SZ['survey'].loc[z].sum())})
    D = SZ['layer'].stack().rename('layer').to_frame().join(SZ['ravkav'].stack().rename('RavKav')).join(SZ['survey'].stack().rename('survey'))
    D = D.reset_index(); D.columns = ['origin super-zone', 'destination super-zone', 'bus 2022 layer', 'RavKav 2022', 'survey']; D.insert(0, 'window', per)
    D['layer / RavKav'] = D['bus 2022 layer'] / D['RavKav 2022'].replace(0, np.nan); D['layer / survey'] = D['bus 2022 layer'] / D['survey'].replace(0, np.nan)
    od_rows.append(D)

T = pd.DataFrame(tot); O = pd.DataFrame(orig_rows); D = pd.concat(od_rows)
out = 'Output/validation_mot/bus_layer_vs_ravkav_vs_survey'
with pd.ExcelWriter(out + '.xlsx') as w:
    T.T.to_excel(w, sheet_name='summary', header=False)
    O.to_excel(w, sheet_name='by_origin_superzone', index=False); D.to_excel(w, sheet_name='superzone_OD_pairs', index=False)
T.to_csv(out + '_summary.csv', index=False, float_format='%.4f'); O.to_csv(out + '_by_origin_superzone.csv', index=False, float_format='%.4f')
pd.set_option('display.width', 250); print(T.set_index('window').T.round(3).to_string())
