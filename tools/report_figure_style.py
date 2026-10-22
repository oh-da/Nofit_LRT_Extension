"""Shared design language for the Hebrew report figures (Output/figures/report/).

Palette is the notebooks' (extension blue, main-route orange, warm greys); text is right-to-left Hebrew
with the action title on the right, a one-line subtitle under it, and a source line at the bottom.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from bidi.algorithm import get_display

BLUE, ORANGE, AQUA, PURPLE, INK, INK2, MUTED, GRID, AXIS = '#2a78d6', '#eb6834', '#1baf7a', '#7b5bd6', '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7'
SEA = '#eef3f8'
FIG_DIR = 'Output/figures/report'
DPI = 200

_have = {f.name for f in font_manager.fontManager.ttflist}
FONT = next((f for f in ('Arial', 'Heebo', 'Assistant', 'Noto Sans Hebrew', 'DejaVu Sans') if f in _have), 'DejaVu Sans')
plt.rcParams.update({'font.family': FONT, 'axes.unicode_minus': False, 'text.color': INK, 'figure.facecolor': 'white'})


try:
    from matplotlib import ft2font; _RAQM = bool(getattr(ft2font, '__libraqm_version__', None))
except Exception: _RAQM = False


def he(s):
    """Hebrew string for matplotlib. With libraqm (matplotlib >= 3.10) the logical string is laid out right-to-left by matplotlib itself;
    without it the string is reordered to visual order here. Latin / digits stay left-to-right inside the Hebrew line."""
    return s if _RAQM else get_display(s, base_dir='R')


def heading(fig, title, subtitle=None, x=0.985):
    """Action title (bold, right-aligned) and subtitle, in figure coordinates."""
    fig.text(x, 0.965, he(title), ha='right', va='top', fontsize=15, fontweight='bold', color=INK)
    if subtitle: fig.text(x, 0.915, he(subtitle), ha='right', va='top', fontsize=10.5, color=INK2)


def source(fig, text, x=0.985):
    fig.text(x, 0.012, he(text), ha='right', va='bottom', fontsize=7.5, color=MUTED)


def save(fig, name):
    import os; os.makedirs(FIG_DIR, exist_ok=True)
    p = f'{FIG_DIR}/{name}'; fig.savefig(p, dpi=DPI, facecolor='white'); plt.close(fig); return p
