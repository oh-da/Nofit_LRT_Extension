"""Hebrew version of Figure 4.1A (AM transit demand on the corridor by scenario, peak hour), 2022 bars removed.
Reuses the data preparation of tools/build_comprehensive_report.py (everything before the chart functions) so the values are the report's own.
Writes Output/figures/he/demand_by_scenario_AM_he.png."""
import os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
src = open('tools/build_comprehensive_report.py', encoding='utf-8').read().splitlines()
exec('\n'.join(src[:69]))                                     # imports, constants, summary tables, phf(), shift_table(), tabs, nice()
plt.rcParams['font.family'] = 'DejaVu Sans'
DEMAND_YMAX = nice(max(max(tabs[(p, REG)]['transit before'].max(), tabs[(p, REG)]['total transit after'].max()) * phf(p, 'transit') for p in ['AM', 'PM']))   # same scale as 4.1B

p = 'AM'
t = tabs[(p, REG)]; t = t[t['scenario'] != '2022'].reset_index(drop=True); f = phf(p, 'transit')
x = np.arange(len(t)); w = 0.2
fig, ax = plt.subplots(figsize=(7.4, 5.8), facecolor='white')
ax.bar(x - 1.5 * w, t['transit before'] * f, w, color='#c7c7c7', label='תחבורה ציבורית לפני (בלי רכבת קלה)')
ax.bar(x - 0.5 * w, t['total transit after'] * f, w, color='#1f77b4', label='סך תחבורה ציבורית אחרי')
ax.bar(x + 0.5 * w, t['LRT'] * f, w, color='#2ca02c', label='רכבת קלה (קו ראשי + הרחבה)')
ax.bar(x + 1.5 * w, t['LRT using the extension'] * f, w, color='#98df8a', label='רכבת קלה המשתמשת בהרחבה')
ax.set_ylim(0, DEMAND_YMAX); ax.set_xticks(x); ax.set_xticklabels(t['scenario'])
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}'))
ax.set_ylabel('נסיעות / שעת שיא')
ax.set_title(f'בוקר — ביקוש לתחבורה ציבורית במסדרון, שעת שיא ({f:.2f} משלוש השעות)', fontsize=11)
ax.grid(axis='y', alpha=0.3); ax.set_axisbelow(True); ax.legend(fontsize=8.5, loc='upper center', bbox_to_anchor=(0.5, -0.09), ncol=2, frameon=False)
os.makedirs('Output/figures/he', exist_ok=True)
fig.tight_layout(); fig.savefig('Output/figures/he/demand_by_scenario_AM_he.png', dpi=150, facecolor='white', bbox_inches='tight'); plt.close(fig)
print(t['scenario'].tolist(), round(f, 3))
