"""Hebrew version of the left panel of Figure 3.1 (modal shares 2018 vs 2022, taxi excluded).
Reads Output/ths2017/three_mode_2022/summary_2018_2022.csv, writes Output/figures/he/three_mode_2022_shares_he.png."""
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

BLUE, AQUA, PURPLE = '#2a78d6', '#1baf7a', '#7b5bd6'
INK, INK2, GRID, AXIS = '#0b0b0b', '#52514e', '#e1e0d9', '#c3c2b7'
plt.rcParams['font.family'] = 'DejaVu Sans'
H = lambda s: s   # matplotlib's text layout (raqm) already handles right-to-left

s = pd.read_csv('Output/ths2017/three_mode_2022/summary_2018_2022.csv', index_col=0)
labels = {'corridor→corridor': 'פנים-פנים', 'corridor→outside': 'פנים-חוץ', 'outside→corridor': 'חוץ-פנים',
          'outside→outside': 'חוץ-חוץ', 'all': 'סה"כ'}
MODES = [('car', 'רכב', BLUE), ('bus', 'אוטובוס', AQUA), ('rail', 'רכבת', PURPLE)]
share = {}
for yr in (2018, 2022):
    tot = s[[f'{m} {yr}' for m, _, _ in MODES]].sum(axis=1)          # car + bus + rail, taxi left out
    for m, _, _ in MODES: share[(m, yr)] = s[f'{m} {yr}'] / tot

fig, ax = plt.subplots(figsize=(9, 5.6), facecolor='white')
n = len(s); w = 0.36
for i, cls in enumerate(s.index):
    xc = n - 1 - i                                                    # right-to-left: פנים-פנים on the right
    for yr, dx, alpha in ((2018, +w / 2, 0.45), (2022, -w / 2, 1.0)):  # 2018 right of 2022 inside a group (reading order)
        bottom = 0
        for m, _, col in MODES:
            v = share[(m, yr)][cls]
            ax.bar(xc + dx, v, width=w * 0.95, bottom=bottom, color=col, alpha=alpha, linewidth=0)
            if m == 'car' or (m == 'bus' and v > 0.04):
                ax.text(xc + dx, bottom + v / 2, f'{v:.1%}', ha='center', va='center', fontsize=8, color='white' if (m == 'car' and alpha == 1) or m == 'bus' and alpha == 1 else INK)
            bottom += v
        r = share[('rail', yr)][cls]
        if r > 0:
            ax.text(xc + dx, 1.012, f'{r:.1%}', ha='center', va='bottom', fontsize=7.5, color=PURPLE)
        ax.text(xc + dx, -0.03, str(yr), ha='center', va='top', fontsize=8, color=INK2)
ax.set_xticks(range(n)); ax.set_xticklabels([H(labels[c]) for c in reversed(list(s.index))], fontsize=10, color=INK)
ax.tick_params(axis='x', pad=18, length=0)
ax.set_ylim(0, 1.07); ax.set_xlim(-0.6, n - 0.4)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0%}' if v <= 1.001 else ''))
ax.set_yticks([0, .2, .4, .6, .8, 1.0]); ax.yaxis.tick_right(); ax.yaxis.set_label_position('right')
ax.set_ylabel(H('חלק מכלל הנסיעות'), color=INK2, fontsize=10)
ax.grid(True, axis='y', color=GRID, linewidth=0.6); ax.set_axisbelow(True)
for sp in ax.spines.values(): sp.set_color(AXIS)
ax.spines['left'].set_visible(False)
ax.tick_params(axis='y', colors=INK2, labelsize=9)
ax.set_title(H('חלוקת הנסיעות לפי אמצעי תחבורה: רכב, אוטובוס ורכבת — 2018 לעומת 2022'), color=INK, fontsize=12, pad=30)
ax.text(0.5, 1.035, H('שעות הבוקר, לפי סוג הזוג מוצא-יעד ביחס למסדרון'), transform=ax.transAxes, ha='center', fontsize=9, color=INK2)
handles = [Patch(color=c, label=H(l)) for m, l, c in MODES]
ax.legend(handles=handles, frameon=False, fontsize=9, loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=3)
fig.text(0.5, 0.005, H('גוון בהיר = 2018, גוון כהה = 2022. מעל כל עמודה: חלק הרכבת.'), ha='center', fontsize=8, color=INK2)
os.makedirs('Output/figures/he', exist_ok=True)
fig.savefig('Output/figures/he/three_mode_2022_shares_he.png', dpi=150, bbox_inches='tight', facecolor='white')
