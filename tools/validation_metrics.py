"""Validation statistics used by the Ministry of Transport guideline (draft 6, September 2024).

One place for the statistics of the guideline's appendix and for its numeric criteria, so that every
validation notebook computes and judges them the same way.  Plain numpy / scipy; no repository paths.

Conventions
-----------
* ``obs`` is the observed / control value (x axis of every scatter), ``mod`` the model value (y axis).
* ``rmse_pct`` = RMSE / mean(obs) * 100, RMSE = sqrt(sum((mod - obs)^2) / N).  The guideline prints the
  formula as an image; this is the standard definition (N, not N - 1).
* ``slope_origin`` is the least-squares slope of mod on obs through the origin (the guideline asks for
  regression lines forced through (0, 0)); ``r2_correl`` is the guideline's R2 = Correl(obs, mod)^2.
* ``coincidence_ratio`` = sum_n min(p_n, q_n) / sum_n max(p_n, q_n) on the two distributions (1.0 perfect).
  Inputs are normalised to proportions first, as the guideline specifies.
* GEH is deliberately absent: the guideline drops it.
"""
import numpy as np
from scipy import stats

# --- the guideline's numeric criteria -------------------------------------------------------------
CRIT = {
    'R2_min': 0.85, 'slope_lo': 0.9, 'slope_hi': 1.1,
    'RMSE_pct_aggregate_max': 35.0,
    'CR_min': 0.6,
    'pct_within_time': {'bus': 15.0, 'metronit': 10.0, 'rail': 10.0, 'car': 15.0}, 'share_within_time_min': 0.85,
    'screenline_pct': {'external': 10.0, 'other': 15.0},
    'metro_section_pct': 20.0,
}
# RMSE% limits by observed volume class: (lower bound inclusive, upper bound exclusive, limit %)
ROAD_RMSE_CLASSES = [(0, 500, 50.0), (500, 1000, 40.0), (1000, 2000, 30.0), (2000, 3000, 25.0),
                     (3000, 6000, 20.0), (6000, 8000, 18.0), (8000, np.inf, 12.0)]
STATION_RMSE_CLASSES = [(0, 100, 50.0), (100, 250, 40.0), (250, 500, 30.0), (500, 750, 20.0),
                        (750, 1000, 15.0), (1000, np.inf, 12.0)]
# allowed absolute difference in % of the observed value, boardings per bus line
LINE_DIFF_CLASSES = [(0, 100, 100.0), (100, 200, 65.0), (200, 500, 35.0), (500, 1000, 25.0),
                     (1000, 2000, 20.0), (2000, np.inf, 10.0)]


def _clean(obs, mod):
    obs = np.asarray(obs, float).ravel(); mod = np.asarray(mod, float).ravel()
    ok = np.isfinite(obs) & np.isfinite(mod)
    return obs[ok], mod[ok]


def r2_correl(obs, mod):
    """Guideline R2 = Correl(obs, mod)^2 (Excel CORREL squared)."""
    o, m = _clean(obs, mod)
    if len(o) < 3 or o.std() == 0 or m.std() == 0:
        return np.nan
    return float(np.corrcoef(o, m)[0, 1] ** 2)


def slope_origin(obs, mod):
    """Slope of mod on obs through the origin."""
    o, m = _clean(obs, mod)
    d = float((o * o).sum())
    return float((o * m).sum() / d) if d > 0 else np.nan


def r2_origin(obs, mod):
    """Uncentred R2 of the regression through the origin: 1 - SSE / sum(mod^2)."""
    o, m = _clean(obs, mod)
    b = slope_origin(o, m)
    den = float((m * m).sum())
    return float(1 - ((m - b * o) ** 2).sum() / den) if den > 0 else np.nan


def mae(obs, mod):
    o, m = _clean(obs, mod); return float(np.abs(m - o).mean()) if len(o) else np.nan


def rmse(obs, mod):
    o, m = _clean(obs, mod); return float(np.sqrt(((m - o) ** 2).mean())) if len(o) else np.nan


def rmse_pct(obs, mod):
    o, m = _clean(obs, mod)
    return float(100 * np.sqrt(((m - o) ** 2).mean()) / o.mean()) if len(o) and o.mean() != 0 else np.nan


def pct_diff(obs, mod):
    """Difference in % of the observed value, elementwise (nan where obs is 0)."""
    obs = np.asarray(obs, float); mod = np.asarray(mod, float)
    return np.where(obs != 0, 100 * (mod - obs) / np.where(obs == 0, 1, obs), np.nan)


def fit_stats(obs, mod):
    """All scatter statistics in one dict, for the summary tables."""
    o, m = _clean(obs, mod)
    return {'n': int(len(o)), 'obs_total': float(o.sum()), 'mod_total': float(m.sum()),
            'total_diff_pct': float(100 * (m.sum() - o.sum()) / o.sum()) if o.sum() else np.nan,
            'R2': r2_correl(o, m), 'slope_origin': slope_origin(o, m), 'R2_origin': r2_origin(o, m),
            'MAE': mae(o, m), 'RMSE': rmse(o, m), 'RMSE_pct': rmse_pct(o, m)}


def coincidence_ratio(p, q):
    """CR on two distributions (arrays of any shape; normalised to proportions first)."""
    p = np.asarray(p, float).ravel(); q = np.asarray(q, float).ravel()
    ok = np.isfinite(p) & np.isfinite(q); p, q = p[ok], q[ok]
    sp, sq = p.sum(), q.sum()
    if sp <= 0 or sq <= 0:
        return np.nan
    p, q = p / sp, q / sq
    return float(np.minimum(p, q).sum() / np.maximum(p, q).sum())


def chi2_test(obs_counts, exp_counts, alpha=0.05):
    """Chi-square on counts (not percentages): returns statistic, critical value (k - 1 df) and pass flag."""
    o = np.asarray(obs_counts, float).ravel(); e = np.asarray(exp_counts, float).ravel()
    ok = e > 0; o, e = o[ok], e[ok]
    x2 = float(((o - e) ** 2 / e).sum()); df = len(o) - 1
    crit = float(stats.chi2.ppf(1 - alpha, df)) if df > 0 else np.nan
    return {'chi2': x2, 'df': df, 'critical': crit, 'pass': bool(x2 < crit) if df > 0 else None}


def kish_n(w):
    """Kish effective sample size of a weight vector."""
    w = np.asarray(w, float); w = w[np.isfinite(w) & (w > 0)]
    return float(w.sum() ** 2 / (w ** 2).sum()) if len(w) else 0.0


def ks_weighted(x1, w1, x2, w2, n1=None, n2=None, alpha=0.05):
    """Two-sample KS statistic D with weights; critical value c(alpha) * sqrt((n1 + n2) / (n1 n2)).

    ``n1`` / ``n2`` default to the Kish effective sample sizes (expansion weights would otherwise make
    every difference significant); pass the unweighted sample counts to use those instead.
    Returns D, the two sample sizes used, the critical value and the pass flag (D < critical)."""
    x1 = np.asarray(x1, float); w1 = np.asarray(w1, float); x2 = np.asarray(x2, float); w2 = np.asarray(w2, float)
    ok1 = np.isfinite(x1) & np.isfinite(w1) & (w1 > 0); ok2 = np.isfinite(x2) & np.isfinite(w2) & (w2 > 0)
    x1, w1, x2, w2 = x1[ok1], w1[ok1], x2[ok2], w2[ok2]
    grid = np.union1d(x1, x2)
    o1 = np.argsort(x1); o2 = np.argsort(x2)
    c1 = np.concatenate([[0], np.cumsum(w1[o1])]) / w1.sum(); c2 = np.concatenate([[0], np.cumsum(w2[o2])]) / w2.sum()
    f1 = c1[np.searchsorted(x1[o1], grid, side='right')]; f2 = c2[np.searchsorted(x2[o2], grid, side='right')]
    D = float(np.abs(f1 - f2).max())
    n1 = kish_n(w1) if n1 is None else n1; n2 = kish_n(w2) if n2 is None else n2
    c_alpha = float(np.sqrt(-0.5 * np.log(alpha / 2)))
    crit = float(c_alpha * np.sqrt((n1 + n2) / (n1 * n2))) if n1 > 0 and n2 > 0 else np.nan
    return {'D': D, 'n1': n1, 'n2': n2, 'critical': crit, 'pass': bool(D < crit)}


def within_pct(obs, mod, limit_pct):
    """Share of measurements whose model value is within +/- limit_pct % of the observation."""
    o, m = _clean(obs, mod)
    ok = o != 0
    return float((np.abs(100 * (m[ok] - o[ok]) / o[ok]) <= limit_pct).mean()) if ok.any() else np.nan


def class_limit(value, classes):
    for lo, hi, lim in classes:
        if lo <= value < hi:
            return lim
    return np.nan


def rmse_by_class(obs, mod, classes):
    """RMSE% per observed-volume class against the class limit.  Returns a list of dict rows."""
    o, m = _clean(obs, mod)
    rows = []
    for lo, hi, lim in classes:
        sel = (o >= lo) & (o < hi)
        if sel.sum() == 0:
            continue
        r = rmse_pct(o[sel], m[sel])
        rows.append({'class': f'{lo:g}-{hi:g}' if np.isfinite(hi) else f'{lo:g}+', 'n': int(sel.sum()),
                     'obs_mean': float(o[sel].mean()), 'RMSE_pct': r, 'limit_pct': lim, 'pass': bool(r <= lim)})
    return rows


def line_diff_check(obs, mod, classes=LINE_DIFF_CLASSES):
    """Per-item |difference %| against the volume-class allowance (guideline's boardings-per-line row)."""
    o, m = _clean(obs, mod)
    d = np.abs(pct_diff(o, m)); lim = np.array([class_limit(v, classes) for v in o])
    return {'share_within_allowance': float(np.mean(d <= lim)), 'n': int(len(o))}


def verdict(ok, explained=None):
    """Status word used in the summary sheet."""
    if ok is None:
        return 'not run'
    if ok:
        return 'pass'
    return 'miss (explained)' if explained else 'miss (unexplained)'
