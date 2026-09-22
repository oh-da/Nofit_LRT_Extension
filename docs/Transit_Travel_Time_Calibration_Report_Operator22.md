**Transit In-Vehicle Travel Time  
Calibration Report**

OperatorRef 22 \| Underground vs other operating sections

Updated calibration using all Thursday observations in the supplied extract

| **Source file**          | New_Query_2026_09_17_15_46_30 (1).csv            |
|--------------------------|--------------------------------------------------|
| **Coverage**             | 25 May 2023 to 10 Sep 2026 (132 Thursdays)       |
| **Source rows**          | 1,078,845 stop records                           |
| **Journey groups**       | 36,939 date-line-journey combinations            |
| **Lines**                | 34447, 34448                                     |
| **Calibration sample**   | 26,653 clean complete journeys; 799,590 sections |
| **Modelling assumption** | 500 m fixed distance between consecutive stops   |

| **T_trip \[min\] = 1.961 × N_UG + 2.393 × N_Other** |
|-----------------------------------------------------|

**Equivalent commercial speeds: 15.30 km/h underground \| 12.54 km/h other**

# 1. Executive summary

This report recalibrates a model-ready transit in-vehicle travel-time function for OperatorRef 22 using the expanded Thursday sample supplied by the user. The source contains 1,078,845 stop observations across 132 Thursdays. After requiring a canonical 31-stop journey and applying timing QA, 26,653 complete journeys remain, providing 799,590 usable stop-to-stop sections.

| **T_trip = 1.960792 × N_UG + 2.392690 × N_Other** |
|---------------------------------------------------|

The calibrated underground coefficient is 1.961 min per 500 m section and the other-section coefficient is 2.393 min per 500 m section. Under the fixed 500 m spacing assumption these correspond to commercial speeds of 15.30 km/h and 12.54 km/h respectively. Underground sections therefore take 18.1% less time per model section.

| **Measure**                                | **Updated result** |
|--------------------------------------------|--------------------|
| Valid complete journeys                    | 26,653             |
| Usable stop-to-stop sections               | 799,590            |
| Underground sections                       | 239,877            |
| Other sections                             | 559,713            |
| Mean observed complete-trip time           | 67.89 min          |
| Model complete-trip time (9 UG + 21 other) | 67.89 min          |
| Trip-level MAE                             | 3.67 min           |
| Trip-level MAPE                            | 5.45%              |

# 2. Data and preprocessing

## 2.1 Supplied extract

The updated CSV contains 1,078,845 stop-level records for LineRef 34447 and 34448. Every record date is a Thursday, consistent with Spark/Databricks WEEKDAY(...)=3. The extract covers 25 May 2023 through 10 September 2026, comprising 132 observed Thursdays and 36,939 date-line-journey groups.

| **Field**                    | **Role in calibration**                                                       |
|------------------------------|-------------------------------------------------------------------------------|
| trip_date                    | Separates repeated journey identifiers across operating days                  |
| LineRef                      | Direction / line identifier                                                   |
| DatedVehicleJourneyRef       | Journey identifier within the operating date                                  |
| Order                        | Stop sequence used to test journey completeness                               |
| StopPointRef / previous_stop | Used to classify each stop-to-stop section                                    |
| minutes_from_previous_stop   | Primary calibration dependent variable                                        |
| avg_velocity                 | Supporting AVL velocity indicator; not the model commercial-speed coefficient |
| total_trip_minutes           | Trip-level validation field                                                   |

## 2.2 Underground classification

A stop-to-stop section is classified as Underground only when both the previous stop and current stop are in the supplied underground-stop list. A transition section with only one underground endpoint is classified as Other. This conservative rule prevents portal/transition links from being assigned the fully underground operating coefficient.

## 2.3 Journey completeness and timing QA

The larger dataset contains partial journeys, duplicated/incomplete sequences and non-physical AVL timing intervals. Calibration therefore uses a reproducible trip-level screening procedure.

| **QA step**                                                  | **Trips / effect** |
|--------------------------------------------------------------|--------------------|
| All date-line-journey groups                                 | 36,939             |
| Canonical complete trips: exactly 31 rows, unique Order 1–31 | 28,299             |
| Trips containing non-positive section time                   | 928                |
| Trips containing section time \> 10 min                      | 1,014              |
| Overlap between the two timing-failure rules                 | 296                |
| Trips excluded by timing QA (union)                          | 1,646              |
| Final clean complete trips                                   | 26,653             |

The 10-minute maximum is a pragmatic AVL quality threshold for a nominal 500 m inter-stop model section. It removes severe timestamp gaps while retaining the operational distribution of normal and congested running times. No valid canonical trips from the isolated 2023 source date survive the completeness/QA criteria; the effective calibration period is therefore 2024–2026.

# 3. Calibration methodology

## 3.1 Segment-level model

Because the modelling assumption fixes each stop-to-stop section at 500 m, the calibration can be expressed directly in elapsed minutes per section. For section s:

| **t_s = β_UG × I_UG,s + β_Other × I_Other,s + ε_s** |
|-----------------------------------------------------|

I_UG,s and I_Other,s are mutually exclusive regime indicators. With no global intercept, least-squares calibration is equivalent to the arithmetic mean observed elapsed time within each regime. The mean is used rather than the median because the objective is to reproduce expected aggregate travel time in the transport model.

## 3.2 Trip-level formulation

| **T_trip = β_UG × N_UG + β_Other × N_Other** |
|----------------------------------------------|

N_UG and N_Other are counts of stop-to-stop sections. For a path with N stops, N_UG + N_Other = N - 1.

## 3.3 Conversion to model commercial speed

For a fixed 0.5 km section, equivalent commercial speed is V = 0.5 / (t/60) = 30/t. This is a path-time equivalent speed and includes the elapsed time embodied in the observed stop-to-stop interval; it should not be interpreted as unconstrained vehicle running speed.

# 4. Calibration results

<table>
<colgroup>
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>Regime</strong></th>
<th><strong>n</strong></th>
<th><strong>Mean time<br />
(min)</strong></th>
<th><strong>Median<br />
(min)</strong></th>
<th><strong>SD<br />
(min)</strong></th>
<th><strong>95% CI mean<br />
(min)</strong></th>
<th><strong>Recorded avg_velocity<br />
(km/h)</strong></th>
<th><strong>Model commercial speed*<br />
(km/h)</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Underground</td>
<td>239,877</td>
<td>1.961</td>
<td>1.800</td>
<td>0.592</td>
<td>1.958–1.963</td>
<td>28.15</td>
<td>15.30</td>
</tr>
<tr class="even">
<td>Other</td>
<td>559,713</td>
<td>2.393</td>
<td>2.133</td>
<td>1.019</td>
<td>2.390–2.395</td>
<td>15.48</td>
<td>12.54</td>
</tr>
</tbody>
</table>

\*Model commercial speed assumes exactly 500 m between consecutive stops. Recorded avg_velocity is a separate source field and is shown only as corroborating operating evidence.

<img src="media/image1.png" style="width:6.6in;height:3.6in" />

*Figure 1. Calibrated mean elapsed time per 500 m section. Error bars show 95% confidence intervals for the sample mean.*

The underground coefficient is 1.961 min per section versus 2.393 min for other sections. The time saving is 18.1% per 500 m model section. The source avg_velocity field also shows materially higher velocities underground (28.15 km/h vs 15.48 km/h), supporting the regime split, although that field is not used to derive the final coefficients.

## 4.1 Temporal stability

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>Year</strong></th>
<th><strong>Underground<br />
min/section</strong></th>
<th><strong>Other<br />
min/section</strong></th>
<th><strong>Valid trips</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>2024</td>
<td>2.007</td>
<td>2.528</td>
<td>9,482</td>
</tr>
<tr class="even">
<td>2025</td>
<td>1.946</td>
<td>2.365</td>
<td>10,752</td>
</tr>
<tr class="odd">
<td>2026</td>
<td>1.919</td>
<td>2.240</td>
<td>6,419</td>
</tr>
</tbody>
</table>

<img src="media/image2.png" style="width:6.6in;height:3.59118in" />

*Figure 2. Mean stop-to-stop elapsed time by year for clean complete Thursday journeys.*

Both regimes show improving observed travel times over the calibration period. This means the full-period coefficients represent an average of 2024–2026 operating conditions. If the modelling base year is intended to reproduce current 2026 operations specifically, a year-specific calibration may be preferable; for a stable general-purpose coefficient, the full-period estimate is retained as the recommended default.

# 5. Trip-level validation

All clean complete journeys contain 30 stop-to-stop sections: 9 underground and 21 other. Consequently, the two-regime model predicts the same canonical complete-trip time for each journey. Validation therefore tests how well that fixed expected travel time represents the observed day-to-day and trip-to-trip distribution.

| **T_complete = 9 × 1.960792 + 21 × 2.392690 = 67.89 min** |
|-----------------------------------------------------------|

| **Metric**               | **Result** |
|--------------------------|------------|
| Clean complete trips     | 26,653     |
| Observed mean            | 67.89 min  |
| Observed median          | 68.47 min  |
| Predicted canonical trip | 67.89 min  |
| MAE                      | 3.67 min   |
| RMSE                     | 4.39 min   |
| MAPE                     | 5.45%      |

<img src="media/image3.png" style="width:6.6in;height:3.59118in" />

*Figure 3. Distribution of observed complete-trip times compared with the model prediction.*

| **LineRef** | **Trips** | **Observed mean** | **Observed median** | **Predicted** | **MAE** | **MAPE** |
|-------------|-----------|-------------------|---------------------|---------------|---------|----------|
| 34447       | 13,765    | 68.92             | 69.10               | 67.89         | 3.66    | 5.27%    |
| 34448       | 12,888    | 66.80             | 67.77               | 67.89         | 3.68    | 5.64%    |

<img src="media/image4.png" style="width:6.6in;height:3.59118in" />

*Figure 4. Mean observed versus predicted complete-trip time by LineRef / direction.*

The model is calibrated to the pooled mean and reproduces the overall observed mean (67.89 min) by construction. Direction-specific means differ: LineRef 34447 is slower on average, while 34448 is faster. A future refinement could introduce direction or time-period factors if the transport model needs that additional fidelity.

# 6. Final model-ready formulation

Recommended implementation for the current model assumption of fixed 500 m spacing:

| **T_trip \[min\] = 1.960792 × N_UG + 2.392690 × N_Other** |
|-----------------------------------------------------------|

| **Model parameter**                     | **Value**                                                    |
|-----------------------------------------|--------------------------------------------------------------|
| Underground section time                | 1.961 min per 500 m                                          |
| Other section time                      | 2.393 min per 500 m                                          |
| Underground equivalent commercial speed | 15.30 km/h                                                   |
| Other equivalent commercial speed       | 12.54 km/h                                                   |
| Classification rule                     | Underground only when both section endpoints are underground |

Equivalent distance form, where D is measured in kilometres:

| **T_trip \[min\] = 3.921585 × D_UG + 4.785381 × D_Other** |
|-----------------------------------------------------------|

Equivalent speed form:

| **T_trip \[min\] = 60 × D_UG / 15.30 + 60 × D_Other / 12.54** |
|---------------------------------------------------------------|

Worked example — 5 stops with 3 underground sections and 1 other section: T = 3×1.961 + 1×2.393 = 8.28 min. The assumed path length is 2.0 km, giving an overall commercial speed of 14.50 km/h.

# 7. Change from the preliminary calibration

The earlier report was based on a very small one-day sample. The expanded Thursday dataset materially reduces sampling risk and replaces those preliminary coefficients.

| **Parameter**             | **Preliminary** | **Updated** | **Change** |
|---------------------------|-----------------|-------------|------------|
| Underground min/section   | 2.171           | 1.961       | -9.7%      |
| Other min/section         | 2.824           | 2.393       | -15.3%     |
| Underground speed @ 500 m | 13.82 km/h      | 15.30 km/h  | 10.7%      |
| Other speed @ 500 m       | 10.62 km/h      | 12.54 km/h  | 18.0%      |

The updated coefficients are recommended for model implementation because they are based on tens of thousands of clean journeys rather than a handful of sampled trips.

# 8. Limitations and recommended future refinement

- The 500 m section length is a modelling assumption. Actual station spacing varies, so the coefficients should be interpreted as equivalent model-link times rather than measured physical running speeds.

- The sample is Thursday-only. Day-of-week effects are intentionally excluded from this calibration.

- All valid canonical trips have the same 9 underground + 21 other section structure, so the two coefficients are identified from segment-level observations rather than variation in trip-level regime counts.

- The 10-minute segment threshold is a QA rule. Sensitivity testing with alternative thresholds can be performed if the model requires a different treatment of severe disruption.

- Observed section times improve from 2024 to 2026. If a specific base year is required, year-specific coefficients should be estimated rather than applying the pooled average.

- A stronger future specification would retain actual inter-stop distance and estimate running-time and stop/dwell components separately, potentially by direction and time period.

# Appendix A. Underground stop definition

The following stop list was supplied by the user. A section is classified as Underground only when both consecutive endpoints are in this list.

| **StopPointRef** | **StopName**   | **IsUnderground** |
|------------------|----------------|-------------------|
| 20707            | יהודית         | 1                 |
| 20709            | שאול המלך      | 1                 |
| 20711            | ארלוזורוב      | 1                 |
| 20713            | אבא הילל       | 1                 |
| 20715            | ביאליק         | 1                 |
| 20717            | בן גוריון      | 1                 |
| 20719            | אהרונוביץ'     | 1                 |
| 20724            | גשר אם המושבות | 1                 |
| 20705            | קרליבך         | 1                 |
| 20703            | אלנבי          | 1                 |
| 20701            | אליפלט         | 1                 |

# Appendix B. Updated source-data inventory

The updated source CSV contains 1,078,845 rows, which is too large to reproduce row-for-row inside a practical Word report. The CSV remains the authoritative raw appendix. This appendix records its schema, coverage and a representative sample so that the calibration is auditable without inflating the report to more than a million table rows.

| **Year** | **Observed Thursdays** | **Source rows** |
|----------|------------------------|-----------------|
| 2023     | 1                      | 52              |
| 2024     | 48                     | 396,853         |
| 2025     | 51                     | 413,801         |
| 2026     | 32                     | 268,139         |

Source columns: trip_date, LineRef, DatedVehicleJourneyRef, Order, StopPointRef, stop_time, previous_stop, previous_stop_time, minutes_from_previous_stop, avg_velocity, n_stops, total_trip_seconds, total_trip_minutes.

| **trip_date** | **LineRef** | **JourneyRef** | **Order** | **StopPointRef** | **Δt min** | **Trip min** |
|---------------|-------------|----------------|-----------|------------------|------------|--------------|
| 2023-05-25    | 34447       | 0              | 2         | 35975            |            | 25.75        |
| 2023-05-25    | 34447       | 0              | 3         | 35988            | -2.00      | 25.75        |
| 2023-05-25    | 34447       | 0              | 4         | 36065            | -9.50      | 25.75        |
| 2023-05-25    | 34447       | 0              | 7         | 36250            | -0.75      | 25.75        |
| 2023-05-25    | 34447       | 0              | 9         | 36304            | -6.75      | 25.75        |
| 2023-05-25    | 34447       | 0              | 10        | 20362            | -3.50      | 25.75        |
| 2023-05-25    | 34447       | 0              | 12        | 20375            | -3.25      | 25.75        |
| 2023-05-25    | 34447       | 0              | 13        | 20399            | 9.25       | 25.75        |
| 2023-05-25    | 34447       | 0              | 14        | 20451            | -9.25      | 25.75        |
| 2023-05-25    | 34447       | 0              | 15        | 20546            | 9.25       | 25.75        |
| 2023-05-25    | 34447       | 0              | 17        | 20703            | -4.00      | 25.75        |
| 2023-05-25    | 34447       | 0              | 18        | 20705            | 2.00       | 25.75        |
| 2023-05-25    | 34447       | 0              | 19        | 20707            | -7.25      | 25.75        |
| 2023-05-25    | 34447       | 0              | 20        | 20709            | 0.75       | 25.75        |
| 2023-05-25    | 34447       | 0              | 21        | 20711            | 2.50       | 25.75        |
| 2023-05-25    | 34447       | 0              | 22        | 20713            | 2.00       | 25.75        |
| 2023-05-25    | 34447       | 0              | 23        | 20715            | -5.25      | 25.75        |
| 2023-05-25    | 34447       | 0              | 24        | 20717            | 0.00       | 25.75        |
| 2023-05-25    | 34447       | 0              | 25        | 20718            | 6.75       | 25.75        |
| 2023-05-25    | 34447       | 0              | 28        | 36309            | 17.50      | 25.75        |

*Table B-1. First 20 sorted raw source records, illustrating the unfiltered AVL data and the need for QA. Full source data remain in the supplied CSV.*

# Appendix C. Reproducible calibration rules

| **Item**              | **Rule**                                                         |
|-----------------------|------------------------------------------------------------------|
| Operating-day filter  | All supplied rows are Thursday observations (Spark WEEKDAY = 3). |
| Trip key              | trip_date + LineRef + DatedVehicleJourneyRef                     |
| Complete journey      | Exactly 31 rows; Order unique and spanning 1 through 31          |
| Segment rows          | Order \> 1, producing 30 stop-to-stop sections per complete trip |
| Timing QA             | Every section time must be \> 0 and \<= 10 min                   |
| Underground segment   | previous_stop and StopPointRef both in Appendix A list           |
| Coefficient estimator | Arithmetic mean minutes_from_previous_stop within regime         |
| Trip prediction       | Sum regime coefficient across all sections                       |
| Distance assumption   | 0.5 km per section                                               |
