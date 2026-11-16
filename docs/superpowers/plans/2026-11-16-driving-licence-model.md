# Driving-Licence Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Estimate a binary logit of car-licence holding on the THS 2017–18 survey and apply it to the 2020, 2040 and 2050 zonal populations, static and cohort carry-forward.

**Architecture:** The reusable logic (data preparation, design matrix, cohort rule, application) is in one module, `tools/licence_model.py`, with hand-checked tests beside it in the repository's plain-assert style. The notebook `notebooks/current/Driving_licence_model.ipynb` (step 46) calls the module, runs the specification search and validation, and writes `Output/licence_model/`.

**Tech Stack:** pandas, numpy, statsmodels (GLM binomial, `freq_weights` normalised, cluster-robust covariance), scikit-learn (`GroupKFold`, AUC, log-loss), matplotlib.

**Spec:** `docs/superpowers/specs/2026-11-16-driving-licence-model-design.md`

## Global Constraints

- Predictors only from the forecast files: age, gender, sector (ara / ort / rest), `SOCECO`, `SETTL_SIZE`, `TABAAT`.
- Estimation sample: `Age >= 17`, `license_car` in yes / no, `Gender` known. Under 17: probability 0.
- Sector map: `arab` → ara, `orto` → ort, everything else → rest.
- Weight `wf_new`, normalised to the sample size; standard errors clustered on `HHID`.
- Age spline knots 19, 26, 36, 65, 75. Survey year 2017. Saturation window 30–39. `keep(a)` = 1 up to 65.
- Input files pulled from LFS with `tools/lfs_pull.py` are never `git add`-ed; restore the pointers before committing.
- No model identifier in any committed file.

## Review Focus

- A zone with zero population in a cell → zero holders, no NaN.
- A zone whose `SOCECO` is 0 (unclassified) → treated as missing and given the population-weighted mean, not as the lowest class.
- A band × sector cell absent from the survey (Haredi 75+) → age and gender distribution falls back to the all-sector distribution for that band.
- A cohort unborn in 2017 (`a0 < 0`) → the saturation branch, not an error.
- The cohort rate may never exceed 1.

---

### Task 1: The module and its tests

**Files:**
- Create: `tools/licence_model.py`, `tools/test_licence_model.py`

**Interfaces — produces:**
- `load_persons(root) -> DataFrame` — estimation sample with `lic, age, male, sec, w, HHID, TAZ, SOCECO, SETTL_SIZE, TABAAT`.
- `age_basis(age) -> ndarray (n, 6)` — linear term from 17 plus hinge terms at the five knots.
- `design(df, spec) -> DataFrame` — the design matrix of a named specification from `SPECS`.
- `fit(df, spec) -> results` — weighted, clustered logit.
- `predict(res, spec, age, male, sec, zone_df) -> ndarray` — probability; 0 under 17.
- `keep_curve(res, spec, ref_zone) -> function(age)`.
- `cohort_rate(p_fn, keep, a, year, sat=(30, 39)) -> ndarray`.
- `within_band_shares(persons_all) -> DataFrame` — weighted share of each single year of age × gender inside band × sector, with the all-sector fallback.
- `apply_zonal(res, spec, zonal, shares, year, method) -> DataFrame` — holders and persons per zone × sector × band.

- [ ] **Step 1:** Write `tools/test_licence_model.py`: `age_basis` at 17, 30 and 80 against hand values; the sector map; `cohort_rate` on a toy `p_fn` for the three branches, for `a0 < 0`, and capped at 1; `apply_zonal` on a one-zone table with a zero cell and a missing survey cell.
- [ ] **Step 2:** Run `python3 tools/test_licence_model.py` — fails on import.
- [ ] **Step 3:** Write `tools/licence_model.py`.
- [ ] **Step 4:** Run the tests — pass.
- [ ] **Step 5:** Commit.

### Task 2: The notebook — estimation, validation, application

**Files:**
- Create: `notebooks/current/Driving_licence_model.ipynb`, `Output/licence_model/*`

- [ ] **Step 1:** Specification ladder M0–M5 (age; + gender; + sector; + sector × gender; + gender × age and sector × age; + zone attributes), with log-likelihood, AIC, BIC, likelihood-ratio tests and five-fold household-grouped AUC and log-loss. Choose the specification by the rule in the spec.
- [ ] **Step 2:** Coefficient table; observed against predicted by age band × gender × sector; the 2020 zonal application against the survey's weighted rate.
- [ ] **Step 3:** Apply to 2020 and BU / HS × 2040 / 2050, static and cohort; the two sensitivity runs.
- [ ] **Step 4:** Figures: age profiles by gender and sector with the survey points; static against cohort by sector and year.
- [ ] **Step 5:** Execute the notebook top to bottom with `nbclient`; check the outputs exist and the totals reconcile (persons in the output = the zonal file's population aged 8 and over minus nothing dropped).
- [ ] **Step 6:** Commit.

### Task 3: Documentation and pipeline entry

**Files:**
- Modify: `pipeline/steps.py`, `README.md`, `METHODOLOGY.md` (new section 6at, output inventory), `docs/PIPELINE.md` (regenerated with `python3 -m pipeline doc`)

- [ ] **Step 1:** Add step `s46`; run `python3 tools/test_pipeline.py` and `python3 -m pipeline doc`.
- [ ] **Step 2:** Write section 6at from the notebook's numbers; add the README row.
- [ ] **Step 3:** Commit and push.
