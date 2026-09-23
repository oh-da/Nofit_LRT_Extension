# Handover — repository conventions and the next eleven steps (23 September 2026)

*Written for whoever — person or model — picks this repository up next. Part 1 is how the
repository works: conventions that are not written down anywhere else in one place. Part 2 is
eleven next steps, each already scoped somewhere in `docs/PLAN_TIGHTENING_AND_SCENARIOS.md`,
`docs/CORRIDOR_DEMAND_TASKS.md` or `docs/RED_TEAM_RESPONSE_2026-09-23.md`; this document pulls
each one into one place with exact inputs, method, outputs, checks and the documents to update,
so it can be started without re-reading the whole history first. Step numbers cited for existing
work (steps 1–36) are fixed; step numbers proposed below for new work are the next free numbers
as of this writing and should be re-checked against `METHODOLOGY.md` §0 before use, since
numbering follows execution order, not this plan.*

## Part 1 — Repository conventions

**One step, one executed notebook.** Every unit of work is a Jupyter notebook that runs
end to end and is committed *executed* (outputs in the cells, not stripped). New notebooks
for the current chain go in `notebooks/current/`; pure test/diagnostic notebooks (similarity
tests, validation, PCA suites) go in `notebooks/diagnostics/`; nothing new goes in
`notebooks/historical/`. Every notebook's first cell changes the working directory to the
repository root, so every path in this document and in `METHODOLOGY.md` is root-relative and
a notebook runs correctly regardless of where it is opened from.

**Document every step in `METHODOLOGY.md`.** One `## 6a<x>. Step N — Title (`notebook.ipynb`)`
section (diagnostics get `, diagnostics)` after the notebook name) with, in order: **Purpose**,
**Inputs**, **Method**, **Results** (with the actual numbers produced, not placeholders),
**Outputs** (every file written, under `Output/…`, plus figures), **Limits** (what the step
does not establish). Do not summarize — quote the numbers a rerun would reproduce.

**Update `METHODOLOGY.md` §0 (status and lineage) every time a step changes a headline
number.** Add a row to the "Conclusions for the corridor" table, or edit the existing row if
the step supersedes it. If a correction changes the *inputs* of already-executed steps (a bug
fix, a corrected code, a new prior), rerun every downstream step and add a dated paragraph
titled **"Rerun, DATE (what changed)."** or **"Rebuild, DATE (what changed)."** to §0, stating
the before → after values for every headline number that moved and which steps were rerun —
see the two existing examples at `METHODOLOGY.md` lines 165 and 215 for the exact form. Never
silently overwrite an old number without that paragraph; the git history is not a substitute
for it because README and the task docs quote numbers directly.

**Update `README.md`.** Its status paragraph carries the same headline numbers as
`METHODOLOGY.md` §0 in prose form, and its Mermaid diagram (`## Current pipeline`) gets a new
node when a notebook joins the *current* chain (not for diagnostics). Keep the "Repository
layout" table's `Output/` line current if a step adds a new top-level `Output/` subdirectory.

**Update the task and plan docs.** `docs/CORRIDOR_DEMAND_TASKS.md` is the checklist: tick an
item `[x]` (or `[~]` for partly done) and append a dated note in place — do not delete the
open description, since the note explains what closed and what is still open. If the item was
tracked in `docs/PLAN_TIGHTENING_AND_SCENARIOS.md` or `docs/RED_TEAM_RESPONSE_2026-09-23.md`
as well (most of the eleven items below are, in both), append the same kind of dated note there
too, in place, rather than rewriting the plan.

**Reports are revised, not rewritten.** `reports/Survey_Matrices_Car_Bus_Rail_Report.docx` and
`reports/V2_Corridor_LRT_Times_and_GC_Inputs_Report.docx` carry a revision number; after a
rerun that changes their numbers, bump the revision and append a dated revision note with the
before/after values rather than rewriting the body text (the body text is allowed to lag the
latest rerun as long as the revision note carries the current numbers).

**Never feed a validation count into matrix estimation.** This is the one rule the red-team
response adopts in place of a formal hold-out (`docs/RED_TEAM_RESPONSE_2026-09-23.md` §1a): any
count obtained (RavKav boardings, road counts, a future passenger count) is for comparison
only. Do not calibrate to it.

**The standard rerun chain.** After any change to the LRT geometry, speed regime, headway, bus
GC, or λ/premium assumptions: **step 25 → 26 → 31 → 32**, about ten minutes end to end
(`METHODOLOGY.md` §9). Run it in full after any of the changes below, not just the step that
changed, since 31 and 32 read 25 and 26's outputs.

**Git LFS in this environment.** `git-lfs` is not installed here, so files under LFS tracking
(`.gitattributes`; broadly `Input/*` except the listed committed substitutes) sit as pointer
stubs after clone/pull — three lines of text, not the data. **Pushing new LFS objects from
this environment does not work** (the note already in `.gitattributes`), but *downloading* them
does: GitHub's LFS batch API is plain HTTPS and answers anonymously for this public repo, and
it is reachable through the environment's proxy. Use `tools/lfs_pull.py` (added with this
handover) before running any notebook that reads an LFS input:

```
python3 tools/lfs_pull.py                              # whole checkout
python3 tools/lfs_pull.py Input/BusRavKav/2025          # just one subtree
python3 tools/lfs_pull.py --dry-run                     # list pointers, no download
```

It finds pointer files, batches them through `origin`'s LFS endpoint, downloads and
checksum-verifies each object against its own oid, and overwrites the pointer in place. A new
large input that only exists on the client side or another machine still needs to be committed
from a machine that has `git-lfs` and push access; this script only pulls what is already in
the remote's LFS store.

**Every number is cited.** State the file or notebook section that produced it. This
repository's whole defensibility rests on every quoted figure being reproducible from a named
notebook cell — the pattern to keep, not a formality.

---

## Part 2 — The next eleven steps

Each entry: what it closes, exact inputs, method, outputs, checks, and the docs to update.
Items 2–3 and 5 share machinery and are best done together; the suggested order is at the end.

### 1. Google Distance Matrix car uplift (task E5)

**Closes.** The survey's car skim is 2017/18 door-to-door time (`Input/THS_2017-2018/
trips_ths_2017.xlsx`, smoothed per area pair as `time ≈ a + b·distance`, already built into
`GC_data_inventory_and_skims.ipynb`, step 26). Nothing in the chain currently corrects it to
2026 congestion levels.

**Inputs.** A Google Distance Matrix API key; ≈ 40 representative OD pairs spanning the
corridor — the 25 V2 area centroids' trunk pairs plus a few branch pairs, chosen to span the
distance range already sampled by the survey skim; `departure_time` set to the next
representative Tuesday at 07:30 (the same "representative weekday" convention used throughout,
e.g. the Tuesday averaging of step 8 and step 34), driving mode, `traffic_model=best_guess`.

**Method.** Query the ~40 pairs once (not all 625 area-pair cells — LRT_CAPTURE_PLAN.md §2
explicitly rejects full coverage as unnecessary and flags the Google ToS point on storing
results: **store only the derived ratio, not raw API responses**, in committed outputs). For
each pair, compare Google's 2026 driving time against the survey's smoothed 2017/18 time for
the same pair. Fit a single uplift ratio, or a ratio per distance band if the ~40 pairs show a
clear trend (the sample is small, so prefer the single ratio unless the banded fit is clearly
better). Apply the ratio to the car skim step 26 currently builds from the survey, and rerun
25 → 26 → 31 → 32.

**Outputs.** `Output/gc/google_distance_matrix_sample.csv` (pair, survey time, Google time,
ratio — no raw API payloads), the applied uplift factor recorded in step 26's notebook and its
`METHODOLOGY.md` section.

**Checks.** Report the ratio with its spread across the ~40 pairs; note how much the central
LRT capture (4,250 underground, §6ac) moves once the car leg of every GC comparison is
uplifted — car getting slower relative to bus/LRT should, if anything, raise the capture.

**Docs to update.** `docs/CORRIDOR_DEMAND_TASKS.md` E5; `docs/LRT_CAPTURE_PLAN.md` §2 (the car
skim bullet); new `METHODOLOGY.md` subsection under step 26's revision history; §0 lineage
table if the capture number moves; README if the headline capture number changes.

### 2. OSM walking access (task E6)

**Closes.** Station and stop access is currently a straight-line distance × 1.3 detour factor
at an assumed 4.8 km/h, population-weighted per area for access and employment-weighted for
egress (`METHODOLOGY.md` line 1650; `docs/PLAIN_ENGLISH_METHODOLOGY.md` line 3219). This is
18 of the 17-minute median LRT–bus generalized-cost gap on the trunk (13.2 vs 4.8 minutes
walk, `docs/PLAN_TIGHTENING_AND_SCENARIOS.md` §2) — the single largest lever after λ itself.

**Inputs.** An OSM footway extract for the study area (Overpass API, or a regional extract
such as Geofabrik's Israel & Palestine, clipped to `TAZ_North.shp`'s bounding box); the 174 V2
TAZ centroids; the 24 LRT station points (`Input/GeneralHalufa/station_hf_lrt_3.geojson`); the
served bus/Metronit stop points already located by step 29 (`GTFS_bus_LOS_TAZ.ipynb`,
`Output/gtfs/`).

**Method.** Build a routable walk graph from the OSM extract (e.g. OSMnx/networkx or pandana
on the `highway=*` footway-passable ways). Route every V2 TAZ centroid — every TAZ for the
trunk areas — to its nearest LRT station and nearest served stop over the network, at the same
4.8 km/h used today so only the *distance* model changes, not the speed assumption. Replace
the straight-line × 1.3 figure with the network time. This is the same notebook as item 3
below (`LRT_capture_TAZ_trunk.ipynb`), since the walking network is what makes the TAZ-level
capture worth doing (a population-weighted area average would still hide the nonlinearity a
network model reveals).

**Outputs.** `Output/skims/walk_access_taz.csv` (TAZ, nearest station, network walk minutes,
nearest stop, network walk minutes to it), figure comparing straight-line × 1.3 against the
network time by distance band.

**Checks.** Expect the network time to exceed the straight-line proxy near barriers (the
railway, the Kishon, arterial roads without crossings) and to fall below it on a direct grid;
report the overall bias, not just the mean. Rerun 26 → 31 → 32 with the new access time.

**Docs to update.** `docs/CORRIDOR_DEMAND_TASKS.md` E6, E2 (E2's "Remaining refinement" note
on station access); `docs/PLAN_TIGHTENING_AND_SCENARIOS.md` item 3a.2 and §2's "Station
access" row; new `METHODOLOGY.md` step section; §0 lineage table and README once the capture
number moves.

### 3. TAZ-level capture on the trunk (tasks A2, E6)

**Closes.** The capture pivot currently runs on 25 V2 *areas*; the logit is nonlinear in
access time, so an area-level average biases the result — more capture is expected within
500 m of a station and less beyond 1.5 km than the area average shows
(`docs/PLAN_TIGHTENING_AND_SCENARIOS.md` item 3).

**Inputs.** The 174-TAZ V2 key (already used by step 29's bus LOS, step 26's skims); item 2's
`walk_access_taz.csv`; the LRT access per TAZ (`Output/lrt_v2/lrt_access_taz_v2.csv`, already
built); the 2022 TAZ-level matrices (`Output/ths2017/three_mode_2022/`).

**Method.** Re-run step 31's nested incremental-logit pivot
(`Mode_skims_and_flow_comparison.ipynb`'s method, §6ac) at TAZ resolution instead of area
resolution: same λ (0.03 central, 0.02–0.05 range), λ_T = 2λ, 5-generalized-minute LRT
premium, free LRT–Metronit transfer, same generalized-cost formula
(`docs/LRT_CAPTURE_PLAN.md` §1) — only the walk-access input and the level at which GC is
computed change. Notebook: `LRT_capture_TAZ_trunk.ipynb` (next free step number).

**Outputs.** `Output/gc/lrt_capture_taz_trunk.csv` (TAZ-level GC and captured LRT trips),
comparison figure against the area-level central case (4,250 underground) by distance-to-
station band.

**Checks.** Report the new central underground/ground totals against the area-level 4,250 /
3,207 and confirm the direction of the bias matches the nonlinearity expectation above (more
capture close in, less far out) before accepting the new total as the central case.

**Docs to update.** `docs/CORRIDOR_DEMAND_TASKS.md` A2, E6; `docs/PLAN_TIGHTENING_AND_SCENARIOS.md`
item 3a.3; `docs/LRT_CAPTURE_PLAN.md` §3 (the central-case numbers); `METHODOLOGY.md` new step
section, §0 lineage table (the central LRT capture row is the most-quoted number in the whole
repository — update README's headline paragraph too).

### 4. Bus generalized cost overhead (task E3)

**Closes.** The GTFS-based bus door-to-door skim (observed running time + walk + wait)
undershoots the survey's reported door-to-door time by a fixed amount not currently in the bus
GC: `docs/PLAN_TIGHTENING_AND_SCENARIOS.md` §2 gives 7 minutes on the trunk pairs;
`METHODOLOGY.md` §6x addenda 2–3 gives the fuller picture — 22.7 vs 32.2 minutes over the same
pairs (≈ 9 minutes, ×1.4), with a clear distance-band pattern: ×1.9 under 3 km, ×1.3–1.5 at
3–20 km, ×0.8 beyond 20 km (short trips are where the schedule most understates the real
door-to-door time — access at the ends dominates a short scheduled ride).

**Inputs.** The existing GTFS bus/Metronit skims (`Output/gtfs/`, steps 29–30); the survey's
reported bus door-to-door times already used for the comparison in §6x.

**Method.** In step 26's GTFS block (`GC_data_inventory_and_skims.ipynb`), either (a) add a
fixed wait/transfer overhead calibrated from the distance-band ratios above (a small change,
as the plan already characterizes it), or (b) set the wait component to the headway of the
single best line serving the pair rather than half the pooled headway across all lines
serving it — the plan lists both as candidate fixes; try (a) first since the distance-band
evidence already exists, and note whether (b) closes most of the same gap on its own before
adding both.

**Outputs.** Revised `Output/gc/gc_data_inventory.csv` bus GC column; before/after comparison
table by distance band.

**Checks.** Confirm the corrected bus GC narrows the 22.7-vs-32.2 gap without overshooting it
on the pairs used for calibration (a leave-one-band-out check is enough given the small
sample). Rerun 31 → 32.

**Docs to update.** `docs/CORRIDOR_DEMAND_TASKS.md` E3; `docs/PLAN_TIGHTENING_AND_SCENARIOS.md`
item 3a.4; `METHODOLOGY.md` step 26's section (revision note, not a new step number); §0 and
README if the capture total moves.

### 5. Mixed LRT regime and headways (step 25/26 revision)

**Closes.** Two pure regimes exist (all-underground 27.6 km/h, all-ground 17.1 km/h) plus a
50 km/h design ceiling with no acceleration allowance. None is the case a real decision would
be made on. Headway is fixed at 5 minutes throughout.

**Inputs.** `hf_lrt_3`'s station spacing and the calibrated running-time/stop-penalty
decomposition already in step 25 (46 km/h + 49 s/stop underground, 31 km/h + 74 s/stop
surface, `docs/LRT_CAPTURE_PLAN.md` §1); a stated acceleration/braking allowance (30–40 s per
stop is the usual range; the calibrated forms already imply 40–65 s including dwell — this is
an open question for the client in §6 of the plan, so pick 35 s as the working midpoint and
flag it as assumed until answered).

**Method.** In `LRT_line_stations_travel_time.ipynb` (step 25): (a) add the acceleration
allowance as a per-stop constant on top of the design-speed regime; (b) build a **mixed
alignment** — Haifa core (approximately S05–S14) underground, the rest at ground level — using
the same per-section speed functions already calibrated for the pure regimes, just applied
section by section instead of uniformly. This mixed case becomes the third line beside the two
pure regimes in every downstream table (GC, capture, forecast), not a replacement for them.
Separately, rerun step 26's headway parameter at 7.5 and 10 minutes (today's assumption is
5 minutes) to show the capture's sensitivity to the operating plan.

**Outputs.** Updated `Output/lrt_v2/` with the mixed-alignment station-to-station times
alongside the two pure regimes; `Output/gc/` and `Output/mode_choice/` outputs run for the
mixed case and for headways 7.5 and 10 at the existing 5-minute case's settings otherwise
unchanged.

**Checks.** The mixed-alignment IVT and capture should sit between the two pure regimes; report
where in that range, since that is the number closest to a real design's likely GC. Report the
headway sensitivity as a simple table (5/7.5/10 → wait time → capture), no recalibration needed
beyond the wait term.

**Docs to update.** `docs/CORRIDOR_DEMAND_TASKS.md` E1's "regime per section" note;
`docs/PLAN_TIGHTENING_AND_SCENARIOS.md` items 3a.5–3a.6 and scenario S1/S2; `METHODOLOGY.md`
§6w (revision) and §6ac/§6ad (new scenario columns); §0 lineage table; README.

### 6. Synthetic branches (task E1, scenario S4)

**Closes.** Fifteen of the 25 V2 areas reach the LRT only through a feeder composite (bus, or
Metronit with a free transfer, to the nearest gateway station area plus an 8-minute transfer
penalty) because the branch alignments (T1 Kiryat Ata–Shefaram–Nazareth, T2 Krayot, T3 Kiryat
Yam, and the Hamifrats–Tsomet Kiryat Ata trunk extension) are not yet supplied by the client.
This is a structural gap, not a behavioral-parameter one (`docs/PLAN_TIGHTENING_AND_SCENARIOS.md`
§2), and the two items it needs from the client — the actual alignments and the operating plan
— are both still outstanding (§4 data-request table). Item 7 below tracks obtaining them; this
item is what can be done **without** waiting for that data.

**Inputs.** The route orders for T1/T2/T3 already defined for the corridor-flow-profile work
(`Corridor_flow_profile_V2_routes.ipynb`, step 24, `Output/corridor_v2/`); the calibrated
speed/stop-penalty function from step 25 (or the mixed-regime function from item 5, once done);
TAZ 1509 (station S13), which task E1 notes is missing from the current V2 aggregation and
should be added.

**Method.** Build **synthetic** branch geometry: place stations at the V2 route order's area
centroids along each branch (T1, T2, T3, and the Hamifrats extension), spaced as the route
order already implies, and apply the calibrated running-time function from step 25/item 5 to
get station-to-station times exactly as the trunk was built — but flagged throughout as
synthetic (not the client's actual alignment) in every output and every downstream table.
Feed this into step 31 in place of the feeder-composite skim for the 15 previously-unserved
areas.

**Outputs.** `Output/lrt_v2/lrt_branches_synthetic.csv` (synthetic station points and
station-to-station times per branch, clearly labeled `synthetic=True`); rerun of 31 → 32 with
the synthetic branches replacing the feeder composite for those 15 areas.

**Checks.** Compare the synthetic-branch capture against today's feeder-composite capture for
the same 15 areas — this isolates what having *any* on-branch stations (even synthetic ones)
adds over a feeder, which is scenario S4's stated purpose ("what the branches add"). Do not
present this as a replacement for the real alignment once obtained (item 7) — re-run with the
real geometry the moment it arrives and note the synthetic version as superseded.

**Docs to update.** `docs/CORRIDOR_DEMAND_TASKS.md` E1; `docs/PLAN_TIGHTENING_AND_SCENARIOS.md`
item 3b.7 and scenario S4; `METHODOLOGY.md` new step section marked synthetic/interim; §0 and
README with the caveat that the branch geometry is synthetic until the client data (item 7 of
`docs/RED_TEAM_RESPONSE_2026-09-23.md` Track B) arrives.

### 7. Bus-network response (scenario S3)

**Closes.** Today's capture assumes full bus competition on every trunk pair (conservative —
an upper bound on how much of the bus market the LRT actually gets, since real operating plans
usually truncate some parallel bus lines into feeders once a rail line opens). The actual
opening-year bus network plan is a client-side input still outstanding
(`docs/PLAN_TIGHTENING_AND_SCENARIOS.md` item 3b.8); this item is the bounding scenario that
does **not** need that data.

**Inputs.** Step 31's existing pair-level GC and mode-choice machinery
(`Mode_skims_and_flow_comparison.ipynb`); no new inputs.

**Method.** Re-run step 31 with the competing direct-bus alternative removed on trunk pairs —
i.e. treat the LRT as the only fast transit option on those pairs, keeping the Metronit and
feeder buses as station-access modes only. This gives the upper bound on capture the way the
full-competition case gives (implicitly) something closer to a lower bound.

**Outputs.** A second capture column in `Output/gc/` and `Output/mode_choice/` alongside the
central full-competition case, same format, clearly labeled as the truncated-bus-network
variant.

**Checks.** Report both bounds (full competition / truncated-to-feeders) side by side with the
central case in every table from here on, the same way the λ range and LRT-premium range are
already carried as whiskers — this scenario is a bound on a structural assumption, not a
sensitivity on a continuous parameter, so keep it visually distinct from those.

**Docs to update.** `docs/CORRIDOR_DEMAND_TASKS.md` (note under E1/C1); `docs/
PLAN_TIGHTENING_AND_SCENARIOS.md` scenario S3 and item 3b.8; `METHODOLOGY.md` §6ac revision;
§0 lineage table's capture row, now reported as a range across this bound in addition to the
λ/premium whiskers.

### 8. The uncertainty factorial (Track A item 7 of the red-team response)

**Closes.** Uncertainty has so far been tested piecemeal (λ range, premium range, transfer
assumption) rather than jointly, and the review's own criticism is that "the behavioural
assumptions currently matter more than the infrastructure question the study is meant to
answer" (`docs/RED_TEAM_RESPONSE_2026-09-23.md` §1) — a joint design is needed to see how the
factors interact, not just their individual ranges.

**Inputs.** Every factor above, once available: coverage threshold/model (the step-15 rule),
TAZ allocation (item 3's TAZ-level vs area-level capture), LRT regime (item 5's underground /
ground / mixed / design-ceiling), λ (0.02–0.05), LRT premium (0–10 generalized minutes),
land-use scenario (BU/HS × 2040/2050 from step 23), bus-network response (item 7's two
bounds) — six or seven factors, per the response's own count.

**Method.** Since the full chain from step 25 through 32 reruns in about ten minutes
(`METHODOLOGY.md` §9), a full or fractional factorial over these six–seven factors is
affordable — the response explicitly prefers this over a Monte Carlo at this stage, since a
factorial identifies *which* factors and interactions drive the range, which a Monte Carlo's
marginal distribution does not show as directly. Build a driver notebook that loops steps
31–32 (or the relevant sub-functions directly, to avoid the full notebook-execution overhead
per cell) over the factorial design, collecting LRT boardings and the critical-link loads
(Namal-Giborim → Hamifrats) for every cell.

**Outputs.** `Output/mode_choice/uncertainty_factorial.csv` (one row per factor combination,
central/low/high LRT boardings and critical-link load per row), a tornado or similar diagram
ranking factors by their effect on the total, consistent with the "ranked drivers" table
already in `docs/PLAN_TIGHTENING_AND_SCENARIOS.md` §2 but now from a joint design rather than
one-factor-at-a-time ranges.

**Checks.** Report central/low/high LRT boardings and critical-link loads as the response asks
(§3 item 7); once an assignment exists (item 10 below), extend the same design to distinguish
unique passengers, boardings, transfers and maximum sectional load rather than just total
boardings.

**Docs to update.** `docs/RED_TEAM_RESPONSE_2026-09-23.md` §3 Track A item 7 (mark done, with
the factorial's headline range); `docs/PLAN_TIGHTENING_AND_SCENARIOS.md` §2 and scenario S9;
`METHODOLOGY.md` new step section; §0 lineage table — the capture number should from this point
be quoted with its factorial-derived range, not just the λ/premium whiskers alone.

### 9. 2025 RavKav journey chaining

**Closes.** The 2025 smart-card extracts (`Input/BusRavKav/2025/Metronit_RavKav_Data.csv`,
`Buses_RavKav.csv`) carry a `JourneyTransfer` tag (`מעבר` transfer / `לא מעבר` first boarding)
that flags only 3.7% of boardings as transfers — far below the May-2022 RavKav files' own
`bus_trip_id` linkage, which found 1.52 legs per journey (a third of all boardings were
transfer legs). The tag evidently marks only boardings charged as a transfer under the fare
rules, not every physical transfer leg, so "2025 journey origins" as currently computed are
much closer to *leg* counts than the 2022 *journey* counts are — a unit mismatch that is the
stated reason the chain was not re-anchored on the 2025 layer
(`METHODOLOGY.md` §6af "Re-anchoring", reason (i)).

**Inputs.** The three 2025 extracts, keyed per tap by `CardIDbi` (card id), `ClusterId` /
`ClusterName` (operator cluster), `StopCode`, `TransactionDate`, `TransactionTime` (to the
minute), `JourneyTransfer` (`METHODOLOGY.md` line 327); the stops-by-(cluster, code) location
table already built by step 34 (`Output/ravkav_2025/stops_located_by_cluster_2025.csv`); step
8's own method as the template for what "chaining" means here
(`BusRavKav_matrix.ipynb`, §6f): a journey is one linked id, a leg one deduplicated tap.

**Method.** The 2022 files carried `bus_trip_id` (passenger + journey-of-day number) directly;
the 2025 files do not, but their card ids allow the same construction by hand
(`METHODOLOGY.md` §6af "Re-anchoring", reason (ii): "which the extract's card IDs allow but
which has not been done"). Sort taps by `(CardIDbi, TransactionDate, TransactionTime)`; group
consecutive taps of the same card and date into one journey while a time-window rule holds
(e.g. a gap under the fare's free-transfer window, cross-checked against `JourneyTransfer`
where it is set, since a `לא מעבר` tap should start a new journey and a `מעבר` tap should
continue one — treat disagreements between the window rule and the tag as evidence about which
one is right, not a contradiction to silently resolve one way). This reproduces step 8's
journey definition on the 2025 extract without needing an operator-provided fix to the tag.

Once journeys are chained, the second half of item (ii) — "a 2025 alighting inference from the
linked taps" — is still open: the 2025 taps are boardings only, so a 2025 *alighting* pattern
(analogous to step 8's own inferred alightings, which since the 23 September rebuild are the
chain's preferred prior over the OnBoard survey) requires either an alighting-inference method
applied to the newly-chained 2025 journeys, or continuing to borrow the 2022 alighting pattern
as step 34 currently does — but now applied to a 2025 volume that is a true journey count
rather than a near-leg count.

**Outputs.** `Output/ravkav_2025/bus_od_taz_2025_chained.csv` (journey OD on the corrected
2025 journey definition), a comparison of chained-journey counts against both the current
`bus_od_taz_2025.csv` (leg-like) and the 2022 `bus_od_taz_avg.csv` (true journeys) at the same
stops.

**Checks.** The 2025 chained-journey transfer share should land much closer to the 2022 figure
(a third of boardings) than to the current 3.7%; if it does not, that is itself evidence about
what the `JourneyTransfer` tag actually encodes and belongs in the write-up. Only once this is
done does the re-anchoring question in §6af become answerable on its true terms — this item
does not itself decide whether to re-anchor, since reasons (i) and (iii) of that paragraph
(the car layer has no 2025 observation at all) are unaffected by it.

**Docs to update.** `METHODOLOGY.md` §6af (append, do not rewrite the existing "Re-anchoring"
paragraph — add a dated follow-on noting which of its three reasons this closes);
`docs/CORRIDOR_DEMAND_TASKS.md` B1d and B1c; `docs/PLAN_TIGHTENING_AND_SCENARIOS.md` item 9's
note on the 2025 layer.

### 10. All-or-nothing assignment link check (tasks B1, C3)

**Closes.** Step 36's car validation compares survey vehicles against counts on closed cordons
without an assignment — a desire-line proxy that cannot see through-traffic from beyond the
study area, double-counts crossings where a cordon polygon clips a road twice, and cannot
produce a *link-level* comparison at all (`METHODOLOGY.md` §6ah "Limits": "no link-level
comparison is possible without an assignment", explicitly task B1/C3).

**Inputs.** The 2022 car layer (`Output/ths2017/three_mode_2022/car_2022_*.csv`, both TAZ and
area level); the Emme network with counts (`Input/Network_with_Counts/
Emme_Links_Final_Res 2026-09-23.*`, LFS — 3,241 directional links, hourly PCE columns
`YARAM6`…`YARAM19`) already used by step 36.

**Method.** An all-or-nothing (AON) assignment — every OD pair's demand loaded entirely onto
its single shortest path by free-flow time, no capacity restraint or iteration — is the
simplest assignment that produces link-level modeled volumes, consistent with this project's
general preference for the simplest defensible method over a more elaborate one where the data
do not yet support the elaboration (the same reasoning that kept the bus coverage rule a
threshold rather than a full choice model until the evidence justified more). Build the
shortest-path tree over the Emme network's car links (the same link set step 36 already
filtered to `a`-mode, connectors excluded) for the 2022 car OD matrix, load every pair's
vehicle-converted demand (the same AM occupancy of 1.33 and PCE factor of 1.10 step 36 used)
onto its path, and sum modeled PCE per link and hour. Compare directly against the counted PCE
per link, superseding the cordon-crossing proxy with an actual link-by-link, direction-by-
direction table — this is what step 36 flagged as still needed.

**Outputs.** `Output/validation/car_assignment_link_volumes.csv` (link, direction, modeled AON
PCE, counted PCE, ratio), figure of modeled vs counted by link, extending
`Output/validation/car_cordon_map.png`'s style.

**Checks.** Report the ratio's spread across links and whether it is tighter or looser than
the cordon-level ratios of step 36 (0.58–0.90) — a link-level check should, if the OD matrix's
spatial pattern is reasonable, show a similar central tendency with more scatter (route choice
that a shortest-path assignment gets wrong on any single link averages out at the cordon
level). Note explicitly that AON has no capacity restraint, so a link at or above its capacity
under AON is not evidence of real congestion — only of relative demand.

**Docs to update.** `docs/CORRIDOR_DEMAND_TASKS.md` B1 (the "link-level comparison" bullet);
`METHODOLOGY.md` §6ah (append a follow-on paragraph, do not rewrite); `docs/
RED_TEAM_RESPONSE_2026-09-23.md` §2 condition 2 ("the rebuilt 2022 base has been compared with
at least one independent count on the Haifa trunk, by direction and hour") — this item is the
mechanism that condition needs but has not yet had.

### 11. Observed design-hour factors (task B1e, caveat 18)

**Closes.** Step 20's peak-hour factors (car 0.62–0.66, bus 0.59, from *survey departure
times*) are now known to overstate real peaking on both modes: step 36's road counts show the
busiest clock hour holds only 0.38–0.43 of the three hours (1.13–1.30 × an average hour, not
1.8–1.9 ×), and step 34's RavKav boarding taps show the same for transit, 0.43–0.48
(`METHODOLOGY.md` §6ah "The peak hour", §8 caveat 18). The step-20/27 factors should be read as
an **upper bound** on peaking, not the design value.

**Inputs.** Step 36's `Output/validation/car_cordon_count_hourly_profile.csv` (the counted
links' hourly PCE profile, clock-hour and sliding-60-minute-window versions — the sliding
window is ≈ 0.45–0.48, slightly above the clock-hour 0.42–0.45); step 34's
`Output/ravkav_2025/boarding_hour_peak_factors_2025.csv` (bus 0.475, Metronit 0.433, trunk
station areas 0.430–0.438).

**Method.** Recompute the corridor's peak-hour outputs — the ones step 20/27 currently produce
from survey departure times — using these observed factors in place of the survey-derived
ones: car at 0.42–0.48 (the sliding-window figure is the safer of the two, already the
recommendation in §6ah), transit at 0.43–0.48 (already recommended in §6af). This is a
substitution of the peaking factor, not a new demand model — the three-hour totals are
unchanged, only how much of them is placed in the design hour.

**Outputs.** Revised `Output/ths2017/study_taz/…peak_hour…` and `Output/corridor_v2/` peak-hour
tables recomputed on the observed factors, alongside the existing survey-departure-based
versions (keep both, labeled, since the survey-based factors are still what step 31/32's
transit-nest pivot was calibrated against and switching silently would change results without
a rerun of that calibration).

**Checks.** Report the revised design-hour link loads next to the current ones (e.g. the
busiest transit link's peak-hour value, currently 1,085 towards Nazareth on the survey factor)
and flag anywhere downstream (step 31/32's peak-hour outputs) that should be recomputed once
this substitution is adopted, rather than silently propagating two inconsistent peaking
conventions through the chain.

**Docs to update.** `docs/CORRIDOR_DEMAND_TASKS.md` B1e (already partly annotated with this
finding — close the "still open" line: "a link-crossing … hour once travel times exist");
`METHODOLOGY.md` §6r (append a follow-on paragraph noting the supersession, keep §6r's original
survey-based numbers as-is with a pointer forward) and §8 caveat 18 (mark addressed);
§0 lineage table's peak-hour rows; README if the headline peak-hour figures change.

---

## Suggested order

1. **Item 4** (bus GC overhead) and **item 1** (Google car uplift) — both quick, both close
   before item 3's TAZ-level rerun so the TAZ capture is not immediately stale.
2. **Items 2–3** together (OSM walking network, then TAZ-level capture) — one notebook, the
   plan's own largest expected revision to the central number.
3. **Item 5** (mixed regime + headways) and **item 11** (design-hour factors) — independent of
   2–3, can run in parallel with them.
4. **Items 6–7** (synthetic branches, bus-network response) — both bounding scenarios needing
   no client data; run once items 2–5 have settled the central case they bound.
5. **Item 9** (2025 journey chaining) and **item 10** (AON assignment) — independent
   validation work, can start any time; item 10 in particular does not depend on 1–8 at all.
6. **Item 8** (the uncertainty factorial) last, once items 1–7 have produced the factor ranges
   it needs to combine.

After every item: rerun 25 → 26 → 31 → 32 as needed, update `METHODOLOGY.md` §0, README, and
the relevant task/plan doc's status line — the checklist in Part 1 above, not a separate one
per item.
