"""Build the scenario workbook: step 45's LRT demand model as live Excel formulas, zone pair by zone pair.

    python3 tools/scenario_metronit_skims.py        # once: the Metronit network variants (Output/scenario_tool/)
    python3 tools/build_scenario_workbook.py        # writes exports/Nofit_LRT_Scenario_Model.xlsx
    python3 tools/build_scenario_workbook.py --check-only

The workbook holds the 26,022 inter-area corridor TAZ pairs that carry any trip in any scenario-year (AM 06:00-09:00) with
their base car and transit trips (2022 and the four forecast sets) and, for every Metronit network variant, alternative
and regime, the precomputed costs of `tools/scenario_metronit_skims.py`. Each pair row runs step 45's incremental logit
(METHODOLOGY 6aq / 6ac) in formulas that read the Inputs sheet, so a change of lambda, lambda_T, the LRT premiums, the
smoothing weight, the LRT headway, station access or running time, the scenario-year, the alternative, the regime or the
Metronit network recalculates every pair, TAZ, area, station and segment.

A network change enters the pivot as the change of the transit nest's composite cost against today's network:
    Delta = (GC_transit_variant - GC_transit_today) - ln(1 + exp(-lambda_T * dL)) / lambda_T,   dL = GC_LRT - premium - GC_transit_variant
which is step 45's logsum term when the Metronit is kept (the first bracket is then zero) and turns negative for transit
(trips move to the car) where a Metronit cut is not made up by the LRT.

Before writing, the script runs the same pivot in numpy at the default inputs with the Metronit as today and checks it
against Output/alternatives/demand_summary.csv (all 20 AM combinations); it stops if any LRT total differs by more than
0.5 trips. The static sheets (reference values, the lambda sweep, the scenario grid) come from that numpy run.
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

from openpyxl import Workbook  # noqa: E402
from openpyxl.chart import BarChart, LineChart, Reference  # noqa: E402
from openpyxl.comments import Comment  # noqa: E402
from openpyxl.chart.series import SeriesLabel  # noqa: E402
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule  # noqa: E402
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side  # noqa: E402
from openpyxl.utils import get_column_letter as CL  # noqa: E402
from openpyxl.workbook.defined_name import DefinedName  # noqa: E402
from openpyxl.worksheet.datavalidation import DataValidation  # noqa: E402

SK_DIR = 'Output/scenario_tool'
OUT_XLSX = 'exports/Nofit_LRT_Scenario_Model.xlsx'

SCEN = ['2022', 'BU_2040', 'BU_2050', 'HS_2040', 'HS_2050']
SCEN_LABEL = {'2022': '2022 (base year)', 'BU_2040': '2040 BU (business as usual)', 'BU_2050': '2050 BU (reference case)',
              'HS_2040': '2040 HS (high growth)', 'HS_2050': '2050 HS (high growth)'}
ALTS = ['main_ext', 'ext']
ALT_LABEL = {'main_ext': 'Main route + extension (through line)', 'ext': 'Extension only (Tirat Carmel - Hamifrats)'}
ALT_SUMMARY = {'main_ext': 'Main route + extension', 'ext': 'Extension only'}
REGS = ['prioritized', 'unprioritized']
REG_LABEL = {'prioritized': 'Prioritized (priority at junctions)', 'unprioritized': 'Unprioritized (at grade)'}
VARS = ['M0', 'M1', 'M2']
VAR_LABEL = {'M0': 'M0 - Metronit as today (all 5 lines)',
             'M1': 'M1 - Metronit cut back to Hamifrats (removed in Haifa)',
             'M2': 'M2 - Metronit removed everywhere'}
W_WAIT = 2.0
DEFAULTS = {'lam': 0.03, 'ratio': 2.0, 'prem_bus': 5.0, 'prem_brt': 2.5, 'k': 20.0, 'headway': 5.0, 'st_access': 0.5,
            'f_ext': 1.0, 'f_main': 1.0, 'lrt_on': 1}
PHF = {'dir1': 0.549, 'dir2': 0.457}             # Output/alternatives/peak_hour_factors.csv, AM line loads by direction
N_EXT = 24                                       # extension stations S01-S24 are orders 1-24 in both alternatives
LAMBDAS = [0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06]


# ----------------------------------------------------------------------------------------------------------------------
# data and the numpy pivot
# ----------------------------------------------------------------------------------------------------------------------
def rdm(path, tazs):
    m = pd.read_csv(path, index_col=0)
    m.columns = m.columns.astype(int)
    m.index = m.index.astype(int)
    return m.reindex(index=tazs, columns=tazs).fillna(0.0).values


def load():
    xl = pd.ExcelFile('Input/Corridor_TAZ_Agg_V2.xlsx')
    areas = xl.parse('AreaCodes')
    key = xl.parse('TazAgg')
    D = {'AREAS': [int(a) for a in areas['AggCode']], 'ANAME': dict(zip(areas['AggCode'].astype(int), areas['AggAreaName']))}
    TAZS = sorted(key['TAZ'].astype(int))
    D['TAZS'] = TAZS
    ta = key.set_index('TAZ')['AggCode'].reindex(TAZS).astype(int).values
    D['ta'] = ta
    D['apos'] = {a: i for i, a in enumerate(D['AREAS'])}
    D['tai'] = np.array([D['apos'][a] for a in ta])
    INTER = ta[:, None] != ta[None, :]
    D['INTER'] = INTER
    zon = pd.read_csv('Input/Zonal_2020.csv', encoding='windows-1255').set_index('TAZ_ID')
    D['pop'] = zon['POPULATION'].reindex(TAZS).fillna(0).values
    D['emp'] = zon['EMPL_TOT'].reindex(TAZS).fillna(0).values
    BASE = {}
    for sc in SCEN:
        if sc == '2022':
            c = rdm('Output/final_2022/car_2022_taz.csv', TAZS)
            t = rdm('Output/final_2022/transit_2022_taz.csv', TAZS)
        else:
            c = rdm(f'Output/forecast_taz/{sc}/car_{sc}_taz.csv', TAZS)
            t = rdm(f'Output/forecast_taz/{sc}/transit_{sc}_taz.csv', TAZS)
        BASE[sc] = (c * INTER, t * INTER)
    D['BASE'] = BASE
    rd = lambda name: pd.read_csv(f'{SK_DIR}/{name}.csv.gz', index_col=0).values  # noqa: E731
    D['GCB'] = {(v, a): rd(f'transit_gc_no_lrt_{v}_{a}') for v in VARS for a in ALTS}
    D['BRT'] = {(v, a): rd(f'metronit_based_{v}_{a}') for v in VARS for a in ALTS}
    D['GCL'] = {(v, a, r): rd(f'lrt_gc_{v}_{a}_{r}') for v in VARS for a in ALTS for r in REGS}
    D['BRD'] = {(v, a, r): rd(f'lrt_board_{v}_{a}_{r}').astype(int) for v in VARS for a in ALTS for r in REGS}
    D['ALI'] = {(v, a, r): rd(f'lrt_alight_{v}_{a}_{r}').astype(int) for v in VARS for a in ALTS for r in REGS}
    D['ST'] = {a: pd.read_csv(f'{SK_DIR}/stations_{a}.csv') for a in ALTS}
    return D


def to_area(D, M):
    A = len(D['AREAS'])
    out = np.zeros((A, A))
    NT = len(D['TAZS'])
    np.add.at(out, (D['tai'][:, None].repeat(NT, 1), D['tai'][None, :].repeat(NT, 0)), np.nan_to_num(M))
    return out


def pivot(D, sc, alt, reg, v, P=None):
    """step 45's pivot for one combination, with the Metronit network variant v; P overrides DEFAULTS"""
    P = {**DEFAULTS, **(P or {})}
    car, tr = D['BASE'][sc]
    n = car + tr
    Fc, Ft = to_area(D, car), to_area(D, tr)
    p0 = Ft.sum() / max((Fc + Ft).sum(), 1e-9)
    S_area = np.where(Fc + Ft > 0, Ft / np.where(Fc + Ft > 0, Fc + Ft, 1), p0)
    S_prior = S_area[np.ix_(D['tai'], D['tai'])]
    S_piv = np.where(n > 0, (tr + P['k'] * S_prior) / (n + P['k']), 0.0)
    gcb0 = np.nan_to_num(D['GCB'][('M0', alt)])
    gcb = np.nan_to_num(D['GCB'][(v, alt)])
    brt0 = D['BRT'][('M0', alt)]
    brt = D['BRT'][(v, alt)]
    gcl = np.nan_to_num(D['GCL'][(v, alt, reg)])
    a, b = D['BRD'][(v, alt, reg)], D['ALI'][(v, alt, reg)]
    avail = (a > 0) & (n > 0) & (P['lrt_on'] == 1)
    t = D['ST'][alt][f'time_from_S01_{reg}'].values
    cumE, cumM = np.minimum(t, t[N_EXT - 1]), np.maximum(0.0, t - t[N_EXT - 1])
    ai, bi = np.where(avail, a - 1, 0), np.where(avail, b - 1, 0)
    ivtE, ivtM = np.abs(cumE[ai] - cumE[bi]), np.abs(cumM[ai] - cumM[bi])
    adj = 2 * (P['st_access'] - 0.5) + W_WAIT * (P['headway'] / 2 - 2.5)
    gcl2 = np.where(avail, gcl + (P['f_ext'] - 1) * ivtE + (P['f_main'] - 1) * ivtM + adj, 0.0)
    prem = np.where(brt == 1, P['prem_brt'], P['prem_bus'])
    lamT = P['lam'] * P['ratio']
    dL = np.where(avail, gcl2 - prem - gcb, 0.0)
    PL = np.where(avail, 1 / (1 + np.exp(np.minimum(500, lamT * dL))), 0.0)
    delta = (gcb - gcb0) + np.where(avail, -np.log1p(np.exp(np.minimum(500, -lamT * dL))) / lamT, 0.0)
    e = np.exp(-P['lam'] * delta)
    S_new = np.where(n > 0, S_piv * e / (S_piv * e + 1 - S_piv), 0.0)
    growth = np.where(S_piv > 0, S_new / np.where(S_piv > 0, S_piv, 1), 1.0)
    tr1 = np.minimum(tr * growth, n)
    car1 = n - tr1
    lrt = tr1 * PL
    R = {'car0': car, 'tr0': tr, 'car1': car1, 'tr1': tr1, 'lrt': lrt, 'PL': PL,
         'lrt_car': np.maximum(0, tr1 - tr) * PL, 'lrt_brt': np.minimum(tr1, tr) * PL * brt0, 'lrt_bus': np.minimum(tr1, tr) * PL * (1 - brt0),
         'brt1': (tr1 - lrt) * brt, 'bus1': (tr1 - lrt) * (1 - brt), 'brt0': tr * brt0, 'bus0': tr * (1 - brt0),
         'tr_to_car': np.maximum(0, tr - tr1), 'a': np.where(avail, a, 0), 'b': np.where(avail, b, 0)}
    R['lrt_ext'] = np.where(avail & (np.minimum(a, b) <= N_EXT - 1), lrt, 0.0)
    nst = len(D['ST'][alt])
    seg1, seg2 = np.zeros(nst - 1), np.zeros(nst - 1)
    board, alight = np.zeros(nst), np.zeros(nst)
    for i, j in zip(*np.where(lrt > 0)):
        oa, ob, x = a[i, j] - 1, b[i, j] - 1, lrt[i, j]
        board[oa] += x
        alight[ob] += x
        if ob > oa:
            seg1[oa:ob] += x
        else:
            seg2[ob:oa] += x
    R.update({'seg1': seg1, 'seg2': seg2, 'board': board, 'alight': alight})
    return R


def totals(R):
    s = {k: float(R[k].sum()) for k in ('car0', 'tr0', 'car1', 'tr1', 'lrt', 'lrt_car', 'lrt_brt', 'lrt_bus', 'brt0', 'bus0', 'brt1', 'bus1', 'tr_to_car', 'lrt_ext')}
    s['busiest'] = float(max(R['seg1'].max(), R['seg2'].max()))
    return s


def check_against_step45(D):
    ds = pd.read_csv('Output/alternatives/demand_summary.csv')
    ds = ds[ds['period'] == 'AM']
    rows, worst = [], 0.0
    for sc in SCEN:
        for alt in ALTS:
            for reg in REGS:
                t = totals(pivot(D, sc, alt, reg, 'M0'))
                r = ds[(ds['scenario'].astype(str) == sc) & (ds['alternative'] == ALT_SUMMARY[alt]) & ds['regime'].str.startswith(REG_LABEL[reg].split(' ')[0])].iloc[0]
                pairs = [('LRT', t['lrt'], r['LRT']), ('car', t['car1'], r['car']), ('bus', t['bus1'], r['bus']), ('Metronit', t['brt1'], r['BRT (Metronit)']),
                         ('LRT from car', t['lrt_car'], r['LRT from car']), ('LRT using extension', t['lrt_ext'], r['LRT trips using the extension (at least one segment S01–S24)']),
                         ('busiest segment', t['busiest'], r['busiest segment load (3 h, one direction)'])]
                for name, mine, pub in pairs:
                    worst = max(worst, abs(mine - pub)) if name == 'LRT' else worst
                    rows.append({'scenario': sc, 'alternative': alt, 'regime': reg, 'measure': name, 'this model': round(mine, 1), 'step 45': pub, 'diff': round(mine - pub, 2)})
    chk = pd.DataFrame(rows)
    return chk, worst, ds


# ----------------------------------------------------------------------------------------------------------------------
# workbook styles
# ----------------------------------------------------------------------------------------------------------------------
FONT = 'Arial'
F_BASE = Font(name=FONT, size=10)
F_INPUT = Font(name=FONT, size=10, color='0000FF')
F_LINK = Font(name=FONT, size=10, color='008000')
F_BOLD = Font(name=FONT, size=10, bold=True)
F_HDR = Font(name=FONT, size=10, bold=True, color='FFFFFF')
F_TITLE = Font(name=FONT, size=14, bold=True)
F_SUB = Font(name=FONT, size=11, bold=True)
F_NOTE = Font(name=FONT, size=9, italic=True, color='595959')
F_GREY = Font(name=FONT, size=10, color='808080')
FILL_INPUT = PatternFill('solid', fgColor='FFFF00')
FILL_HDR = PatternFill('solid', fgColor='1F4E78')
FILL_BLOCK = PatternFill('solid', fgColor='D9E1F2')
FILL_DATA = PatternFill('solid', fgColor='F2F2F2')
FILL_KEY = PatternFill('solid', fgColor='E2EFDA')
THIN = Side(style='thin', color='BFBFBF')
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical='top')
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
VMID = Alignment(vertical='center', wrap_text=True)
VMID_R = Alignment(vertical='center', horizontal='right')
NF_TRIPS = '#,##0;(#,##0);-'
NF_TRIPS2 = '#,##0.00;(#,##0.00);-'
NF_PCT = '0.0%;(0.0%);-'
NF_GC = '0.0'
NF_SHARE = '0.000'


def name(wb, nm, ref):
    wb.defined_names[nm] = DefinedName(nm, attr_text=ref)


def hdr(ws, row, col, text, width=None, fill=FILL_HDR, font=F_HDR):
    c = ws.cell(row=row, column=col, value=text)
    c.font, c.fill, c.alignment, c.border = font, fill, CENTER, BOX
    if width:
        ws.column_dimensions[CL(col)].width = width
    return c


def put(ws, row, col, value, font=F_BASE, nf=None, fill=None, align=None, border=None):
    c = ws.cell(row=row, column=col, value=value)
    c.font = font
    if nf:
        c.number_format = nf
    if fill:
        c.fill = fill
    if align:
        c.alignment = align
    if border:
        c.border = border
    return c


# ----------------------------------------------------------------------------------------------------------------------
# the workbook
# ----------------------------------------------------------------------------------------------------------------------
def build(D, ds):
    TAZS, AREAS, ANAME = D['TAZS'], D['AREAS'], D['ANAME']
    NT = len(TAZS)
    U = np.zeros((NT, NT), bool)
    for sc in SCEN:
        U |= (D['BASE'][sc][0] + D['BASE'][sc][1]) > 0
    I, J = np.where(U)
    NP = len(I)
    R0, R1 = 3, 3 + NP - 1                       # data rows of OD_Pairs
    print(f'{NP:,} TAZ pairs')

    wb = Workbook()
    ws_g = wb.active
    ws_g.title = 'Guide'
    ws_in = wb.create_sheet('Inputs')
    ws_res = wb.create_sheet('Results')
    ws_ar = wb.create_sheet('Areas')
    ws_tz = wb.create_sheet('TAZ')
    ws_st = wb.create_sheet('Stations')
    ws_sw = wb.create_sheet('Lambda_Sweep')
    ws_grid = wb.create_sheet('Scenario_Grid')
    ws_od = wb.create_sheet('OD_Pairs')
    ws_pr = wb.create_sheet('Area_Prior')
    ws_ref = wb.create_sheet('Reference')

    # ------------------------------------------------------------------ Inputs
    ws = ws_in
    ws.column_dimensions['A'].width = 3
    ws.column_dimensions['B'].width = 46
    ws.column_dimensions['C'].width = 52
    ws.column_dimensions['D'].width = 14
    ws.column_dimensions['E'].width = 70
    put(ws, 1, 2, 'Inputs - change the yellow cells; everything else recalculates', F_TITLE)
    put(ws, 2, 2, 'AM peak 06:00-09:00, the 174 corridor TAZs (25 areas). Default values are the study\'s central case (METHODOLOGY 6aq).', F_NOTE)
    lists = {'scen': [SCEN_LABEL[s] for s in SCEN], 'alt': [ALT_LABEL[a] for a in ALTS], 'reg': [REG_LABEL[r] for r in REGS],
             'var': [VAR_LABEL[v] for v in VARS], 'yesno': ['Yes', 'No']}
    ws_l = wb.create_sheet('Lists')
    put(ws_l, 1, 1, 'Dropdown lists of the Inputs sheet (do not edit)', F_NOTE)
    list_ref = {}
    for k, (key_, vals) in enumerate(lists.items()):
        col = 1 + k
        ws_l.column_dimensions[CL(col)].width = 50
        put(ws_l, 2, col, key_, F_BOLD)
        for i, v in enumerate(vals):
            put(ws_l, 3 + i, col, v, F_BASE)
        list_ref[key_] = f'Lists!${CL(col)}$3:${CL(col)}${2 + len(vals)}'
        name(wb, f'List_{key_}', list_ref[key_])
    ws_l.sheet_state = 'hidden'

    r = 4
    hdr(ws, r, 2, 'Assumption'); hdr(ws, r, 3, 'Value'); hdr(ws, r, 4, 'Index / unit'); hdr(ws, r, 5, 'What it does')
    INP = {}

    def section(title):
        nonlocal r
        r += 1
        put(ws, r, 2, title, F_SUB, fill=FILL_BLOCK)
        for c in (3, 4, 5):
            ws.cell(row=r, column=c).fill = FILL_BLOCK

    def inp(key_, label, value, unit, note, nf=None, dv=None, idx_formula=None, nm=None):
        nonlocal r
        r += 1
        put(ws, r, 2, label, F_BASE, align=VMID)
        c = put(ws, r, 3, value, F_INPUT, nf=nf, fill=FILL_INPUT, border=BOX, align=VMID if isinstance(value, str) else VMID_R)
        if dv is not None:
            dv.add(c)
        if idx_formula:
            put(ws, r, 4, idx_formula.format(r=r), F_BASE, align=VMID)
        else:
            put(ws, r, 4, unit, F_GREY, align=VMID)
        put(ws, r, 5, note, F_NOTE, align=VMID)
        fit(r, note)
        INP[key_] = r
        if nm:
            name(wb, nm, f'Inputs!$C${r}')
        return r

    def derived(key_, label, formula, unit, note, nf=None, nm=None):
        nonlocal r
        r += 1
        put(ws, r, 2, label, F_BASE, align=VMID)
        put(ws, r, 3, formula.format(r=r), F_BASE, nf=nf, border=BOX, align=VMID_R)
        put(ws, r, 4, unit, F_GREY, align=VMID)
        put(ws, r, 5, note, F_NOTE, align=VMID)
        fit(r, note)
        INP[key_] = r
        if nm:
            name(wb, nm, f'Inputs!$C${r}')

    def fixed(label, value, unit, note):
        nonlocal r
        r += 1
        put(ws, r, 2, label, F_GREY, align=VMID)
        put(ws, r, 3, value, F_GREY, border=BOX, align=VMID)
        put(ws, r, 4, unit, F_GREY, align=VMID)
        put(ws, r, 5, note, F_NOTE, align=VMID)
        fit(r, note)

    def fit(row, note):
        lines = max(1, -(-len(note) // 82))
        ws.row_dimensions[row].height = max(18, 12.5 * lines + 3)

    dvs = {k: DataValidation(type='list', formula1=f'={v}', allow_blank=False, showDropDown=False) for k, v in list_ref.items()}
    for dv in dvs.values():
        dv.error, dv.errorTitle = 'Pick a value from the list', 'Not in the list'
        ws.add_data_validation(dv)
    dv_pos = DataValidation(type='decimal', operator='greaterThan', formula1='0', allow_blank=False)
    dv_pos.error, dv_pos.errorTitle = 'Enter a number greater than 0', 'Must be positive'
    dv_nonneg = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', allow_blank=False)
    dv_nonneg.error, dv_nonneg.errorTitle = 'Enter a number of 0 or more', 'Must not be negative'
    ws.add_data_validation(dv_pos)
    ws.add_data_validation(dv_nonneg)

    section('1. What to model')
    inp('scen', 'Scenario-year (demand)', SCEN_LABEL['BU_2050'], '', 'Base car and transit trips of the year: 2022 = the survey-based 2022 matrices (step 22); 2040 / 2050 BU / HS = the demographic forecasts (step 23). 2050 BU is the study\'s reference case.',
        dv=dvs['scen'], idx_formula='=MATCH(C{r},List_scen,0)')
    name(wb, 'ScenIdx', f'Inputs!$D${r}')
    inp('alt', 'LRT alternative', ALT_LABEL['main_ext'], '', 'Through line Tirat Carmel - Hamifrats - Nazareth (43 stations), or the extension alone (24 stations S01-S24).',
        dv=dvs['alt'], idx_formula='=MATCH(C{r},List_alt,0)')
    name(wb, 'AltIdx', f'Inputs!$D${r}')
    inp('reg', 'LRT running regime on the extension', REG_LABEL['prioritized'], '', 'Prioritized = step 25 underground-calibrated running times (priority at junctions); Unprioritized = at-grade times. The main route runs at 80 km/h in both.',
        dv=dvs['reg'], idx_formula='=MATCH(C{r},List_reg,0)')
    name(wb, 'RegIdx', f'Inputs!$D${r}')
    inp('var', 'Metronit network', VAR_LABEL['M0'], '', 'M0: the five Metronit lines as they run today (the study\'s convention). M1: Metronit ride segments with a stop in Haifa south/west of Hamifrats removed (Matam, Hof HaCarmel, Bat Galim, downtown, Hadar, Carmel) - the lines still run Hamifrats - Krayot / Kiryat Ata and feed the LRT there. M2: no Metronit at all. Riders of removed sections re-route on the regular buses; the paths were recomputed for each variant (tools/scenario_metronit_skims.py).',
        dv=dvs['var'], idx_formula='=MATCH(C{r},List_var,0)')
    name(wb, 'MetIdx', f'Inputs!$D${r}')
    inp('lrt_on', 'LRT in service?', 'Yes', '', 'No = the network change alone (e.g. the Metronit cut without the LRT): shows what the Metronit removal costs transit before the LRT replaces it.',
        dv=dvs['yesno'], idx_formula='=IF(C{r}="Yes",1,0)')
    name(wb, 'LrtOn', f'Inputs!$D${r}')

    section('2. Behaviour: the logit parameters')
    inp('lam', 'λ - cost sensitivity, car <-> transit', DEFAULTS['lam'], 'per gen. min', 'Upper level of the nest: how strongly the transit share reacts to a change in transit generalized cost. Assumed 0.03 (range 0.02-0.05); the person-level estimate of step 33 gives 0.035. This is the assumption that moves the result most.',
        nf='0.000', dv=dv_pos, nm='Lambda')
    inp('ratio', 'λ_T / λ - nest ratio', DEFAULTS['ratio'], 'ratio', 'λ_T = ratio x λ is the sensitivity inside the transit nest (LRT vs bus / Metronit). The study uses λ_T = 2λ (ratio 2). The ratio must be at least 1 for a consistent nest.',
        nf='0.00', dv=dv_pos)
    derived('lamT', 'λ_T - cost sensitivity, LRT <-> bus / Metronit', '=Lambda*C' + str(r), 'per gen. min', 'Calculated: λ x ratio.', nf='0.000', nm='LambdaT')
    inp('prem_bus', 'LRT premium against a bus-based path', DEFAULTS['prem_bus'], 'gen. min', 'Rail bonus: the LRT is preferred as if it were this many generalized minutes cheaper than a competing path that rides mainly the bus.',
        nf='0.0', dv=dv_nonneg, nm='PremBus')
    inp('prem_brt', 'LRT premium against a Metronit-based path', DEFAULTS['prem_brt'], 'gen. min', 'The same against a path that rides the Metronit for at least half its in-vehicle time (estimated 2.5, range 1.5-3.5).',
        nf='0.0', dv=dv_nonneg, nm='PremMetronit')
    inp('k', 'k - smoothing weight of the base transit share', DEFAULTS['k'], 'trips', 'Each pair\'s 2022 transit share is pulled towards its area pair\'s share with the weight of k trips (Empirical Bayes). Larger k = more weight on the area pair.',
        nf='0', dv=dv_nonneg, nm='K_EB')

    section('3. LRT service')
    inp('headway', 'LRT headway', DEFAULTS['headway'], 'minutes', 'Wait = headway / 2, weighted x2 in the generalized cost. Default 5 minutes.', nf='0.0', dv=dv_pos, nm='Headway')
    inp('st_access', 'Station access time per end', DEFAULTS['st_access'], 'minutes', 'Platform access added at boarding and at alighting (decision of 5 October 2026: 0.5 per end).', nf='0.0', dv=dv_nonneg, nm='StAccess')
    inp('f_ext', 'Running-time factor, extension (S01-S24)', DEFAULTS['f_ext'], 'x', 'Multiplies the LRT in-vehicle time on the extension stations of the selected regime (1.10 = 10 % slower).', nf='0.00', dv=dv_pos, nm='RunFactorExt')
    inp('f_main', 'Running-time factor, main route (S24-Nazareth)', DEFAULTS['f_main'], 'x', 'The same on the main route (80 km/h + 10 s dwell by default). Only acts in the through-line alternative.', nf='0.00', dv=dv_pos, nm='RunFactorMain')
    derived('gcadj', 'LRT generalized-cost change from headway and access', f'=2*(StAccess-0.5)+{W_WAIT:g}*(Headway/2-2.5)', 'gen. min', 'Calculated: added to every LRT path (0 at the defaults).', nf='0.00', nm='LrtGcAdj')

    section('4. Reporting')
    inp('phf1', 'Peak-hour factor, line loads towards Nazareth / Hamifrats', PHF['dir1'], 'share of 3 h', 'Busiest hour / three hours for the LRT line loads (step 27 network bus factor, AM).', nf='0.000', dv=dv_pos, nm='PHF1')
    inp('phf2', 'Peak-hour factor, line loads towards Tirat Carmel', PHF['dir2'], 'share of 3 h', 'As above, the other direction.', nf='0.000', dv=dv_pos, nm='PHF2')

    section('5. Selection indices (calculated - do not edit)')
    derived('netcol', 'Network column (variant x alternative)', '=(MetIdx-1)*2+AltIdx', '1-6', 'Picks the transit cost column in OD_Pairs.', nm='NetCol')
    derived('combocol', 'LRT column (variant x alternative x regime)', '=(MetIdx-1)*4+(AltIdx-1)*2+RegIdx', '1-12', 'Picks the LRT cost and station columns in OD_Pairs.', nm='ComboCol')
    derived('refcol', 'Reference combination (scenario x alternative x regime)', '=(ScenIdx-1)*4+(AltIdx-1)*2+RegIdx', '1-20', 'Picks the reference values (Metronit as today, default parameters).', nm='RefCol')
    derived('nst', 'Stations on the selected line', '=IF(AltIdx=1,43,24)', 'stations', '', nm='NStations')

    section('Fixed in the precomputed paths (change needs tools/scenario_metronit_skims.py)')
    fixed('Walk weight / wait weight / transfer penalty', '2 / 2 / 8', 'gen. min', 'Generalized cost = in-vehicle + 2 x walk + 2 x wait + 8 per transfer (OVT central set, METHODOLOGY 6al).')
    fixed('Boarding penalty onto the LRT', '8 after a bus, 4 after the Metronit, 0 on foot', 'gen. min', 'Each end boards at its cheapest-access station (step 31 gateway rule).')
    fixed('Walking speed / detour', '4 km/h, straight line x 1.3', '', 'Access 1 km from TAZ centroids, 400 m stop-station, 300 m stop-stop transfers.')
    fixed('Bus and Metronit times', 'May 2026 observed bus speeds, GTFS AM timetable', '', 'Level of service held at May 2026 in every scenario-year (the study\'s convention).')
    fixed('Car cost', 'not used by the pivot', '', 'The incremental logit moves trips on the change of the transit nest only, so a car-side change does not register (METHODOLOGY 6aq addendum 3).')
    ws.freeze_panes = 'B5'

    # ------------------------------------------------------------------ OD_Pairs
    ws = ws_od
    static = []                                   # (key, header, block, values, number format)
    static += [('o_taz', 'Origin TAZ', 'Keys', np.array(TAZS)[I], '0'), ('d_taz', 'Destination TAZ', 'Keys', np.array(TAZS)[J], '0'),
               ('o_area', 'Origin area', 'Keys', D['ta'][I], '0'), ('d_area', 'Destination area', 'Keys', D['ta'][J], '0'),
               ('o_idx', 'Origin area #', 'Keys', D['tai'][I] + 1, '0'), ('d_idx', 'Destination area #', 'Keys', D['tai'][J] + 1, '0')]
    for sc in SCEN:
        static.append((f'car_{sc}', f'Car {sc}', 'Base car trips (no LRT)', D['BASE'][sc][0][I, J], NF_TRIPS2))
    for sc in SCEN:
        static.append((f'tr_{sc}', f'Transit {sc}', 'Base transit trips (bus + Metronit + rail, no LRT)', D['BASE'][sc][1][I, J], NF_TRIPS2))
    for v in VARS:
        for a in ALTS:
            static.append((f'gcb_{v}_{a}', f'{v} {a}', 'Transit GC without LRT (best bus / Metronit path)', D['GCB'][(v, a)][I, J], NF_GC))
    for v in VARS:
        for a in ALTS:
            static.append((f'brt_{v}_{a}', f'{v} {a}', 'Metronit-based path (1 = yes)', D['BRT'][(v, a)][I, J].astype(int), '0'))
    for v in VARS:
        for a in ALTS:
            for rg in REGS:
                g = D['GCL'][(v, a, rg)][I, J]
                static.append((f'gcl_{v}_{a}_{rg}', f'{v} {a} {rg[:5]}', 'LRT GC (access + wait + line + egress); blank = no LRT path', g, NF_GC))
    for v in VARS:
        for a in ALTS:
            for rg in REGS:
                code = D['BRD'][(v, a, rg)][I, J] * 100 + D['ALI'][(v, a, rg)][I, J]
                static.append((f'gw_{v}_{a}_{rg}', f'{v} {a} {rg[:5]}', 'LRT stations: board x 100 + alight (station order; 0 = none)', code, '0'))
    COL = {}
    for k, (key_, *_rest) in enumerate(static):
        COL[key_] = CL(k + 1)
    first_formula = len(static) + 1

    F = [  # (key, header, block, formula template, number format, comment)
        ('car0', 'Car before', 'Selected base demand', '=INDEX({car_2022}{r}:{car_HS_2050}{r},1,ScenIdx)', NF_TRIPS2, 'Base car trips of the selected scenario-year'),
        ('tr0', 'Transit before', 'Selected base demand', '=INDEX({tr_2022}{r}:{tr_HS_2050}{r},1,ScenIdx)', NF_TRIPS2, 'Base transit trips of the selected scenario-year'),
        ('n', 'Car + transit', 'Selected base demand', '={car0}{r}+{tr0}{r}', NF_TRIPS2, None),
        ('s_prior', 'Area-pair transit share', 'Pivot share', '=INDEX(AreaShare,{o_idx}{r},{d_idx}{r})', NF_SHARE, 'Transit share of the area pair (Area_Prior sheet); the study-area share where the area pair has no trips'),
        ('s_piv', 'Smoothed transit share S', 'Pivot share', '=IF({n}{r}>0,({tr0}{r}+K_EB*{s_prior}{r})/({n}{r}+K_EB),0)', NF_SHARE, 'S = (transit + k x area share) / (car + transit + k)'),
        ('gcb0', 'Transit GC today', 'Transit path', '=INDEX({gcb_M0_main_ext}{r}:{gcb_M2_ext}{r},1,AltIdx)', NF_GC, 'Best bus / Metronit path on today\'s network (Metronit as today)'),
        ('gcb', 'Transit GC in scenario', 'Transit path', '=INDEX({gcb_M0_main_ext}{r}:{gcb_M2_ext}{r},1,NetCol)', NF_GC, 'Best bus / Metronit path on the selected Metronit network'),
        ('brt0', 'Metronit-based today', 'Transit path', '=INDEX({brt_M0_main_ext}{r}:{brt_M2_ext}{r},1,AltIdx)', '0', None),
        ('brt', 'Metronit-based in scenario', 'Transit path', '=INDEX({brt_M0_main_ext}{r}:{brt_M2_ext}{r},1,NetCol)', '0', None),
        ('gw', 'LRT station code', 'LRT path', '=INDEX({gw_M0_main_ext_prioritized}{r}:{gw_M2_ext_unprioritized}{r},1,ComboCol)', '0', None),
        ('board', 'Board station #', 'LRT path', '=INT({gw}{r}/100)', '0', 'Order of the boarding station (Stations sheet)'),
        ('alight', 'Alight station #', 'LRT path', '=MOD({gw}{r},100)', '0', None),
        ('avail', 'LRT available', 'LRT path', '=IF(AND({gw}{r}>0,{n}{r}>0,LrtOn=1),1,0)', '0', None),
        ('gcl0', 'LRT GC precomputed', 'LRT path', '=IF({avail}{r}=1,INDEX({gcl_M0_main_ext_prioritized}{r}:{gcl_M2_ext_unprioritized}{r},1,ComboCol),0)', NF_GC, None),
        ('ivtE', 'LRT minutes on extension', 'LRT path', '=IF({avail}{r}=1,ABS(INDEX(StCumE,{board}{r})-INDEX(StCumE,{alight}{r})),0)', NF_GC, None),
        ('ivtM', 'LRT minutes on main route', 'LRT path', '=IF({avail}{r}=1,ABS(INDEX(StCumM,{board}{r})-INDEX(StCumM,{alight}{r})),0)', NF_GC, None),
        ('gcl', 'LRT GC', 'LRT path', '=IF({avail}{r}=1,{gcl0}{r}+(RunFactorExt-1)*{ivtE}{r}+(RunFactorMain-1)*{ivtM}{r}+LrtGcAdj,0)', NF_GC, 'Precomputed LRT GC + running-time factors + headway / access change'),
        ('prem', 'LRT premium', 'Logit', '=IF({brt}{r}=1,PremMetronit,PremBus)', NF_GC, None),
        ('dL', 'dL = GC_LRT - premium - GC_transit', 'Logit', '=IF({avail}{r}=1,{gcl}{r}-{prem}{r}-{gcb}{r},0)', NF_GC, None),
        ('pl', 'P(LRT | transit)', 'Logit', '=IF({avail}{r}=1,1/(1+EXP(MIN(500,LambdaT*{dL}{r}))),0)', NF_SHARE, '1 / (1 + exp(λ_T x dL))'),
        ('delta', 'Δ transit composite cost', 'Logit', '=({gcb}{r}-{gcb0}{r})+IF({avail}{r}=1,-LN(1+EXP(MIN(500,-LambdaT*{dL}{r})))/LambdaT,0)', NF_GC, 'Change of the transit nest logsum against today, in gen. minutes (negative = transit better)'),
        ('s_new', 'New transit share', 'Logit', '=IF({n}{r}>0,{s_piv}{r}*EXP(-Lambda*{delta}{r})/({s_piv}{r}*EXP(-Lambda*{delta}{r})+1-{s_piv}{r}),0)', NF_SHARE, 'S\' = S e^(-λΔ) / (S e^(-λΔ) + 1 - S)'),
        ('growth', 'Transit growth factor', 'Logit', '=IF({s_piv}{r}>0,{s_new}{r}/{s_piv}{r},1)', '0.0000', None),
        ('tr1', 'Transit after', 'Travellers after', '=MIN({tr0}{r}*{growth}{r},{n}{r})', NF_TRIPS2, 'Observed transit trips x growth (the pivot)'),
        ('car1', 'Car after', 'Travellers after', '={n}{r}-{tr1}{r}', NF_TRIPS2, None),
        ('lrt', 'LRT', 'Travellers after', '={tr1}{r}*{pl}{r}', NF_TRIPS2, None),
        ('brt1', 'Metronit after', 'Travellers after', '=({tr1}{r}-{lrt}{r})*{brt}{r}', NF_TRIPS2, None),
        ('bus1', 'Bus after', 'Travellers after', '=({tr1}{r}-{lrt}{r})*(1-{brt}{r})', NF_TRIPS2, None),
        ('brt0x', 'Metronit before', 'Travellers before', '={tr0}{r}*{brt0}{r}', NF_TRIPS2, None),
        ('bus0', 'Bus before', 'Travellers before', '={tr0}{r}*(1-{brt0}{r})', NF_TRIPS2, None),
        ('lrt_car', 'LRT from car', 'LRT sources', '=MAX(0,{tr1}{r}-{tr0}{r})*{pl}{r}', NF_TRIPS2, None),
        ('lrt_bus', 'LRT from bus', 'LRT sources', '=MIN({tr1}{r},{tr0}{r})*{pl}{r}*(1-{brt0}{r})', NF_TRIPS2, 'Today\'s bus-based riders'),
        ('lrt_brt', 'LRT from Metronit', 'LRT sources', '=MIN({tr1}{r},{tr0}{r})*{pl}{r}*{brt0}{r}', NF_TRIPS2, 'Today\'s Metronit-based riders'),
        ('tr_to_car', 'Transit lost to car', 'LRT sources', '=MAX(0,{tr0}{r}-{tr1}{r})', NF_TRIPS2, 'Where the network change makes transit worse than today'),
        ('lrt_ext', 'LRT using the extension', 'LRT sources', '=IF(AND({avail}{r}=1,MIN({board}{r},{alight}{r})<=' + str(N_EXT - 1) + '),{lrt}{r},0)', NF_TRIPS2, 'Rides at least one segment S01-S24'),
    ]
    for k, (key_, *_rest) in enumerate(F):
        COL[key_] = CL(first_formula + k)
    # headers
    blocks = {}
    for k, (key_, header, block, *_rest) in enumerate(static):
        blocks.setdefault(block, []).append(k + 1)
        hdr(ws, 2, k + 1, header, width=9 if k >= 6 else 8, fill=PatternFill('solid', fgColor='7F7F7F'))
    for k, (key_, header, block, tmpl, nf, cmt) in enumerate(F):
        col = first_formula + k
        blocks.setdefault(block, []).append(col)
        c = hdr(ws, 2, col, header, width=11)
        if cmt:
            c.comment = Comment(cmt, 'model')
    for block, cols in blocks.items():
        c0, c1 = min(cols), max(cols)
        c = ws.cell(row=1, column=c0, value=block)
        c.font, c.fill, c.alignment = F_BOLD, FILL_BLOCK, CENTER
        if c1 > c0:
            ws.merge_cells(start_row=1, start_column=c0, end_row=1, end_column=c1)
    ws.row_dimensions[2].height = 54
    # data
    print('writing OD_Pairs ...', flush=True)
    for k, (key_, header, block, vals, nf) in enumerate(static):
        col = k + 1
        is_key = k < 6
        for i in range(NP):
            v = vals[i]
            if isinstance(v, (float, np.floating)):
                v = None if not np.isfinite(v) else round(float(v), 4)
            else:
                v = int(v)
            c = ws.cell(row=R0 + i, column=col, value=v)
            c.font = F_BASE if is_key else F_INPUT
            c.number_format = nf
    for k, (key_, header, block, tmpl, nf, cmt) in enumerate(F):
        col = first_formula + k
        t = tmpl
        for kk, letter in COL.items():
            t = t.replace('{' + kk + '}', letter)
        for i in range(NP):
            rr = R0 + i
            c = ws.cell(row=rr, column=col, value=t.replace('{r}', str(rr)))
            c.font = F_BASE
            c.number_format = nf
    ws.freeze_panes = ws.cell(row=3, column=7)
    ws.column_dimensions.group(CL(7), CL(first_formula - 1), hidden=True, outline_level=1)   # precomputed blocks, collapsed (click + to open)
    ws.auto_filter.ref = f'A2:{CL(first_formula + len(F) - 1)}{R1}'
    rng = lambda key_: f'OD_Pairs!${COL[key_]}${R0}:${COL[key_]}${R1}'  # noqa: E731
    for key_ in ['o_taz', 'd_taz', 'o_area', 'd_area', 'car0', 'tr0', 'car1', 'tr1', 'lrt', 'brt1', 'bus1', 'brt0x', 'bus0', 'lrt_car', 'lrt_bus', 'lrt_brt', 'tr_to_car', 'lrt_ext', 'board', 'alight']:
        name(wb, f'od_{key_}', rng(key_))

    # ------------------------------------------------------------------ Area_Prior
    ws = ws_pr
    A = len(AREAS)
    put(ws, 1, 1, 'Area-pair base trips of the selected scenario-year and the transit share the pivot smooths towards (formulas)', F_SUB)
    put(ws, 2, 1, 'Rows = origin area, columns = destination area, in the order of the Areas sheet. Intra-area pairs are outside the model (blank).', F_NOTE)
    blocks_pr = {'car': 4, 'tr': 4 + A + 3, 'share': 4 + 2 * (A + 3)}
    titles = {'car': 'Car trips before (selected scenario-year)', 'tr': 'Transit trips before', 'share': 'Transit share (study-area share where empty)'}
    for b, r0 in blocks_pr.items():
        put(ws, r0 - 1, 1, titles[b], F_BOLD)
        hdr(ws, r0, 1, 'Area')
        hdr(ws, r0, 2, 'Name', width=22)
        for j, a in enumerate(AREAS):
            hdr(ws, r0, 3 + j, a, width=7)
        for i, a in enumerate(AREAS):
            rr = r0 + 1 + i
            put(ws, rr, 1, a, F_BOLD)
            put(ws, rr, 2, ANAME[a], F_BASE)
            for j, bb in enumerate(AREAS):
                col = 3 + j
                if a == bb:
                    continue
                if b == 'car':
                    f = f'=SUMIFS(od_car0,od_o_area,$A{rr},od_d_area,{CL(col)}${r0})'
                    put(ws, rr, col, f, F_BASE, nf=NF_TRIPS)
                elif b == 'tr':
                    f = f'=SUMIFS(od_tr0,od_o_area,$A{rr},od_d_area,{CL(col)}${r0})'
                    put(ws, rr, col, f, F_BASE, nf=NF_TRIPS)
                else:
                    rc, rt_ = blocks_pr['car'] + 1 + i, blocks_pr['tr'] + 1 + i
                    f = f'=IF({CL(col)}{rc}+{CL(col)}{rt_}>0,{CL(col)}{rt_}/({CL(col)}{rc}+{CL(col)}{rt_}),StudyShare)'
                    put(ws, rr, col, f, F_BASE, nf=NF_SHARE)
    rs = blocks_pr['share']
    name(wb, 'AreaShare', f'Area_Prior!$C${rs + 1}:${CL(2 + A)}${rs + A}')
    rc, rt_ = blocks_pr['car'], blocks_pr['tr']
    put(ws, 1, 30, 'Study-area transit share', F_BOLD)
    put(ws, 2, 30, f'=SUM(C{rt_ + 1}:{CL(2 + A)}{rt_ + A})/(SUM(C{rc + 1}:{CL(2 + A)}{rc + A})+SUM(C{rt_ + 1}:{CL(2 + A)}{rt_ + A}))', F_BASE, nf=NF_SHARE)
    ws.column_dimensions[CL(30)].width = 24
    name(wb, 'StudyShare', f'Area_Prior!${CL(30)}$2')

    # ------------------------------------------------------------------ Stations
    ws = ws_st
    STm = D['ST']['main_ext']                    # the through line's 43 stations; the extension's 24 are its first rows
    put(ws, 1, 1, 'Stations and line loads of the selected alternative and regime (AM, three hours and peak hour)', F_TITLE)
    put(ws, 2, 1, 'Station order = position on the line from Tirat Carmel (S01). Extension S01-S24; main route M02-M20 (M01 = S24 at Hamifrats). '
                  'Segment k runs from station k to station k+1. Reference = Metronit as today, default parameters, same scenario / alternative / regime.', F_NOTE)
    heads = ['Order', 'Station', 'Line', 'TAZ', 'Area', 'Min from S01 prioritized (static)', 'Min from S01 unprioritized (static)', 'Min from S01, selected regime',
             'Cum. minutes on extension', 'Cum. minutes on main route', 'Boardings (3 h)', 'Alightings (3 h)', 'Boardings, reference', 'Boardings: live - reference',
             'Segment', 'Load towards Nazareth / Hamifrats (3 h)', 'Load towards Tirat Carmel (3 h)', 'Peak hour towards Nazareth / Hamifrats', 'Peak hour towards Tirat Carmel',
             'Reference load towards Nazareth / Hamifrats (3 h)', 'Reference load towards Tirat Carmel (3 h)']
    widths = [7, 9, 10, 7, 7, 11, 11, 11, 11, 11, 11, 11, 11, 11, 13, 13, 13, 12, 12, 13, 13]
    for k, (h, w) in enumerate(zip(heads, widths)):
        hdr(ws, 4, k + 1, h, width=w)
    ws.row_dimensions[4].height = 66
    S0 = 5
    n_st = len(STm)
    RS0, RS1 = 6, 6 + n_st - 1                     # rows of the station block on the Reference sheet
    for k in range(n_st):
        rr = S0 + k
        srow = STm.iloc[k]
        put(ws, rr, 1, k + 1, F_BASE)
        put(ws, rr, 2, f'=IF(A{rr}<=NStations,"{srow["station_id"]}","")', F_BASE)
        put(ws, rr, 3, f'=IF(A{rr}<=NStations,"{srow["line"]}","")', F_BASE)
        taz = srow.get('TAZ', np.nan)
        put(ws, rr, 4, int(taz) if pd.notna(taz) else None, F_INPUT)
        ag = srow.get('AggCode', np.nan)
        put(ws, rr, 5, int(ag) if pd.notna(ag) else None, F_INPUT)
        put(ws, rr, 6, round(float(srow['time_from_S01_prioritized']), 2), F_INPUT, nf=NF_GC)
        put(ws, rr, 7, round(float(srow['time_from_S01_unprioritized']), 2), F_INPUT, nf=NF_GC)
        put(ws, rr, 8, f'=CHOOSE(RegIdx,F{rr},G{rr})', F_BASE, nf=NF_GC)
        put(ws, rr, 9, f'=MIN(H{rr},$H${S0 + N_EXT - 1})', F_BASE, nf=NF_GC)
        put(ws, rr, 10, f'=MAX(0,H{rr}-$H${S0 + N_EXT - 1})', F_BASE, nf=NF_GC)
        put(ws, rr, 11, f'=IF(A{rr}<=NStations,SUMIFS(od_lrt,od_board,A{rr}),"")', F_BASE, nf=NF_TRIPS)
        put(ws, rr, 12, f'=IF(A{rr}<=NStations,SUMIFS(od_lrt,od_alight,A{rr}),"")', F_BASE, nf=NF_TRIPS)
        put(ws, rr, 13, f'=IF(A{rr}<=NStations,INDEX(Reference!$B${RS0}:$CC${RS1},A{rr},(RefCol-1)*4+1),"")', F_LINK, nf=NF_TRIPS)
        put(ws, rr, 14, f'=IF(A{rr}<=NStations,K{rr}-M{rr},"")', F_BASE, nf=NF_TRIPS)
        if k < n_st - 1:
            put(ws, rr, 15, f'=IF(A{rr}<NStations,B{rr}&"-"&B{rr + 1},"")', F_BASE)
            put(ws, rr, 16, f'=IF(A{rr}<NStations,SUMIFS(od_lrt,od_board,"<="&A{rr},od_alight,">="&(A{rr}+1)),"")', F_BASE, nf=NF_TRIPS)
            put(ws, rr, 17, f'=IF(A{rr}<NStations,SUMIFS(od_lrt,od_alight,"<="&A{rr},od_board,">="&(A{rr}+1)),"")', F_BASE, nf=NF_TRIPS)
            put(ws, rr, 18, f'=IF(A{rr}<NStations,P{rr}*PHF1,"")', F_BASE, nf=NF_TRIPS)
            put(ws, rr, 19, f'=IF(A{rr}<NStations,Q{rr}*PHF2,"")', F_BASE, nf=NF_TRIPS)
            put(ws, rr, 20, f'=IF(A{rr}<NStations,INDEX(Reference!$B${RS0}:$CC${RS1},A{rr},(RefCol-1)*4+3),"")', F_LINK, nf=NF_TRIPS)
            put(ws, rr, 21, f'=IF(A{rr}<NStations,INDEX(Reference!$B${RS0}:$CC${RS1},A{rr},(RefCol-1)*4+4),"")', F_LINK, nf=NF_TRIPS)
    name(wb, 'StCumE', f'Stations!$I${S0}:$I${S0 + n_st - 1}')
    name(wb, 'StCumM', f'Stations!$J${S0}:$J${S0 + n_st - 1}')
    rt = S0 + n_st + 1
    put(ws, rt, 1, 'Totals / maxima', F_BOLD)
    put(ws, rt, 11, f'=SUM(K{S0}:K{S0 + n_st - 1})', F_BOLD, nf=NF_TRIPS)
    put(ws, rt, 12, f'=SUM(L{S0}:L{S0 + n_st - 1})', F_BOLD, nf=NF_TRIPS)
    put(ws, rt, 13, f'=SUM(M{S0}:M{S0 + n_st - 1})', F_BOLD, nf=NF_TRIPS)
    for col in (16, 17, 18, 19, 20, 21):
        put(ws, rt, col, f'=MAX({CL(col)}{S0}:{CL(col)}{S0 + n_st - 2})', F_BOLD, nf=NF_TRIPS)
    name(wb, 'BusiestSeg', f'Stations!$S${rt}')
    name(wb, 'BusiestSeg3h1', f'Stations!$P${rt}')
    name(wb, 'BusiestSeg3h2', f'Stations!$Q${rt}')
    ws.freeze_panes = 'C5'
    ch = BarChart()
    ch.type, ch.grouping = 'col', 'clustered'
    ch.title = 'LRT line load by segment, three hours (live)'
    ch.y_axis.title = 'LRT trips'
    ch.x_axis.title = 'Segment (from station order k to k+1)'
    ch.add_data(Reference(ws, min_col=16, min_row=4, max_col=17, max_row=S0 + n_st - 2), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=15, min_row=S0, max_row=S0 + n_st - 2))
    ch.x_axis.title = 'Segment'
    ch.height, ch.width = 10, 30
    ws.add_chart(ch, f'B{rt + 3}')

    # ------------------------------------------------------------------ Reference (static, from the numpy pivot)
    ws = ws_ref
    put(ws, 1, 1, 'Reference values (static): the study model at its default inputs with the Metronit as today, for each scenario-year x alternative x regime', F_SUB)
    put(ws, 2, 1, 'Computed by tools/build_scenario_workbook.py with the same equations as OD_Pairs (they reproduce Output/alternatives/demand_summary.csv). Do not edit.', F_NOTE)
    combos = [(sc, a, rg) for sc in SCEN for a in ALTS for rg in REGS]
    REF = {}
    for cmb in combos:
        REF[cmb] = pivot(D, *cmb, 'M0')
    # block 1: stations (43 rows x 20 combos x 4: boardings, alightings, seg dir1, seg dir2), rows RS0-RS1
    put(ws, RS0 - 2, 1, 'Stations and segments by order: per combination boardings, alightings, segment load towards Nazareth / Hamifrats, towards Tirat Carmel (3 h)', F_BOLD)
    hdr(ws, RS0 - 1, 1, 'Order')
    for ci, cmb in enumerate(combos):
        for m_, lab in enumerate(['board', 'alight', 'seg dir1', 'seg dir2']):
            hdr(ws, RS0 - 1, 2 + ci * 4 + m_, f'{cmb[0]} {cmb[1]} {cmb[2][:5]} {lab}', width=9, fill=PatternFill('solid', fgColor='7F7F7F'))
    for k in range(n_st):
        put(ws, RS0 + k, 1, k + 1, F_BOLD)
        for ci, cmb in enumerate(combos):
            R = REF[cmb]
            vals = [R['board'], R['alight'], R['seg1'], R['seg2']]
            for m_, arr in enumerate(vals):
                if k < len(arr):
                    put(ws, RS0 + k, 2 + ci * 4 + m_, round(float(arr[k]), 2), F_INPUT, nf=NF_TRIPS)
    # block 2: TAZ (174 rows x 20 combos x 4: LRT by origin, LRT by destination, transit after by origin, car after by origin)
    RT0 = RS1 + 5
    put(ws, RT0 - 2, 1, 'TAZ: per combination LRT trips by origin, LRT trips by destination, transit after by origin, car after by origin (3 h)', F_BOLD)
    hdr(ws, RT0 - 1, 1, 'TAZ')
    for ci, cmb in enumerate(combos):
        for m_, lab in enumerate(['LRT orig', 'LRT dest', 'transit orig', 'car orig']):
            hdr(ws, RT0 - 1, 2 + ci * 4 + m_, f'{cmb[0]} {cmb[1]} {cmb[2][:5]} {lab}', width=9, fill=PatternFill('solid', fgColor='7F7F7F'))
    for t_i, taz in enumerate(TAZS):
        put(ws, RT0 + t_i, 1, taz, F_BOLD)
        for ci, cmb in enumerate(combos):
            R = REF[cmb]
            vals = [R['lrt'].sum(1)[t_i], R['lrt'].sum(0)[t_i], R['tr1'].sum(1)[t_i], R['car1'].sum(1)[t_i]]
            for m_, x in enumerate(vals):
                put(ws, RT0 + t_i, 2 + ci * 4 + m_, round(float(x), 2), F_INPUT, nf=NF_TRIPS)
    RT1 = RT0 + NT - 1
    # block 3: published totals of step 45 (demand_summary.csv) and this model's own totals
    RP0 = RT1 + 5
    put(ws, RP0 - 2, 1, 'Totals per combination: step 45 as published (Output/alternatives/demand_summary.csv, AM) and this workbook\'s reference run', F_BOLD)
    tot_heads = ['Combination #', 'Scenario', 'Alternative', 'Regime', 'Car (pub.)', 'Bus (pub.)', 'Metronit (pub.)', 'LRT (pub.)', 'Total transit (pub.)', 'LRT from car (pub.)',
                 'LRT using the extension (pub.)', 'Busiest segment 3 h (pub.)', 'LRT (this model)', 'LRT from bus (this model)', 'LRT from Metronit (this model)', 'Car before', 'Transit before', 'Metronit before']
    for k, h in enumerate(tot_heads):
        hdr(ws, RP0 - 1, 1 + k, h, width=11)
    for ci, cmb in enumerate(combos):
        sc, a, rg = cmb
        rr = RP0 + ci
        rp = ds[(ds['scenario'].astype(str) == sc) & (ds['alternative'] == ALT_SUMMARY[a]) & ds['regime'].str.startswith(REG_LABEL[rg].split(' ')[0])].iloc[0]
        t = totals(REF[cmb])
        row = [ci + 1, sc, ALT_SUMMARY[a], rg, rp['car'], rp['bus'], rp['BRT (Metronit)'], rp['LRT'], rp['total transit'], rp['LRT from car'],
               rp['LRT trips using the extension (at least one segment S01–S24)'], rp['busiest segment load (3 h, one direction)'], t['lrt'], t['lrt_bus'], t['lrt_brt'], t['car0'], t['tr0'], t['brt0']]
        for k, x in enumerate(row):
            put(ws, rr, 1 + k, round(float(x), 1) if isinstance(x, (float, np.floating)) else x, F_INPUT if k >= 4 else F_BASE, nf=NF_TRIPS if k >= 4 else None)
    RP1 = RP0 + len(combos) - 1
    name(wb, 'RefTotals', f'Reference!$A${RP0}:$R${RP1}')
    ws.freeze_panes = 'B6'
    name(wb, 'RefTAZ', f'Reference!$B${RT0}:$CC${RT1}')
    name(wb, 'RefTAZKeys', f'Reference!$A${RT0}:$A${RT1}')

    # ------------------------------------------------------------------ TAZ
    ws = ws_tz
    put(ws, 1, 1, 'Travellers by TAZ (AM three hours): before the LRT, after (live), and against the reference', F_TITLE)
    put(ws, 2, 1, 'By origin unless the header says destination. Before = base trips with today\'s network and no LRT. Reference = the study model for the same scenario / alternative / regime with the Metronit as today and default parameters.', F_NOTE)
    th = ['TAZ', 'Area', 'Area name', 'Population 2020', 'Employment 2020', 'Car before', 'Transit before', 'of which Metronit-based', 'Car after', 'Transit after',
          'Bus after', 'Metronit after', 'LRT (by origin)', 'LRT (by destination)', 'LRT from car', 'LRT from bus', 'LRT from Metronit', 'Transit lost to car',
          'Transit share before', 'Transit share after', 'LRT share of transit', 'LRT reference (by origin)', 'LRT: live - reference', 'Transit after: live - reference', 'Car after: live - reference']
    tw = [7, 6, 20, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 9, 10, 10, 10, 10]
    for k, (h, w) in enumerate(zip(th, tw)):
        hdr(ws, 4, k + 1, h, width=w)
    ws.row_dimensions[4].height = 54
    T0 = 5
    for t_i, taz in enumerate(TAZS):
        rr = T0 + t_i
        a = int(D['ta'][t_i])
        put(ws, rr, 1, taz, F_BOLD)
        put(ws, rr, 2, a, F_BASE)
        put(ws, rr, 3, ANAME[a], F_BASE)
        put(ws, rr, 4, int(D['pop'][t_i]), F_INPUT, nf=NF_TRIPS)
        put(ws, rr, 5, int(D['emp'][t_i]), F_INPUT, nf=NF_TRIPS)
        sm = lambda col: f'=SUMIFS({col},od_o_taz,$A{rr})'  # noqa: E731
        put(ws, rr, 6, sm('od_car0'), F_BASE, nf=NF_TRIPS)
        put(ws, rr, 7, sm('od_tr0'), F_BASE, nf=NF_TRIPS)
        put(ws, rr, 8, sm('od_brt0x'), F_BASE, nf=NF_TRIPS)
        put(ws, rr, 9, sm('od_car1'), F_BASE, nf=NF_TRIPS)
        put(ws, rr, 10, sm('od_tr1'), F_BASE, nf=NF_TRIPS)
        put(ws, rr, 11, sm('od_bus1'), F_BASE, nf=NF_TRIPS)
        put(ws, rr, 12, sm('od_brt1'), F_BASE, nf=NF_TRIPS)
        put(ws, rr, 13, sm('od_lrt'), F_BASE, nf=NF_TRIPS)
        put(ws, rr, 14, f'=SUMIFS(od_lrt,od_d_taz,$A{rr})', F_BASE, nf=NF_TRIPS)
        put(ws, rr, 15, sm('od_lrt_car'), F_BASE, nf=NF_TRIPS)
        put(ws, rr, 16, sm('od_lrt_bus'), F_BASE, nf=NF_TRIPS)
        put(ws, rr, 17, sm('od_lrt_brt'), F_BASE, nf=NF_TRIPS)
        put(ws, rr, 18, sm('od_tr_to_car'), F_BASE, nf=NF_TRIPS)
        put(ws, rr, 19, f'=IF(F{rr}+G{rr}>0,G{rr}/(F{rr}+G{rr}),0)', F_BASE, nf=NF_PCT)
        put(ws, rr, 20, f'=IF(I{rr}+J{rr}>0,J{rr}/(I{rr}+J{rr}),0)', F_BASE, nf=NF_PCT)
        put(ws, rr, 21, f'=IF(J{rr}>0,M{rr}/J{rr},0)', F_BASE, nf=NF_PCT)
        put(ws, rr, 22, f'=INDEX(RefTAZ,MATCH($A{rr},RefTAZKeys,0),(RefCol-1)*4+1)', F_LINK, nf=NF_TRIPS)
        put(ws, rr, 23, f'=M{rr}-V{rr}', F_BASE, nf=NF_TRIPS)
        put(ws, rr, 24, f'=J{rr}-INDEX(RefTAZ,MATCH($A{rr},RefTAZKeys,0),(RefCol-1)*4+3)', F_BASE, nf=NF_TRIPS)
        put(ws, rr, 25, f'=I{rr}-INDEX(RefTAZ,MATCH($A{rr},RefTAZKeys,0),(RefCol-1)*4+4)', F_BASE, nf=NF_TRIPS)
    T1 = T0 + NT - 1
    rr = T1 + 1
    put(ws, rr, 1, 'Total', F_BOLD)
    for col in list(range(4, 19)) + [22, 23, 24, 25]:
        put(ws, rr, col, f'=SUM({CL(col)}{T0}:{CL(col)}{T1})', F_BOLD, nf=NF_TRIPS)
    put(ws, rr, 19, f'=IF(F{rr}+G{rr}>0,G{rr}/(F{rr}+G{rr}),0)', F_BOLD, nf=NF_PCT)
    put(ws, rr, 20, f'=IF(I{rr}+J{rr}>0,J{rr}/(I{rr}+J{rr}),0)', F_BOLD, nf=NF_PCT)
    put(ws, rr, 21, f'=IF(J{rr}>0,M{rr}/J{rr},0)', F_BOLD, nf=NF_PCT)
    ws.freeze_panes = 'D5'
    ws.auto_filter.ref = f'A4:{CL(len(th))}{T1}'
    for col in (23, 24, 25):
        ws.conditional_formatting.add(f'{CL(col)}{T0}:{CL(col)}{T1}', CellIsRule(operator='greaterThan', formula=['0.5'], font=Font(name=FONT, color='006100'), fill=PatternFill('solid', fgColor='C6EFCE')))
        ws.conditional_formatting.add(f'{CL(col)}{T0}:{CL(col)}{T1}', CellIsRule(operator='lessThan', formula=['-0.5'], font=Font(name=FONT, color='9C0006'), fill=PatternFill('solid', fgColor='FFC7CE')))
    name(wb, 'tz_taz', f'TAZ!$A${T0}:$A${T1}')
    name(wb, 'tz_area', f'TAZ!$B${T0}:$B${T1}')
    name(wb, 'tz_ref_lrt', f'TAZ!$V${T0}:$V${T1}')
    name(wb, 'tz_pop', f'TAZ!$D${T0}:$D${T1}')
    name(wb, 'tz_emp', f'TAZ!$E${T0}:$E${T1}')

    # ------------------------------------------------------------------ Areas
    ws = ws_ar
    put(ws, 1, 1, 'Travellers by area (the 25 corridor areas, the V2 superzones), AM three hours', F_TITLE)
    put(ws, 2, 1, 'By origin area unless stated. Areas 201-210 lie on the extension (Tirat Carmel to Hamifrats), 211-217 on the main route to Nazareth, 101-104 and 301-304 are the Krayot.', F_NOTE)
    ah = ['Area', 'Name', 'TAZs', 'Population 2020', 'Employment 2020', 'Car before', 'Transit before', 'of which Metronit-based', 'Car after', 'Transit after', 'Bus after',
          'Metronit after', 'LRT (by origin)', 'LRT (by destination)', 'LRT from car', 'LRT from bus', 'LRT from Metronit', 'Transit lost to car', 'Transit share before',
          'Transit share after', 'LRT share of transit', 'LRT reference (by origin)', 'LRT: live - reference']
    aw = [7, 22, 6, 11, 11, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 9, 10, 10]
    for k, (h, w) in enumerate(zip(ah, aw)):
        hdr(ws, 4, k + 1, h, width=w)
    ws.row_dimensions[4].height = 54
    A0 = 5
    for i, a in enumerate(AREAS):
        rr = A0 + i
        put(ws, rr, 1, a, F_BOLD)
        put(ws, rr, 2, ANAME[a], F_BASE)
        put(ws, rr, 3, f'=COUNTIF(tz_area,A{rr})', F_BASE)
        put(ws, rr, 4, f'=SUMIF(tz_area,A{rr},tz_pop)', F_BASE, nf=NF_TRIPS)
        put(ws, rr, 5, f'=SUMIF(tz_area,A{rr},tz_emp)', F_BASE, nf=NF_TRIPS)
        sm = lambda col: f'=SUMIFS({col},od_o_area,$A{rr})'  # noqa: E731
        for col, key_ in zip(range(6, 19), ['od_car0', 'od_tr0', 'od_brt0x', 'od_car1', 'od_tr1', 'od_bus1', 'od_brt1', 'od_lrt', None, 'od_lrt_car', 'od_lrt_bus', 'od_lrt_brt', 'od_tr_to_car']):
            if key_ is None:
                put(ws, rr, col, f'=SUMIFS(od_lrt,od_d_area,$A{rr})', F_BASE, nf=NF_TRIPS)
            else:
                put(ws, rr, col, sm(key_), F_BASE, nf=NF_TRIPS)
        put(ws, rr, 19, f'=IF(F{rr}+G{rr}>0,G{rr}/(F{rr}+G{rr}),0)', F_BASE, nf=NF_PCT)
        put(ws, rr, 20, f'=IF(I{rr}+J{rr}>0,J{rr}/(I{rr}+J{rr}),0)', F_BASE, nf=NF_PCT)
        put(ws, rr, 21, f'=IF(J{rr}>0,M{rr}/J{rr},0)', F_BASE, nf=NF_PCT)
        put(ws, rr, 22, f'=SUMIF(tz_area,A{rr},tz_ref_lrt)', F_LINK, nf=NF_TRIPS)
        put(ws, rr, 23, f'=M{rr}-V{rr}', F_BASE, nf=NF_TRIPS)
    A1 = A0 + len(AREAS) - 1
    rr = A1 + 1
    put(ws, rr, 1, 'Total', F_BOLD)
    for col in list(range(3, 19)) + [22, 23]:
        put(ws, rr, col, f'=SUM({CL(col)}{A0}:{CL(col)}{A1})', F_BOLD, nf=NF_TRIPS)
    put(ws, rr, 19, f'=IF(F{rr}+G{rr}>0,G{rr}/(F{rr}+G{rr}),0)', F_BOLD, nf=NF_PCT)
    put(ws, rr, 20, f'=IF(I{rr}+J{rr}>0,J{rr}/(I{rr}+J{rr}),0)', F_BOLD, nf=NF_PCT)
    put(ws, rr, 21, f'=IF(J{rr}>0,M{rr}/J{rr},0)', F_BOLD, nf=NF_PCT)
    ws.conditional_formatting.add(f'W{A0}:W{A1}', CellIsRule(operator='greaterThan', formula=['0.5'], font=Font(name=FONT, color='006100'), fill=PatternFill('solid', fgColor='C6EFCE')))
    ws.conditional_formatting.add(f'W{A0}:W{A1}', CellIsRule(operator='lessThan', formula=['-0.5'], font=Font(name=FONT, color='9C0006'), fill=PatternFill('solid', fgColor='FFC7CE')))
    AT = A1 + 2
    # area x area LRT matrix (live)
    M0r = AT + 3
    put(ws, M0r - 1, 1, 'LRT trips between areas (live; rows = origin area, columns = destination area)', F_SUB)
    hdr(ws, M0r, 1, 'From \\ to')
    hdr(ws, M0r, 2, 'Name')
    for j, a in enumerate(AREAS):
        hdr(ws, M0r, 3 + j, a, width=None)
    hdr(ws, M0r, 3 + len(AREAS), 'Total')
    for i, a in enumerate(AREAS):
        rr = M0r + 1 + i
        put(ws, rr, 1, a, F_BOLD)
        put(ws, rr, 2, ANAME[a], F_BASE)
        for j, bb in enumerate(AREAS):
            put(ws, rr, 3 + j, f'=SUMIFS(od_lrt,od_o_area,$A{rr},od_d_area,{CL(3 + j)}${M0r})', F_BASE, nf=NF_TRIPS)
        put(ws, rr, 3 + len(AREAS), f'=SUM(C{rr}:{CL(2 + len(AREAS))}{rr})', F_BOLD, nf=NF_TRIPS)
    rr = M0r + 1 + len(AREAS)
    put(ws, rr, 1, 'Total', F_BOLD)
    for j in range(len(AREAS) + 1):
        put(ws, rr, 3 + j, f'=SUM({CL(3 + j)}{M0r + 1}:{CL(3 + j)}{rr - 1})', F_BOLD, nf=NF_TRIPS)
    ws.conditional_formatting.add(f'C{M0r + 1}:{CL(2 + len(AREAS))}{M0r + len(AREAS)}',
                                  ColorScaleRule(start_type='num', start_value=0, start_color='FFFFFF', end_type='max', end_color='5B9BD5'))
    ws.freeze_panes = 'C5'
    ch = BarChart()
    ch.type, ch.grouping = 'col', 'clustered'
    ch.title = 'LRT trips by origin area: live vs reference'
    ch.y_axis.title = 'LRT trips (3 h)'
    ch.add_data(Reference(ws, min_col=13, min_row=4, max_row=A1), titles_from_data=True)
    ch.add_data(Reference(ws, min_col=22, min_row=4, max_row=A1), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=2, min_row=A0, max_row=A1))
    ch.height, ch.width = 9, 26
    ws.add_chart(ch, f'B{M0r + len(AREAS) + 4}')

    # ------------------------------------------------------------------ Results
    ws = ws_res
    ws.column_dimensions['A'].width = 3
    ws.column_dimensions['B'].width = 44
    for col in 'CDEFG':
        ws.column_dimensions[col].width = 16
    put(ws, 1, 2, 'Results - LRT demand and the travellers it moves (AM 06:00-09:00, corridor TAZ pairs)', F_TITLE)
    put(ws, 2, 2, '="Scenario: "&Inputs!C' + str(INP['scen']) + '&"  |  "&Inputs!C' + str(INP['alt']) + '&"  |  "&Inputs!C' + str(INP['reg']), F_LINK)
    put(ws, 3, 2, '="Metronit: "&Inputs!C' + str(INP['var']) + '&"  |  LRT in service: "&Inputs!C' + str(INP['lrt_on']) + '&"  |  λ = "&TEXT(Lambda,"0.000")&", λ_T = "&TEXT(LambdaT,"0.000")', F_LINK)
    put(ws, 5, 2, 'Trips by mode', F_SUB)
    rh = ['Mode', 'Before (no LRT, today\'s network)', 'After (live)', 'Change (after - before)', 'Reference after (published)', 'Live - reference']
    for k, h in enumerate(rh):
        hdr(ws, 6, 2 + k, h)
    ws.row_dimensions[6].height = 42
    TZT = T1 + 1                                        # the TAZ totals row
    ref = lambda col: f'INDEX(RefTotals,RefCol,{col})'  # noqa: E731
    rows = [
        ('Car', f'=TAZ!F{TZT}', f'=TAZ!I{TZT}', '=' + ref(5)),
        ('Bus', '=SUM(od_bus0)', f'=TAZ!K{TZT}', '=' + ref(6)),
        ('Metronit', f'=TAZ!H{TZT}', f'=TAZ!L{TZT}', '=' + ref(7)),
        ('LRT', 0, f'=TAZ!M{TZT}', '=' + ref(8)),
        ('Total transit', f'=TAZ!G{TZT}', f'=TAZ!J{TZT}', '=' + ref(9)),
        ('Total car + transit', '=C7+C11', '=D7+D11', '=F7+F11'),
    ]
    for i, (lab, before, after, refv) in enumerate(rows):
        rr = 7 + i
        bold = F_BOLD if lab.startswith('Total') else F_BASE
        put(ws, rr, 2, lab, bold)
        put(ws, rr, 3, before, F_LINK if isinstance(before, str) and before.startswith('=TAZ') else bold, nf=NF_TRIPS)
        put(ws, rr, 4, after, F_LINK if after.startswith('=TAZ') else bold, nf=NF_TRIPS)
        put(ws, rr, 5, f'=D{rr}-C{rr}', bold, nf=NF_TRIPS)
        put(ws, rr, 6, refv, F_LINK, nf=NF_TRIPS)
        put(ws, rr, 7, f'=D{rr}-F{rr}', bold, nf=NF_TRIPS)
    put(ws, 13, 2, 'Transit share of car + transit')
    put(ws, 13, 3, '=C11/C12', F_BASE, nf=NF_PCT)
    put(ws, 13, 4, '=D11/D12', F_BASE, nf=NF_PCT)
    put(ws, 13, 5, '=D13-C13', F_BASE, nf=NF_PCT)
    put(ws, 13, 6, '=F11/F12', F_BASE, nf=NF_PCT)
    put(ws, 13, 7, '=D13-F13', F_BASE, nf=NF_PCT)
    put(ws, 14, 2, 'LRT share of transit')
    put(ws, 14, 4, '=IF(D11>0,D10/D11,0)', F_BASE, nf=NF_PCT)
    put(ws, 14, 6, '=IF(F11>0,F10/F11,0)', F_BASE, nf=NF_PCT)
    put(ws, 14, 7, '=D14-F14', F_BASE, nf=NF_PCT)

    put(ws, 16, 2, 'Where the LRT riders come from', F_SUB)
    for k, h in enumerate(['Source', 'Live', 'Share of LRT', 'Reference', 'Live - reference']):
        hdr(ws, 17, 2 + k, h)
    src = [('From the car', f'=TAZ!O{TZT}', '=' + ref(10)), ('From today\'s bus riders', f'=TAZ!P{TZT}', '=' + ref(14)),
           ('From today\'s Metronit riders', f'=TAZ!Q{TZT}', '=' + ref(15))]
    for i, (lab, live, refv) in enumerate(src):
        rr = 18 + i
        put(ws, rr, 2, lab)
        put(ws, rr, 3, live, F_LINK, nf=NF_TRIPS)
        put(ws, rr, 4, f'=IF($D$10>0,C{rr}/$D$10,0)', F_BASE, nf=NF_PCT)
        put(ws, rr, 5, refv, F_LINK, nf=NF_TRIPS)
        put(ws, rr, 6, f'=C{rr}-E{rr}', F_BASE, nf=NF_TRIPS)
    put(ws, 21, 2, 'Total LRT', F_BOLD)
    put(ws, 21, 3, '=SUM(C18:C20)', F_BOLD, nf=NF_TRIPS)
    put(ws, 21, 5, '=SUM(E18:E20)', F_BOLD, nf=NF_TRIPS)
    put(ws, 21, 6, '=C21-E21', F_BOLD, nf=NF_TRIPS)
    put(ws, 22, 2, 'Transit trips lost to the car (network change)')
    put(ws, 22, 3, f'=TAZ!R{TZT}', F_LINK, nf=NF_TRIPS)
    put(ws, 22, 5, 0, F_INPUT, nf=NF_TRIPS)
    put(ws, 22, 6, '=C22-E22', F_BASE, nf=NF_TRIPS)

    put(ws, 24, 2, 'On the line', F_SUB)
    for k, h in enumerate(['Measure', 'Live', 'Reference', 'Live - reference']):
        hdr(ws, 25, 2 + k, h)
    line_rows = [('LRT trips using the extension (at least one segment S01-S24)', '=SUM(od_lrt_ext)', '=' + ref(11)),
                 ('Busiest segment, three hours, one direction', '=MAX(BusiestSeg3h1,BusiestSeg3h2)', '=' + ref(12)),
                 ('Busiest segment, peak hour (x peak-hour factor)', f'=MAX(Stations!R{rt},Stations!S{rt})', f'=MAX(Stations!T{rt}*PHF1,Stations!U{rt}*PHF2)')]
    for i, (lab, live, refv) in enumerate(line_rows):
        rr = 26 + i
        put(ws, rr, 2, lab, align=WRAP)
        put(ws, rr, 3, live, F_BASE, nf=NF_TRIPS)
        put(ws, rr, 4, refv, F_LINK, nf=NF_TRIPS)
        put(ws, rr, 5, f'=C{rr}-D{rr}', F_BASE, nf=NF_TRIPS)

    put(ws, 30, 2, 'Model check', F_SUB)
    put(ws, 31, 2, 'LRT total, this workbook at the default inputs - published step 45 value', F_BASE, align=WRAP)
    put(ws, 31, 3, '=INDEX(RefTotals,RefCol,13)-INDEX(RefTotals,RefCol,8)', F_BASE, nf='0.0')
    put(ws, 31, 4, '=IF(ABS(C31)<1,"OK - reproduces step 45","CHECK")', F_BOLD)
    put(ws, 32, 2, 'Inputs at the study defaults?', F_BASE)
    dflt = (f'AND(Inputs!C{INP["var"]}="{VAR_LABEL["M0"]}",LrtOn=1,Lambda={DEFAULTS["lam"]},Inputs!C{INP["ratio"]}={DEFAULTS["ratio"]},PremBus={DEFAULTS["prem_bus"]},'
            f'PremMetronit={DEFAULTS["prem_brt"]},K_EB={DEFAULTS["k"]},Headway={DEFAULTS["headway"]},StAccess={DEFAULTS["st_access"]},RunFactorExt=1,RunFactorMain=1)')
    put(ws, 32, 3, f'=IF({dflt},"Yes","No")', F_BOLD)
    put(ws, 33, 2, 'At the defaults the live LRT total must equal the reference (difference below 1 trip)', F_BASE, align=WRAP)
    put(ws, 33, 3, '=IF(C32="Yes",IF(ABS(D10-F10)<1,"OK","CHECK"),"n/a - inputs changed")', F_BOLD)
    ws.row_dimensions[31].height = 28
    ws.row_dimensions[33].height = 28
    put(ws, 35, 2, 'Reference = the study model for the same scenario-year, alternative and regime with the Metronit as today and every parameter at its default (step 45, '
                   'Output/alternatives/demand_summary.csv). Bus and Metronit before are split by today\'s best path: a pair is Metronit-based when that path rides the Metronit '
                   'for at least half of its in-vehicle time.', F_NOTE, align=WRAP)
    ws.merge_cells('B35:G37')
    ch2 = BarChart()
    ch2.type, ch2.grouping = 'col', 'clustered'
    ch2.title = 'Transit trips by mode: before, after (live), reference'
    ch2.y_axis.title = 'Trips, AM 3 h'
    for col in (3, 4, 6):
        s = Reference(ws, min_col=col, min_row=8, max_row=10)
        ch2.add_data(s, titles_from_data=False)
    for s_, lab in zip(ch2.series, ['Before', 'After (live)', 'Reference']):
        s_.tx = SeriesLabel(v=lab)
    ch2.set_categories(Reference(ws, min_col=2, min_row=8, max_row=10))
    ch2.height, ch2.width = 8, 16
    ws.add_chart(ch2, 'I5')
    ch3 = BarChart()
    ch3.type, ch3.grouping = 'bar', 'clustered'
    ch3.title = 'LRT riders by source: live vs reference'
    for col, lab in ((3, 'Live'), (5, 'Reference')):
        ch3.add_data(Reference(ws, min_col=col, min_row=18, max_row=20), titles_from_data=False)
    for s_, lab in zip(ch3.series, ['Live', 'Reference']):
        s_.tx = SeriesLabel(v=lab)
    ch3.set_categories(Reference(ws, min_col=2, min_row=18, max_row=20))
    ch3.height, ch3.width = 7, 16
    ws.add_chart(ch3, 'I22')
    ws.freeze_panes = 'A5'

    # ------------------------------------------------------------------ Lambda_Sweep (static)
    ws = ws_sw
    put(ws, 1, 1, 'λ sweep (static): LRT trips against the cost sensitivity λ, for each Metronit network (λ_T = 2λ, other inputs at their defaults)', F_TITLE)
    put(ws, 2, 1, 'Precomputed by tools/build_scenario_workbook.py with the same equations as OD_Pairs. It does not follow the Inputs sheet; set λ on the Inputs sheet to see any one point live.', F_NOTE)
    r = 4
    sweep_rows = []
    for sc in ('2022', 'BU_2050'):
        for a in ALTS:
            put(ws, r, 1, f'{SCEN_LABEL[sc]}, {ALT_LABEL[a]}, {REG_LABEL["prioritized"]}', F_SUB)
            r += 1
            heads = ['λ'] + [f'LRT, {v}' for v in VARS] + [f'LRT from car, {v}' for v in VARS] + [f'Transit after, {v}' for v in VARS] + [f'Transit lost to car, {v}' for v in VARS]
            for k, h in enumerate(heads):
                hdr(ws, r, 1 + k, h, width=12)
            ws.row_dimensions[r].height = 40
            h_row = r
            for lam in LAMBDAS:
                r += 1
                put(ws, r, 1, lam, F_INPUT, nf='0.000')
                for vi, v in enumerate(VARS):
                    t = totals(pivot(D, sc, a, 'prioritized', v, {'lam': lam}))
                    put(ws, r, 2 + vi, round(t['lrt'], 1), F_INPUT, nf=NF_TRIPS)
                    put(ws, r, 5 + vi, round(t['lrt_car'], 1), F_INPUT, nf=NF_TRIPS)
                    put(ws, r, 8 + vi, round(t['tr1'], 1), F_INPUT, nf=NF_TRIPS)
                    put(ws, r, 11 + vi, round(t['tr_to_car'], 1), F_INPUT, nf=NF_TRIPS)
            sweep_rows.append((sc, a, h_row, r))
            r += 2
    put(ws, r, 1, f'λ_T sweep at λ = 0.03: {SCEN_LABEL["BU_2050"]}, {ALT_LABEL["main_ext"]}, {REG_LABEL["prioritized"]}', F_SUB)
    r += 1
    put(ws, r, 1, 'λ_T is the sensitivity inside the transit nest (LRT against the bus / Metronit path). At TAZ level it moves the LRT more than λ does; λ moves the car shift.', F_NOTE)
    r += 1
    heads = ['λ_T'] + [f'LRT, {v}' for v in VARS] + [f'LRT from car, {v}' for v in VARS]
    for k, h in enumerate(heads):
        hdr(ws, r, 1 + k, h, width=12)
    ws.row_dimensions[r].height = 40
    h0t = r
    for lt in [0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12]:
        r += 1
        put(ws, r, 1, lt, F_INPUT, nf='0.000')
        for vi, v in enumerate(VARS):
            t = totals(pivot(D, 'BU_2050', 'main_ext', 'prioritized', v, {'lam': 0.03, 'ratio': lt / 0.03}))
            put(ws, r, 2 + vi, round(t['lrt'], 1), F_INPUT, nf=NF_TRIPS)
            put(ws, r, 5 + vi, round(t['lrt_car'], 1), F_INPUT, nf=NF_TRIPS)
    ch = LineChart()
    ch.title = 'LRT trips vs λ_T (λ = 0.03) - BU_2050, Main route + extension'
    ch.y_axis.title = 'LRT trips (AM 3 h)'
    ch.x_axis.title = 'λ_T (per generalized minute)'
    ch.add_data(Reference(ws, min_col=2, min_row=h0t, max_col=4, max_row=r), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=h0t + 1, max_row=r))
    ch.height, ch.width = 7.5, 14
    ws.add_chart(ch, 'P36')
    for i, (sc, a, h0, h1) in enumerate(sweep_rows):
        ch = LineChart()
        ch.title = f'LRT trips vs λ - {sc}, {ALT_SUMMARY[a]}'
        ch.y_axis.title = 'LRT trips (AM 3 h)'
        ch.x_axis.title = 'λ (per generalized minute)'
        ch.add_data(Reference(ws, min_col=2, min_row=h0, max_col=4, max_row=h1), titles_from_data=True)
        ch.set_categories(Reference(ws, min_col=1, min_row=h0 + 1, max_row=h1))
        ch.height, ch.width = 7.5, 14
        ws.add_chart(ch, f'{"P" if i % 2 == 0 else "Y"}{4 + (i // 2) * 16}')

    # ------------------------------------------------------------------ Scenario_Grid (static)
    ws = ws_grid
    put(ws, 1, 1, 'Scenario grid (static): every scenario-year x alternative x regime x Metronit network at the default parameters', F_TITLE)
    put(ws, 2, 1, 'Precomputed by tools/build_scenario_workbook.py with the same equations as OD_Pairs; AM three hours. "LRT off" rows show the Metronit change alone.', F_NOTE)
    gh = ['Scenario', 'Alternative', 'Regime', 'Metronit', 'LRT in service', 'LRT', 'LRT using the extension', 'LRT from car', 'LRT from bus', 'LRT from Metronit',
          'Bus after', 'Metronit after', 'Transit before', 'Transit after', 'Transit lost to car', 'Car before', 'Car after', 'Busiest segment (3 h)', 'LRT vs M0 same case']
    for k, h in enumerate(gh):
        hdr(ws, 4, 1 + k, h, width=12 if k > 3 else 16)
    ws.row_dimensions[4].height = 40
    r = 5
    base_lrt = {}
    for sc in SCEN:
        for a in ALTS:
            for rg in REGS:
                for v in VARS:
                    t = totals(pivot(D, sc, a, rg, v))
                    if v == 'M0':
                        base_lrt[(sc, a, rg)] = t['lrt']
                    vals = [sc, ALT_SUMMARY[a], rg, v, 'Yes', t['lrt'], t['lrt_ext'], t['lrt_car'], t['lrt_bus'], t['lrt_brt'], t['bus1'], t['brt1'], t['tr0'], t['tr1'],
                            t['tr_to_car'], t['car0'], t['car1'], t['busiest'], t['lrt'] / base_lrt[(sc, a, rg)] - 1]
                    for k, x in enumerate(vals):
                        nf = NF_PCT if k == 18 else (NF_TRIPS if k >= 5 else None)
                        put(ws, r, 1 + k, round(x, 4) if isinstance(x, float) else x, F_INPUT if k >= 5 else F_BASE, nf=nf)
                    r += 1
    for sc in SCEN:
        for v in VARS[1:]:
            t = totals(pivot(D, sc, 'main_ext', 'prioritized', v, {'lrt_on': 0}))
            vals = [sc, '(no LRT)', '-', v, 'No', 0, 0, 0, 0, 0, t['bus1'], t['brt1'], t['tr0'], t['tr1'], t['tr_to_car'], t['car0'], t['car1'], 0, None]
            for k, x in enumerate(vals):
                put(ws, r, 1 + k, round(x, 4) if isinstance(x, float) else x, F_INPUT if k >= 5 else F_BASE, nf=NF_TRIPS if 5 <= k < 18 else None)
            r += 1
    ws.freeze_panes = 'E5'
    ws.auto_filter.ref = f'A4:{CL(len(gh))}{r - 1}'

    # ------------------------------------------------------------------ Guide
    ws = ws_g
    ws.column_dimensions['A'].width = 3
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 110
    put(ws, 1, 2, 'Nofit LRT extension - scenario model in Excel', F_TITLE)
    put(ws, 2, 2, 'Step 45 of the study (METHODOLOGY 6aq) rebuilt as live formulas: change the modes and the logit parameters and see every TAZ, area, station and segment respond.', F_NOTE)
    g = 4
    guide = [
        ('HOW TO USE', None),
        ('1. Inputs', 'Change the yellow cells: scenario-year, LRT alternative, running regime, Metronit network (e.g. M1 = Metronit removed in Haifa), LRT in service, λ, λ_T / λ, the LRT premiums, k, headway, station access, running-time factors. Excel recalculates at once (about 1 million formulas; allow a few seconds).'),
        ('2. Results', 'Trips by mode before the LRT, after (live) and in the published reference case; where the LRT riders come from; trips on the extension; the busiest segment; a model check that the defaults reproduce step 45.'),
        ('3. Areas', 'The 25 corridor areas (V2 superzones): travellers by mode before / after, LRT by origin and destination, shift sources, shares, live vs reference, and the area-to-area LRT matrix.'),
        ('4. TAZ', 'The 174 corridor TAZs with population and jobs: the same measures per TAZ, with green / red where the live result is above / below the reference. Use the filter arrows to sort.'),
        ('5. Stations', 'Boardings, alightings and line loads by segment and direction, three hours and peak hour, live vs reference.'),
        ('6. Lambda_Sweep', 'Static: LRT trips for λ from 0.01 to 0.06 (λ_T = 2λ) and for λ_T from 0.03 to 0.12 (λ = 0.03) under each Metronit network, with charts. At TAZ level λ_T, the sensitivity inside the transit nest, moves the LRT more than λ does.'),
        ('7. Scenario_Grid', 'Static: every scenario-year x alternative x regime x Metronit network at the default parameters, plus the Metronit change without the LRT.'),
        ('8. OD_Pairs', 'The engine: one row per origin-destination TAZ pair (26,022 inter-area pairs with any trip in any year). Columns {G0}-{G1} (grouped; click + above the column letters to open) hold the precomputed data; the formula columns to the right run the model. Area_Prior holds the area-pair shares; Reference the static reference values.'),
        ('COLOUR CODE', None),
        ('Yellow fill, blue text', 'An input you may change.'),
        ('Blue text', 'Data written by the Python model (base trips, precomputed path costs, reference values). Do not edit.'),
        ('Black text', 'A formula.'),
        ('Green text', 'A formula that brings a value from another sheet.'),
        ('Grey text', 'Fixed in the precomputed paths: shown for information.'),
        ('THE MODEL, PAIR BY PAIR', None),
        ('Base demand', 'Car and transit trips of the pair in the scenario-year without the LRT (2022: step 22; 2040 / 2050: step 23). Transit = bus + Metronit + rail; taxi is outside the choice.'),
        ('Smoothed share S', 'S = (transit + k x S_area) / (car + transit + k): the pair\'s observed transit share pulled towards its area pair\'s share (Area_Prior), k = 20.'),
        ('Lower level: LRT vs bus / Metronit', 'dL = GC_LRT - premium - GC_transit.  P(LRT | transit) = 1 / (1 + exp(λ_T dL)). The premium is 5 against a bus-based path and 2.5 against a Metronit-based one.'),
        ('Upper level: car vs transit', 'Δ = (GC_transit,scenario - GC_transit,today) - ln(1 + exp(-λ_T dL)) / λ_T: the change of the transit nest\'s composite cost. S\' = S e^(-λΔ) / (S e^(-λΔ) + 1 - S). Δ < 0 draws car trips to transit; Δ > 0 (a Metronit cut that the LRT does not make up) sends transit trips to the car.'),
        ('Pivot', 'Transit after = transit before x S\' / S (capped at the pair\'s total); car after = total - transit after; LRT = transit after x P(LRT | transit); the rest stays on its bus or Metronit path. With the Metronit as today and the LRT out of service the model returns the base trips exactly.'),
        ('Generalized cost', 'In-vehicle + 2 x walk + 2 x wait + 8 per transfer (bus to LRT 8, Metronit to LRT 4). LRT path = access leg (walk, bus or Metronit) to the cheapest-access station + 2 x headway/2 + 0.5 station access per end + line time + egress leg. Paths come from the May 2026 timetable and observed bus speeds (steps 29, 30, 44, 45).'),
        ('Metronit networks', 'M0 = today. M1 = Metronit cut back to Hamifrats: every Metronit ride segment with a stop in Haifa south / west of Hamifrats (corridor areas 202-209 and the Haifa zones 1300-1899) removed; lines 1, 2 and 4 then run Hamifrats - Krayot / Kiryat Ata and line 3 keeps its Krayot loop. M2 = all five lines removed. Bus and Metronit paths, the Metronit-based flag and the LRT feeder legs are recomputed for each (tools/scenario_metronit_skims.py; Output/scenario_tool/).'),
        ('WHAT IT CANNOT DO', None),
        ('Network changes beyond the three Metronit variants', 'Bus routes, frequencies, walk / wait weights and penalties are inside the precomputed paths. A new variant needs a run of tools/scenario_metronit_skims.py (add it to VARIANTS) and of tools/build_scenario_workbook.py.'),
        ('Car-side changes', 'The pivot moves trips on the change of the transit nest only, so road congestion, parking or car cost do not register (METHODOLOGY 6aq addendum 3).'),
        ('Capacity, fares, PM peak', 'No capacity restraint, no fare (flat integrated fare by decision), AM peak only. The line loads are screening values, not design loads.'),
        ('Parallel buses', 'Every regular bus line is kept as it runs today; truncating the parallel buses would raise the LRT further (METHODOLOGY 6ac, task C7).'),
        ('SOURCES', None),
        ('Model and numbers', 'METHODOLOGY.md 6ac (the pivot), 6aq (step 45), 6ae (λ); Output/alternatives/demand_summary.csv (the published totals this workbook reproduces at its defaults).'),
        ('Rebuild', 'python3 tools/scenario_metronit_skims.py ; python3 tools/build_scenario_workbook.py (about 2 minutes; the skims need Input/Corridor_TAZ_Agg_V2.xlsx and Input/Main_Nofit/Main_Nofit_StopsID.csv from LFS: python3 tools/lfs_pull.py <file>).'),
    ]
    for lab, txt in guide:
        g += 1
        if txt:
            txt = txt.replace('{G0}', CL(7)).replace('{G1}', CL(first_formula - 1))
        if txt is None:
            g += 1
            put(ws, g, 2, lab, F_SUB, fill=FILL_BLOCK)
            ws.cell(row=g, column=3).fill = FILL_BLOCK
            continue
        put(ws, g, 2, lab, F_BOLD, align=WRAP)
        put(ws, g, 3, txt, F_BASE, align=WRAP)
        ws.row_dimensions[g].height = max(15, 14 * (len(txt) // 120 + 1))
    # legend swatches
    ws.cell(row=g + 2, column=2, value='Example input cell').font = F_INPUT
    ws.cell(row=g + 2, column=2).fill = FILL_INPUT
    ws.sheet_view.showGridLines = False
    ws_in.sheet_view.showGridLines = False
    ws_res.sheet_view.showGridLines = False

    # sheet tab colours
    ws_in.sheet_properties.tabColor = 'FFFF00'
    ws_res.sheet_properties.tabColor = '00B050'
    for w_ in (ws_ar, ws_tz, ws_st):
        w_.sheet_properties.tabColor = '5B9BD5'
    for w_ in (ws_sw, ws_grid):
        w_.sheet_properties.tabColor = 'A5A5A5'
    for w_ in (ws_od, ws_pr, ws_ref):
        w_.sheet_properties.tabColor = '7F7F7F'
    wb.active = 1
    from openpyxl.workbook.properties import CalcProperties
    wb.calculation = CalcProperties(fullCalcOnLoad=True)
    os.makedirs(os.path.dirname(OUT_XLSX), exist_ok=True)
    print('saving ...', flush=True)
    wb.save(OUT_XLSX)
    print(f'written {OUT_XLSX} ({os.path.getsize(OUT_XLSX) / 1e6:.1f} MB)')
    return {'INP': INP, 'NP': NP, 'COL': COL, 'R0': R0, 'R1': R1, 'TZT': TZT}


def main():
    D = load()
    chk, worst, ds = check_against_step45(D)
    lrt = chk[chk['measure'] == 'LRT']
    print(lrt[['scenario', 'alternative', 'regime', 'this model', 'step 45', 'diff']].to_string(index=False))
    print(f'largest LRT difference against step 45: {worst:.3f} trips; all measures: {chk["diff"].abs().max():.3f}')
    if worst > 0.5:
        sys.exit('the numpy pivot does not reproduce step 45 - stopping')
    if '--check-only' in sys.argv:
        print(chk.to_string(index=False))
        return
    build(D, ds)


if __name__ == '__main__':
    main()
