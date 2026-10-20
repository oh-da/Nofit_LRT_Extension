"""Map of the 25 aggregated corridor areas (V2 aggregation, codes 101-304) with the whole LRT line (extension + main route) and its stops in black.
Inputs: Input/TAZ_North/TAZ_North.shp, Input/Corridor_TAZ_Agg_V2.xlsx, Input/GeneralHalufa/hf_lrt_3.shp (extension alignment),
Input/Main_Nofit/Main_Nofit 2026-10-05.shp (main route), Output/alternatives/stations_main_ext.csv (43 stops).
Writes Output/figures/he/corridor_map_areas_lrt_he.png."""
import os
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

plt.rcParams['font.family'] = 'DejaVu Sans'
taz = gpd.read_file('Input/TAZ_North/TAZ_North.shp'); crs = taz.crs
agg = pd.read_excel('Input/Corridor_TAZ_Agg_V2.xlsx', sheet_name='TazAgg')
taz = taz.merge(agg, left_on='TAZ_NUMBER', right_on='TAZ', how='left')
areas = taz.dropna(subset=['AggCode']).dissolve(by='AggCode').reset_index()
ext = gpd.read_file('Input/GeneralHalufa/hf_lrt_3.shp').to_crs(crs)
main = gpd.read_file('Input/Main_Nofit/Main_Nofit 2026-10-05.shp').to_crs(crs)
st = pd.read_csv('Output/alternatives/stations_main_ext.csv'); st = gpd.GeoDataFrame(st, geometry=gpd.points_from_xy(st.x, st.y), crs=crs)

fig, ax = plt.subplots(figsize=(15, 7.6), facecolor='white')
taz[taz.AggCode.isna()].plot(ax=ax, facecolor='#f0efe9', edgecolor='#dcdbd3', linewidth=0.3)
areas.plot(ax=ax, facecolor='#cfe0f3', edgecolor='white', linewidth=1.4)
areas.boundary.plot(ax=ax, color='#7c9cc4', linewidth=0.6)
ext.plot(ax=ax, color='black', linewidth=2.6, zorder=5); main.plot(ax=ax, color='black', linewidth=2.6, zorder=5)
st.plot(ax=ax, color='black', markersize=22, zorder=6)
halo = [pe.withStroke(linewidth=3, foreground='white')]
for _, r in areas.iterrows():
    p = r.geometry.representative_point()
    ax.annotate(f'{int(r.AggCode)}', (p.x, p.y), ha='center', va='center', fontsize=10.5, fontweight='bold', color='#0b3d7a', path_effects=halo, zorder=7)
minx, miny, maxx, maxy = areas.total_bounds; pad = 1500
ax.set_xlim(minx - pad, maxx + pad); ax.set_ylim(miny - pad, maxy + pad); ax.set_aspect('equal'); ax.set_axis_off()
# scale bar (5 km) and north arrow
x0, y0 = ax.get_xlim()[0] + 800, ax.get_ylim()[0] + 900
ax.plot([x0, x0 + 5000], [y0, y0], color='black', lw=3, zorder=8); ax.text(x0 + 2500, y0 + 350, '5 ק"מ', ha='center', fontsize=9, zorder=8)
ax.annotate('', xy=(x0 + 6800, y0 + 1700), xytext=(x0 + 6800, y0 - 100), arrowprops=dict(arrowstyle='-|>', color='black', lw=1.6), zorder=8); ax.text(x0 + 6800, y0 + 1900, 'צפון', ha='center', fontsize=9, zorder=8)
ax.legend(handles=[Patch(facecolor='#cfe0f3', edgecolor='#7c9cc4', label='אזורי המסדרון המצטברים (25) — המספר הוא קוד האזור'),
                   Line2D([0], [0], color='black', lw=2.6, label='תוואי הרכבת הקלה (הרחבה + קו ראשי)'),
                   Line2D([0], [0], color='black', marker='o', ls='', ms=5.5, label='תחנות (43)'),
                   Patch(facecolor='#f0efe9', edgecolor='#dcdbd3', label='שאר אזורי התנועה')], loc='lower center', bbox_to_anchor=(0.36, 0.03), fontsize=10, frameon=True, framealpha=0.95, edgecolor='#c3c2b7')
ax.set_title('25 האזורים המצטברים של המסדרון ותוואי הרכבת הקלה', fontsize=14, pad=10)
os.makedirs('Output/figures/he', exist_ok=True)
fig.savefig('Output/figures/he/corridor_map_areas_lrt_he.png', dpi=150, bbox_inches='tight', facecolor='white'); plt.close(fig)
print(len(areas), len(st), areas.total_bounds)
