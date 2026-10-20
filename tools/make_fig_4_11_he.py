"""Hebrew versions of Figures 4.11A (AM) and 4.11B (PM): mode split on the corridor after the LRT, 2022 removed, % on the y axis.
Reuses the data preparation of tools/build_comprehensive_report.py (everything before the chart functions).
Writes Output/figures/he/mode_split_AM_he.png and mode_split_PM_he.png."""
import os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
src = open('tools/build_comprehensive_report.py', encoding='utf-8').read().splitlines()
exec('\n'.join(src[:69]))                        # constants, summary tables, phf(), shift_table(), tabs
plt.rcParams['font.family'] = 'DejaVu Sans'
LRI, PDI = '⁦', '⁩'
PERIOD_HE = {'AM': 'בוקר', 'PM': 'אחה"צ'}
os.makedirs('Output/figures/he', exist_ok=True)
for p in ['AM', 'PM']:
    t = tabs[(p, REG)]; t = t[t['scenario'] != '2022'].reset_index(drop=True); x = np.arange(len(t)); w = 0.6
    fig, ax = plt.subplots(figsize=(7.4, 5.8), facecolor='white')
    ax.bar(x, t['car share'] * 100, w, color='#7f7f7f', label='רכב')
    ax.bar(x, t['bus share'] * 100, w, bottom=t['car share'] * 100, color='#aec7e8', label='אוטובוס')
    ax.bar(x, t['BRT share'] * 100, w, bottom=(t['car share'] + t['bus share']) * 100, color='#1f77b4', label='מטרונית')
    ax.bar(x, t['LRT share'] * 100, w, bottom=(t['car share'] + t['bus share'] + t['BRT share']) * 100, color='#2ca02c', label='רק"ל')
    for i, r in t.iterrows():
        ax.text(i, 101, f'תח"צ {LRI}{r["transit share"] * 100:.1f}%{PDI}\nרק"ל {LRI}{r["LRT share"] * 100:.1f}%{PDI}', ha='center', va='bottom', fontsize=8.5)
    ax.set_xticks(x); ax.set_xticklabels(t['scenario']); ax.set_ylim(0, 115); ax.set_yticks(range(0, 101, 20))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:.0f}%'))
    ax.set_ylabel('אחוז מנסיעות רכב + תח"צ')
    ax.set_title(f'פיצול אמצעים במסדרון הרק"ל, שעת שיא {PERIOD_HE[p]}, לפי תרחיש', fontsize=11)
    ax.grid(axis='y', alpha=0.3); ax.set_axisbelow(True)
    ax.legend(fontsize=9, loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=4, frameon=False)
    fig.tight_layout(); fig.savefig(f'Output/figures/he/mode_split_{p}_he.png', dpi=150, facecolor='white', bbox_inches='tight'); plt.close(fig)
    print(p, t['scenario'].tolist())
