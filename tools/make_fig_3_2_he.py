"""Hebrew version of Figure 3.2 (corridor transit profiles, calibrated survey vs RavKav ticketing), one PNG per panel.
Reads Output/corridor_v2/corridor_v2_survey_vs_ticketing.csv; writes Output/figures/he/corridor_v2_<route>_<direction>_he.png (8 files)."""
import os
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

BLUE, ORANGE, AQUA, PURPLE = '#2a78d6', '#eb6834', '#1baf7a', '#7b5bd6'
INK, INK2, MUTED, GRID, AXIS = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7'
plt.rcParams['font.family'] = 'DejaVu Sans'

import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from he_area_names import HE, CODE
SERIES = [('step: survey bus 2018 (raw)', 'סקר 2018 (אוטובוס, גולמי)', MUTED, ':', 1.8, 1.0),
          ('ticketing: bus (RavKav, own alightings)', 'רב-קו (ירידות רב-קו עצמן)', ORANGE, '-', 2.2, 1.0),
          ('survey: bus (calibrated)', 'מטריצת אוטובוס 2022', BLUE, '-', 2.2, 1.0)]
DIR = {'up': 'כיוון עולה (מטירת כרמל והלאה)', 'down': 'כיוון יורד (לכיוון טירת כרמל)'}
SCOPE = {'T1': 'מסלול T1 (נצרת)', 'T2': 'מסלול T2 (הקריות)', 'T3': 'מסלול T3 (קריית ים)', 'network': 'רשת העץ (24 קטעים)'}
N_TRUNK = 12                                              # areas 201-212, common to the three routes; the branches (shaded) start at the last of them

cmp = pd.read_csv('Output/corridor_v2/corridor_v2_survey_vs_ticketing.csv')
os.makedirs('Output/figures/he', exist_ok=True)
for scope, ext in [('T1', False), ('T2', False), ('T3', False), ('network', False), ('network', True)]:   # ext: only the extension, Tirat Carmel to Tsomet Kiryat Ata (links 1-11)
    for dname in ['up', 'down']:
        s = cmp[(cmp.scope == scope) & (cmp.direction == dname)].sort_values('link')
        if ext: s = s[s.segment == 'trunk']
        n = len(s); x = np.arange(n + 1)
        if scope == 'network':
            labels = [f'{HE[a]} – {HE[b]}' for a, b in zip(s.from_area, s.to_area)]; fig, ax = plt.subplots(figsize=(10, 6.6) if ext else (12, 7.2), facecolor='white')
        else:
            seq = list(s.from_area) + [s.to_area.iloc[-1]]; labels = [f'{HE[a]} · {CODE[a]}' for a in seq]; fig, ax = plt.subplots(figsize=(9.5, 6.2), facecolor='white')
        handles = []
        for col, lab, color, ls, lw, al in SERIES:
            ax.stairs(s[col].values, x, color=color, linestyle=ls, linewidth=lw, alpha=al, label=lab)
        if scope != 'network':
            ax.axvspan(N_TRUNK - 1, n, color=MUTED, alpha=0.07, lw=0)
        ax.set_xlim(0, n); ax.set_ylim(bottom=0); ax.grid(True, color=GRID, linewidth=0.6, axis='y'); ax.set_axisbelow(True)
        for sp in ax.spines.values(): sp.set_color(AXIS)
        ax.tick_params(colors=INK2); ax.set_ylabel('נסיעות החוצות את הקטע, \u206606:00–09:00\u2069', color=INK2, fontsize=10)
        if scope == 'network': ax.set_xticks(x[:-1] + 0.5); ax.set_xticklabels(labels, rotation=65 if ext else 70, ha='right', fontsize=8.5 if ext else 7, color=INK2)
        else: ax.set_xticks(x); ax.set_xticklabels(labels, rotation=60, ha='right', fontsize=8, color=INK2)
        ax.set_title(DIR[dname] if scope == 'network' else f'{SCOPE[scope]} — {DIR[dname]}', color=INK, fontsize=12.5, pad=10)
        h, l = ax.get_legend_handles_labels()
        if scope != 'network': h.append(Patch(facecolor=MUTED, alpha=0.15)); l.append('ענף מעבר לצומת קריית אתא (מוצל)')
        ax.legend(h, l, frameon=False, fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.30 if scope != 'network' else (-0.38 if ext else -0.36)), ncol=2)
        fig.text(0.5, 0.995, 'סכומי שלוש שעות של תנועות פוטנציאליות בין אזורי הקו, לא עומסים', ha='center', va='top', fontsize=9, color=INK2)
        fig.savefig(f'Output/figures/he/corridor_v2_{scope}_{dname}{'_ext' if ext else ''}_he.png', dpi=150, bbox_inches='tight', facecolor='white'); plt.close(fig)
print('done')
