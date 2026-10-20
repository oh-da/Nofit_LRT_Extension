"""Hebrew versions of Figures 4.21 and 4.22 (and their zoom-ins on the extension): LRT trips drawn from bus-based paths and from Metronit-based paths,
by origin TAZ, AM peak hour, 2050 BU. The data and the colour scales are those of tools/build_alternatives_maps.py (single-panel maps).
Writes Output/figures/he/map_shift_{bus,brt}_AM_BU_2050_he.png and ..._zoom_he.png."""
import os, textwrap
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from shapely.geometry import LineString

plt.rcParams['font.family'] = 'DejaVu Sans'
OUT = 'Output/alternatives'; os.makedirs('Output/figures/he', exist_ok=True)
INK, AXIS = '#0b0b0b', '#c3c2b7'
LRI, PDI = '⁦', '⁩'
p, sc, a, r = 'AM', 'BU_2050', 'main_ext', 'prioritized'
tzg = gpd.read_file('Input/TAZ_North/TAZ_North.shp', engine='pyogrio'); tzg['TAZ'] = tzg['TAZ_NUMBER'].astype(int); tzg = tzg.drop_duplicates('TAZ').set_index('TAZ')
def rd(path):
    m = pd.read_csv(path, index_col=0); m.columns = m.columns.astype(int); m.index = m.index.astype(int); return m
PHF = pd.read_csv(f'{OUT}/peak_hour_factors.csv').set_index(['period', 'layer', 'direction'])['PHF3h']; f = float(PHF[(p, 'transit', 'all')])
TAZS = list(rd(f'{OUT}/AM/2022/ext_prioritized/t_lrt_taz.csv.gz').index); corr = tzg.loc[[t for t in TAZS if t in tzg.index]]
fb = (rd(f'{OUT}/{p}/{sc}/{a}_{r}/from_bus_taz.csv.gz') * f).sum(1); fm = (rd(f'{OUT}/{p}/{sc}/{a}_{r}/from_brt_taz.csv.gz') * f).sum(1); vmax_s = max(fb.max(), fm.max())
ext_st = pd.read_csv(f'{OUT}/stations_ext.csv'); main_nodes = pd.read_csv(f'{OUT}/main_route_nodes.csv')
ext_line = LineString(ext_st[['x', 'y']].values); main_line = LineString(main_nodes[['x', 'y']].values)
XMIN, XMAX, YMIN, YMAX = 188000, 236000, 727000, 752000
ZOOM = (ext_st['x'].min() - 1500, ext_st['x'].max() + 2500, ext_st['y'].min() - 1500, ext_st['y'].max() + 1500)
print('bus', round(fb.sum()), 'brt', round(fm.sum()))

def draw(ax, series, cmap, label, zoom):
    tzg.boundary.plot(ax=ax, color='#eeede8', lw=.25); corr.boundary.plot(ax=ax, color=AXIS, lw=.35)
    norm = Normalize(0, vmax_s); g = corr.assign(v=series.reindex(corr.index).values)
    g.plot(ax=ax, column='v', cmap=cmap, norm=norm, edgecolor=AXIS, linewidth=.3, missing_kwds={'color': '#f4f3ef'})
    for ln in (ext_line, main_line): ax.plot(*ln.xy, color=INK, lw=1.2, alpha=.8)
    ax.set_xlim(*(ZOOM[:2] if zoom else (XMIN, XMAX))); ax.set_ylim(*(ZOOM[2:] if zoom else (YMIN, YMAX))); ax.set_axis_off()
    cb = plt.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax, shrink=.55, pad=.01); cb.set_label(label, fontsize=9); cb.ax.tick_params(labelsize=8)

SPECS = [('bus', fb, 'YlGnBu', 'נסיעות רק"ל מנתיבי אוטובוס לכל אזור תנועה', 'נסיעות רק"ל שעברו מאוטובוסים'),
         ('brt', fm, 'BuPu', 'נסיעות רק"ל ממסלולי מטרונית לכל אזור תנועה', 'נסיעות רק"ל שעברו מהמטרונית')]
for key, series, cmap, cblabel, head in SPECS:
    base_title = f'{head}, שעת שיא בוקר {LRI}2050{PDI}, המשך מגמות ({LRI}{series.sum():,.0f}{PDI} נסיעות)'
    for zoom in (False, True):
        fig, ax = plt.subplots(figsize=(9, 9) if zoom else (12, 6.8), facecolor='white'); draw(ax, series, cmap, cblabel, zoom)
        title = base_title + (': תקריב על מקטע ההארכה' if zoom else '')
        ax.set_title(textwrap.fill(title, 60 if zoom else 100), fontsize=10.5, loc='right'); plt.tight_layout()
        fig.savefig(f'Output/figures/he/map_shift_{key}_AM_BU_2050{"_zoom" if zoom else ""}_he.png', dpi=150, bbox_inches='tight', facecolor='white'); plt.close(fig)
