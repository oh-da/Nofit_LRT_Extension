"""Hand-checked tests for tools/validation_metrics.py.  Run:  python3 tools/test_validation_metrics.py"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validation_metrics as vm

def close(a, b, tol=1e-9): assert abs(a - b) < tol, (a, b)

obs = np.array([100., 200., 300., 400.]); mod = np.array([110., 190., 330., 380.])
# hand calculation: errors 10, -10, 30, -20 -> squares 100 + 100 + 900 + 400 = 1500
close(vm.rmse(obs, mod), np.sqrt(1500 / 4)); close(vm.rmse_pct(obs, mod), 100 * np.sqrt(1500 / 4) / 250)
close(vm.mae(obs, mod), (10 + 10 + 30 + 20) / 4)
close(vm.slope_origin(obs, mod), (100*110 + 200*190 + 300*330 + 400*380) / (100**2 + 200**2 + 300**2 + 400**2))
close(vm.r2_correl(obs, mod), np.corrcoef(obs, mod)[0, 1] ** 2)
close(vm.r2_correl(obs, obs), 1.0); close(vm.slope_origin(obs, 2 * obs), 2.0); close(vm.r2_origin(obs, 2 * obs), 1.0)
fs = vm.fit_stats(obs, mod); close(fs['total_diff_pct'], 1.0); assert fs['n'] == 4
# coincidence ratio: p = (.5, .5), q = (.25, .75) -> min .25 + .5 = .75 ; max .5 + .75 = 1.25 -> 0.6
close(vm.coincidence_ratio([1, 1], [1, 3]), 0.6); close(vm.coincidence_ratio([5, 5], [1, 1]), 1.0)
close(vm.coincidence_ratio([1, 0], [0, 1]), 0.0)
# chi-square on counts: obs (30, 70), exp (50, 50) -> 400/50 + 400/50 = 16 ; critical df 1 = 3.841
c = vm.chi2_test([30, 70], [50, 50]); close(c['chi2'], 16.0); assert c['pass'] is False; close(c['critical'], 3.841, 1e-3)
# KS: identical samples -> D 0; fully separated -> D 1
r = vm.ks_weighted([1, 2, 3], [1, 1, 1], [1, 2, 3], [1, 1, 1]); close(r['D'], 0.0); assert r['pass']
r = vm.ks_weighted(np.arange(30), np.ones(30), np.arange(30) + 100, np.ones(30)); close(r['D'], 1.0); assert not r['pass']
# KS with weights: a doubled weight is the same as a repeated point
a = vm.ks_weighted([1, 2], [2, 1], [1, 1, 2], [1, 1, 1]); close(a['D'], 0.0)
# KS critical value for n1 = n2 = 100: 1.358 * sqrt(2/100) = 0.1921
r = vm.ks_weighted(np.arange(100), np.ones(100), np.arange(100) + 0.5, np.ones(100), n1=100, n2=100)
close(r['critical'], 1.3581 * np.sqrt(0.02), 1e-3)
close(vm.kish_n([1, 1, 1, 1]), 4.0); close(vm.kish_n([1, 3]), 16 / 10)
# within_pct and class limits
close(vm.within_pct([100, 100, 100, 100], [105, 120, 90, 115], 15), 0.75)
assert vm.class_limit(750, vm.ROAD_RMSE_CLASSES) == 40.0 and vm.class_limit(9000, vm.ROAD_RMSE_CLASSES) == 12.0
assert vm.class_limit(80, vm.STATION_RMSE_CLASSES) == 50.0 and vm.class_limit(1200, vm.STATION_RMSE_CLASSES) == 12.0
rows = vm.rmse_by_class([400, 450, 1500, 1600], [420, 430, 1700, 1400], vm.ROAD_RMSE_CLASSES)
assert [r['class'] for r in rows] == ['0-500', '1000-2000'] and rows[0]['pass'] and rows[1]['pass']
close(vm.line_diff_check([50, 300, 3000], [90, 330, 3200])['share_within_allowance'], 1.0)
assert vm.verdict(True) == 'pass' and vm.verdict(False, True) == 'miss (explained)' and vm.verdict(None) == 'not run'
print('validation_metrics: all tests passed')
