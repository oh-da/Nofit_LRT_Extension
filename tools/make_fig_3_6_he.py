"""Hebrew version of Figure 3.6 (observed transit share against the cost difference, by car-availability segment), the two panels as separate PNGs.
Reads Output/mode_choice/estimation_sample_person_level.csv (step 33); writes Output/figures/he/mode_choice_by_segment_bus_he.png and ..._best_he.png."""
import os
import numpy as np, pandas as pd
import matplotlib.pyplot as plt

BLUE, ORANGE, AQUA, PURPLE = '#2a78d6', '#eb6834', '#1baf7a', '#7b5bd6'
INK, INK2, GRID, AXIS = '#0b0b0b', '#52514e', '#e1e0d9', '#c3c2b7'
plt.rcParams['font.family'] = 'DejaVu Sans'
LRI, PDI = '⁦', '⁩'
os.makedirs('Output/figures/he', exist_ok=True)
S = pd.read_csv('Output/mode_choice/estimation_sample_person_level.csv')
bins = [-20, 0, 5, 10, 15, 20, 30, 45, 90]
SEGS = [('no_car_hh', 'משק בית ללא רכב', PURPLE), ('no_licence', 'ללא רישיון נהיגה', ORANGE), ('competition', 'יותר רישיונות מרכבים', AQUA), ('car_available', 'רכב זמין', BLUE)]
PANELS = [('dGC', 'bus', 'עלות האוטובוס', f'הפרש העלות {LRI}ΔGC{PDI}: עלות מוכללת בתחבורה ציבורית פחות עלות מוכללת ברכב (דקות מוכללות)'),
          ('dGC_best', 'best', 'הזול מבין אוטובוס ומטרונית', f'הפרש העלות {LRI}ΔGC_best{PDI}: תחבורה ציבורית (הזול מבין אוטובוס ומטרונית) פחות רכב (דקות מוכללות)')]
for col, tag, sub, xlabel in PANELS:
    fig, ax = plt.subplots(figsize=(7.4, 5.6), facecolor='white')
    for seg, lab, color in SEGS:
        g = S[S.car_seg == seg].copy(); g['bin'] = pd.cut(g[col], bins)
        b = pd.DataFrame([{'mid': k.mid, 'share': np.average(x.transit, weights=x.w)} for k, x in g.groupby('bin', observed=True)])
        ax.plot(b.mid, b.share, 'o-', color=color, ms=5, label=lab)
    ax.set_ylim(0, 1); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
    for sp in ['top', 'right']: ax.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']: ax.spines[sp].set_color(AXIS)
    ax.tick_params(colors=INK2)
    ax.set_xlabel(xlabel, color=INK2, fontsize=9.5); ax.set_ylabel('חלק התחבורה הציבורית מתוך רכב + תחבורה ציבורית (משוקלל)', color=INK2, fontsize=9.5)
    ax.set_title('חלק התחבורה הציבורית כנגד הפרש העלות, לפי פלח זמינות רכב', color=INK, fontsize=12, pad=40)
    ax.text(0.5, 1.07, f'עלות התחבורה הציבורית לפי: {sub}', transform=ax.transAxes, ha='center', fontsize=9.5, color=INK)
    ax.text(0.5, 1.025, 'נסיעות בוקר, 25 אזורי המסדרון, סקר הרגלי נסיעה 2017/18', transform=ax.transAxes, ha='center', fontsize=8.5, color=INK2)
    ax.legend(frameon=False, fontsize=9, loc='upper right')
    fig.savefig(f'Output/figures/he/mode_choice_by_segment_{tag}_he.png', dpi=150, bbox_inches='tight', facecolor='white'); plt.close(fig)
print('done')
