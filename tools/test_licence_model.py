"""Hand-checked tests for tools/licence_model.py.  Run:  python3 tools/test_licence_model.py"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import licence_model as lm

def close(a, b, tol=1e-9): assert np.allclose(a, b, atol=tol), (a, b)

# age curve: knots 19, 26, 36, 65, 75 ; held flat outside 17-90
close(lm.age_basis([17])[0], [0, 0, 0, 0, 0, 0])
close(lm.age_basis([30])[0], [13, 11, 4, 0, 0, 0])
close(lm.age_basis([80])[0], [63, 61, 54, 44, 15, 5])
close(lm.age_basis([105])[0], lm.age_basis([90])[0]); close(lm.age_basis([5])[0], lm.age_basis([17])[0])

# sectors and bands
assert list(lm.sector_of(['arab', 'orto', 'secular', 'religious', 'other', None])) == ['ara', 'ort', 'rest', 'rest', 'rest', 'rest']
assert list(lm.band_of([0, 7.9, 8, 18, 19, 25, 26, 35, 36, 64, 65, 107])) == ['0_7', '0_7', '8_18', '8_18', '19_25', '19_25', '26_35', '26_35', '36_64', '36_64', '65', '65']

# SOCECO 0 is 'not classified', not the lowest class
close(lm.clean_soceco([0, 3, np.nan, 10], 4.5), [4.5, 3, 4.5, 10])

# design: the M3 columns, and the Haredi interactions use the reduced curve
X = lm.design('M3', [30], [1], ['ara'])
assert list(X.columns) == ['const', 'age17', 'age19', 'age26', 'age36', 'age65', 'age75', 'male', 'ara', 'ort', 'ara:male', 'ort:male']
close(X.iloc[0].to_numpy(), [1, 13, 11, 4, 0, 0, 0, 1, 1, 0, 1, 0])
X = lm.design('M5', [70, 70], [1, 0], ['ort', 'rest'])
assert [c for c in X.columns if c.startswith('ort:male:')] == ['ort:male:age17', 'ort:male:age26', 'ort:male:age65']
close(X.loc[0, ['ort:age17', 'ort:age26', 'ort:age65']].to_numpy(float), [53, 44, 5]); close(X.loc[1, 'ort:age17'], 0)

# predict: 0 under 17; the logistic of the linear index otherwise
par = pd.Series({'const': 0.0, 'age17': 0.1})
close(lm.predict(par, ('age',), [16, 17, 27], [0, 0, 0], ['rest'] * 3), [0, 0.5, 1 / (1 + np.exp(-1.0))])

# cohort rule on a toy profile: p rises to 0.8 at 30-39, is 0.5 from 40 ; keep falls 2 % a year after 65
p_fn = lambda a: np.where(a < 17, 0.0, np.where(a < 30, 0.4, np.where(a < 40, 0.8, 0.5)))
keep = lambda a: np.where(np.asarray(a) <= 65, 1.0, 1.0 - 0.02 * (np.asarray(a) - 65))
r = lm.cohort_rate(p_fn, keep, np.array([10., 25., 45., 60., 70., 90.]), 2040)
close(r[0], 0.0)                 # a child
close(r[1], 0.4)                 # under 30: the 2017 rate at that age
close(r[2], 0.8)                 # 45 in 2040 was 22 in 2017 -> saturation rate
close(r[3], 0.8)                 # 60 in 2040 was 37 in 2017 -> keeps the 0.8 it had
close(r[4], 0.5 * 0.9)           # 70 in 2040 was 47 -> 0.5, then five years of giving up
close(r[5], 0.5 * 0.5 / 0.96)    # 90 was 67: p(67) * keep(90) / keep(67)
close(lm.cohort_rate(p_fn, keep, np.array([40.]), 2060), 0.8)           # unborn in 2017 -> saturation branch
close(lm.cohort_rate(lambda a: np.full(np.shape(a), 0.99), lambda a: np.where(np.asarray(a) > 65, 0.5, 1.0), np.array([60.]), 2020), 0.99)
assert lm.cohort_rate(lambda a: np.full(np.shape(a), 0.99), lambda a: np.where(np.asarray(a) >= 65, 0.5, 1.0), np.array([64.]), 2010)[0] <= 1.0   # capped

# keep curve from a model whose rest-sector men lose 0.1 of log-odds a year after 65
par = pd.Series({'const': 2.0, 'age65': -0.1})
k = lm.keep_curve(par, ('age',), 5.0)
sig = lambda x: 1 / (1 + np.exp(-x))
close(k([40, 65]), [1, 1]); close(k([75]), sig(1.0) / sig(2.0)); assert k([80])[0] < k([75])[0]
close(lm.keep_curve(pd.Series({'const': 2.0, 'age65': +0.1}), ('age',), 5.0)([80]), 1.0)   # never above 1

# shares inside a band: a thin cell falls back to the all-sector distribution
per = pd.DataFrame({'age': [20, 20, 22, 22, 21], 'male': [1, 0, 1, 0, 1], 'sec': ['rest'] * 4 + ['ort'], 'w': [1, 1, 1, 1, 2.]})
sh = lm.within_band_shares(per, min_n=2)
c = sh[(sh.band == '19_25') & (sh.sec == 'rest')]; close(c.share.sum(), 1); close(c.share.to_numpy(), [.25] * 4); assert not c.fallback.any()
c = sh[(sh.band == '19_25') & (sh.sec == 'ort')]; assert c.fallback.all(); close(c.share.sum(), 1)
close(c[c.age == 21].share.sum(), 2 / 6)

# application: one zone, a zero cell stays zero, totals reconcile, no NaN
sh = pd.DataFrame([dict(band=b, sec=s, age=a, male=m, share=0.5) for b, a in [('0_7', 4), ('8_18', 17), ('19_25', 22), ('26_35', 30), ('36_64', 50), ('65', 70)]
                   for s in lm.SECTORS for m in (0, 1)])
zon = pd.DataFrame({'TAZ_ID': [1], 'SOCECO': [0], 'SETTL_SIZE': [3], 'TABAAT': [1]})
for b in lm.BANDS:
    for s in lm.SECTORS: zon[f'AGE_{b}_{lm.ZCOL[s]}'] = 100.0
zon['AGE_36_64_ORT'] = 0.0
par = pd.Series({'const': 0.0, 'male': 1.0})
o = lm.apply_zonal(par, ('age', 'male'), zon, sh, 2040, fill=5.0, method='static')
assert len(o) == 18 and o.notna().all().all(); close(o.persons.sum(), 1700)
close(o[(o.band == '36_64') & (o.sec == 'ort')].holders, 0); close(o[o.band == '0_7'].holders, 0)
close(o[(o.band == '26_35') & (o.sec == 'ara')].holders, 50 * 0.5 + 50 * sig(1.0))
oc = lm.apply_zonal(par, ('age', 'male'), zon, sh, 2040, fill=5.0, method='cohort')
close(oc.holders.sum(), o.holders.sum())      # a flat profile: cohort = static
ol = lm.apply_zonal(par, ('age', 'male'), zon, sh, 2040, fill=5.0, method='late'); assert (ol.holders >= oc.holders - 1e-9).all()
print('licence_model: all tests passed')
