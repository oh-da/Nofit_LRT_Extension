"""Convert the client FAQ Markdown (English or Hebrew) to a DOCX: headings, hard-wrapped paragraphs, bullet and numbered lists
with continuation lines, any number of tables, **bold**, `code`. Direction is right-to-left when the file holds a <div dir="rtl">.
Usage: python3 tools/faq_md_to_docx.py docs/CLIENT_FAQ.md reports/Nofit_LRT_Extension_Client_FAQ.docx
       python3 tools/faq_md_to_docx.py docs/CLIENT_FAQ_HE.md reports/Nofit_LRT_Extension_Client_FAQ_HE.docx"""
import re, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

src, dst = sys.argv[1], sys.argv[2]
raw = [l.rstrip('\n') for l in open(src, encoding='utf-8')]
RTL = any(l.strip().startswith('<div dir="rtl"') for l in raw)
lines = [l for l in raw if not l.strip().startswith('<div') and l.strip() != '</div>']
FONT = 'Arial'; NAVY = '1F3864'; BLUE = '2F5597'; TEXTW = 16.6
ALIGN = WD_ALIGN_PARAGRAPH.RIGHT if RTL else WD_ALIGN_PARAGRAPH.LEFT
doc = Document(); sec = doc.sections[0]; sec.left_margin = sec.right_margin = Cm(2.2); sec.top_margin = sec.bottom_margin = Cm(2)
st = doc.styles['Normal']; st.font.name = FONT; st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn('w:cs'), FONT); st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)

LRM = '‎'
RANGE = re.compile(r'(\d[\d.,:]*%?)\s?([–-])\s?(\d[\d.,:]*%?)')          # number ranges stay left-to-right inside right-to-left text
def fix(t):
    if not RTL: return t.replace(' %', '\u00a0%')
    return RANGE.sub(lambda m: f'{LRM}{m.group(1)}{LRM}{m.group(2)}{LRM}{m.group(3)}{LRM}', t.replace(' %', '%'))
def fmt(r, size=None, bold=False, mono=False, color=None):
    rPr = r._r.get_or_add_rPr(); name = 'Consolas' if mono else FONT
    r.font.name = name; rPr.rFonts.set(qn('w:cs'), name)
    if RTL and not mono: rPr.append(OxmlElement('w:rtl'))
    if size: r.font.size = Pt(size); sz = OxmlElement('w:szCs'); sz.set(qn('w:val'), str(int(size * 2))); rPr.append(sz)
    if bold: r.bold = True; rPr.append(OxmlElement('w:bCs'))
    if color: r.font.color.rgb = RGBColor.from_string(color)
TOK = re.compile(r'(\*\*.+?\*\*|`.+?`)')
def inline(p, text, size=None, bold=False, color=None):
    for part in TOK.split(fix(text)):
        if not part: continue
        if part.startswith('**'): fmt(p.add_run(part[2:-2]), size, True, color=color)
        elif part.startswith('`'): fmt(p.add_run(part[1:-1]), (size or 11) - 1, bold, mono=True, color=color)
        else: fmt(p.add_run(part), size, bold, color=color)
def par(text, size=11, after=6, before=0, bold=False, color=None, indent=0, hang=0, keep=False, container=None):
    p = (container or doc).add_paragraph(); pf = p.paragraph_format
    if RTL: p._p.get_or_add_pPr().append(OxmlElement('w:bidi'))
    p.alignment = ALIGN; pf.space_after = Pt(after); pf.space_before = Pt(before); pf.keep_with_next = keep
    if indent and RTL: pf.right_indent = Cm(indent - hang)
    elif indent: pf.left_indent = Cm(indent); pf.first_line_indent = Cm(-hang)
    inline(p, text, size, bold, color); return p
def shade(cell, fill):
    sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:fill'), fill); cell._tc.get_or_add_tcPr().append(sh)
def table(rows_md):
    rows = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows_md if not re.match(r'^\|[-:| ]+\|$', r.strip())]
    n = len(rows[0]); wid = {2: [5.0, TEXTW - 5.0], 3: [6.6, 5.4, 4.6]}.get(n, [TEXTW / n] * n)
    t = doc.add_table(rows=len(rows), cols=n); t.style = 'Table Grid'; t.alignment = 2 if RTL else 0; t.autofit = False
    if RTL: t._tbl.tblPr.append(OxmlElement('w:bidiVisual'))
    for ri, row in enumerate(rows):
        for ci, txt in enumerate(row):
            c = t.rows[ri].cells[ci]; c.width = Cm(wid[ci]); c.paragraphs[0]._p.getparent().remove(c.paragraphs[0]._p)
            par(txt, 10, 2, bold=(ri == 0), color='FFFFFF' if ri == 0 else None, container=c)
            if ri == 0: shade(c, NAVY)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

# group the hard-wrapped lines into blocks
blocks = []; cur = None
def close():
    global cur
    if cur: blocks.append(cur)
    cur = None
for l in lines:
    s = l.strip()
    if not s or s == '---': close(); continue
    if s.startswith('|'):
        if not cur or cur[0] != 'table': close(); cur = ['table', []]
        cur[1].append(s); continue
    m = re.match(r'^(#{1,3}) (.*)$', s)
    if m: close(); blocks.append(['h%d' % len(m.group(1)), m.group(2)]); continue
    m = re.match(r'^(\d+)\. (.*)$', s) if not s.startswith('**') else None
    if m: close(); cur = ['num', m.group(2), m.group(1)]; continue
    if s.startswith('- '): close(); cur = ['bul', s[2:]]; continue
    if cur and cur[0] in ('p', 'num', 'bul'): cur[1] += ' ' + s
    else: close(); cur = ['p', s]
close()

for b in blocks:
    k = b[0]
    if k == 'table': table(b[1])
    elif k == 'h1': par(b[1], 17, 10, bold=True, color=NAVY)
    elif k == 'h2': par(b[1], 13.5, 6, 14, bold=True, color=NAVY, keep=True)
    elif k == 'h3': par(b[1], 12, 4, 10, bold=True, color=BLUE, keep=True)
    elif k == 'num': par(f'{b[2]}. {b[1]}', 11, 4, indent=1.0, hang=0.6)
    elif k == 'bul': par('• ' + b[1], 11, 4, indent=1.0, hang=0.4)
    elif re.match(r'^\*\*\d+\. .*\*\*$', b[1]): par(b[1][2:-2], 11.5, 3, 8, bold=True, color=BLUE, keep=True)   # a question
    else: par(b[1], 11)
doc.save(dst); print('saved', dst, 'RTL' if RTL else 'LTR', len(blocks), 'blocks')
