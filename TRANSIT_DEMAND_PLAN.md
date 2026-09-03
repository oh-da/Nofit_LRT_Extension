# Corridor Transit Demand — Decision and Plan (pending train matrix)

*Status: agreed 2026-09. Execute when the train OD matrix arrives.*

## Decision

For estimating **corridor transit demand**, use the **RavKav × OnBoard bus matrix**
(`Output/bus/bus_od_area_new_filtered.csv`), not THS TRANSIT. The THS all-mode matrix
remains the base for CAR / OTHER and for behavioral context.

### Evidence behind the decision

- **Level**: RavKav is a near-census of actual boardings; THS TRANSIT rests on ~1,000
  sampled transit trips/day expanded ×~150. Their ratio in the sub-area is 1.58
  (41,351 vs 26,247 avg-weekday passengers) and near-uniform 1.5–1.8 across most
  areas — a frame difference (the household survey misses non-residents: soldiers,
  students, visitors) plus 2018-vs-2022 vintage, not survey noise. The LRT will carry
  non-residents, so the ticketing frame is the right frame for demand sizing.
- **Pattern**: r = 0.75 between the sources at area level on counts (major flows agree);
  divergence concentrates in thin cells and at hubs (Hamifrats: 120 THS vs 2,213
  RavKav), where ticketing actually observes the demand.
- **Growth context**: area-wide bus growth 2018→2022 is only +6.7% total (+1.6%/yr);
  the sub-area ratio 1.58 is therefore mostly frame + concentration, not growth
  (`Output/bus/bus_growth_2018_2022.csv`).

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

- The substitution mildly inflates transit share (non-residents enter the transit
  layer but not the CAR/OTHER base) — conservative in the right direction for
  car-to-LRT shift analysis; document it.
- RavKav journey origins are **boarding locations**, not doorsteps: right for corridor
  boardings, slightly too concentrated for true door-to-door OD.
- Hub areas (Hamifrats and similar) represent transfer-driven demand — real for LRT
  ridership, not trip generation by the hub's land use.
- The OnBoard destination pattern replaced RavKav's inferred alightings (they agree
  only at r ≈ 0.13 at TAZ level); 5.5% of bus volume (uncovered origins) still carries
  RavKav's own inferred destinations.

## Key inputs and outputs referenced

| File | Role |
|---|---|
| `Output/bus/bus_od_area_new_filtered.csv` | Bus transit demand, 26 areas, avg Tuesday 6–9 |
| `Output/ths2017/study_taz/submatrices/matrix_avg_{ALL,TRANSIT,RAIL}_area.csv` | Survey all-mode base and components to subtract |
| `Output/ths2017/study_taz/submatrices/area_legend.csv` | Area names + LRT-corridor flags |
| `Input/Submatrix_tazs.xlsx` | 205-TAZ → 28-area key |
| `BusRavKav_matrix.ipynb`, `BusOnBoard_matrix.ipynb` | Templates for the train processing and combination |
