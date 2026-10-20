"""Hebrew versions of Figures 4.4 and 4.5 (LRT flow by segment and direction, AM peak hour, 2040 BU and 2050 BU), with three location pointers
on the x axis (Tirat Carmel, Hamifrats central station, Nazareth) and thousands separators on the y axis.
Reuses the data preparation of tools/build_comprehensive_report.py (everything up to YMAX). Writes Output/figures/he/flow_lrt_AM_<scenario>_he.png."""
import os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
src = open('tools/build_comprehensive_report.py', encoding='utf-8').read().splitlines()
exec('\n'.join(src[:70]))          # constants, loads(), phf(), seg_lab, n_ext, SCS, DIRS, YMAX
plt.rcParams['font.family'] = 'DejaVu Sans'
os.makedirs('Output/figures/he', exist_ok=True)
LRI, PDI = '⁦', '⁩'
DIRS_HE = ['לכיוון נצרת (S01 → M20)', 'לכיוון טירת כרמל (M20 → S01)']
SC_YEAR = {'BU_2040': '2040', 'BU_2050': '2050'}      # BU = המשך מגמות (business as usual)
p, kind = 'AM', 'lrt'
for sc in ['BU_2040', 'BU_2050']:
    l = loads(p, sc, kind); x = np.arange(len(l)); fig, ax = plt.subplots(figsize=(13, 5.2), facecolor='white')
    for i, ((col, _, c), lab) in enumerate(zip(DIRS, DIRS_HE)): ax.bar(x + (i - 0.5) * 0.4, l[col], 0.4, color=c, label=lab)
    ax.axvline(n_ext - 0.5, color='k', ls='--', lw=0.8); ax.text(n_ext - 0.3, YMAX[kind] * 0.95, 'הרחבה | קו ראשי', fontsize=8, va='top')
    ax.set_ylim(0, YMAX[kind]); ax.set_xlim(-0.7, len(l) - 0.3)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}'))
    ax.set_ylabel('נוסעים / שעת שיא'); ax.set_xticks(x); ax.set_xticklabels(seg_lab, rotation=90, fontsize=6.5)
    ax.grid(axis='y', alpha=0.3); ax.set_axisbelow(True); ax.legend(fontsize=9, loc='upper right')
    ax.set_title(f'פרופיל קו הרק"ל לפי קטע וכיוון, שעת שיא בוקר, תרחיש: {LRI}{SC_YEAR[sc]}{PDI} המשך מגמות', fontsize=12)
    # location pointers on the x axis: S01 = Tirat Carmel (start of the first segment), S24 = Hamifrats central station (the extension / main route junction), M20 = Nazareth (end of the last segment)
    for xp, name, ha in [(-0.5, 'טירת כרמל', 'left'), (n_ext - 0.5, 'מרכזית המפרץ', 'center'), (len(l) - 0.5, 'נצרת', 'right')]:
        ax.annotate('', xy=(xp, 0), xycoords=('data', 'axes fraction'), xytext=(xp, -0.22), textcoords=('data', 'axes fraction'),
                    arrowprops=dict(arrowstyle='-|>', color='black', lw=1.4, shrinkA=0, shrinkB=0), annotation_clip=False)
        ax.text(xp, -0.235, name, transform=ax.get_xaxis_transform(), ha=ha, va='top', fontsize=11, fontweight='bold', clip_on=False)
    fig.tight_layout(); fig.savefig(f'Output/figures/he/flow_{kind}_{p}_{sc}_he.png', dpi=150, facecolor='white', bbox_inches='tight'); plt.close(fig)
    print(sc, round(YMAX[kind]), n_ext, len(l))
