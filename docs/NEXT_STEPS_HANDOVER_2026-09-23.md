# Handover — the next steps, in detail (written 23 September 2026)

This document is for whoever picks up the work next, human or model. It is self-contained:
part A says how this repository is worked (conventions that every step must follow), part B
says where the model stands today, part C specifies each next step — inputs by exact path,
method, outputs by exact path, acceptance checks, and the documents to update — and part D gives
the order and the standing data requests. Read `METHODOLOGY.md` §0 first; it is the authoritative
status page and the lineage of every product. Step numbers, section letters and caveat numbers
below continue the ones used there: **the next step is 37, the next methodology section is
§6ai, the next caveat is 19.**

---

## A. How this repository is worked

### A1. Repository layout and the chain

- `Input/` — raw inputs. **Every file directly under `Input/` and in most sub-folders is a Git
  LFS pointer** (`.gitattributes`); the few committed CSV substitutes are listed there with
  `-filter`. `Output/` — every product, committed as ordinary files (no LFS). `notebooks/current/`
  — the chain, one notebook per step; `notebooks/diagnostics/` — tests and validations;
  `notebooks/historical/` — superseded work, never edited. `docs/` — plans, tasks, the
  plain-English companion. `reports/` — the two Word reports. `tools/lfs_pull.py` — see A3.
- The chain and its order are in `METHODOLOGY.md` §9 ("Reproduction"). Every notebook starts
  with `while not os.path.exists('METHODOLOGY.md'): os.chdir('..')`, so it runs from the
  repository root wherever it is launched. Steps that feed each other: 15 → 16 → 17/18/20/22 →
  23 → 27 → 24 → 28; 29 → 30 → 26 → 31 → 32; 33 stands alone; 34 → 35; 36 stands alone.
  Changing anything in 25 / 26 / 31 / 32 needs only `25 → 26 → 31 → 32` rerun (≈ 10 minutes).
- Execution: `MPLBACKEND=Agg jupyter nbconvert --to notebook --execute --inplace
  --ExecutePreprocessor.timeout=3000 notebooks/current/<name>.ipynb`. Long chains go in a
  background shell script that appends `=== START/OK/FAILED <notebook>` lines to a log; watch the
  log rather than blocking the session. Executed notebooks (with outputs) are committed.

### A2. Writing a new step

- Author the step as a script with `# %%` / `# %% [markdown]` cell markers, convert it to a
  notebook with `nbformat` (see any recent step: markdown cells explain purpose, method, results
  and limits in full sentences; the first markdown cell states the question), execute it in
  place, then commit the executed notebook. Keep the script in a scratch folder, not the repo.
- Style of the existing notebooks: pandas + numpy + matplotlib (`Agg`), geopandas 1.1 for
  geometry (EPSG:2039, Israel TM Grid, for every distance), the palette
  `BLUE '#2a78d6', ORANGE '#eb6834', AQUA '#1baf7a', PURPLE '#7b5bd6', INK '#0b0b0b'`, figures to
  `Output/figures/<step-slug>_*.png` at 150 dpi, CSV outputs with `float_format`.
- **Library pitfalls met so far (pandas 3.0.6):** `DataFrame.stack(dropna=False)` is gone — use
  `MultiIndex.from_product` + `reindex`; `groupby(...).apply` drops the grouping column — iterate
  groups; `read_excel` needs `engine='openpyxl'` for the `.xlsx` inputs; statsmodels cluster-robust
  errors with `var_weights` are wrong — compute the sandwich by hand (step 33 has the class);
  geopandas `unary_union` is deprecated → `union_all()`; shapefile Hebrew names in
  `Input/Network_with_Counts` read correctly with `encoding='utf-8'`; `kill` background jobs by
  PID, never `pkill -f` (it kills the session shell).
- Every number printed by a notebook that is quoted in a document must come from the executed
  notebook or its CSV outputs, never from memory.

### A3. LFS inputs without the git-lfs client

The remote environment has no `git-lfs`. `python3 tools/lfs_pull.py Input/<path>` fetches the
object of a pointer file from GitHub's LFS batch API, verifies the sha256 and writes it in place.
Pull only what the step needs (`Input/BusRavKav/2025/*` alone is 2.3 GB; the north stops file
946 MB). **Before every commit run `git checkout -- Input/ && git clean -fdq Input/`** so the
pointers are restored: with no LFS filter installed, `git add` of a pulled file would commit its
content as a plain blob. Keep pulled copies in the scratch folder if a rerun is likely.

Which inputs each step needs is stated at the head of its §9 line. In short: steps 15–33 need
`Input/THS_2017-2018/*.xlsx`, `Input/Submatrix_tazs.xlsx`, `Input/TAZ_2636_Keys.xlsx`,
`Input/6_9_BusProbability_ByTAZ.xlsx`, `Input/Corridor_TAZ_Agg_V2.xlsx`; step 23 the
`Input/Demographic_Forecast/Zonal_*.csv`; steps 29–30 the GTFS zip and
`Input/BusSpeedData/std_202605.csv`; step 34 the three 2025 RavKav files and the north stops file;
step 36 `Input/Network_with_Counts/*`.

### A4. Documentation that every step updates (no exceptions)

1. `METHODOLOGY.md`: a new section `§6ai. Step 37 — …` before `## 7.` (purpose, method, results
   with the actual numbers, outputs by path, limits); an **"Update, <date> (step 37 — …)"**
   paragraph in §0 after the last update paragraph; new rows in the §0 conclusions table when the
   step changes a headline quantity; a row in the §0 product table (`| Product | Built by | … |`)
   and, for a new input, in the §1 input table; a numbered caveat in §8 for anything left open;
   the execution line in §9. When a step changes numbers that earlier sections quote, correct
   those sections and say in brackets what the value was and why it moved (see §6m, §6n, §6z for
   the pattern), and repoint the plans (`docs/PLAN_TIGHTENING_AND_SCENARIOS.md`,
   `docs/LRT_CAPTURE_PLAN.md`) and task list (`docs/CORRIDOR_DEMAND_TASKS.md`, tick the item and
   write the result under it in italics).
2. `README.md`: a sentence in the status paragraph, a row in the notebook table, the `git lfs
   pull` line for any new input, the mermaid node when the step joins the chain.
3. `docs/PLAIN_ENGLISH_METHODOLOGY.md`: a new sub-section in **Part 5** (5.x) in plain language —
   what was done, what came out, what it means — and the "Where things stand now" sub-section
   moved to the end and refreshed.
4. The two reports under `reports/` are **not** rewritten per step; they carry a dated revision
   note at the top (python-docx; the pattern is in the 23 September notes) when a headline
   quantity they print changes. Bump their revision number (next: 2.3 and 1.5).

### A5. Git

- Work on the branch given for the session; `git push -u origin <branch>`; never push
  elsewhere. Commit executed notebooks, outputs and docs together, with a message that says what
  changed and why, in plain words. The commit trailer lines required by the session apply; **no
  model identifiers anywhere in the repository** (commit messages, docs, notebooks).
- A stop hook requires a clean tree: commit before ending, after restoring the Input pointers.
- Merged pull requests are finished; follow-up work starts from the latest `main`.

---

## B. Where the model stands (23 September 2026, evening)

All values are in `METHODOLOGY.md` §0 (headline table) and are reproduced by the committed
notebooks. In one paragraph: the base is a survey-only 2022 layer set (car 1,353,798; bus
117,961 calibrated to the May 2022 RavKav journeys on RavKav's own alightings; taxi-type 9,451;
rail 4,050; AM 06:00–09:00, 778 TAZs). The corridor is analysed on the V2 aggregation (25 areas,
trunk + three branches). The LRT capture (step 31, nested incremental logit pivoted on the 2022
transit share, λ = 0.03 assumed and supported by the person-level 0.035 of step 33, λ_T = 2λ,
premium 5, free LRT–Metronit transfer) is **4,250 trips 06:00–09:00 all-underground / 3,207
all-ground / 5,095 in the 50 km/h design regime**, growing to 5,390–6,516 on the 2040 / 2050 sets.

The open items the next steps address, with their caveat numbers in §8:

| Open item | Caveat | What closes it |
|---|---|---|
| Car skims are 2017/18 survey door-to-door times; no 2026 uplift | §6x, task E5 | Google Distance Matrix sample (C1) |
| Station access is straight-line × 1.3, population-weighted per area | task E6 | OSM walking network (C2), TAZ-level capture (C3) |
| Bus generalized cost misses a ≈ 9-minute door-to-door overhead | §6x addendum, task E3 | wait = best-line headway + overhead (C4) |
| LRT regime: only pure underground / pure ground / 50 km/h ceiling | §6w | mixed alignment + acceleration allowance, headway 7.5 / 10 (C5) |
| 15 of 25 areas reach the LRT by a synthetic feeder | task E1 | synthetic branch alignments (C6) until drawings arrive |
| Capture assumes full bus competition | task S3 | truncated-feeder scenario (C7) |
| One central case with whiskers, no designed uncertainty | task C3 | factorial experiment (C8) |
| 2025 RavKav has no alightings of its own; base not re-anchored | 16, §6af | card-level journey chaining (C9) |
| Car layer checked on cordons only, 40–85 % imputed on four of six | §6ah, task B1 | all-or-nothing assignment link check (C10) |
| Survey departure profile peakier than road and fare gates | 18 | count / boarding-based design-hour factors as the carried case (C11) |
| Nazareth branch: the two alighting inferences differ 13 × | 17 | a bus passenger count (data request) |
| Choice-rider λ, λ_T, premium not identified | 15 | stated-preference survey (data request) |

---

## C. The steps, in order

Each step: **Goal · Inputs · Method · Outputs · Checks · Documents · Effort.** Paths are exact.
"Area" means one of the 25 V2 areas (`AggCode` in `Input/Corridor_TAZ_Agg_V2.xlsx`, sheet
`AreaCodes`; the TAZ → area key is sheet `TazAgg`; the ten trunk station areas are 201–210). The
step-31 skims are in `Output/skims/skim_{mode}_{component}.csv` (25 × 25, modes `car`, `bus`,
`brt`, `lrt_all_underground`, `lrt_all_ground`, `lrt_design_50kmh`; components `ivt`, `walk`,
`wait`, `transfers`, `gc`, `status`) and in long form `Output/skims/skims_area_v2_long.csv`.
Generalized cost everywhere is `GC = IVT + 2·walk + 2·wait + 8·transfers` (money out by
decision; constants at the top of steps 26 and 31).

### C1. Step 37 — Car travel times from the Google Distance Matrix API (task E5)

**Goal.** A 2026 car in-vehicle time per area pair for the AM peak, to (a) measure the uplift on
the 2017/18 survey door-to-door times that step 26 uses as the car skim and (b) run the capture
on the uplifted skim.

**Inputs.** `Output/gc/car_ivt_survey_area_v2.csv` (survey car IVT, 25 × 25, the current skim) and
`Output/gc/car_ivt_n_sampled_area_v2.csv` (its sample sizes); `Input/Corridor_TAZ_Agg_V2.xlsx`;
`Input/TAZ_North/TAZ_North.shp` (TAZ polygons, EPSG:2039) and `Input/Zonal_2020.csv` (cp1255;
population and employment per TAZ) for the representative points; an API key in the environment
variable `GOOGLE_MAPS_API_KEY` (never in the repository).

**Method.**
1. One representative point per area: the population-weighted centroid of its TAZs (employment-
   weighted for the pure-employment areas Matam-NeotPeres, Bazan-Hutsot, Namal-Giborim), snapped
   to the nearest road by the API itself. Save the points (`Output/gc/google_dm_area_points.csv`,
   WGS 84 lat/lon).
2. Query all 600 off-diagonal pairs: 25 requests of one origin × 25 destinations (Distance Matrix
   allows 25 destinations and 100 elements per request), `mode=driving`,
   `departure_time` = the next Tuesday 07:30 Israel time (as a Unix timestamp; the API only
   accepts future times), `traffic_model=best_guess`; read `duration_in_traffic` and
   `distance`. Repeat once for 07:45 and once for 22:00 (free flow) — three sweeps, 1,875
   elements, well under a dollar of quota at 2026 prices. Cache every raw response as JSON
   under `Output/gc/google_dm_raw/` so the step reruns without the key.
3. Build `car_ivt_google_area_v2.csv` (mean of the two peak sweeps), `car_ivt_google_freeflow_area_v2.csv`,
   `car_km_google_area_v2.csv`. Compare with the survey skim pair by pair: ratio Google ÷ survey
   by centroid-distance band (< 3, 3–6, 6–10, 10–20, > 20 km) and for the 90 trunk pairs,
   trip-weighted by the 2022 car flows (`Output/skims/pair_flows_and_skims_2022.csv`). Note that
   the survey time is door-to-door (includes parking and walking) and the API time is kerb to
   kerb, so expect Google below survey on short pairs and a peak ÷ free-flow ratio of 1.3–1.8 on
   the trunk.
4. Add a switch `CAR_SOURCE = 'survey' | 'google'` at the top of step 26
   (`GC_data_inventory_and_skims.ipynb`): with `google`, car IVT = Google peak time + a fixed
   terminal allowance (parking + walk, 3 minutes, stated) and the survey time is kept as the
   check. Rerun 26 → 31 → 32 with `google` and report the capture beside the central case.
   Do not make `google` the default until the user decides; save the alternative outputs under
   `Output/skims/car_google/` rather than overwriting.

**Outputs.** `Output/gc/google_dm_area_points.csv`,
`car_ivt_google_area_v2.csv`, `car_ivt_google_freeflow_area_v2.csv`, `car_km_google_area_v2.csv`,
`car_google_vs_survey_pairs.csv`, `car_google_vs_survey_summary.csv`; the alternative-skim run
under `Output/skims/car_google/` (same file names as step 31 / 32); figure
`Output/figures/car_google_vs_survey.png`.

**Checks.** Every pair returns a status `OK`; symmetric pairs differ by less than 30 %; the
free-flow sweep is below the peak sweep on at least 90 % of pairs; the trunk-pair ratio to the
survey is reported with the survey's sample size beside it.

**Documents.** §6ai; §0 update paragraph and a headline row "car time uplift 2017/18 → 2026";
§6x addendum stating the switch; task E5 ticked; plain-English 5.x. Effort: half a day.

**Status, 23 September 2026 — attempted, blocked and partly amended.** No `GOOGLE_MAPS_API_KEY`
is available in this environment and none was fabricated; the user decided to skip the API
queries for now rather than substitute another source. Part 1 (representative points) was
built and verified without the key — 25 areas, 174 TAZs join cleanly against `TAZ_North.shp`
and `Zonal_2020.csv` with no missing geometry or population/employment; TsometKiryatAta (212)
has zero resident and zero job population (a junction area) and falls back to an unweighted
centroid of its 3 TAZs, flagged in the output rather than silently weighted by zero — but the
points were not committed, since the step is not otherwise executable and a partial output would
misstate progress. **The raw-response caching in step 2 above is superseded by the user's
decision the same day: do not commit raw Google API JSON to this public repository (Maps
Platform ToS restricts storing/redistributing raw results) — keep only the derived aggregates
(`car_ivt_google_area_v2.csv` etc.) in `Output/gc/`, and drop `google_dm_raw/*.json` from the
outputs list above.** Resume once a key with the Distance Matrix API enabled and billing on is
available; the representative-point script is reusable (not yet in the repository — see the
person who resumes this item for it, or rebuild it from this method paragraph, it is short).

### C2. Step 38 — Walking-network access to stations and stops from OpenStreetMap (task E6)

**Goal.** Replace the straight-line × 1.3 walk in the LRT and bus skims with a walking-network
distance from each TAZ to its nearest LRT station and nearest served bus stop.

**Inputs.** OSM extract: download `israel-and-palestine-latest.osm.pbf` from Geofabrik
(≈ 250 MB), place it under `Input/OSM/` (it falls under the `Input/*` LFS rule; commit through
the normal route, or ask the user to add it), and read it with `pyrosm` (install
`pip install pyrosm`; no network access is needed once the file is local — `osmnx` needs
Overpass and is the fallback only if the environment can reach it). Stations:
`Output/lrt_v2/lrt_stations_hf_lrt_3.csv` (24 stations, EPSG:2039 coordinates). Bus stops with
peak service: `Output/gtfs/stops_study_area.csv` (stop_id, x, y, TAZ) with the departures of
`Output/gtfs/stop_times_study_area_am_trips.csv.gz` (keep stops with ≥ 4 departures 07:00–08:00).
TAZ polygons `Input/TAZ_North/TAZ_North.shp`; population per TAZ from `Input/Zonal_2020.csv`.

**Method.**
1. Clip the OSM network to the study-area bounding box (the `TAZ_North` extent buffered 2 km),
   keep the walkable ways (`highway` in footway, path, pedestrian, steps, living_street,
   residential, unclassified, tertiary, tertiary_link, secondary, secondary_link, service,
   track, cycleway; exclude motorway, trunk, primary carriageways unless `sidewalk`/`foot=yes`),
   build a `networkx` graph with edge length in metres, take the largest connected component.
2. Origin points per TAZ: the polygon's representative point plus, for TAZs larger than 1 km²,
   four more points (the quadrant representative points), each weighted equally (a building
   layer is not in the repository). Snap each point and each station / stop to the nearest
   graph node (record the snap distance; flag > 300 m).
3. Multi-source Dijkstra from the 24 station nodes (one run, `networkx.multi_source_dijkstra`
   with the station as the source label) and from the served-stop nodes; for each origin point
   read the network distance and the nearest station / stop; average over the TAZ's points.
4. Per TAZ: `walk_station_m_network`, `walk_station_m_straight`, `detour_station`,
   `nearest_station`, the same four for bus stops, and the walk minutes at 80 m/min (the
   step-26 constant). Aggregate to areas population-weighted for access and employment-weighted
   for egress, as step 26 does now.
5. Add a switch `WALK_SOURCE = 'straight_x1.3' | 'osm'` at the top of step 26 (both LRT access
   and bus stop access read it) and rerun 26 → 31 → 32 with `osm`; report the detour-factor
   distribution (median, p10, p90, by area), the change in trunk-pair LRT GC and the capture.

**Outputs.** `Output/access/walk_network_summary.csv` (nodes, edges, snap statistics),
`walk_access_taz.csv` (778 rows), `walk_access_area_v2.csv` (25 rows, access and egress),
`walk_access_station_catchment.png` (map: network distance bands around the stations);
alternative-skim run under `Output/skims/walk_osm/`.

**Checks.** Median detour factor between 1.2 and 1.6 (a value outside says the graph is broken);
no TAZ in the V2 areas with a snap distance > 500 m; the ten trunk areas' access walk changes by
a stated amount against the current `Output/gc/lrt_access_area_v2.csv`.

**Documents.** §6aj; §0 update and headline row; task E6 partly ticked; plain-English 5.x.
Effort: one day (most of it the OSM handling).

### C3. Step 39 — TAZ-level LRT capture on the trunk (tasks A2, E6)

**Goal.** Run the step-31 pivot on the 174 V2 TAZs instead of the 25 areas, because the logit is
nonlinear in access time and averaging the walk before applying it biases the area result:
expect more capture within 500 m of a station and less beyond 1.5 km.

**Inputs.** 2022 TAZ layers `Output/final_2022/{car,transit}_2022_taz.csv` restricted to the 174
TAZs of `TazAgg`; the area skims of step 31 (`Output/skims/skim_*_*.csv`) for IVT, wait and
transfers; the TAZ-level access walks of C2 (`Output/access/walk_access_taz.csv`; fall back to
`Output/gc/lrt_access_taz_v2.csv` and `Output/gtfs/bus_los_taz.csv` column `bus_nearest_stop_m`
× 1.3 if C2 is not done); the step-31 constants and functions (copy them; do not import across
notebooks).

**Method.**
1. TAZ-pair generalized cost for every mode = the area pair's IVT + wait + transfer penalty
   (from the area skims, mode by mode, including the LRT feeder composition and gateway
   stations recorded in `skim_lrt_*_legs.csv` / `gateway_o` / `gateway_d`) + 2 × (origin TAZ
   access walk + destination TAZ egress walk) at TAZ level. Car: area IVT (there is no TAZ car
   skim) — say so.
2. The pivot exactly as step 31 (Empirical-Bayes-smoothed observed transit share per TAZ pair
   towards the area pair's share, k = 20; `P_LRT|T` within the nest; the incremental logit on
   the transit-nest logsum), central case and the λ / premium ranges, both regimes plus the
   design regime.
3. Aggregate the TAZ results to areas and to the trunk links (the same link-loading rule as
   step 31, by gateway area), and compare with the area-level result: total capture, boardings by
   station, busiest link, and the capture rate by access-distance band (< 500 m, 500–1,000,
   1,000–1,500, > 1,500 m).

**Outputs.** `Output/skims/taz/lrt_trips_2022_taz_{scenario}_central.csv`,
`lrt_capture_scenarios_taz.csv`, `lrt_boardings_by_station_taz.csv`,
`lrt_capture_by_access_band.csv`, `taz_vs_area_capture_comparison.csv`; figure
`Output/figures/lrt_capture_taz_vs_area.png`.

**Checks.** With every TAZ given its area's average walk the TAZ run reproduces the area
result within 1 % (the regression test of the construction); the 2022 no-build flows are
returned exactly when the LRT is removed.

**Documents.** §6ak; §0 update and a headline row beside the area-level capture; tasks A2 and E6
ticked; `docs/LRT_CAPTURE_PLAN.md` §3 addendum; plain-English 5.x. Effort: one day.

### C4. Bus generalized cost with the observed overhead (task E3; a step-26 change, no new step)

**Goal.** Close the ≈ 9-minute gap between the GTFS-based bus door-to-door time and what
surveyed bus users report (`Output/gc/bus_gtfs_vs_survey_summary.csv`).

**Method.** In step 26, two changes behind a switch `BUS_WAIT_RULE = 'half_headway' |
'best_line'`: wait = half the headway of the best single line actually needed for the pair
(`Output/gtfs/bus_direct_skim_area_v2.csv` carries the combined headway; add the best-line
headway there from the step-29 line table) instead of half the pooled headway, capped at 10;
and a stated transfer allowance on the 178 pairs without a direct service (they sit on a scaled
floor today). Rerun 26 → 31 → 32; report bus GC on the trunk pairs before / after and the capture
change. Keep the current rule as the default until the user decides.

**Outputs.** Alternative run under `Output/skims/bus_wait_best_line/`. **Documents.** §6x
addendum, §6ac addendum with the capture change, task E3 ticked. Effort: two hours.

**Status, 23 September 2026 — the wait-rule half done; the overhead itself still open.** Step
29 was extended to carry a best-single-line headway per area pair alongside the existing
pooled one (grouping the same peak-hour trips by `(o, d, route_code)`; §6aa addendum). Step 26
gained the `BUS_WAIT_RULE` switch reading from an environment variable, and — found while
implementing it — the 178 non-direct pairs' transfer count was silently defaulting to 0 via a
`fillna`, inconsistent with step 31, which already assumes 1 transfer on these pairs when it
reads this table; step 26 now states that assumption directly (`gc_area_v2_bus.csv` and
`gc_trunk_pairs_comparison.csv` move on exactly those 178 cells, +8.0 generalized minutes
each; the capture is unaffected, since step 31 already forced this value — confirmed by an
exact rerun). Step 31 gained a matching `GC_SOURCE_DIR` switch so the comparison reruns
without editing either notebook. Results: trip-weighted trunk-pair bus GC 30.7 → 34.9 minutes
under `'best_line'`; central-case LRT capture 4,250 → 4,879 underground (+15%), 3,207 → 3,733
ground (+16%), 5,095 → 5,777 design regime (+13%) (`Output/skims/bus_wait_best_line/`, all
five λ/premium cases). The default chain (`BUS_WAIT_RULE` unset) reproduces every prior output
to the last decimal — confirmed, not just asserted. **Not done:** the door-to-door overhead
itself (the ≈ 9-minute gap this item's Goal names) as a wait/transfer *addition* on top of the
GTFS skim — the two "changes" turned out to be the headway rule and a data-consistency fix,
not the overhead; and step 32's forecast-year rerun under `'best_line'` (only the 2022 central
case was compared). Full detail in `METHODOLOGY.md` §6x addendum 6, §6aa addendum, §6ac
addendum.

### C5. Realistic LRT regime and headway sensitivities (scenarios S1, S2; steps 25 / 26 changes)

**Goal.** The case a decision would be made on: the Haifa core underground (stations S05–S14,
the assumption until the client says which sections are underground) and the rest at ground
level, with a 30–40 s acceleration and braking allowance per stop; and the capture at 7.5 and
10-minute headways.

**Method.** Step 25 (`LRT_line_stations_travel_time.ipynb`): add a per-section regime table
`Input/lrt_section_regime.csv` (columns `station_from, station_to, regime` with `underground`
/ `ground`; commit it as a plain CSV — add a `-filter` line for it in `.gitattributes` as the
other committed CSVs have) and a scenario `mixed_core_underground` built section by section
from the two calibrated coefficients (1.961 / 2.393 minutes per calibrated section, transferred
through the Red Line spacing as the notebook does), plus a variant of each regime with the
allowance (`ACCEL_ALLOWANCE_S = 35`, range 30–40) added per stop; save
`Output/lrt_v2/lrt_station_times_mixed_core_underground.csv` and the area IVT. Step 26: read the
new scenario like the others; `HEADWAY['lrt']` as a list [5, 7.5, 10]; step 31: loop the LRT
scenarios and headways, write `lrt_capture_scenarios.csv` with one row per (regime, headway,
case). Rerun 25 → 26 → 31 → 32.

**Outputs.** The new station-time and area-IVT files; `Output/skims/lrt_capture_scenarios.csv`
extended; `Output/skims/forecast/lrt_capture_scenarios_forecast.csv` extended; a summary table
`Output/skims/lrt_capture_regime_headway_matrix.csv` (regime × headway → central capture, λ
range, busiest link). **Checks.** The mixed case lies between the pure regimes; 10-minute
headway lowers the capture (wait enters GC at weight 2). **Documents.** §6w addendum, §6ac /
§6ad addenda, headline rows, `docs/PLAN_TIGHTENING_AND_SCENARIOS.md` §4 rows S1 / S2 ticked.
Effort: half a day.

**Status, 23 September 2026 — done for 2022, two method choices worth flagging.** Both
scenarios built and run (25 → 26 → 31): `design_50kmh_accel` (39.7 min end to end, central
capture 4,300) and `mixed_core_underground` (56.1 min, central capture 3,520), plus the
headway sensitivity for every regime, not just the new ones
(`Output/skims/lrt_capture_regime_headway_matrix.csv`). Two deviations from the method above,
both deliberate: (1) no `Input/lrt_section_regime.csv` was added — the core boundary (S05–S14)
is a hardcoded set in the notebook, since a committed per-section file for one assumed rule
seemed like the wrong kind of permanence before the client's actual design exists; trivial to
replace once real per-section data arrives. (2) the acceleration/braking allowance was added
**only** to the design_50kmh scenario, not to all three regimes as "a variant of each regime"
could be read to mean — the two calibrated regimes (all_underground, all_ground) already carry
real acceleration, braking and dwell inside their fitted Red Line stop penalty, so adding a
further allowance to them would double-count it. **Not done:** the per-(regime, headway) loop
inside `lrt_capture_scenarios.csv` itself (each combination instead lives in its own directory
under `Output/skims/`, assembled into the matrix above by reading the five files together, not
by a new loop inside step 31); step 32's forecast-year rerun for either new scenario or for the
headway sensitivity (2022 central case only, matching the precedent set by C4).

### C6. Synthetic branch alignments T1 / T2 / T3 (task E1, scenario S4) — until drawings arrive

**Goal.** Replace the feeder composite for the 15 off-trunk areas with an LRT service along the
V2 route orders, flagged synthetic.

**Method.** From `Input/Corridor_TAZ_Agg_V2.xlsx` (`Order_T1` / `Order_T2` / `Order_T3`) and the
area representative points (`Output/corridor_v2/area_legend_v2.csv` has names; compute
population-weighted points from the TAZ polygons), draw each branch as the polyline through the
branch areas' points from Tsomet Kiryat Ata (T1: Kiryat Ata North → Nazareth; T2: Kiryat Haim →
Tsur Shalom; T3: Kiryat Haim West → Savyoney Yam), one station per area, ground-level section
times from the calibrated ground coefficient at the branch spacing (as step 25 transfers it),
through-running from each branch onto the trunk, headway 10 per branch (5 on the trunk). In step
26 / 31 the off-trunk areas then get a direct LRT leg instead of `brt→LRT` / `bus→LRT`; keep the
feeder composite as the comparison. Rerun 25 → 26 → 31 → 32.

**Outputs.** `Output/lrt_v2/lrt_synthetic_branches.geojson`,
`lrt_station_times_branches_synthetic.csv`; alternative run under `Output/skims/branches_synthetic/`.
**Checks.** Trunk-pair results unchanged; the branch areas' LRT GC falls below their feeder GC.
**Documents.** §6al, headline row, task E1 ticked "synthetic, flagged", plain-English 5.x. Effort:
one day. When the planning team's drawings arrive, replace the polylines and rerun.

**Status, 23 September 2026 — built; the plan's own "GC falls below feeder" check does NOT
hold, and that is the finding.** Trunk-pair results are unchanged exactly (checked to 0.00e+00
min in the notebook). Central-case capture: **3,639**, *lower* than the all-underground
feeder-composite case (4,254) — because for 14 of the 15 off-trunk areas, the synthetic
ground-level branch's generalized cost is *higher* than the feeder composite it replaces
(`Output/lrt_v2/lrt_branches_vs_feeder_gc.csv`), from +5.9 minutes (Bazan-Hutsot) to +92.1
minutes at Nazareth (114 → 206). This is not a bug: it is what "one station per area, ground
level, no alignment yet" actually implies once run through the same generalized-cost formula
as everything else — a real bus/Metronit feeder is often faster than a hypothetical
ground-level LRT stopping once per area, and for a large, spread-out area like Nazareth (38
TAZs) the single station's walk access dominates the comparison, not the running speed. Kiryat
Ata North-East is the one area that comes out roughly even. Deviations from the method: no
committed `Input/lrt_section_regime.csv`-style file was needed (the branches are ground level
throughout, by the method's own instruction); output file names differ slightly from the
method's suggestion (`lrt_area_ivt_branches_synthetic.csv` rather than
`lrt_station_times_branches_synthetic.csv`, since the branches have no calibrated "section
form" the way the trunk regimes do — one number per area pair is all there is). **Not done:**
step 32's forecast-year rerun for this scenario. **Recommendation for whoever picks this up:**
do not read 3,639 as "branches hurt the case for the LRT" — read it as evidence that the branch
geometry, station count and placement (especially through Nazareth) matter more to the branch
areas' own result than anything else tested so far, which is exactly why task E1's real
drawings are worth obtaining.

### C7. Bus-network response (scenario S3; step-31 switch)

Add `BUS_COMPETITION = 'full' | 'truncated'` to step 31: with `truncated`, the direct-bus
alternative is removed on the trunk pairs (bus GC set to the feeder-to-LRT GC), an upper bound
on capture. Rerun 31 → 32; report both. **Outputs.** `Output/skims/bus_truncated/`. **Documents.**
§6ac addendum, S3 ticked. Effort: two hours.

**Status, 23 September 2026 — done for 2022; step 32 not rerun.** Implemented literally as
specified: on the 90 trunk pairs, `bus_gc_eff` is overwritten with that LRT scenario's own GC
(`SK[sc]['gc']`) before the `dL` pivot, per scenario per λ/premium case — off-trunk pairs keep
the real bus GC, since the bus is already only a feeder there. Central case, `'full'` →
`'truncated'`: underground 4,254 → 5,754 (+35%), ground 3,206 → 5,270 (+64%), design (no accel)
5,095 → 6,159 (+21%), design + accel 4,300 → 5,776 (+34%), mixed 3,520 → 5,318 (+51%) — the
regimes whose bus alternative was previously closest to competitive gain the most. **Not
done:** step 32's forecast-year rerun under `'truncated'` (2022 central case only, matching the
precedent set by C4 and C5).

### C8. Designed uncertainty experiment (task C3)

A full factorial over: coverage threshold in step 15 (the saved variants
`Output/ths2017/two_mode/bus_calibrated_{binary_guard,all_ravkav}_taz.csv` and the sweep files),
LRT regime (underground / mixed / ground / design), headway (5 / 7.5 / 10), λ (0.02 / 0.03 /
0.05), premium (0 / 5 / 10), bus competition (full / truncated), walk source (straight / OSM),
car source (survey / Google). Steps 31 / 32 already run in a minute; wrap them as a function of
a parameter dict (a new notebook `LRT_capture_uncertainty.ipynb`, step 40) that reads the
alternative skims produced by C1–C7 and writes one row per combination:
`Output/skims/uncertainty/lrt_capture_factorial.csv` with central, low, high LRT boardings,
trunk-pair share and busiest link; a tornado figure by factor. **Documents.** §6am, headline
row "capture range across the design", task C3 ticked. Effort: half a day after C1–C7.

### C9. Step 41 — RavKav 2025 journeys on their own alightings (caveat 16; prerequisite for re-anchoring)

**Goal.** Give the 2025 layer an alighting inference of its own, so that it can be compared with
2022 as a pattern and, if the user decides, replace it as the anchor.

**Inputs.** `Input/BusRavKav/2025/Buses_RavKav.csv` and `Metronit_RavKav_Data.csv` (LFS, 1.6 GB
+ 69 MB; read in chunks with `usecols`); the stop locations of step 34
(`Output/ravkav_2025/stops_located_by_cluster_2025.csv`); the 2022 method in
`notebooks/current/BusRavKav_matrix.ipynb` (step 8) — note that the 2022 file arrived with the
provider's `alight_stop_code` and `bus_trip_id` (journey id) already in it; the 2025 file has
neither, only `CardIDbi`, cluster, stop code, date, time and the transfer tag.

**Method.** Per date, sort each card's taps by time; the alighting of a tap is inferred as the
stop nearest (on the same line direction if the line is known, else by distance) to the card's
next tap that day, provided the next tap is within 90 minutes and within 20 km; the last tap of
the day takes the day's first tap's stop (the return-home rule) if that stop is on a plausible
line, else is unallocated. Chain taps into journeys with the step-8 rule (a next boarding within
the transfer window at or near the inferred alighting), and compare the chained transfer share
with the file's tag (3.7 %) and with 2022 (a third of legs). Build the journey OD by TAZ on the
inferred alightings for 06:00–09:00 on the 42 representative Tuesdays, average it, and compare
with `Output/bus/bus_od_taz_avg.csv` (cosine, KS, PCA — reuse the step-35 functions) and with
step 34's borrowed-pattern OD. Report the unallocated share.

**Outputs.** `Output/ravkav_2025/bus_od_taz_2025_own_alightings.csv`, `journeys_2025_summary.csv`
(taps, legs, journeys, transfer share by the chain vs by the tag, unallocated), the comparison
table; figure of the inferred-alighting distance distribution. **Checks.** ≥ 85 % of taps get an
alighting; the chained transfer share is reported against the tag's; the OD's row sums equal
the journey origins of step 34 within 2 %. **Documents.** §6an, caveat 16 updated, §6af
"Re-anchoring" updated with the decision inputs (the user decides whether to move the base to
2025; the car layer would be grown to 2025 with the step-16 factors on `Zonal_BU_2025.csv`).
Effort: one day; memory-bound (chunk the 1.6 GB file by date).

### C10. Step 42 — All-or-nothing assignment link check of the car layer (task B1)

**Goal.** A link-level comparison with the 3,241 counted links that the cordon test of step 36
could not give.

**Inputs.** `Input/Network_with_Counts/Emme_Links_Final_Res 2026-09-23.*` (LFS; fields
`INODE`, `JNODE`, `LENGTH`, `TYPE`, `LANES`, `MODES`, `VDF`, the counts `YARAM6..8`; centroid
connectors are `TYPE 9` and carry the `TAZ` number); `Output/ths2017/three_mode_2022/car_2022_taz.csv`;
the occupancy 1.33 and PCE 1.10 of step 36.

**Method.** Build a directed `networkx` graph of the car links; free-flow speed by `TYPE`
(there is no speed field: assume 90 / 70 / 60 / 50 / 40 / 30 km/h for types 1–6 and state it;
check `DATA1`–`DATA3` and `UL1` first — one of them may be a speed or capacity); connectors
join each TAZ to the network. Assign the 2022 car vehicle matrix (÷ 1.33) all-or-nothing on
free-flow times (Dijkstra from each of the 778 origins; ~ 25,000 non-empty cells). Compare the
assigned volume with the count (÷ 1.10) on the counted links: GEH per link, the share of counted
links within GEH 5 and 10 (flow-weighted), the ratio by road type and by cordon, and the
screenline sums of step 36 recomputed from the assignment. Expect a poor link-level fit
(all-or-nothing, no congestion, no external trips) but a usable one on the screenlines and by
type; say so. If the fit by type is systematically low by the same factor as the cordons
(0.6–0.7), that is the external / commercial share, not an error.

**Outputs.** `Output/validation/car_aon_link_flows.csv` (every car link: assigned vehicles,
count, GEH), `car_aon_fit_by_type.csv`, `car_aon_screenlines.csv`; figure
`Output/figures/car_aon_vs_counts.png` (scatter, log axes). **Documents.** §6ao, task B1 ticked,
caveat on the assignment's limits. Effort: one day.

### C11. Design-hour factors on the observed profiles (caveat 18; steps 20 / 27 / 31 / 32 switch)

**Goal.** Carry the count-based car factor and the boarding-based transit factor into the
peak-hour products, keeping the survey's departure factors as the upper bound.

**Method.** A switch `PHF_SOURCE = 'survey' | 'observed'` read by steps 24, 27, 31 and 32 (they
take the factors from `Output/corridor_v2/peak_hour_factors_v2_applied.csv`): with `observed`,
car = the count-based clock-hour factor per cordon direction (`Output/validation/car_cordon_counts.csv`,
column "count PHF3h"; network value ≈ 0.42–0.45, and a sliding-window correction of +0.03 stated),
transit = the RavKav boarding factor (`Output/ravkav_2025/boarding_hour_peak_factors_2025.csv`,
bus 0.475 / Metronit 0.433, trunk station areas 0.43). Rerun 24, 31, 32 with `observed` and
publish both peak-hour sets side by side (`corridor_v2_link_flows_long.csv` gains a column
`flow_peak_hour_observed`; the LRT trunk-link peak-hour loads likewise).

**Documents.** §6r / §6y / §6ac / §6ad addenda, the §0 headline rows for peak-hour quantities
carrying both values, caveat 18 updated, the reports' next revision note. Effort: half a day.

**Status, 23 September 2026 — done for steps 24/27/31; step 32 and a PHF_SOURCE switch not
built.** Implemented as side-by-side columns rather than a `PHF_SOURCE` switch with a rerun, per
the Method's own "publish both peak-hour sets side by side" — one execution of each notebook
now carries both factors, so there was nothing to gate behind an environment variable. Car
observed = mean of the 12 cordon-direction `count PHF3h` values (step 36) + the stated 0.03
sliding-window correction = 0.435, applied uniformly (the six cordons do not map onto
individual V2 routes). Transit observed = the RavKav study-area boarding factor (step 34,
bus, all boardings) = 0.4755, applied to bus, Metronit/rail and taxi alike (no independent
observed source for taxi). Because the transit observed factor is one number for both
directions while the survey factor splits 0.549 up / 0.457 down, the trunk's peak-hour LRT
loads move to 0.865–0.866 (up) / 1.041 (down) of the survey-based figure — not a uniform
correction. **Not done:** step 32's forecast-year peak-hour outputs; a car observed factor
split by cordon/direction (one representative number was used instead, matching the existing
study-area-fallback simplification already in step 27).

### C12. Housekeeping that goes with the above

- When C1–C7 add switches, the default run of the chain must still reproduce today's numbers
  exactly (regression: rerun 26 → 31 → 32 with defaults and diff `lrt_capture_scenarios.csv`).
- `METHODOLOGY.md` §9 gets one line per new step with its LFS needs and run time.
- The README notebook table and the mermaid chain (steps 36–42 are not in the mermaid yet; add
  36 as a diagnostics node off step 16 and the new ones where they attach).

---

## D. Order, effort and the standing data requests

**Order.** C1 (car uplift, half a day) → C2 (OSM access, one day) → C3 (TAZ capture, one day) →
C4, C5, C7 (a day together) → C6 (synthetic branches, one day) → C11 (design-hour factors, half a
day) → C8 (factorial, half a day) → C9 (2025 chaining, one day) → C10 (assignment check, one
day). C9 and C10 are independent of the others and can run in parallel sessions. Each step is
committed and pushed on its own, with its documents, before the next starts.

**Data still requested from the client side** (repeat at every hand-over; details in
`METHODOLOGY.md` §8 and `docs/RED_TEAM_RESPONSE_2026-09-23.md` §4):

1. Bus passenger counts on the Haifa trunk and the Nazareth branch by section, direction and
   hour (APC or manual) — decides the Nazareth branch (caveat 17) and validates the transit base.
2. The two RavKav definitions: what the 2025 `JourneyTransfer` tag means under the daily cap,
   and for May 2022 the operators covered, cash boardings and the alighting inference method.
3. Branch alignments and stations (T1 / T2 / T3, Hamifrats → Tsomet Kiryat Ata), the
   underground / ground regime per section, headways and the through-running pattern.
4. The opening-year bus network plan (lines truncated to feeders, lines kept).
5. The national transport model's mode-choice parameters and values of time (substitute for the
   stated-preference survey that will not be collected).
6. CBS population and employment by statistical area for 2018 and 2022 (medium).
7. The OnBoard survey codebook — unit per row and expansion (lower priority since the chain no
   longer depends on its pattern).

Not needed / not coming, by the user's decision on 23 September 2026: Metronit 2013 ridership,
a stated-preference survey, parking supply, the cellular product's trip definition.
