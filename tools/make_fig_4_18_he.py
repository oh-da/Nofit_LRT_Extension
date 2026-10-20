"""Hebrew versions of Figures 4.18, 4.19, 4.22, 4.23 (AM) and 4.25, 4.26, 4.29, 4.30 (PM): LRT flow between the corridor areas along the line, peak hour, 2040 BU and 2050 BU,
with three location pointers on the x axis and thousands separators on the y axis.
Reuses the data preparation of tools/build_comprehensive_report.py (the part that defines the loads and the area loads, not the chart loops).
Writes Output/figures/he/areaflow_lrt_<AM|PM>_<scenario>_he.png."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
from he_area_names import HE
src = open('tools/build_comprehensive_report.py', encoding='utf-8').read().splitlines()
i0 = next(i for i, l in enumerate(src) if l.startswith('# ---- flows by corridor area')); i1 = next(i for i, l in enumerate(src) if l.startswith('def area_flow_chart('))
exec('\n'.join(src[:70] + src[i0:i1]))          # constants, loads(), phf(), SCS, DIRS, then area_loads(), area_lab, n_ext_area, AYMAX
plt.rcParams['font.family'] = 'DejaVu Sans'
os.makedirs('Output/figures/he', exist_ok=True)
LRI, PDI = '⁦', '⁩'
DIRS_HE = ['לכיוון נצרת (S01 → M20)', 'לכיוון טירת כרמל (M20 → S01)']
SC_YEAR = {'BU_2040': '2040', 'BU_2050': '2050'}      # BU = המשך מגמות (business as usual)
PERIOD_HE = {'AM': 'בוקר', 'PM': 'אחה"צ'}
eng = {v: k for k, v in names.items()}                # English area name -> code, to label the links in Hebrew
kind = 'lrt'
for p, sc in [(a, b) for a in ('AM', 'PM') for b in ('BU_2040', 'BU_2050')]:
    g = area_loads(p, sc, kind); x = np.arange(len(g)); fig, ax = plt.subplots(figsize=(13, 7.4), facecolor='white')
    labels = [f'{HE[names[a]]} – {HE[names[b]]}' for a, b in zip(g['a_from'], g['a_to'])]
    for i, ((col, _, c), lab) in enumerate(zip(DIRS, DIRS_HE)): ax.bar(x + (i - 0.5) * 0.4, g[col], 0.4, color=c, label=lab)
    ax.axvline(n_ext_area - 0.5, color='k', ls='--', lw=0.8); ax.text(n_ext_area - 0.3, AYMAX[kind] * 0.95, 'הרחבה | קו ראשי', fontsize=8, va='top')
    ax.set_ylim(0, AYMAX[kind]); ax.set_xlim(-0.7, len(g) - 0.3)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}'))
    ax.set_ylabel('נוסעים / שעת שיא'); ax.set_xticks(x); ax.set_xticklabels(labels, rotation=90, ha='center', fontsize=8.5)
    ax.grid(axis='y', alpha=0.3); ax.set_axisbelow(True); ax.legend(fontsize=9, loc='upper right')
    ax.set_title(f'פרופיל קו הרק"ל לפי מרחבים במסדרון הרק"ל וכיוון, שעת שיא {PERIOD_HE[p]}, תרחיש: {LRI}{SC_YEAR[sc]}{PDI} המשך מגמות', fontsize=12)
    # location pointers: the start of the first link (Tirat Carmel), the extension / main route boundary at Hamifrats (the central station) and the end of the last link (Nazareth)
    for xp, name, ha in [(-0.5, 'טירת כרמל', 'left'), (n_ext_area - 0.5, 'מרכזית המפרץ', 'center'), (len(g) - 0.5, 'נצרת', 'right')]:
        ax.annotate('', xy=(xp, 0), xycoords=('data', 'axes fraction'), xytext=(xp, -0.72), textcoords=('data', 'axes fraction'),
                    arrowprops=dict(arrowstyle='-|>', color='black', lw=1.4, shrinkA=0, shrinkB=0), annotation_clip=False)
        ax.text(xp, -0.735, name, transform=ax.get_xaxis_transform(), ha=ha, va='top', fontsize=11, fontweight='bold', clip_on=False)
    fig.subplots_adjust(left=0.07, right=0.99, top=0.93, bottom=0.5); fig.savefig(f'Output/figures/he/areaflow_{kind}_{p}_{sc}_he.png', dpi=150, facecolor='white', bbox_inches='tight'); plt.close(fig)
    print(p, sc, round(AYMAX[kind]), n_ext_area, len(g))

# ---- all four scenarios side by side, one direction per chart: Figures 4.22, 4.23 (AM) and 4.29, 4.30 (PM)
COLS = {'BU_2040': '#9ecae1', 'BU_2050': '#3182bd', 'HS_2040': '#fdae6b', 'HS_2050': '#e6550d'}
SC_LAB_HE = {'BU_2040': '2040 המשך מגמות', 'BU_2050': '2050 המשך מגמות', 'HS_2040': '2040 אסטרטגית דיור', 'HS_2050': '2050 אסטרטגית דיור'}
DIR_HE = {'dir1': ('dir1_towards_Nazareth_end', 'כיוון נצרת'), 'dir2': ('dir2_towards_TiratCarmel', 'כיוון טירת כרמל')}
for p in ('AM', 'PM'):
    for tag, (col, dname) in DIR_HE.items():
        fig, ax = plt.subplots(figsize=(13, 7.4), facecolor='white')
        for i, sc in enumerate(SCEN):
            g = area_loads(p, sc, kind); x = np.arange(len(g)); ax.bar(x + (i - 1.5) * 0.2, g[col], 0.2, color=COLS[sc], label=LRI + SC_LAB_HE[sc][:4] + PDI + SC_LAB_HE[sc][4:])
        labels = [f'{HE[names[a]]} – {HE[names[b]]}' for a, b in zip(g['a_from'], g['a_to'])]
        ax.axvline(n_ext_area - 0.5, color='k', ls='--', lw=0.8); ax.text(n_ext_area - 0.3, AYMAX[kind] * 0.95, 'הרחבה | קו ראשי', fontsize=8, va='top')
        ax.set_ylim(0, AYMAX[kind]); ax.set_xlim(-0.7, len(g) - 0.3)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}'))
        ax.set_ylabel('נוסעים / שעת שיא'); ax.set_xticks(x); ax.set_xticklabels(labels, rotation=90, ha='center', fontsize=8.5)
        ax.grid(axis='y', alpha=0.3); ax.set_axisbelow(True); ax.legend(fontsize=9, ncol=2, loc='upper right')
        ax.set_title(f'פרופיל קו הרק"ל לפי מרחבים במסדרון הרק"ל, כל התרחישים, שעת שיא {PERIOD_HE[p]} - {dname}', fontsize=12)
        for xp, name, ha in [(-0.5, 'טירת כרמל', 'left'), (n_ext_area - 0.5, 'מרכזית המפרץ', 'center'), (len(g) - 0.5, 'נצרת', 'right')]:
            ax.annotate('', xy=(xp, 0), xycoords=('data', 'axes fraction'), xytext=(xp, -0.72), textcoords=('data', 'axes fraction'),
                        arrowprops=dict(arrowstyle='-|>', color='black', lw=1.4, shrinkA=0, shrinkB=0), annotation_clip=False)
            ax.text(xp, -0.735, name, transform=ax.get_xaxis_transform(), ha=ha, va='top', fontsize=11, fontweight='bold', clip_on=False)
        fig.subplots_adjust(left=0.07, right=0.99, top=0.93, bottom=0.5); fig.savefig(f'Output/figures/he/areaflow_{kind}_{p}_scenarios_{tag}_he.png', dpi=150, facecolor='white', bbox_inches='tight'); plt.close(fig)
        print(p, tag)
