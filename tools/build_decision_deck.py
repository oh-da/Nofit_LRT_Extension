"""Build the decision-maker slide deck of the Nofit LRT extension demand study:
   reports/Nofit_LRT_Extension_Decision_Deck.html   -- one self-contained HTML file (keyboard / swipe navigation, inline SVG charts)
Every number is taken from reports/Nofit_LRT_Extension_Comprehensive_Report.docx (built by tools/build_comprehensive_report.py);
the table or section it comes from is named beside each value below. The route map is Output/figures/lrt_alternatives_lines.png,
cropped and embedded. The narrative follows the storytelling-with-data structure: lead with the answer, then the evidence, then the ask.
Run:  python3 tools/build_decision_deck.py [--body-only out.html]   (--body-only writes the page without the html/head/body skeleton)"""
import base64, io, os, sys
while not os.path.exists('METHODOLOGY.md') and os.getcwd() != '/': os.chdir('..')
OUT_HTML = 'reports/Nofit_LRT_Extension_Decision_Deck.html'
MAP_PNG = 'Output/figures/lrt_alternatives_lines.png'

# ---------------- the numbers (reference case 2050 BU, main route + extension, Prioritized, AM 06:00-09:00 unless stated) ----------------
SCEN = ['2022', '2040 BU', '2050 BU', '2040 HS', '2050 HS']
LRT_TOTAL = [5193, 6309, 7433, 7476, 9225]            # Table 4.3 (AM three hours)
LRT_EXT = [4004, 4950, 6003, 5651, 7010]              # Table 4.3, "LRT using the extension"
PEAK_LOAD = [840, 966, 1071, 1146, 1397]              # Table 4.2a, through line peak load on the line (AM peak hour, one direction)
MARKETS = [('Tirat Carmel ↔ Haifa', 2189), ('Haifa internal (Matam – Hamifrats)', 1663), ('Krayot ↔ Haifa (by feeder)', 1665),
           ('Main route ↔ Haifa', 891), ('Main route ↔ Krayot / Tirat Carmel', 522),
           ('Within the main route', 306), ('Krayot ↔ Tirat Carmel', 193)]      # Table 4.5
SOURCES = [('From the Metronit', 3731, '33 % of its corridor passengers'), ('From buses', 2881, '31 % of their corridor passengers'),
           ('From cars', 818, '0.9 % of corridor car trips')]                  # Table 4.3, 2050 BU
THROUGH = {'ext_only': (5939, 5939), 'through': (6003, 7433)}                  # Table 4.1: (extension riders, total LRT riders)
REGIME = [('2040, with priority', 6309), ('2050, with priority', 7433), ('2050, no priority', 5700)]   # Tables 4.3, 4.8
RANGE = {'low': 5532, 'central': 7433, 'high': 10537, 'unprioritized': 5700, 'slow_bus': 7804}       # Executive summary planning range; 4.9

# ---------------- SVG chart helpers (marks: bars <= 24 px, 4 px rounded data-end, square at the baseline; hairline grid) ----------------
def fmt(n): return f'{n:,.0f}'
def col_path(x, y, w, h, r=4):
    """Column standing on the baseline y+h, rounded at the top only."""
    if h <= r: return f'M{x},{y + h} v{-h} h{w} v{h} z'
    return f'M{x},{y + h} v{-(h - r)} a{r},{r} 0 0 1 {r},{-r} h{w - 2 * r} a{r},{r} 0 0 1 {r},{r} v{h - r} z'
def bar_path(x, y, w, h, r=4):
    """Horizontal bar growing from x, rounded at the right end only."""
    if w <= r: return f'M{x},{y} h{w} v{h} h{-w} z'
    return f'M{x},{y} h{w - r} a{r},{r} 0 0 1 {r},{r} v{h - 2 * r} a{r},{r} 0 0 1 {-r},{r} h{-(w - r)} z'
def nice_ticks(vmax, n=4):
    import math
    raw = vmax / n; mag = 10 ** math.floor(math.log10(raw)); step = min(s for s in (1, 2, 2.5, 5, 10) if s * mag >= raw) * mag
    ticks = []; v = 0
    while v <= vmax + 1e-9: ticks.append(v); v += step
    if ticks[-1] < vmax: ticks.append(ticks[-1] + step)
    return ticks

def grouped_columns(cats, series, title, unit='', width=640, height=340, legend=True, cap=None):
    """series: list of (name, class, values). One y scale, columns in groups, 2 px surface gap between neighbours."""
    L, R, T, B = 56, 12, 16, 56
    pw, ph = width - L - R, height - T - B
    vmax = max(max(v) for _, _, v in series) if cap is None else cap
    ticks = nice_ticks(vmax); ymax = ticks[-1]
    def y(v): return T + ph - ph * v / ymax
    bw = min(24, (pw / len(cats) - 16) / len(series) - 2)
    out = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">']
    for t in ticks:
        out.append(f'<line class="grid" x1="{L}" x2="{L + pw}" y1="{y(t):.1f}" y2="{y(t):.1f}"/>')
        out.append(f'<text class="tick" x="{L - 8}" y="{y(t) + 4:.1f}" text-anchor="end">{fmt(t)}</text>')
    for i, c in enumerate(cats):
        gx = L + pw * (i + 0.5) / len(cats); gw = len(series) * (bw + 2) - 2; x0 = gx - gw / 2
        for j, (name, cls, vals) in enumerate(series):
            v = vals[i]; x = x0 + j * (bw + 2); top = y(v)
            out.append(f'<path class="mark {cls}" d="{col_path(x, top, bw, T + ph - top)}"><title>{c} · {name}: {fmt(v)}{unit}</title></path>')
            # value on the cap; in a pair the labels split around the gap so they never collide
            lx, anchor = (x + bw / 2, 'middle') if len(series) == 1 else ((x + bw, 'end') if j == 0 else (x, 'start'))
            out.append(f'<text class="vlabel" x="{lx:.1f}" y="{top - 6:.1f}" text-anchor="{anchor}">{fmt(v)}</text>')
        out.append(f'<text class="cat" x="{gx:.1f}" y="{T + ph + 20}" text-anchor="middle">{c}</text>')
    out.append(f'<line class="axis" x1="{L}" x2="{L + pw}" y1="{T + ph}" y2="{T + ph}"/>')
    if legend and len(series) > 1:
        lx = L
        for name, cls, _ in series:
            out.append(f'<rect class="mark {cls}" x="{lx}" y="{height - 14}" width="12" height="12" rx="2"/>')
            out.append(f'<text class="legend" x="{lx + 18}" y="{height - 4}">{name}</text>'); lx += 18 + 7 * len(name) + 24
    out.append('</svg>'); return '\n'.join(out)

def hbars(rows, title, cls='c1', width=640, row_h=34, label_w=250, classes=None, notes=None, total=None):
    """rows: list of (label, value). Values at the bar tip; optional note after the value; optional share of total."""
    L, R, T = label_w, 110, 8
    height = T + row_h * len(rows) + 8; pw = width - L - R
    vmax = max(v for _, v in rows); bw = 22
    out = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">']
    for i, (lab, v) in enumerate(rows):
        yy = T + i * row_h + (row_h - bw) / 2; w = pw * v / vmax; c = classes[i] if classes else cls
        out.append(f'<text class="cat" x="{L - 12}" y="{yy + bw / 2 + 4:.1f}" text-anchor="end">{lab}</text>')
        out.append(f'<path class="mark {c}" d="{bar_path(L, yy, w, bw)}"><title>{lab}: {fmt(v)}</title></path>')
        val = fmt(v) + (f' <tspan class="share">({v / total:.0%})</tspan>' if total else '')
        out.append(f'<text class="vlabel" x="{L + w + 8:.1f}" y="{yy + bw / 2 + 4:.1f}">{val}</text>')
        if notes: out.append(f'<text class="note" x="{L + w + 8:.1f}" y="{yy + bw / 2 + 4 + 14:.1f}"></text>')
    out.append(f'<line class="axis" x1="{L}" x2="{L}" y1="{T}" y2="{T + row_h * len(rows)}"/>')
    out.append('</svg>'); return '\n'.join(out)

def range_chart(width=640, height=196):
    """The planning range as one horizontal scale: low, central, high, plus the design choice as a hollow marker."""
    L, R = 40, 140; pw = width - L - R; vmin, vmax = 0, 12000; yb = 84   # R leaves room for the label right of the optimistic dot
    def x(v): return L + pw * (v - vmin) / (vmax - vmin)
    out = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="Planning range of morning LRT riders">']
    for t in range(0, 12001, 2000):
        out.append(f'<line class="grid" x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{yb - 30}" y2="{yb + 64}"/>')
        out.append(f'<text class="tick" x="{x(t):.1f}" y="{yb + 80}" text-anchor="middle">{fmt(t)}</text>')
    lo, ce, hi, un = RANGE['low'], RANGE['central'], RANGE['high'], RANGE['unprioritized']
    out.append(f'<rect class="mark c1 wash" x="{x(lo):.1f}" y="{yb - 10}" width="{x(hi) - x(lo):.1f}" height="20" rx="4"/>')
    out.append(f'<line class="mark-line c1" x1="{x(lo):.1f}" x2="{x(hi):.1f}" y1="{yb}" y2="{yb}"/>')
    for v, lab, anchor in ((lo, 'Cautious case', 'end'), (hi, 'Optimistic case', 'start')):
        out.append(f'<circle class="dot c1" cx="{x(v):.1f}" cy="{yb}" r="6"/>')
        out.append(f'<text class="vlabel" x="{x(v) + (12 if anchor == "start" else -12):.1f}" y="{yb + 4}" text-anchor="{anchor}">{lab}: {fmt(v)}</text>')
    out.append(f'<circle class="dot c1" cx="{x(ce):.1f}" cy="{yb}" r="9"/>')
    out.append(f'<text class="vlabel strong" x="{x(ce):.1f}" y="{yb - 22}" text-anchor="middle">Central case: {fmt(ce)}</text>')
    out.append(f'<circle class="dot hollow" cx="{x(un):.1f}" cy="{yb + 40}" r="6"/>')
    out.append(f'<text class="note" x="{x(un) + 12:.1f}" y="{yb + 37}">No priority at junctions: {fmt(un)}</text>')
    out.append(f'<text class="note" x="{x(un) + 12:.1f}" y="{yb + 52}">a design choice, not an uncertainty</text>')
    out.append(f'<text class="tick" x="{L}" y="{yb + 100}">Morning LRT riders, 06:00–09:00, 2050</text>')
    out.append('</svg>'); return '\n'.join(out)

def map_data_uri():
    from PIL import Image
    im = Image.open(MAP_PNG).convert('RGB').crop((120, 120, 1620, 960)); im.thumbnail((1200, 800))
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=82, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()

# ---------------- charts ----------------
CH_DEMAND = grouped_columns(SCEN, [('Whole line (Tirat Carmel – Nazareth)', 'c2', LRT_TOTAL), ('Of which use the extension', 'c1', LRT_EXT)],
                            'LRT riders by scenario, morning 06:00–09:00', cap=10000)
CH_MARKETS = hbars(MARKETS, 'Where the LRT riders travel, 2050', total=sum(v for _, v in MARKETS))
CH_SOURCES = hbars([(a, b) for a, b, _ in SOURCES], 'Where the LRT riders come from, 2050', classes=['o1', 'o2', 'o3'])
CH_THROUGH = grouped_columns(['Riders using the extension', 'Riders on the whole line'],
                             [('Extension ends at Hamifrats', 'c3', [THROUGH['ext_only'][0], THROUGH['ext_only'][1]]),
                              ('One line through to Nazareth', 'c1', [THROUGH['through'][0], THROUGH['through'][1]])],
                             'Through-running against terminating at Hamifrats, 2050', cap=8500)
CH_REGIME = grouped_columns([r[0] for r in REGIME], [('Morning LRT riders', 'c1', [r[1] for r in REGIME])], 'Priority at junctions against growth', legend=False, cap=8500)
CH_PEAK = grouped_columns(SCEN, [('Passengers per hour, one direction', 'c1', PEAK_LOAD)], 'Busiest hour load at the Hamifrats junction', legend=False, cap=1600)
CH_RANGE = range_chart()

# ---------------- the slides ----------------
def slide(n, kind, eyebrow, title, body, source=''):
    src = f'<p class="source">{source}</p>' if source else ''
    return f'''<section class="slide {kind}" id="s{n}" aria-label="Slide {n}">
  <div class="inner">
    <p class="eyebrow">{eyebrow}</p>
    <h2>{title}</h2>
    {body}
    {src}
  </div>
</section>'''

MAP = map_data_uri()
SLIDES = []
SLIDES.append(f'''<section class="slide cover" id="s1" aria-label="Slide 1">
  <div class="inner">
    <p class="eyebrow">Decision brief · Nofit light rail · October 2026</p>
    <h1>Should the Nofit light rail continue through Haifa to Tirat Carmel?</h1>
    <p class="lede">What the travel demand evidence says, in plain language. Prepared for decision makers from the comprehensive demand report of 5 October 2026.</p>
    <div class="cover-facts">
      <div><span class="k">Reference case</span><span class="v">Year 2050, business-as-usual growth, trams with priority at road junctions</span></div>
      <div><span class="k">Period</span><span class="v">Morning peak, 06:00–09:00, unless stated</span></div>
      <div><span class="k">Navigate</span><span class="v">Arrow keys, space, or the buttons below</span></div>
    </div>
  </div>
</section>''')

SLIDES.append(slide(2, 'answer', 'The short answer',
  'The extension has a real light-rail market. It needs priority at the junctions more than it needs a through service, and the numbers are ready for sizing the line, not yet for buying trains.',
  f'''<div class="tiles">
    <div class="tile"><span class="big">7,400</span><span class="lab">people ride the whole line each morning peak in 2050</span></div>
    <div class="tile"><span class="big">4 in 5</span><span class="lab">of them use the extension through Haifa</span></div>
    <div class="tile"><span class="big">−23 %</span><span class="lab">riders lost if trams queue at junctions like cars</span></div>
  </div>
  <div class="cols">
    <div>
      <h3>What the evidence says</h3>
      <ul>
        <li>The riders are in Haifa and Tirat Carmel, in three markets of similar size.</li>
        <li>Most of them switch from the Metronit and buses. Few leave their cars.</li>
        <li>Running through to Nazareth saves a change of vehicle; it does not add riders to the extension.</li>
      </ul>
    </div>
    <div>
      <h3>What we ask you to decide</h3>
      <ul>
        <li>Plan on the 2050 reference case, with 5,500 to 10,500 morning riders as the range.</li>
        <li>Protect tram priority at the junctions in the design.</li>
        <li>Settle the future of the Metronit on the shared trunk before any capacity work.</li>
      </ul>
    </div>
  </div>''', 'Source: executive decision summary of the comprehensive report.'))

SLIDES.append(slide(3, 'map', 'The question',
  'The main line to Nazareth is being built. The question is whether to continue it 18.7 km through Haifa to Tirat Carmel, and whether to run both as one line.',
  f'''<div class="cols map-cols">
    <figure class="mapfig"><img src="{MAP}" alt="Map of the two lines: the extension from Tirat Carmel along the Haifa seafront to Hamifrats in blue, and the main route from Hamifrats to Nazareth in orange"><figcaption>Extension (blue, stations S01–S24) and main route (orange, M01–M20). Both meet at Hamifrats.</figcaption></figure>
    <div class="facts">
      <div><span class="k">Extension</span><span class="v">24 stations, 18.7 km along the seafront and the lower city</span></div>
      <div><span class="k">Tirat Carmel to Hamifrats</span><span class="v">41 minutes with priority at junctions; 66 minutes without</span></div>
      <div><span class="k">Service assumed</span><span class="v">A tram every 5 minutes, running through to Nazareth without a change</span></div>
      <div><span class="k">Three choices on the table</span><span class="v">Build the extension or not · one line or two · priority at junctions or not</span></div>
    </div>
  </div>''', 'Source: section 1 and Table 4.10 of the comprehensive report; map from Output/figures/lrt_alternatives_lines.png.'))

SLIDES.append(slide(4, 'method', 'How we answered it',
  'We took today’s travellers, grew them to 2050, and offered them the light rail as a new choice.',
  '''<ol class="steps">
    <li><span class="n">1</span><div><strong>Today’s travel.</strong> Who travels where in the morning peak, by car, bus, Metronit and train, from the household travel survey and smart-card ticketing, checked against traffic counts.</div></li>
    <li><span class="n">2</span><div><strong>Growth to 2040 and 2050.</strong> The same travel pattern scaled by the official population and jobs forecasts. Corridor travel grows by 30 to 60 percent. Habits stay as they were in 2022.</div></li>
    <li><span class="n">3</span><div><strong>Today’s service, plus the light rail.</strong> The May 2026 timetable and measured speeds for every bus, Metronit and car trip. The light rail is added as a new option; nothing else is cut or changed.</div></li>
    <li><span class="n">4</span><div><strong>Who switches.</strong> Travellers pick the trip that feels shortest: riding, walking, waiting and changing vehicles all count. We count how many choose the light rail, and from which mode.</div></li>
  </ol>
  <p class="aside">The result is a corridor demand screening with a documented, reproducible chain of 45 steps. It is not a full regional transport model and not an economic appraisal.</p>''',
  'Source: section 2 of the comprehensive report.'))

SLIDES.append(slide(5, 'chart', 'How many',
  'About 7,400 people would ride the line in the morning peak in 2050, and four in five of them use the extension.',
  f'''<div class="cols chart-cols">
    <div class="chartbox">{CH_DEMAND}<p class="caption">Morning LRT riders, 06:00–09:00, with priority at junctions. BU is business-as-usual growth; HS is the high-growth scenario.</p></div>
    <div class="facts">
      <div><span class="k">Busiest hour, 2050</span><span class="v">About 4,400 riders on the line</span></div>
      <div><span class="k">Afternoon peak</span><span class="v">About 85 percent of the morning</span></div>
      <div><span class="k">Growth 2040 to 2050</span><span class="v">About 18 percent, in step with the corridor</span></div>
      <div><span class="k">High-growth scenario</span><span class="v">Adds 15 to 25 percent in the same year</span></div>
    </div>
  </div>''', 'Source: Table 4.3 of the comprehensive report.'))

SLIDES.append(slide(6, 'chart', 'Where',
  'The riders are in Haifa and Tirat Carmel: three markets of similar size make up three quarters of the demand.',
  f'''<div class="cols chart-cols">
    <div class="chartbox">{CH_MARKETS}<p class="caption">Morning LRT riders by the areas at the two ends of their trip, 2050, both directions. Share of all 7,400 riders in brackets.</p></div>
    <div class="facts">
      <div><span class="k">Largest single flow</span><span class="v">Tirat Carmel ↔ Bat Galim, 820 riders a morning</span></div>
      <div><span class="k">Crossing Hamifrats</span><span class="v">38 percent of riders travel between the two parts of the line</span></div>
      <div><span class="k">The Krayot</span><span class="v">Off the line; residents reach it by Metronit or bus feeder</span></div>
      <div><span class="k">Main route beyond Kiryat Ata</span><span class="v">A few hundred riders per direction</span></div>
    </div>
  </div>''', 'Source: Tables 4.5 and 4.7 of the comprehensive report.'))

SLIDES.append(slide(7, 'chart', 'From where',
  'Most riders are today’s Metronit and bus passengers on a faster vehicle. The car gives up less than one trip in a hundred.',
  f'''<div class="cols chart-cols">
    <div class="chartbox">{CH_SOURCES}
      <ul class="keylist"><li><span class="sw o1"></span>Metronit: 33 % of its corridor passengers</li><li><span class="sw o2"></span>Buses: 31 % of their corridor passengers</li><li><span class="sw o3"></span>Cars: 0.9 % of corridor car trips</li></ul>
      <p class="caption">Where the 7,400 morning LRT riders of 2050 come from.</p></div>
    <div class="facts">
      <div><span class="k">Transit’s share of corridor travel</span><span class="v">19.3 % before the LRT, 20.6 % after</span></div>
      <div><span class="k">What this means</span><span class="v">The light rail reorganises transit more than it creates new travel</span></div>
      <div><span class="k">What not to promise</span><span class="v">Large relief on the roads. The car shift is a few hundred to a thousand trips, and it is the least certain number here</span></div>
    </div>
  </div>''', 'Source: Table 4.3 and section 4.4 of the comprehensive report.'))

SLIDES.append(slide(8, 'chart', 'One line or two',
  'Running through to Nazareth does not add riders to the extension. What it buys is a saved change of vehicle for the 38 percent who cross Hamifrats.',
  f'''<div class="cols chart-cols">
    <div class="chartbox">{CH_THROUGH}<p class="caption">Morning riders in 2050, with priority at junctions. Terminating at Hamifrats was run; the main route alone was not.</p></div>
    <div class="facts">
      <div><span class="k">Extension riders</span><span class="v">6,003 as one line, 5,939 if it ends at Hamifrats: a 1 percent difference</span></div>
      <div><span class="k">The +25 % on the whole line</span><span class="v">Is the main route’s own passengers, carried either way</span></div>
      <div><span class="k">Who gains from one line</span><span class="v">2,849 riders a morning who would otherwise change trains at Hamifrats. The Metronit carries them through today</span></div>
    </div>
  </div>''', 'Source: Table 4.1 and section 4.1 of the comprehensive report.'))

SLIDES.append(slide(9, 'chart', 'Priority at junctions',
  'Priority at the junctions is worth a quarter of the riders, more than ten years of growth.',
  f'''<div class="cols chart-cols">
    <div class="chartbox">{CH_REGIME}<p class="caption">Morning LRT riders on the whole line. "No priority" means the extension runs at street level and waits at junctions with the traffic.</p></div>
    <div class="facts">
      <div><span class="k">Tirat Carmel to Hamifrats</span><span class="v">41 minutes with priority, 66 without</span></div>
      <div><span class="k">Ten years of growth</span><span class="v">Add 18 percent of riders</span></div>
      <div><span class="k">Losing priority</span><span class="v">Removes 23 percent, mostly on the extension itself</span></div>
      <div><span class="k">In every scenario and period</span><span class="v">The loss is 20 to 23 percent</span></div>
    </div>
  </div>''', 'Source: Tables 4.8 and 4.10 of the comprehensive report.'))

SLIDES.append(slide(10, 'chart', 'How full',
  'In the busiest hour, about 1,000 to 1,100 passengers per direction pass the Hamifrats junction: a light-rail scale of demand, not a metro one.',
  f'''<div class="cols chart-cols">
    <div class="chartbox">{CH_PEAK}<p class="caption">Busiest segment, busiest morning hour, one direction, with priority at junctions. These are potential movements with no capacity limit applied.</p></div>
    <div class="facts">
      <div><span class="k">Busiest point</span><span class="v">Entering Hamifrats towards Tirat Carmel in the morning</span></div>
      <div><span class="k">On the extension itself</span><span class="v">About 1,030 per hour in 2050, on the Carmel coast</span></div>
      <div><span class="k">Afternoon</span><span class="v">Lower and more balanced between the two directions</span></div>
    </div>
  </div>''', 'Source: Table 4.2a and section 4.5 of the comprehensive report.'))

SLIDES.append(slide(11, 'chart', 'How sure',
  'A fair planning range is 5,500 to 10,500 morning riders. The central figure sits on the cautious side.',
  f'''<div class="cols chart-cols">
    <div class="chartbox">{CH_RANGE}<p class="caption">The range comes from how strongly travellers respond to a faster trip, the widest single uncertainty tested.</p></div>
    <div class="facts">
      <div><span class="k">Firm part</span><span class="v">The switch from the Metronit and buses rests on observed travel and measured timetables</span></div>
      <div><span class="k">Soft part</span><span class="v">The switch from cars. Read it as an order of magnitude</span></div>
      <div><span class="k">A cautious assumption</span><span class="v">Roads and buses keep 2026 speeds in 2050. If buses slow with traffic, the LRT gains about 5 percent</span></div>
    </div>
  </div>''', 'Source: executive summary planning range; sections 3.4 and 4.9 of the comprehensive report.'))

SLIDES.append(slide(12, 'text', 'The open question',
  'The biggest open question is not in the model: will the Metronit and the light rail share the trunk?',
  '''<div class="cols">
    <div>
      <h3>What the model assumes</h3>
      <ul>
        <li>Every Metronit and bus line keeps running next to the light rail, exactly as today.</li>
        <li>About a third of Metronit passengers on the corridor switch; 7,800 stay because their trip is still quicker on the Metronit.</li>
        <li>This is the cautious case for the light rail.</li>
      </ul>
    </div>
    <div>
      <h3>What a network decision would do</h3>
      <ul>
        <li>Cut the Metronit back on the overlap, and up to its 11,300 morning corridor trips could move to the light rail.</li>
        <li>Reorganise the Metronit to feed the light-rail stations, and the light rail gains riders too.</li>
        <li>Either choice moves the figures more than any uncertainty in this report. Settle it before using them for capacity.</li>
      </ul>
    </div>
  </div>''', 'Source: section 4.4 of the comprehensive report.'))

SLIDES.append(slide(13, 'text', 'Fitness for use',
  'Use these numbers to size the market and rank the options. Do not use them yet to buy trains or set frequencies.',
  '''<div class="cols fit">
    <div class="good">
      <h3>Good for</h3>
      <ul>
        <li>Sizing the extension’s market and locating it: which areas, which stations.</li>
        <li>Ranking the options: one line or two, priority or not.</li>
        <li>The order of magnitude of the draw from the Metronit, buses and cars.</li>
        <li>The scale of the peak load, for the design hour.</li>
      </ul>
    </div>
    <div class="bad">
      <h3>Not yet good for</h3>
      <ul>
        <li>Fleet size, frequencies or capacity: the loads have no capacity limit and were not checked link by link.</li>
        <li>An economic appraisal.</li>
        <li>Any claim about road congestion in 2040 or 2050.</li>
        <li>Numbers for a single station or a single neighbourhood.</li>
      </ul>
    </div>
  </div>''', 'Source: section 3.5 of the comprehensive report.'))

SLIDES.append(slide(14, 'cta', 'The ask',
  'Five decisions we ask you to take.',
  '''<ol class="decisions">
    <li><span class="n">1</span><div><strong>Plan on the 2050 reference case.</strong> About 7,400 morning riders on the line, 6,000 of them on the extension, with 5,500 to 10,500 as the planning range.</div></li>
    <li><span class="n">2</span><div><strong>Protect priority at the junctions in the design.</strong> Without it a quarter of the riders go, and the trip from Tirat Carmel to Hamifrats takes 66 minutes instead of 41.</div></li>
    <li><span class="n">3</span><div><strong>Treat through-running as a question of transfers, not of ridership.</strong> One line spares 2,849 riders a morning a change of trains at Hamifrats; it does not add riders to the extension.</div></li>
    <li><span class="n">4</span><div><strong>Decide the future of the Metronit on the shared trunk</strong> before any capacity or fleet work, because that decision moves the figures more than any uncertainty here.</div></li>
    <li><span class="n">5</span><div><strong>Commission four pieces of work before appraisal:</strong> a split of trips by purpose, a proper afternoon forecast, the main route’s operating plan, and a survey of how willing car owners are to switch.</div></li>
  </ol>''', 'Source: executive decision summary and section 5 of the comprehensive report.'))

SLIDES.append(slide(15, 'recap', 'In one breath',
  'A light-rail-sized market in Haifa and Tirat Carmel, carried mostly from today’s transit, that lives or dies on priority at the junctions.',
  '''<div class="recap-grid">
    <div><span class="big">7,400</span><span class="lab">morning riders on the line in 2050; four in five on the extension</span></div>
    <div><span class="big">3</span><span class="lab">markets of similar size: Tirat Carmel ↔ Haifa, Haifa internal, Krayot by feeder</span></div>
    <div><span class="big">−23 %</span><span class="lab">without priority at junctions, more than ten years of growth adds</span></div>
    <div><span class="big">+1 %</span><span class="lab">extension riders from running through to Nazareth; the gain is a saved transfer</span></div>
  </div>
  <p class="aside">Next: settle the Metronit question, protect priority, and commission the four pieces of work before any appraisal or fleet decision.</p>''',
  ''))

SLIDES.append(slide(16, 'appendix', 'Appendix',
  'Where the numbers come from.',
  '''<div class="cols">
    <div>
      <h3>Data behind the study</h3>
      <ul class="tight">
        <li>Household travel survey 2017/18: 16,401 people, 5,108 households.</li>
        <li>Smart-card bus journeys, May 2022; boardings through 2025.</li>
        <li>Population and jobs forecasts for 2040 and 2050, two scenarios (BU, HS).</li>
        <li>National timetable of 22 May 2026; measured bus and car speeds, May 2026.</li>
        <li>Planned alignment and stations of the extension (22 Sep 2026) and the main route (5 Oct 2026).</li>
        <li>Light-rail running times transferred from the Tel Aviv Red Line.</li>
      </ul>
    </div>
    <div>
      <h3>Terms used here</h3>
      <ul class="tight">
        <li><strong>BU / HS</strong>: business-as-usual and high-growth demographic scenarios.</li>
        <li><strong>With priority</strong>: trams get the green at road junctions ("Prioritized" in the report). <strong>No priority</strong>: street running, queuing with traffic ("Unprioritized").</li>
        <li><strong>Morning peak</strong>: trips leaving 06:00 to 09:00. The busiest hour is about 59 percent of that.</li>
        <li><strong>Riders</strong>: boardings on the light rail, including trips that start or end on a feeder bus or Metronit.</li>
        <li><strong>Corridor</strong>: 25 areas and 174 traffic zones from Tirat Carmel to Nazareth.</li>
      </ul>
    </div>
  </div>
  <p class="aside">Every figure traces to reports/Nofit_LRT_Extension_Comprehensive_Report.docx and the files under Output/ it names. This deck is built by tools/build_decision_deck.py.</p>''',
  ''))

# ---------------- page ----------------
HEAD = '''<title>Nofit Extension Decision Brief</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Public+Sans:ital,wght@0,400;0,600;1,400&display=swap">
<style>
/* Layout: one slide per screen, scroll-snapped vertically; a fixed bottom bar with the counter. Signage-like type, cool neutrals, LRT blue as the accent. */
:root {
  --bg: #eef1f5; --surface: #ffffff; --ink: #14202e; --ink-2: #4b5665; --muted: #7d8794; --hair: #d9dee6; --grid: #e6eaf0;
  --accent: #2a78d6; --accent-ink: #1c5cab; --orange: #eb6834; --aqua: #1baf7a; --wash: rgba(42,120,214,0.12);
  --o1: #184f95; --o2: #3987e5; --o3: #86b6ef; --good: #006300; --bad: #b3261e;
  --display: "Archivo", "Helvetica Neue", Arial, sans-serif; --body: "Public Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0f1419; --surface: #1a2028; --ink: #f2f4f7; --ink-2: #b4bcc7; --muted: #8b95a1; --hair: #2c343e; --grid: #242c36;
  --accent: #3987e5; --accent-ink: #86b6ef; --orange: #d95926; --aqua: #199e70; --wash: rgba(57,135,229,0.18);
  --o1: #86b6ef; --o2: #3987e5; --o3: #1c5cab; --good: #4fc24f; --bad: #f28b82; color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #0f1419; --surface: #1a2028; --ink: #f2f4f7; --ink-2: #b4bcc7; --muted: #8b95a1; --hair: #2c343e; --grid: #242c36;
  --accent: #3987e5; --accent-ink: #86b6ef; --orange: #d95926; --aqua: #199e70; --wash: rgba(57,135,229,0.18);
  --o1: #86b6ef; --o2: #3987e5; --o3: #1c5cab; --good: #4fc24f; --bad: #f28b82; color-scheme: dark; }
html, body { height: 100%; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--body); font-size: 17px; line-height: 1.5; }
.deck { height: 100%; overflow-y: auto; scroll-snap-type: y mandatory; scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { .deck { scroll-behavior: auto; } }
.slide { min-height: 100%; box-sizing: border-box; scroll-snap-align: start; display: flex; align-items: center; padding: 24px 16px 72px; border-bottom: 1px solid var(--hair); }
.inner { width: 100%; max-width: 1080px; margin: 0 auto; display: flex; flex-direction: column; gap: 18px; min-width: 0; overflow-wrap: anywhere; }
.eyebrow { margin: 0; font-family: var(--display); font-weight: 600; font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent-ink); }
h1, h2, h3 { font-family: var(--display); margin: 0; text-wrap: balance; line-height: 1.15; }
h1 { font-size: clamp(2rem, 5vw, 3.6rem); font-weight: 700; max-width: 18ch; }
h2 { font-size: clamp(1.3rem, 2.3vw, 1.8rem); font-weight: 600; max-width: 38ch; }
h3 { font-size: 1.05rem; font-weight: 600; margin-bottom: 8px; }
p { margin: 0; max-width: 68ch; }
.lede { font-size: 1.15rem; color: var(--ink-2); max-width: 60ch; }
.cover .inner { gap: 26px; }
.cover-facts, .facts { display: grid; gap: 12px; align-content: start; }
.cover-facts { grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); border-top: 1px solid var(--hair); padding-top: 18px; }
.cover-facts > div, .facts > div { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.k { font-family: var(--display); font-size: 0.78rem; letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); }
.v { color: var(--ink); }
.facts > div { padding: 10px 0 10px 14px; border-left: 3px solid var(--accent); }
.cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 28px; align-items: start; }
.cols > div { min-width: 0; }
.chart-cols { grid-template-columns: minmax(0, 3fr) minmax(260px, 2fr); }
.map-cols { grid-template-columns: minmax(0, 3fr) minmax(260px, 2fr); }
@media (max-width: 760px) { .chart-cols, .map-cols { grid-template-columns: 1fr; } }
ul { margin: 0; padding-left: 20px; display: flex; flex-direction: column; gap: 8px; }
ul.tight { gap: 5px; font-size: 0.95rem; }
li { max-width: 60ch; }
.tiles, .recap-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; }
.tile, .recap-grid > div { background: var(--surface); border: 1px solid var(--hair); border-radius: 8px; padding: 12px 16px; display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.big { font-family: var(--display); font-weight: 700; font-size: clamp(1.6rem, 3.5vw, 2.3rem); color: var(--accent-ink); line-height: 1.05; }
.lab { color: var(--ink-2); font-size: 0.95rem; }
.steps, .decisions { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; }
.steps { grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); }
.steps li, .decisions li { display: flex; gap: 12px; align-items: flex-start; background: var(--surface); border: 1px solid var(--hair); border-radius: 8px; padding: 14px 16px; min-width: 0; }
.n { flex: none; width: 30px; height: 30px; border-radius: 50%; background: var(--accent); color: #fff; font-family: var(--display); font-weight: 700; display: grid; place-items: center; font-size: 0.95rem; }
.decisions li > div, .steps li > div { max-width: 70ch; }
.aside { color: var(--ink-2); font-size: 0.95rem; border-left: 3px solid var(--hair); padding-left: 12px; }
.chartbox { background: var(--surface); border: 1px solid var(--hair); border-radius: 8px; padding: 14px 16px 12px; min-width: 0; }
.chart { width: 100%; height: auto; display: block; font-family: var(--body); }
.caption { font-size: 0.85rem; color: var(--muted); margin-top: 8px; }
.source { font-size: 0.8rem; color: var(--muted); }
.mapfig { margin: 0; background: #fff; border: 1px solid var(--hair); border-radius: 8px; padding: 8px; min-width: 0; }
.mapfig img { display: block; width: 100%; height: auto; max-width: 100%; border-radius: 4px; }
.mapfig figcaption { font-size: 0.85rem; color: var(--muted); padding: 8px 4px 2px; }
.fit .good h3 { color: var(--good); } .fit .bad h3 { color: var(--bad); }
.fit > div { background: var(--surface); border: 1px solid var(--hair); border-radius: 8px; padding: 16px 18px; }
.keylist { list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 0.85rem; color: var(--ink-2); margin-top: 6px; }
.keylist li { display: flex; align-items: center; gap: 6px; }
.sw { width: 12px; height: 12px; border-radius: 2px; display: inline-block; }
.sw.o1 { background: var(--o1); } .sw.o2 { background: var(--o2); } .sw.o3 { background: var(--o3); }
/* chart ink */
.chart .grid { stroke: var(--grid); stroke-width: 1; }
.chart .axis { stroke: var(--hair); stroke-width: 1; }
.chart .tick, .chart .legend, .chart .note { fill: var(--muted); font-size: 12.5px; }
.chart .cat { fill: var(--ink-2); font-size: 13px; }
.chart .vlabel { fill: var(--ink); font-size: 13px; font-weight: 600; font-variant-numeric: tabular-nums; }
.chart .vlabel.strong { font-size: 13.5px; }
.chart .share { fill: var(--muted); font-weight: 400; }
.chart .mark.c1 { fill: var(--accent); } .chart .mark.c2 { fill: var(--orange); } .chart .mark.c3 { fill: var(--aqua); }
.chart .mark.o1 { fill: var(--o1); } .chart .mark.o2 { fill: var(--o2); } .chart .mark.o3 { fill: var(--o3); }
.chart .mark.wash { fill: var(--wash); }
.chart .mark-line { stroke: var(--accent); stroke-width: 2; stroke-linecap: round; }
.chart .dot.c1 { fill: var(--accent); stroke: var(--surface); stroke-width: 2; }
.chart .dot.hollow { fill: var(--surface); stroke: var(--accent); stroke-width: 2; }
.chart path.mark:hover { opacity: 0.8; }
/* nav */
.bar { position: fixed; left: 0; right: 0; bottom: 0; display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 8px 16px; padding-bottom: calc(8px + env(safe-area-inset-bottom, 0px)); background: var(--surface); border-top: 1px solid var(--hair); font-size: 0.85rem; color: var(--ink-2); z-index: 5; }
.bar .title { font-family: var(--display); font-weight: 600; color: var(--ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
.bar .ctl { display: flex; align-items: center; gap: 8px; flex: none; }
.bar button { font: inherit; font-weight: 600; color: var(--ink); background: var(--bg); border: 1px solid var(--hair); border-radius: 6px; padding: 5px 12px; cursor: pointer; }
.bar button:hover { border-color: var(--accent); } .bar button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.bar .count { font-variant-numeric: tabular-nums; min-width: 4.5ch; text-align: center; }
.progress { position: fixed; left: 0; top: env(safe-area-inset-top, 0px); height: 3px; background: var(--accent); width: 0; z-index: 6; transition: width 0.2s; }
@media (prefers-reduced-motion: reduce) { .progress { transition: none; } }
</style>'''

BODY = f'''<div class="progress" id="progress"></div>
<main class="deck" id="deck">
{chr(10).join(SLIDES)}
</main>
<nav class="bar" aria-label="Slide navigation">
  <span class="title">Nofit light rail · extension through Haifa to Tirat Carmel</span>
  <span class="ctl"><button type="button" id="prev" aria-label="Previous slide">‹ Prev</button><span class="count" id="count">1 / {len(SLIDES)}</span><button type="button" id="next" aria-label="Next slide">Next ›</button></span>
</nav>
<script>
(function () {{
  var deck = document.getElementById('deck'), slides = Array.prototype.slice.call(deck.querySelectorAll('.slide'));
  var count = document.getElementById('count'), progress = document.getElementById('progress'), cur = 0;
  function show(i) {{ i = Math.max(0, Math.min(slides.length - 1, i)); slides[i].scrollIntoView({{ block: 'start' }}); }}
  function update() {{
    var top = deck.scrollTop, best = 0, bestD = Infinity;
    slides.forEach(function (s, i) {{ var d = Math.abs(s.offsetTop - top); if (d < bestD) {{ bestD = d; best = i; }} }});
    cur = best; count.textContent = (cur + 1) + ' / ' + slides.length; progress.style.width = ((cur + 1) / slides.length * 100) + '%';
    try {{ localStorage.setItem('nofit-deck-slide', String(cur)); }} catch (e) {{}}
  }}
  deck.addEventListener('scroll', update, {{ passive: true }});
  document.getElementById('prev').addEventListener('click', function () {{ show(cur - 1); }});
  document.getElementById('next').addEventListener('click', function () {{ show(cur + 1); }});
  document.addEventListener('keydown', function (e) {{
    if (e.target && /input|textarea|select/i.test(e.target.tagName)) return;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === 'PageDown' || e.key === ' ') {{ e.preventDefault(); show(cur + 1); }}
    else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'PageUp') {{ e.preventDefault(); show(cur - 1); }}
    else if (e.key === 'Home') {{ e.preventDefault(); show(0); }} else if (e.key === 'End') {{ e.preventDefault(); show(slides.length - 1); }}
  }});
  var hash = (location.hash || '').replace('#', ''); var m = /^s(\\d+)$/.exec(hash);
  if (m) {{ show(parseInt(m[1], 10) - 1); }}
  update();
}})();
</script>'''

def main():
    body_only = '--body-only' in sys.argv
    if body_only:
        out = sys.argv[sys.argv.index('--body-only') + 1]
        open(out, 'w', encoding='utf-8').write(HEAD + '\n' + BODY + '\n')
    else:
        html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                + HEAD + '\n</head>\n<body>\n' + BODY + '\n</body>\n</html>\n')
        open(OUT_HTML, 'w', encoding='utf-8').write(html); print(OUT_HTML, f'{len(html) / 1024:.0f} KB', f'{len(SLIDES)} slides')

if __name__ == '__main__': main()
