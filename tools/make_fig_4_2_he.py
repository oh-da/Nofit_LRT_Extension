"""Hebrew versions of Figures 4.2A (AM) and 4.2B (PM): where the LRT trips come from, peak hour, 2022 bars removed.
Reuses the data preparation of tools/build_comprehensive_report.py (everything before the chart functions).
Writes Output/figures/he/shift_sources_AM_he.png and shift_sources_PM_he.png."""
import os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
src = open('tools/build_comprehensive_report.py', encoding='utf-8').read().splitlines()
exec('\n'.join(src[:69]))                                     # imports, constants, summary tables, phf(), shift_table(), tabs, nice()
plt.rcParams['font.family'] = 'DejaVu Sans'
SHIFT_YMAX = nice(max(tabs[(p, REG)]['LRT'].max() * phf(p, 'transit') for p in ['AM', 'PM']))      # same scale for AM and PM
PERIOD_HE = {'AM': 'בוקר', 'PM': 'אחר הצהריים'}
os.makedirs('Output/figures/he', exist_ok=True)
for p in ['AM', 'PM']:
    t = tabs[(p, REG)].copy(); t = t[t['scenario'] != '2022'].reset_index(drop=True); f = phf(p, 'transit')
    x = np.arange(len(t)); w = 0.35
    for c in ['car → LRT', 'BRT → LRT', 'bus → LRT', 'ext: from car', 'ext: from BRT', 'ext: from bus']: t[c] = t[c] * f
    fig, ax = plt.subplots(figsize=(7.4, 5.8), facecolor='white')
    ax.bar(x - w / 2, t['car → LRT'], w, color='#7f7f7f', label='מרכב (כל הקו)')
    ax.bar(x - w / 2, t['BRT → LRT'], w, bottom=t['car → LRT'], color='#1f77b4', label='ממטרונית')
    ax.bar(x - w / 2, t['bus → LRT'], w, bottom=t['car → LRT'] + t['BRT → LRT'], color='#aec7e8', label='מאוטובוס')
    ax.bar(x + w / 2, t['ext: from car'], w, color='#7f7f7f', alpha=0.5, hatch='//', label='מתוכם: משתמשים בהרחבה')
    ax.bar(x + w / 2, t['ext: from BRT'], w, bottom=t['ext: from car'], color='#1f77b4', alpha=0.5, hatch='//')
    ax.bar(x + w / 2, t['ext: from bus'], w, bottom=t['ext: from car'] + t['ext: from BRT'], color='#aec7e8', alpha=0.5, hatch='//')
    ax.set_ylim(0, SHIFT_YMAX); ax.set_xticks(x); ax.set_xticklabels(t['scenario'])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}'))
    ax.set_ylabel('נסיעות רכבת קלה / שעת שיא')
    ax.set_title(f'{PERIOD_HE[p]} — מאיפה מגיעות נסיעות הרכבת הקלה, שעת שיא ({f:.2f} משלוש השעות)', fontsize=11)
    ax.grid(axis='y', alpha=0.3); ax.set_axisbelow(True)
    ax.legend(fontsize=8.5, loc='upper center', bbox_to_anchor=(0.5, -0.09), ncol=2, frameon=False)
    fig.tight_layout(); fig.savefig(f'Output/figures/he/shift_sources_{p}_he.png', dpi=150, facecolor='white', bbox_inches='tight'); plt.close(fig)
    print(p, t['scenario'].tolist(), round(f, 3))
