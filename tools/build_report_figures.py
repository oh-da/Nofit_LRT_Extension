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

# ---------- Figure 2: zoom on the extension, Tirat Carmel - Merkazit Hamifrats ----------
# label offsets (m) for the zoom; station codes shown for all 24 stations
ZOOM_LABELS = {
    'S02': ('טירת כרמל', (-450, -150), 'right'), 'S06': ('מת"ם', (-450, 0), 'right'), 'S08': ('חוף הכרמל', (-450, 0), 'right'),
    'S10': ('הכט – שפרינצק', (-450, 0), 'right'), 'S12': ('עין הים', (-450, 350), 'right'), 'S15': ('בת גלים', (0, 700), 'center'),
    'S17': ('המושבה הגרמנית', (-1000, -1000), 'center'), 'S19': ('העיר התחתית', (400, 800), 'center'), 'S22': ('הנמל – הגיבורים', (-100, -900), 'center'),
    'S24': ('מרכזית המפרץ', (-100, -900), 'center'),
}
CODE_OFF = {'S13': (0, 150), 'S14': (0, 150), 'S15': (-150, 150), 'S16': (-160, -80), 'S17': (150, 200), 'S18': (-90, -150), 'S19': (150, -120), 'S20': (150, 90),
            'S21': (150, 90), 'S23': (0, 140), 'S11': (-300, 60)}
ext_tot_km = st_ext.chainage_m.iloc[-1] / 1000; mean_gap = np.diff(st_ext.chainage_m.values).mean() / 1000
fig, ax = plt.subplots(figsize=(8.6, 8.1)); fig.subplots_adjust(left=.01, right=.99, top=.875, bottom=.05)
tz.boundary.plot(ax=ax, color=S.GRID, lw=.4)
ax.plot(st_ext.x, st_ext.y, color=S.BLUE, lw=3.5, solid_capstyle='round', zorder=3)
ax.scatter(st_ext.x, st_ext.y, s=40, color=S.INK, zorder=5)
for sid, r in st_ext.iterrows():
    dx, dy = CODE_OFF.get(sid, (130, 90)); ax.text(r.x + dx, r.y + dy, sid, fontsize=8, color=S.INK2, ha='left' if dx >= 0 else 'right', va='center', zorder=6)
for sid, (name, (dx, dy), ha) in ZOOM_LABELS.items():
    r = st_ext.loc[sid]
    ax.annotate(he(name), (r.x, r.y), xytext=(r.x + dx, r.y + dy), ha=ha, va='center', fontsize=10.5, fontweight='bold', color=S.INK, zorder=7,
                arrowprops=dict(arrowstyle='-', color=S.MUTED, lw=.7, shrinkA=0, shrinkB=4) if dy else None)
ax.text(195000, 743800, he('הים התיכון'), fontsize=10, color=S.MUTED, style='italic', ha='center', rotation=90)
ax.set_xlim(194200, 205200); ax.set_ylim(738600, 749300); ax.set_aspect('equal'); ax.set_axis_off()
x0, y0 = 194600, 739000; ax.plot([x0, x0 + 1000], [y0, y0], color=S.INK, lw=2); ax.text(x0 + 500, y0 + 150, he('1 ק"מ'), ha='center', fontsize=8, color=S.INK2)
ax.legend(handles=[Line2D([], [], color=S.BLUE, lw=3.5), Line2D([], [], color=S.INK, marker='o', ls='', ms=5)],
          labels=[he(f'ההארכה: {ext_tot_km:.1f} ק"מ'), he('תחנה (S01–S24)')], frameon=False, loc='lower right', fontsize=9.5)
S.heading(fig, f'ההארכה: 24 תחנות לאורך {ext_tot_km:.1f} ק"מ, בממוצע כ-{mean_gap:.1f} ק"מ בין תחנות',
          'תקריב על מסלול ההארכה (hf_lrt_3) מטירת כרמל עד מרכזית המפרץ, על רקע אזורי התנועה')
S.source(fig, 'מקור: שלב 45 (stations_main_ext.csv); אזורי תנועה: TAZ_North')
print(S.save(fig, 'fig02_extension_zoom_he.png'))

# ---------- Figure 3: the model structure (section 2.1) ----------
import textwrap
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ranges use a hyphen, not an en dash: an en dash splits the number run in right-to-left text and flips the range
BLOCKS = {
    'base': dict(color=S.AQUA, num='1', title='שנת הבסיס: כמה נוסעים היום', wrap=37, bullets=[
        'נסיעות אנשים לפי אמצעי: רכב, אוטובוס ורכבת',
        'שיא בוקר, 06:00-09:00',
        '781 אזורי תנועה במחוז הצפון',
        'לפי סקר נסיעות 2017/18, מתוקן לנסיעות האוטובוס במאי 2022',
        'הכול מקודם מ-2018 ל-2022']),
    'forecast': dict(color=S.AQUA, num='2', title='התחזית: כמה יסעו בעתיד', wrap=37, bullets=[
        'מגדילים את נסיעות 2022 ל-2040 ול-2050',
        'לפי גידול האוכלוסייה והתעסוקה בכל אזור',
        'הרגלי הנסיעה נשארים כמו ב-2022']),
    'los': dict(color=S.PURPLE, num='3', title='רמת השירות: כמה זמן ועלות לכל נסיעה', wrap=100, bullets=[
        'לכל זוג אזורים: הליכה, המתנה, נסיעה והחלפה, מאוחדים לעלות אחת',
        'רכב: מהירויות הכבישים ממאי 2026',
        'אוטובוס ומטרונית: לוחות הזמנים של משרד התחבורה וזמני נסיעה שנמדדו',
        'רכבת קלה: נוסחת זמן שנלמדה מהקו האדום בתל אביב']),
    'pivot': dict(color=S.BLUE, num='4', title='קליטה: כמה יעברו לרכבת הקלה', wrap=37, bullets=[
        'מתחילים ממה שנצפה ב-2022 בכל זוג אזורים',
        'מי שהרכבת הקלה נוחה לו יותר מאוטובוס או מטרונית עובר אליה',
        'כשהתחבורה הציבורית משתפרת, גם נוסעי רכב עוברים אליה',
        'מריצים לכל חלופה, משטר, שעת שיא ותרחיש']),
}
LINE_H, HEAD_H, PAD = 2.3, 5.6, 2.0


def block_lines(key):
    b = BLOCKS[key]; lines = []
    for t in b['bullets']:
        ws = textwrap.wrap(t, b['wrap']); lines += [('\u2022 ' + ws[0], True)] + [(l, False) for l in ws[1:]]
    return lines


def block_h(key): return HEAD_H + PAD * 2 + len(block_lines(key)) * LINE_H


def draw_block(ax, key, x_right, y_top, w, h):
    b = BLOCKS[key]; x0 = x_right - w; y0 = y_top - h
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle='round,pad=0,rounding_size=1.2', fc='white', ec=b['color'], lw=1.6, zorder=2))
    ax.add_patch(FancyBboxPatch((x0, y_top - HEAD_H), w, HEAD_H, boxstyle='round,pad=0,rounding_size=1.2', fc=b['color'], ec=b['color'], lw=1.6, zorder=3))
    ax.add_patch(plt.Rectangle((x0, y_top - HEAD_H), w, 2, fc=b['color'], ec='none', zorder=3))   # square the header's lower corners
    ax.text(x_right - 1.5, y_top - HEAD_H / 2, he(f"{b['num']}. {b['title']}"), ha='right', va='center', fontsize=13, fontweight='bold', color='white', zorder=4)
    y = y_top - HEAD_H - PAD - LINE_H / 2
    for txt, first in block_lines(key):
        ax.text(x_right - 1.5 - (0 if first else 1.3), y, he(txt), ha='right', va='center', fontsize=10.5, color=S.INK, zorder=4); y -= LINE_H
    return dict(x0=x0, x1=x_right, y0=y0, y1=y_top, h=h)


def arrow(ax, p0, p1, color):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle='-|>', mutation_scale=18, lw=2.4, color=color, zorder=1, shrinkA=0, shrinkB=0))


fig = plt.figure(figsize=(12.4, 6.4)); ax = fig.add_axes([.01, .03, .98, .83]); ax.set_xlim(0, 100); ax.set_axis_off()
WN, GAP = 28.2, 7.0; XR1 = 99.4; XR2 = XR1 - WN - GAP; XR4 = XR2 - WN - GAP
h_top = max(block_h('base'), block_h('forecast')); h_low = block_h('los'); ROW_GAP = 3.5
b1 = draw_block(ax, 'base', XR1, 59.5, WN, h_top); b2 = draw_block(ax, 'forecast', XR2, 59.5, WN, h_top)
y_low = 59.5 - h_top - ROW_GAP
b3 = draw_block(ax, 'los', XR1, y_low, WN * 2 + GAP, h_low)
b4 = draw_block(ax, 'pivot', XR4, 59.5, WN, 59.5 - (y_low - h_low))
ym1 = 59.5 - h_top / 2; ym2 = y_low - h_low / 2
arrow(ax, (b1['x0'], ym1), (b2['x1'], ym1), S.AQUA)
arrow(ax, (b2['x0'], ym1), (b4['x1'], ym1), S.AQUA)
arrow(ax, (b3['x0'], ym2), (b4['x1'], ym2), S.PURPLE)
for xc, y, txt, col in ((b2['x1'] + GAP / 2, ym1, 'מטריצות\n2022\n2040\n2050', S.AQUA), (b4['x1'] + GAP / 2, ym2, 'עלויות\nמוכללות\nלכל\nאמצעי', S.PURPLE)):
    pass
ax.text(b4['x1'] + GAP / 2, ym1 + 3.4, he('מטריצות\nנסיעות'), ha='center', va='bottom', fontsize=8.4, fontweight='bold', color=S.INK2, linespacing=1.15)
ax.text(b4['x1'] + GAP / 2, ym2 + 3.4, he('עלויות\nמוכללות'), ha='center', va='bottom', fontsize=8.4, fontweight='bold', color=S.INK2, linespacing=1.15)
ax.text(b2['x1'] + GAP / 2, ym1 + 3.4, he('מטריצות\nבסיס'), ha='center', va='bottom', fontsize=8.4, fontweight='bold', color=S.INK2, linespacing=1.15)
ax.set_ylim(b4['y0'] - 1, 60)
# output band at the foot of block 4
oy = b4['y0'] + 1.6; oh = 6.2
ax.add_patch(FancyBboxPatch((b4['x0'] + 1.3, oy), WN - 2.6, oh, boxstyle='round,pad=0,rounding_size=1', fc=S.BLUE, ec='none', zorder=3))
ax.text(b4['x0'] + WN / 2, oy + oh / 2, he('תוצר: ביקוש לרכבת הקלה'), ha='center', va='center', fontsize=11.5, fontweight='bold', color='white', zorder=4)
S.heading(fig, 'ביקוש ושירות מזינים את הערכת הנסיעות לרכבת הקלה',
          'המודל: שרשרת של 45 שלבים מתועדים וניתנים לשחזור, בארבעה גושים')
S.source(fig, 'מקור: הדוח המסכם, סעיף 2.1; כל שלב הוא מחברת Jupyter מתועדת וניתנת לשחזור')
print(S.save(fig, 'fig03_model_structure_he.png'))

# ---------- Figure 3b: the model structure as a flow chart, headers only ----------
def flow_box(ax, x_right, y_c, w, h, color, label, num=None, outline=False, fs=14):
    x0 = x_right - w; y0 = y_c - h / 2
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle='round,pad=0,rounding_size=1.4', fc='white' if outline else color, ec=color, lw=2.2, zorder=3))
    txt_col = color if outline else 'white'
    if num:
        ax.add_patch(plt.Circle((x_right - 2.6, y_c), 1.45, fc='white', ec='none', zorder=4))
        ax.text(x_right - 2.6, y_c - .05, num, ha='center', va='center', fontsize=12, fontweight='bold', color=color, zorder=5)
    ax.text(x_right - (5.0 if num else 1.8), y_c, he(label), ha='right', va='center', fontsize=fs, fontweight='bold', color=txt_col, zorder=4, linespacing=1.25)
    return dict(x0=x0, x1=x_right, yc=y_c, y0=y0, y1=y0 + h)


def flow_arrow(ax, pts, color):
    xs, ys = zip(*pts)
    ax.plot(xs[:-1], ys[:-1], color=color, lw=2.6, solid_capstyle='butt', zorder=2)
    ax.plot(xs[-2:], ys[-2:], color=color, lw=0, zorder=2)
    ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle='-|>', mutation_scale=20, lw=2.6, color=color, zorder=2, shrinkA=0, shrinkB=0))


fig = plt.figure(figsize=(12.4, 4.3)); ax = fig.add_axes([.01, .03, .98, .80]); ax.set_xlim(0, 100); ax.set_ylim(3.5, 36); ax.set_axis_off()
W_, H_ = 20, 10.5; ROWS = dict(top=30, mid=20, bot=10)
XA, XB, XC, XD = 99.0, 99.0 - (W_ + 5.5), 99.0 - 2 * (W_ + 5.5), 99.0 - 3 * (W_ + 5.5)
f1 = flow_box(ax, XA, ROWS['top'], W_, H_, S.AQUA, 'שנת הבסיס', '1')
f2 = flow_box(ax, XB, ROWS['top'], W_, H_, S.AQUA, 'התחזית', '2')
f3 = flow_box(ax, XA, ROWS['bot'], W_, H_, S.PURPLE, 'רמת השירות', '3')
f4 = flow_box(ax, XC, ROWS['mid'], W_, H_, S.BLUE, 'קליטת הנסיעות\nלרכבת הקלה', '4', fs=13)
fo = flow_box(ax, XD, ROWS['mid'], W_, H_, S.BLUE, 'ביקוש\nלרכבת הקלה', outline=True)
cx4 = (f4['x0'] + f4['x1']) / 2
flow_arrow(ax, [(f1['x0'], ROWS['top']), (f2['x1'], ROWS['top'])], S.AQUA)
flow_arrow(ax, [(f2['x0'], ROWS['top']), (cx4, ROWS['top']), (cx4, f4['y1'])], S.AQUA)
flow_arrow(ax, [(f3['x0'], ROWS['bot']), (cx4, ROWS['bot']), (cx4, f4['y0'])], S.PURPLE)
flow_arrow(ax, [(f4['x0'], ROWS['mid']), (fo['x1'], ROWS['mid'])], S.BLUE)
S.heading(fig, 'ביקוש ושירות מזינים את הערכת הנסיעות לרכבת הקלה', 'המודל: שרשרת של 45 שלבים מתועדים וניתנים לשחזור, בארבעה גושים')
S.source(fig, 'מקור: הדוח המסכם, סעיף 2.1')
print(S.save(fig, 'fig03b_model_flow_he.png'))
