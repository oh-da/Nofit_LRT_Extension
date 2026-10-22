"""Hebrew versions of the four figures of Appendix A (speed and time function of the LRT) of the appendices report:
A.1 mean stop-to-stop time by regime, A.2 distribution of clean complete journey times, A.3 calibrated section time against station spacing, A.4 cumulative travel time along the extension.
A.1 is drawn from the calibration report's published means and intervals; A.2 is rebuilt from the bar heights of the published figure (appA_redline_trip_time_distribution.png, +-10 trips per bar,
26,518 of the 26,653 journeys; the bars beyond 82 minutes hold under 10 trips each and are not visible); A.3 and A.4 from the chain's own numbers (tools/report_appendices.py, Output/lrt_v2/).
Writes Output/figures/he/appA_*_he.png."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from report_appendices import UG_SEC, GR_SEC, RL_SPACING, HAIFA_SPACING, section_time

plt.rcParams['font.family'] = 'DejaVu Sans'
BLUE, ORANGE, AQUA, PURPLE, INK, INK2, MUTED, GRID, AXIS = '#2a78d6', '#eb6834', '#1baf7a', '#7b5bd6', '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7'
LRI, PDI = '⁦', '⁩'
OUTD = 'Output/figures/he'; os.makedirs(OUTD, exist_ok=True)
def N(s): return f'{LRI}{s}{PDI}'                                  # keep a number or Latin token left-to-right inside Hebrew text

# ---- A.1 mean stop-to-stop time by regime
fig, ax = plt.subplots(figsize=(7.4, 4.2), dpi=150, facecolor='white')
vals, lo, hi = [UG_SEC, GR_SEC], [1.958, 2.390], [1.963, 2.395]
ax.bar([0, 1], vals, color='#2077b4', width=0.8)
ax.errorbar([0, 1], vals, yerr=[[v - l for v, l in zip(vals, lo)], [h - v for v, h in zip(vals, hi)]], fmt='none', ecolor='black', capsize=12, lw=1.6)
for x, v in enumerate(vals): ax.text(x, v + 0.06, f'{N(f"{v:.3f}")} דקות', ha='center', fontsize=10)
ax.set_xticks([0, 1]); ax.set_xticklabels(['תת-קרקעי', 'אחר (על פני הקרקע)'], fontsize=10.5)
ax.set_ylabel('דקות למקטע בין תחנות'); ax.set_ylim(0, 2.98); ax.grid(axis='y', alpha=0.3); ax.set_axisbelow(True)
ax.set_title('זמן מכויל בין תחנות לפי משטר הפעלה (קו אדום)', fontsize=12)
fig.tight_layout(); fig.savefig(f'{OUTD}/appA_1_section_time_by_regime_he.png', bbox_inches='tight'); plt.close(fig)

# ---- A.2 distribution of clean complete journey times (rebuilt from the published figure)
hd = json.load(open('tools/appA_trip_time_histogram.json')); edges, counts = np.array(hd['edges']), np.array(hd['counts'])
fig, ax = plt.subplots(figsize=(7.4, 4.2), dpi=150, facecolor='white')
ax.bar(edges[:-1], counts, width=np.diff(edges), align='edge', color='#5599c8', edgecolor='none')
ax.axvline(67.89, color='#1f77b4', lw=2.2, label=f'תחזית המודל = {N("67.89")} דקות'); ax.axvline(67.89, color='white', lw=1, ls=(0, (4, 4)))
ax.plot([], [], color='#1f77b4', lw=2.2, ls='--', label=f'ממוצע נצפה = {N("67.89")} דקות')
ax.set_xlim(53, 95); ax.set_ylim(0, 3800); ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}'))
ax.set_xlabel('זמן הנסיעה הכולל שנצפה (דקות)'); ax.set_ylabel('מספר נסיעות'); ax.grid(axis='y', alpha=0.3); ax.set_axisbelow(True)
ax.set_title('התפלגות זמני הנסיעה השלמים והנקיים בקו האדום', fontsize=12); ax.legend(frameon=False, loc='upper right', fontsize=9.5)
fig.tight_layout(); fig.savefig(f'{OUTD}/appA_2_trip_time_distribution_he.png', bbox_inches='tight'); plt.close(fig)

# ---- A.3 calibrated section time against station spacing
fig, ax = plt.subplots(figsize=(7.6, 4.0), dpi=150, facecolor='white')
km = np.linspace(0.3, 1.5, 100)
for regime, col, lab in [('underground', '#2a78d6', 'מופרד / תת-קרקעי (משמש במשטר "עם עדיפות")'), ('ground', '#eb6834', 'ברמת הרחוב (משמש במשטר "בלי עדיפות")')]:
    ax.plot(km * 1000, section_time(km, regime), color=col, lw=2, label=lab)
    t = section_time(RL_SPACING[regime] / 1000, regime); ax.plot([RL_SPACING[regime]], [t], 'o', color=col, ms=7)
    ug = regime == 'underground'
    ax.annotate(f'מרווח ממוצע בקו האדום {N(str(RL_SPACING[regime]))} מ\'\n{N(f"{t:.2f}")} דקות (מכויל {N(f"{UG_SEC if ug else GR_SEC:.3f}")})', (RL_SPACING[regime], t),
                xytext=(10, -34) if ug else (-8, 20), ha='left' if ug else 'right', textcoords='offset points', fontsize=8, color=col)
ax.axvline(HAIFA_SPACING, color='#7d8794', lw=1, ls='--'); ax.text(HAIFA_SPACING + 12, 0.45, f'מרווח ממוצע בהרחבה\nבחיפה {N(str(HAIFA_SPACING))} מ\'', fontsize=8, color='#4b5665')
ax.axvline(500, color='#c3c2b7', lw=1, ls=':'); ax.text(505, 0.45, 'הנחת 500 מ\'\nשל הדוח המקורי', fontsize=8, color='#7d8794')
ax.set_xlabel('המרחק בין תחנות עוקבות (מ\')'); ax.set_ylabel('הזמן מתחנה אחת לבאה (דקות)'); ax.set_ylim(0, 4.2); ax.grid(alpha=0.25)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.legend(loc='upper left', fontsize=8, frameon=False); ax.set_title('זמן מכויל בין תחנות: זמן נסיעה + קנס עצירה קבוע, לפי משטר', fontsize=11)
fig.tight_layout(); fig.savefig(f'{OUTD}/appA_3_section_time_vs_spacing_he.png', bbox_inches='tight'); plt.close(fig)

# ---- A.4 cumulative travel time along the extension (hf_lrt_3) and the stations on the alignment
prof = pd.read_csv('Output/lrt_v2/lrt_line_profile.csv'); stn = pd.read_csv('Output/lrt_v2/lrt_stations_hf_lrt_3.csv')
line = gpd.read_file('Input/GeneralHalufa/hf_lrt_3.shp').to_crs(2039).geometry.iloc[0]; geoms = list(line.geoms) if hasattr(line, 'geoms') else [line]
fig, axes = plt.subplots(1, 2, figsize=(16, 6.5), facecolor='white', gridspec_kw={'width_ratios': [1.6, 1]})
ax = axes[0]; ch = prof['chainage_m'] / 1000
for sc, color, nm in [('all_underground', BLUE, 'כולו תת-קרקעי'), ('all_ground', ORANGE, 'כולו על פני הקרקע')]:
    ax.plot(ch, prof[f'cum_min_{sc}'], color=color, lw=2.4, marker='o', ms=3.5, label=f'{nm} — צורה מפורקת (אומדן)')
    ax.plot(ch, prof[f'cum_min_{sc}_section_form'], color=color, lw=1.1, ls='--', label=f'{nm} — צורת מקטע (חסם מהיר)')
    ax.plot(ch, prof[f'cum_min_{sc}_nominal500m_form'], color=color, lw=0.9, ls=':', alpha=0.7, label=f'{nm} — צורה נומינלית של 500 מ\' (גרסה 1)')
ax.plot(ch, prof['cum_min_design_50kmh'], color=AQUA, lw=2.0, marker='s', ms=3, label='תכנון 50 קמ"ש + 10 שניות לתחנה (נקבע)')
ax.plot(ch, prof['cum_min_design_50kmh_accel'], color=AQUA, lw=1.3, ls='--', marker='s', ms=2.5, label='תכנון 50 קמ"ש + 10 שניות עצירה + 35 שניות האצה (משימה C5)')
ax.plot(ch, prof['cum_min_mixed_core_underground'], color=PURPLE, lw=2.0, marker='^', ms=3.5, label='מעורב: ליבת חיפה תת-קרקעית, השאר על הקרקע (משימה C5)')
for _, r in prof.iterrows(): ax.axvline(r['chainage_m'] / 1000, color=GRID, lw=0.5, zorder=0)
ax.set_xlabel('המרחק מקצה טירת כרמל (ק"מ)', color=INK2); ax.set_ylabel('זמן מצטבר ברכב מ-S01 (דקות)', color=INK2)
ax.set_title('זמן נסיעה מצטבר לאורך ההרחבה: שני תרחישים מכוילים × שלוש קריאות, ומשטר התכנון 50 קמ"ש', color=INK, fontsize=11); ax.legend(frameon=False, fontsize=8, loc='upper left')
ax.grid(True, color=GRID, lw=0.6); [s_.set_color(AXIS) for s_ in ax.spines.values()]
sec = ax.secondary_xaxis('top'); sec.set_xticks(ch); sec.set_xticklabels(prof['station_id'], fontsize=7, rotation=90, color=INK2)
ax = axes[1]
for gi, g in enumerate(geoms): ax.plot(*g.xy, color=MUTED, lw=2, label='תוואי ההרחבה' if gi == 0 else None)
ax.scatter(stn['x'], stn['y'], c=[BLUE if pd.notna(a) else ORANGE for a in stn['AggCode']], s=28, zorder=3, label='תחנות (כתום: אזור תנועה מחוץ לאגרגציית V2)')
for _, r in stn.iterrows(): ax.annotate(r['station_id'], (r['x'], r['y']), fontsize=6.5, color=INK2, xytext=(3, 3), textcoords='offset points')
ax.set_aspect('equal'); ax.set_title('התחנות לאורך התוואי (רשת ישראל החדשה)', color=INK, fontsize=12); ax.legend(frameon=False, fontsize=8, loc='lower right'); ax.tick_params(labelsize=7, colors=INK2)
[s_.set_color(AXIS) for s_ in ax.spines.values()]
fig.tight_layout(); fig.savefig(f'{OUTD}/appA_4_line_profile_he.png', dpi=150, bbox_inches='tight', facecolor='white'); plt.close(fig)
print('done')
