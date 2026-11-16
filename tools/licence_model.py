"""Driving-licence model (step 46): a binary logit of car-licence holding on the THS 2017-18
persons, and its application to the zonal population of a scenario year.

Design: docs/superpowers/specs/2026-11-16-driving-licence-model-design.md
Used by notebooks/current/Driving_licence_model.ipynb.  Tests: python3 tools/test_licence_model.py

Every predictor exists in the forecast zonal files: age, gender (applied with the survey's split),
sector (ara / ort / rest) and the zone's socio-economic index, settlement size and ring.
"""
import os
import warnings
import numpy as np
import pandas as pd

SURVEY_YEAR = 2017
MIN_AGE = 17                       # under 17: probability 0 (survey: 0.7 % at 16)
MAX_AGE = 90                       # the age curve is held flat beyond this
KNOTS = (19, 26, 36, 65, 75)       # the forecast's band limits, plus 75 for the old-age decline
KNOTS_ARA = (26, 36, 65)           # sector x age terms use reduced curves: the full one separates
KNOTS_ORT = (26, 65)               # (no Arab woman of 80+ in the sample holds a licence); Haredi cells are thin
BANDS = {'0_7': (0, 7), '8_18': (8, 18), '19_25': (19, 25), '26_35': (26, 35), '36_64': (36, 64), '65': (65, 120)}
SECTORS = ('rest', 'ara', 'ort')
ZCOL = {'rest': 'REST', 'ara': 'ARA', 'ort': 'ORT'}
SAT = (30, 39)                     # saturation window of the cohort rule
KEEP_FROM = 65                     # giving-up starts here

# the specification ladder: each model adds term groups to the one before
SPECS = {
    'M0': ('age',),
    'M1': ('age', 'male'),
    'M2': ('age', 'male', 'sec'),
    'M3': ('age', 'male', 'sec', 'sec_male'),
    'M4': ('age', 'male', 'sec', 'sec_male', 'male_age', 'sec_age'),
    'M5': ('age', 'male', 'sec', 'sec_male', 'male_age', 'sec_age', 'sec_male_age'),
    'M6': ('age', 'male', 'sec', 'sec_male', 'male_age', 'sec_age', 'sec_male_age', 'zone'),
    'M7': ('age', 'male', 'sec', 'sec_male', 'male_age', 'sec_age', 'sec_male_age', 'zone', 'zone_sec'),
    'M8': ('age', 'male', 'sec', 'sec_male', 'male_age', 'sec_age', 'sec_male_age', 'zone', 'zone_sec', 'settl'),
}

FINAL = 'M7'                       # chosen in the notebook (step 46, section 3)


def sector_of(hhtype):
    """arab -> ara, orto -> ort, everything else (secular, religious, other) -> rest."""
    return pd.Series(hhtype).map({'arab': 'ara', 'orto': 'ort'}).fillna('rest').to_numpy()


def band_of(age):
    age = np.floor(np.asarray(age, float))
    out = np.full(age.shape, '65', dtype=object)
    for b, (lo, hi) in BANDS.items():
        out[(age >= lo) & (age <= hi)] = b
    return out


def _hinges(age, knots):
    a = np.clip(np.asarray(age, float), MIN_AGE, MAX_AGE)
    return np.column_stack([a - MIN_AGE] + [np.clip(a - k, 0, None) for k in knots])


def age_basis(age):
    """Piecewise-linear curve: (age - 17) and a hinge at each knot. Shape (n, 6)."""
    return _hinges(age, KNOTS)


def clean_soceco(s, fill):
    """SOCECO 0 means 'not classified': replaced by `fill`, never read as the lowest class."""
    s = pd.to_numeric(pd.Series(s), errors='coerce').astype(float)
    return s.where(s > 0, fill).fillna(fill).to_numpy()


def design(spec, age, male, sec, soceco=None, settl=None, ring=None):
    """Design matrix of a specification in SPECS. `soceco` must already be cleaned."""
    terms = SPECS[spec] if isinstance(spec, str) else tuple(spec)
    age = np.asarray(age, float); male = np.asarray(male, float); sec = np.asarray(sec, object)
    A = age_basis(age); R = _hinges(age, KNOTS_ORT); Q = _hinges(age, KNOTS_ARA)
    an = ['age17'] + [f'age{k}' for k in KNOTS]; rn = ['age17'] + [f'age{k}' for k in KNOTS_ORT]; qn = ['age17'] + [f'age{k}' for k in KNOTS_ARA]
    ara = (sec == 'ara').astype(float); ort = (sec == 'ort').astype(float)
    X = {'const': np.ones(len(age))}
    def add(prefix, flag, M, names):
        for j, n in enumerate(names):
            X[f'{prefix}{n}'] = flag * M[:, j]
    for t in terms:
        if t == 'age': add('', 1.0, A, an)
        elif t == 'male': X['male'] = male
        elif t == 'sec': X['ara'] = ara; X['ort'] = ort
        elif t == 'sec_male': X['ara:male'] = ara * male; X['ort:male'] = ort * male
        elif t == 'male_age': add('male:', male, A, an)
        elif t == 'sec_age': add('ara:', ara, Q, qn); add('ort:', ort, R, rn)
        elif t == 'sec_male_age': add('ara:male:', ara * male, Q, qn); add('ort:male:', ort * male, R, rn)
        elif t == 'zone':
            se = np.asarray(soceco, float) - 5.0; rg = np.asarray(ring, float)
            X['soceco'] = se
            for r in (2, 3, 4): X[f'ring{r}'] = (rg == r).astype(float)
        elif t == 'settl':
            st = np.asarray(settl, float)
            X['settl2'] = (st == 2).astype(float); X['settl3'] = (st == 3).astype(float)
        elif t == 'zone_sec':
            se = np.asarray(soceco, float) - 5.0
            X['ara:soceco'] = ara * se; X['ort:soceco'] = ort * se
        else:
            raise KeyError(t)
    return pd.DataFrame(X)


def load_persons(root='.', estimation=True):
    """THS persons with household weight and zone attributes.
    estimation=True: aged 17+, licence answered, gender known. False: everyone with age and gender
    (for the age / gender distribution inside the forecast's bands)."""
    p = pd.read_csv(os.path.join(root, 'Input/THS_2017-2018/PersonsFin2.csv'), low_memory=False)
    w = pd.read_csv(os.path.join(root, 'Input/Matrices/households_with_weights.csv'))[['HHID', 'wf_new']]
    z = pd.read_csv(os.path.join(root, 'Input/Zonal_2020.csv'), encoding='cp1255')[['TAZ_ID', 'SOCECO', 'SETTL_SIZE', 'TABAAT']]
    d = p.merge(w, on='HHID', how='left').merge(z, left_on='TAZ', right_on='TAZ_ID', how='left')
    assert d.wf_new.notna().all() and d.TAZ_ID.notna().all(), 'a household without weight or zone'
    d['lic'] = d.license_car.map({'yes': 1.0, 'no': 0.0})
    d['male'] = d.Gender.map({'male': 1.0, 'female': 0.0})
    d['sec'] = sector_of(d.Hhtype)
    d['age'] = np.floor(d.Age)
    d = d[d.age.notna() & d.male.notna()]
    if estimation:
        d = d[(d.age >= MIN_AGE) & d.lic.notna()]
    d = d.rename(columns={'wf_new': 'wraw'}).reset_index(drop=True)
    d['w'] = d.wraw * len(d) / d.wraw.sum()
    return d[['INDIVID', 'HHID', 'TAZ', 'lic', 'age', 'male', 'sec', 'Hhtype', 'SOCECO', 'SETTL_SIZE', 'TABAAT', 'wraw', 'w']]


def soceco_fill(df):
    """Weighted mean of the classified zones' index over the sample: the stand-in for SOCECO = 0."""
    ok = df.SOCECO > 0
    return float(np.average(df.SOCECO[ok], weights=df.w[ok]))


def fit(df, spec, fill=None):
    """Weighted binary logit, standard errors clustered on the household."""
    import statsmodels.api as sm
    fill = soceco_fill(df) if fill is None else fill
    X = design(spec, df.age, df.male, df.sec, clean_soceco(df.SOCECO, fill), df.SETTL_SIZE, df.TABAAT)
    with warnings.catch_warnings():      # statsmodels warns that cluster + freq_weights is 'not fully supported';
        warnings.simplefilter('ignore')  # the notebook checks these standard errors against a hand-built sandwich
        res = sm.GLM(df.lic.to_numpy(), X, family=sm.families.Binomial(), freq_weights=df.w.to_numpy()).fit(
            cov_type='cluster', cov_kwds={'groups': df.HHID.to_numpy()})
    res.licence_spec = spec; res.licence_fill = fill
    return res


def predict(params, spec, age, male, sec, soceco=None, settl=None, ring=None):
    """Probability of holding a licence; 0 under MIN_AGE. `params` is a Series of coefficients."""
    age = np.asarray(age, float)
    X = design(spec, age, male, sec, soceco, settl, ring)
    eta = X[list(params.index)].to_numpy() @ np.asarray(params, float)
    return np.where(age < MIN_AGE, 0.0, 1.0 / (1.0 + np.exp(-eta)))


def keep_curve(params, spec, soceco, settl=3, ring=1):
    """Giving-up curve keep(age): 1 up to KEEP_FROM, then the model's rate for men of the rest
    sector relative to their rate at KEEP_FROM (their rate has long been near saturation, so the
    decline after 65 is read as giving up). Never above 1, never rising with age."""
    ages = np.arange(0, 131)
    one = np.ones(len(ages))
    p = predict(params, spec, ages, one, np.array(['rest'] * len(ages), object), soceco * one, settl * one, ring * one)
    k = np.where(ages <= KEEP_FROM, 1.0, p / p[KEEP_FROM])
    k = np.minimum.accumulate(np.minimum(k, 1.0))
    return lambda a: k[np.clip(np.floor(np.asarray(a, float)).astype(int), 0, 130)]


def keep_rows(params, spec, soceco, settl, ring):
    """The giving-up curve evaluated row by row, in each row's own zone: keep(ages) for arrays aligned
    with the zone arrays. Same definition as keep_curve; used in the application so that the cohort
    rate of rest-sector men who were 65+ in the survey year equals their static rate exactly."""
    n = len(soceco); one = np.ones(n); rest = np.array(['rest'] * n, object)
    p65 = predict(params, spec, KEEP_FROM * one, one, rest, soceco, settl, ring)
    def keep(a):
        a = np.asarray(a, float)
        p = predict(params, spec, np.maximum(a, KEEP_FROM), one, rest, soceco, settl, ring)
        return np.minimum(1.0, p / p65)
    return keep


def cohort_rate(p_fn, keep, a, year, sat=SAT, survey_year=SURVEY_YEAR):
    """Cohort carry-forward rate at age `a` in `year`.
    p_fn(ages) -> the 2017 model rate for the same rows at other ages; keep(ages) -> giving-up curve.
      a < sat[0]                   : p(a)
      a >= sat[0], a0 >= sat[0]    : p(a0) * keep(a) / keep(a0)      a0 = a - (year - survey_year)
      a >= sat[0], a0 <  sat[0]    : S * keep(a),  S = mean of p over the saturation window
    """
    a = np.asarray(a, float); a0 = a - (year - survey_year)
    S = np.mean([p_fn(np.full(a.shape, float(k))) for k in range(sat[0], sat[1] + 1)], axis=0)
    a0c = np.clip(a0, sat[0], None)
    old = p_fn(a0c) * keep(a) / keep(a0c)
    out = np.where(a < sat[0], p_fn(a), np.where(a0 >= sat[0], old, S * keep(a)))
    return np.clip(out, 0.0, 1.0)


def within_band_shares(persons, min_n=30):
    """Weighted share of each (single year of age, gender) inside a band x sector cell of the survey.
    A cell with fewer than `min_n` persons takes the all-sector distribution of its band."""
    d = persons.assign(band=band_of(persons.age), age=np.clip(persons.age, 0, 100))
    wcol = 'wraw' if 'wraw' in d else 'w'
    allsec = d.groupby(['band', 'age', 'male'])[wcol].sum()
    out = []
    for b in BANDS:
        if b not in allsec.index.get_level_values(0):
            continue                       # a band the survey does not cover at all: apply_zonal refuses it
        for s in SECTORS:
            c = d[(d.band == b) & (d.sec == s)]
            g = c.groupby(['age', 'male'])[wcol].sum() if len(c) >= min_n else allsec.loc[b]
            g = (g / g.sum()).rename('share').reset_index()
            out.append(g.assign(band=b, sec=s, n_survey=len(c), fallback=len(c) < min_n))
    return pd.concat(out, ignore_index=True)[['band', 'sec', 'age', 'male', 'share', 'n_survey', 'fallback']]


def apply_zonal(params, spec, zonal, shares, year, fill, method='cohort', sat=SAT, giving_up=True, detail=False):
    """Licence holders per zone x sector x band of a zonal file.
    method: 'static' (the 2017 rate at each age), 'cohort' (carry-forward), 'late' (the larger of the two).
    Returns TAZ_ID, sec, band, persons, holders (and per age x gender rows when detail=True)."""
    z = zonal[['TAZ_ID', 'SOCECO', 'SETTL_SIZE', 'TABAAT']].copy()
    z['soceco'] = clean_soceco(z.SOCECO, fill)
    pop = pd.concat([pd.DataFrame({'TAZ_ID': zonal.TAZ_ID, 'sec': s, 'band': b,
                                   'persons': pd.to_numeric(zonal[f'AGE_{b}_{ZCOL[s]}'], errors='coerce').fillna(0.0)})
                     for b in BANDS for s in SECTORS], ignore_index=True)
    have = set(map(tuple, shares[['band', 'sec']].drop_duplicates().to_numpy()))
    assert all((b, s) in have for b in BANDS for s in SECTORS), 'a band x sector cell has no age / gender distribution'
    g = pop.merge(shares[['band', 'sec', 'age', 'male', 'share']], on=['band', 'sec']).merge(z, on='TAZ_ID')
    g['n'] = g.persons * g.share
    sec = g.sec.to_numpy(object); male = g.male.to_numpy(); zz = (g.soceco.to_numpy(), g.SETTL_SIZE.to_numpy(), g.TABAAT.to_numpy())
    p_fn = lambda ages: predict(params, spec, ages, male, sec, *zz)
    age = g.age.to_numpy(float)
    static = p_fn(age)
    if method == 'static':
        rate = static
    else:
        keep = keep_rows(params, spec, *zz) if giving_up else (lambda a: np.ones(np.shape(a)))
        rate = cohort_rate(p_fn, keep, age, year, sat)
        if method == 'late':
            rate = np.maximum(rate, static)
    g['rate'] = rate; g['holders'] = g.n * g.rate
    if detail:
        return g[['TAZ_ID', 'sec', 'band', 'age', 'male', 'n', 'rate', 'holders']]
    out = g.groupby(['TAZ_ID', 'sec', 'band'], sort=False).agg(persons=('n', 'sum'), holders=('holders', 'sum')).reset_index()
    return out
