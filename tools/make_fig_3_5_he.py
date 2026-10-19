"""Hebrew version of Figure 3.5 (observed vs scheduled bus in-vehicle time, May 2026, step 30), the two panels as separate PNGs.
Left: Output/gtfs/bus_observed_skim_area_v2.csv.  Right: Output/gtfs/bus_segments_observed.csv with the scheduled time of each segment rebuilt
from Output/gtfs/stop_times_study_area_am_trips.csv.gz exactly as in notebooks/current/GTFS_bus_observed_times.ipynb.
Writes Output/figures/he/gtfs_observed_vs_scheduled_scatter_he.png and gtfs_observed_vs_scheduled_bands_he.png."""
import os
import numpy as np, pandas as pd
import matplotlib.pyplot as plt

BLUE, ORANGE, MUTED = '#2a78d6', '#eb6834', '#898781'
INK, INK2, GRID, AXIS = '#0b0b0b', '#52514e', '#e1e0d9', '#c3c2b7'
plt.rcParams['font.family'] = 'DejaVu Sans'
LRI, PDI = '⁦', '⁩'                       # keep number ranges left-to-right inside Hebrew text
os.makedirs('Output/figures/he', exist_ok=True)
SUB = 'זמן נצפה (רשת מהירויות אוטובוס נמדדות, מאי 2026) מול זמן מתוכנן (לוח זמנים GTFS)'

# ---- left: area pairs
skim = pd.read_csv('Output/gtfs/bus_observed_skim_area_v2.csv')
trunk = skim.o.between(201, 210) & skim.d.between(201, 210)
fig, ax = plt.subplots(figsize=(7.4, 7.2), facecolor='white')
ax.scatter(skim.loc[~trunk, 'bus_ivt_scheduled_min'], skim.loc[~trunk, 'bus_ivt_observed_min'], s=18, color=MUTED, alpha=0.6, edgecolors='none', label='זוגות אזורים אחרים')
ax.scatter(skim.loc[trunk, 'bus_ivt_scheduled_min'], skim.loc[trunk, 'bus_ivt_observed_min'], s=26, color=BLUE, alpha=0.85, edgecolors='white', linewidths=0.4,
           label=f'זוגות בציר המרכזי ({LRI}201–210{PDI})')
lim = float(np.nanmax([skim.bus_ivt_scheduled_min.max(), skim.bus_ivt_observed_min.max()])) * 1.05
ax.plot([0, lim], [0, lim], color=AXIS, lw=1.3, label='זמן נצפה = זמן מתוכנן')
ax.set_xlim(0, lim); ax.set_ylim(0, lim); ax.set_aspect('equal')
ax.set_xlabel('זמן נסיעה מתוכנן ברכב (דקות)', color=INK2, fontsize=10); ax.set_ylabel('זמן נסיעה נצפה ברכב (דקות)', color=INK2, fontsize=10)
ax.set_title('זמן נסיעה באוטובוס בין זוגות אזורי V2', color=INK, fontsize=12.5, pad=26)
ax.text(0.5, 1.025, SUB, transform=ax.transAxes, ha='center', fontsize=8.5, color=INK2)
ax.legend(frameon=False, fontsize=9, loc='upper left'); ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
for sp in ax.spines.values(): sp.set_color(AXIS)
ax.tick_params(colors=INK2)
fig.savefig('Output/figures/he/gtfs_observed_vs_scheduled_scatter_he.png', dpi=150, bbox_inches='tight', facecolor='white'); plt.close(fig)

# ---- right: ratio by routed segment length
st = pd.read_csv('Output/gtfs/stop_times_study_area_am_trips.csv.gz', dtype={'trip_id': str, 'stop_id': str}).sort_values(['trip_id', 'stop_sequence']).reset_index(drop=True)
st['stop_b'] = st.groupby('trip_id')['stop_id'].shift(-1); st['arr_b'] = st.groupby('trip_id')['arr'].shift(-1)
sg = st.dropna(subset=['stop_b']).copy(); sg['stop_a'] = sg['stop_id']; sg['sched_sec'] = sg['arr_b'] - sg['dep']
pr = sg.groupby(['stop_a', 'stop_b']).agg(sched_sec_mean=('sched_sec', 'mean')).reset_index()
p = pd.read_csv('Output/gtfs/bus_segments_observed.csv', dtype={'stop_a': str, 'stop_b': str}).merge(pr, on=['stop_a', 'stop_b'], how='left')
p['sched_min'] = p.sched_sec_mean / 60
rows = []
for lo, hi in [(0, 500), (500, 1000), (1000, 2000), (2000, np.inf)]:
    s = p[p.routed_m.between(lo, hi, inclusive='left' if hi != np.inf else 'both') & p.flag.isin(['ok', 'ok_undirected'])]
    rows.append((lo, hi, (s.observed_min * s.n_trips).sum() / (s.sched_min * s.n_trips).sum(), s.covered_m.sum() / s.routed_m.sum()))
labels = [f'{LRI}0–500{PDI} מ׳', f'{LRI}500–1,000{PDI} מ׳', f'{LRI}1,000–2,000{PDI} מ׳', f'מעל {LRI}2,000{PDI} מ׳']
fig, ax = plt.subplots(figsize=(7.6, 6.4), facecolor='white')
for i, (lo, hi, r, c) in enumerate(rows):
    x = len(rows) - 1 - i                                             # right-to-left: the shortest segments on the right
    ax.bar(x, r, 0.55, color=ORANGE)
    ax.annotate(f'{c:.0%}\nמכוסה', (x, r), textcoords='offset points', xytext=(0, 4), ha='center', fontsize=8.5, color=INK2)
ax.axhline(1.0, color=AXIS, lw=1, ls='--')
ax.set_xticks(range(len(rows))); ax.set_xticklabels(labels[::-1], fontsize=9.5, color=INK)
ax.set_ylim(0, 1.6); ax.yaxis.tick_right(); ax.yaxis.set_label_position('right')
ax.set_ylabel('זמן נצפה ÷ זמן מתוכנן (יחס סכומים משוקללים לפי נסיעות-קטעים)', color=INK2, fontsize=9.5)
ax.set_title('יחס זמן נצפה למתוכנן לפי אורך קטע בין תחנות', color=INK, fontsize=12.5, pad=26)
ax.text(0.5, 1.025, 'מעל כל עמודה: חלק מאורך הקטע שיש בו קישור עם מהירות נמדדת', transform=ax.transAxes, ha='center', fontsize=8.5, color=INK2)
ax.grid(True, color=GRID, lw=0.6, axis='y'); ax.set_axisbelow(True)
for sp in ax.spines.values(): sp.set_color(AXIS)
ax.spines['left'].set_visible(False); ax.tick_params(axis='y', colors=INK2)
fig.savefig('Output/figures/he/gtfs_observed_vs_scheduled_bands_he.png', dpi=150, bbox_inches='tight', facecolor='white'); plt.close(fig)
print([(a, b, round(c, 3), round(d, 3)) for a, b, c, d in rows])
