# Driving-licence model — design

16 November 2026. Status: approved and built (step 46, METHODOLOGY §6at).

## Intent

A model that predicts whether a person holds a car driving licence, estimated on the
2017–18 travel habits survey (THS) and applied to the 2040 and 2050 population of the
BU and HS demographic scenarios. The product is the number of licence holders per zone,
sector and age band in each scenario year — an input for later car-ownership or
mode-choice work.

## Goals, non-goals, anti-goals

- **Goal:** a binary logit whose every predictor exists in the 2040 / 2050 zonal files.
- **Goal:** two forecasts side by side — the static cross-section (option 1, lower bound)
  and the cohort carry-forward (option 2, the adopted one).
- **Non-goal:** modelling household cars, employment or education. They are decided
  together with the licence and are not in the forecast files.
- **Non-goal:** a trend in the licence uptake of new cohorts. One survey year cannot
  identify it.
- **Non-goal:** feeding the result into steps 31–45. Nothing downstream changes.
- **Anti-goal:** a model that fits 2017 well through variables that cannot be forecast.

## Data

| File | Use |
|---|---|
| `Input/THS_2017-2018/PersonsFin2.csv` | `license_car` (dependent), `Age`, `Gender`, `Hhtype`, `HHID`, `TAZ` |
| `Input/Matrices/households_with_weights.csv` | `wf_new`, the household expansion weight |
| `Input/Zonal_2020.csv` | zone attributes for estimation: `SOCECO`, `SETTL_SIZE`, `TABAAT` |
| `Input/Demographic_Forecast/Zonal_{BU,HS}_{2040,2050}.csv` | application: `AGE_<band>_{REST,ARA,ORT}` per zone, and the same zone attributes |

Estimation sample: persons aged 17 and over with a licence answer and a known gender —
about 10,900 persons in 5,098 households (licence rate 70.6 %). Persons under 17 are
given probability zero (the survey: 0.7 % at 16).

## Approaches considered

1. **Static cross-section** — the 2017 logit applied directly to the 2040 / 2050 cells.
   Simple, but it treats a generation effect as an ageing effect: Arab women are 77 %
   licensed at 30–35 and 25 % at 55–64 in the survey, and the 30–35 group will be 53–58
   in 2040. Kept as the lower bound.
2. **Cohort carry-forward — chosen.** The same logit; each birth cohort keeps the rate
   it has reached. Chosen because the licence, once obtained, is kept, and the forecast
   years are 23 and 33 years out — longer than the generation gap in the data.
3. **Cohort plus an uptake trend** — rejected as a main result: the trend would be an
   outside assumption, not an estimate.

## The model

Binary logit, weighted by `wf_new` (normalised to the sample size), standard errors
clustered on the household.

- **Age:** piecewise-linear spline, knots at 19, 26, 36, 65 and 75. The first four are
  the forecast's band limits; 75 is added for the old-age decline.
- **Gender**, and gender × age.
- **Sector** in the forecast's three groups: Arab; Haredi (`orto`); rest (`secular`,
  `religious`, `other`). Sector × gender, and sector × age where the data supports it.
- **Zone:** socio-economic index, settlement size, ring.

Specification search: a ladder from main effects to the full interaction set, compared
by likelihood-ratio test, AIC and BIC; a term stays if it is significant or needed for
the calibration of a forecast cell. The Haredi cells are thin (about 20–50 persons per
age band and gender), so Haredi × age terms are the first to be pooled.

Validation:
- five-fold cross-validation with whole households held out (AUC, log-loss);
- observed against predicted rate for every age band × gender × sector cell;
- the model applied to the 2020 zonal file against the survey's weighted total.

## Application

For each zone, sector and age band of a scenario year:

- **Single years of age within a band:** the survey's weighted distribution for that
  band and sector (this also gives the share of the 8–18 band that is 17–18).
- **Gender:** the survey's weighted split for that band and sector.
- **Static rate:** the model's probability at age *a*, `p(a)`.
- **Cohort rate.** With *a0* = *a* − (year − 2017), the cohort's age in the survey year:
  - *a* < 30: `p(a)` — young people are still acquiring; the uptake profile is unchanged.
  - *a* ≥ 30 and *a0* ≥ 30: `p(a0) × keep(a) / keep(a0)` — the rate the cohort had in 2017.
  - *a* ≥ 30 and *a0* < 30: `S × keep(a)`, with `S` the model's mean rate at 30–39 for
    that gender, sector and zone.
  - `keep(a)` is the giving-up curve: 1 up to 65, then the ratio of the model's rate at
    *a* to its rate at 65 for men of the rest sector. Their licence rate has been near
    saturation for decades (0.92 at 36–64 in the survey), so their decline after 65 is
    read as giving up, not generation, and is applied to every group.

Sensitivity runs of the cohort forecast: the saturation window (26–35 against 30–39) and
no giving-up at all.

## Deliverables

- `notebooks/current/Driving_licence_model.ipynb` — step 46, executed and committed.
- `Output/licence_model/`: coefficient table, specification ladder, validation tables,
  licence holders per zone × sector × age band for 2020 and each scenario year under
  both methods, a summary by sector, figures.
- `METHODOLOGY.md` section 6at, a README row, a `pipeline/steps.py` entry.
- `statsmodels` is already in the pipeline's package list.

## Calls made here (not decided in conversation)

- Age 17 as the lower limit; under-17s at zero.
- The three-sector grouping, forced by the forecast files.
- Gender in the model, applied with the survey's split because the forecast has none.
- The spline knots, the 30–39 saturation window and the giving-up curve from rest-sector
  men.
- Zone attributes are those of the forecast zone; people who move take the zone's
  attributes, not their own history.
- Step number 46, section 6at, output folder `Output/licence_model/`.

## Left to the builder

The final interaction set (by the tests above), figure design, table layouts.

## Changes made while building

- The Arab × age terms use a reduced curve (knots 26, 36, 65): the full curve separated.
- Settlement size was tested and left out (Wald p = 0.40); the zone terms are the index, the
  ring and index × sector.
- The giving-up curve is evaluated in each zone, not at one reference zone, so that the cohort
  rate of rest-sector men aged 65+ in 2017 equals their static rate.
- A third sensitivity run was added: late acquisition (the larger of cohort and static).
- A fixed 20 % of households is held out, in addition to the five-fold cross-validation, and the
  model-against-data charts are drawn for both (requested during the build).

## Revision of the cohort rule (16 November 2026, after the first results)

Decided in conversation: **a licence, once obtained, is not given up**, and the peak of each
sector and gender is used for the generations that have not reached it. The adopted rule is now
`lm.peak_rate`: a cohort holds the highest rate of the 2017 profile between its age in 2017 and
its age in the forecast year. The giving-up curve and the 30–39 saturation window described
above are no longer the adopted rule; they remain as two sensitivity runs. The "late
acquisition" run is dropped, because the adopted rule already contains it.
