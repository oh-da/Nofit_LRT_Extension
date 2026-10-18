"""Figures for the Hebrew report -> Output/figures/report/. Run from the repository root: python tools/build_report_figures.py"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT); sys.path.insert(0, os.path.join(ROOT, 'tools'))
import numpy as np, pandas as pd, geopandas as gpd
from matplotlib.lines import Line2D
import report_figure_style as S
from report_figure_style import he, plt

# ---------- Figure 1: the two lines, in Hebrew ----------
# main sections: area code -> (Hebrew name, station that anchors the label, label offset in metres (dx, dy), ha)
AREAS_HE = {
    201: ('טירת כרמל', 'S02', (-700, 0), 'right'),
    202: ('מת"ם', 'S06', (-700, 0), 'right'),
    203: ('חוף הכרמל', 'S08', (-700, 0), 'right'),
    204: ('הכט – שפרינצק', 'S10', (-700, -150), 'right'),
    205: ('עין הים', 'S12', (-900, 250), 'right'),
    206: ('בת גלים', 'S15', (200, 1250), 'center'),
    207: ('המושבה הגרמנית', 'S17', (1700, 1250), 'center'),
    208: ('העיר התחתית', 'S19', (3000, 800), 'center'),
    209: ('הנמל – הגיבורים', 'S22', (-1300, -1500), 'center'),
    210: ('מרכזית המפרץ', 'S24', (1500, -1500), 'center'),
    211: ('בז"ן – חוצות המפרץ', 'M02', (-600, 1500), 'center'),
    212: ('צומת קריית אתא', 'M03', (800, -1500), 'center'),
    213: ('קריית אתא', 'M04', (0, 1100), 'center'),
    217: ('נצרת', 'M16', (500, -1400), 'center'),
}

st = pd.read_csv('Output/alternatives/stations_main_ext.csv').set_index('station_id')
st_main = st[st.line == 'main']; st_ext = st[st.line == 'extension']
nodes = pd.read_csv('Output/alternatives/main_route_nodes.csv')
tz = gpd.read_file('Input/TAZ_North/TAZ_North.shp', engine='pyogrio')

fig, ax = plt.subplots(figsize=(11, 6.6)); fig.subplots_adjust(left=.01, right=.99, top=.88, bottom=.05)
tz.boundary.plot(ax=ax, color=S.GRID, lw=.3)
ext_line = pd.concat([st_ext[['x', 'y']], st_main.iloc[:0][['x', 'y']]])
ax.plot(ext_line.x, ext_line.y, color=S.BLUE, lw=3, solid_capstyle='round', zorder=3)
ax.plot(nodes.x, nodes.y, color=S.ORANGE, lw=3, solid_capstyle='round', zorder=3)
ax.scatter(st.x, st.y, s=16, color=S.INK, zorder=5)
# station codes (unchanged, Latin): every third, as in the original map
for sid, r in st.iloc[::3].iterrows(): ax.annotate(sid, (r.x, r.y), xytext=(4, 4), textcoords='offset points', fontsize=6.5, color=S.INK2)
# Hebrew names of the main sections
for code, (name, anchor, (dx, dy), ha) in AREAS_HE.items():
    r = st.loc[anchor]
    ax.annotate(he(name), (r.x, r.y), xytext=(r.x + dx, r.y + dy), textcoords='data', ha=ha, va='center', fontsize=9, fontweight='bold', color=S.INK,
                arrowprops=dict(arrowstyle='-', color=S.MUTED, lw=.7, shrinkA=0, shrinkB=3) if dy else None, zorder=6)
ax.text(192500, 736000, he('הים התיכון'), fontsize=10, color=S.MUTED, style='italic', ha='center', rotation=90)
ax.set_xlim(190000, 236000); ax.set_ylim(729000, 750500); ax.set_aspect('equal'); ax.set_axis_off()
# scale bar (5 km) and north arrow
x0, y0 = 192000, 729900; ax.plot([x0, x0 + 5000], [y0, y0], color=S.INK, lw=2); ax.text(x0 + 2500, y0 + 350, he('5 ק"מ'), ha='center', fontsize=8, color=S.INK2)
ax.annotate('', xy=(x0 + 8500, y0 + 1500), xytext=(x0 + 8500, y0 - 200), arrowprops=dict(arrowstyle='-|>', color=S.INK, lw=1.2)); ax.text(x0 + 8500, y0 + 1750, he('צ'), ha='center', fontsize=8, color=S.INK2)
leg = ax.legend(handles=[Line2D([], [], color=S.BLUE, lw=3), Line2D([], [], color=S.ORANGE, lw=3), Line2D([], [], color=S.INK, marker='o', ls='', ms=4)],
                labels=[he('ההארכה: טירת כרמל – מרכזית המפרץ, 24 תחנות, 18.9 ק"מ'), he('הקו הראשי (בבנייה): מרכזית המפרץ – נצרת, 20 תחנות, 40.7 ק"מ'), he('תחנה: S – ההארכה, M – הקו הראשי (M01 = S24)')],
                frameon=False, loc='lower right', fontsize=9, handlelength=1.8)
S.heading(fig, 'ההארכה והקו הראשי יוצרים קו רציף אחד: 43 תחנות, כ-60 ק"מ מטירת כרמל לנצרת',
          'מסלול ההארכה (כחול) והקו הראשי (כתום) על רקע אזורי התנועה במסדרון; החיבור במרכזית המפרץ')
S.source(fig, 'מקור: שלב 45 (stations_main_ext.csv, main_route_nodes.csv); אזורי תנועה: TAZ_North; רשימת עצירות הקו הראשי מאוקטובר 2026')
print(S.save(fig, 'fig01_lrt_lines_map_he.png'))
