# Corridor Transit Demand — Decision and Plan (pending train matrix)

*Status: **executed 2026-09-08** in `Transit_complete_matrix.ipynb` (train matrix:
`Input/Matrices/Train_mtx_table.csv`, 2019 smartcards). Outputs under `Output/train/`
and `Output/transit/`. **Rebuilt later the same day** after fixing the RavKav journey
deduplication (`passanger_trip_id` is unique per boarding, `bus_trip_id` is the
linked-journey id; the original build counted every transfer leg as a full journey,
inflating bus OD volumes ×1.52). This document records the decision and its rationale
with the corrected numbers; step 5 (vintage alignment) remains optional and
unexecuted.*

## Decision

For estimating **corridor transit demand**, use the **RavKav × OnBoard bus matrix**
(`Output/bus/bus_od_area_new_filtered.csv`), not THS TRANSIT. The THS all-mode matrix
remains the base for CAR / OTHER and for behavioral context.

### Evidence behind the decision (corrected 2026-09-08)

- **Scale**: with journeys counted once, the two independent sources corroborate each
  other — sub-area totals 23,995 (RavKav×OnBoard) vs 26,247 (THS TRANSIT) avg-weekday
  passengers, ratio 0.91, and the large residential areas sit near parity (Kiryat Yam
  0.96, Kiryat Motzkin-Bialik 0.89, Tirat Carmel 0.99). The substitution is therefore
  scale-neutral; the choice between the sources is about *reliability, frame and
  pattern*, not size.
- **Reliability**: RavKav is a near-census of actual journeys (~550k/day nationally);
  THS TRANSIT rests on ~1,000 sampled transit trips/day expanded ×~150, so individual
  area-to-area cells are statistically thin in the survey but stable in ticketing.
- **Frame and pattern**: r = 0.76 between the sources on area-cell counts (major flows
  agree); divergence concentrates at hubs and boundary areas (Hamifrats: 120 THS vs
  1,079 RavKav; Neve Yosef 1.8×; Kiryat Ata Center 1.9×), where ticketing observes
  transfer-driven and non-resident demand the household frame misses — demand the LRT
  will actually carry. Journey origins are boarding locations, so hub attribution is
  right for corridor loading (see caveats).
- **Growth context**: read as 2018→2022 change, the sub-area ratio is −8.6% total
  (−2.2%/yr) — consistent with 2022 bus ridership still below pre-COVID levels
  (`Output/bus/bus_growth_2018_2022.csv`). The previously reported +6.7% rested on
  the leg-inflated volumes.

## Plan — when the train matrix arrives

1. **Process the train data** with the same treatment as RavKav bus
   (`BusRavKav_matrix.ipynb` as the template): station→TAZ tagging against
   `Input/TAZ_North/TAZ_North.shp`, weekday-3 / hour 6–8 filter, day averaging;
   prefer the same Tuesdays (2022-05-03/17/24/31) if available.
2. **Complete transit matrix** = bus (`bus_od_area_new_filtered.csv`) + train,
   aggregated to the 28 areas of `Input/Submatrix_tazs.xlsx` (noise filter:
   `MIN_ACTIVITY = 50` total daily origins+destinations per area).
3. **Build the adjusted all-mode matrix** at area level, by substitution — not
   averaging:

   ```
   ALL_adjusted = (matrix_avg_ALL_area − matrix_avg_TRANSIT_area − matrix_avg_RAIL_area)
                  + bus_od_area_new_filtered + train_area
   ```

   Survey keeps CAR / OTHER (its only-source components); measured ticketing replaces
   the survey's weakest components (TRANSIT + RAIL).
4. **Produce the mode-share table** per area (and corridor-only, via `IsLRT_Corridor`
   in `area_legend.csv`) from the adjusted matrix.
5. **Optional vintage alignment**: the base is residents-2018, the transit layer
   everyone-2022. If a single-year footing is required, grow CAR/OTHER to 2022 with a
   population-based factor for the Krayot (the bus signal suggests only ~1.6%/yr
   overall); otherwise keep un-grown and state the vintage mix.

## Caveats to carry into the deliverable

- The measured transit layer carries non-residents while the CAR/OTHER base counts
  residents only; overall the adjusted transit share (9.5%) lands slightly *below*
  the survey's own (10.1%) because 2022 ridership sits below the 2018 survey level.
  Document the frame mix rather than reading the share change as behavior.
- RavKav journey origins are **boarding locations**, not doorsteps: right for corridor
  boardings, slightly too concentrated for true door-to-door OD (Neve Yosef's 75%
  "transit share" is the clearest example — three boundary/trunk stops collect
  journeys the survey attributes to neighboring areas).
- Hub areas (Hamifrats and similar) represent transfer-driven demand — real for LRT
  ridership, not trip generation by the hub's land use.
- The OnBoard destination pattern replaced RavKav's inferred alightings (they agree
  only at r ≈ 0.09 at TAZ level); 6.4% of bus volume (uncovered origins) still carries
  RavKav's own inferred destinations.

## Key inputs and outputs referenced

| File | Role |
|---|---|
| `Output/bus/bus_od_area_new_filtered.csv` | Bus transit demand, 25 areas, avg Tuesday 6–9 |
| `Output/ths2017/study_taz/submatrices/matrix_avg_{ALL,TRANSIT,RAIL}_area.csv` | Survey all-mode base and components to subtract |
| `Output/ths2017/study_taz/submatrices/area_legend.csv` | Area names + LRT-corridor flags |
| `Input/Submatrix_tazs.xlsx` | 205-TAZ → 28-area key |
| `BusRavKav_matrix.ipynb`, `BusOnBoard_matrix.ipynb` | Templates for the train processing and combination |
