"""The manifest of the chain: every step in run order.

The list order IS the run order (each step comes after every step it ``needs``); the ``stage`` is the
grouping used by the command line and by docs/PIPELINE.md.  Step numbers and section references are
those of METHODOLOGY.md.  Nothing here changes what a notebook does: a step's ``env`` is exactly the
environment METHODOLOGY §9 sets on its command line, and ``knobs`` lists the variables a notebook reads so
that an alternative run can be composed with ``python3 -m pipeline run --only <id> --env NAME=value``.

Conventions
  optional   not part of the default run: heavy rebuilds of committed upstream products, sensitivities,
             validation.  Selected with --with-optional or by name.
  cached     skipped when its outputs exist unless --force (products rebuilt only on a new input).
  inplace    the executed notebook replaces the committed one (the repository convention); alternative
             runs set inplace=False so the executed copy goes to the scratch folder instead, or name a
             committed copy with out_notebook (the PM / midday notebooks under periods/).
  restore    files to `git checkout --` after the run (an alternative run redraws default figures).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# packages every notebook needs; a step lists the extra ones it imports (import names)
BASE_PACKAGES = ("pandas", "numpy", "scipy", "matplotlib", "openpyxl")

STAGES: list[tuple[str, str, str]] = [
    # key, title, what the stage does
    ("upstream", "Upstream inputs from raw records",
     "Smart-card and survey files turned into the matrices the chain starts from. Heavy LFS inputs; outputs committed, rerun only when the raw files change."),
    ("base_year", "Base year 2022",
     "Survey matrices (car, transit) with the bus calibrated to RavKav; grown to 2022 and split into car / bus / taxi-type / rail; corridor profiles and peak hour; the deliverable 2022 matrices."),
    ("periods", "PM and midday base matrices",
     "Steps 15 and 16 run on the 16:00–19:00 and 09:00–15:00 windows (NOFIT_PERIOD); the PM layers feed the PM runs of the alternatives."),
    ("forecast", "Forecast 2040 / 2050",
     "The 2022 matrices grown to the BU and HS demographic scenarios."),
    ("corridor_lrt", "Corridor aggregation and LRT line",
     "The 25-area V2 aggregation, peak-hour factors per route, survey vs smart-card profiles, the drawn extension turned into stations and running times."),
    ("los", "Level of service",
     "Bus and Metronit times from the national timetable routed over measured bus speeds; the generalized-cost inventory between the 25 areas; the May 2026 car speed network."),
    ("capture", "LRT capture",
     "The incremental logit between the 25 areas and its forecast; the person-level λ; car and transit level of service zone by zone; the capture zone by zone; the uncertainty analysis."),
    ("alternatives", "LRT alternatives (the deliverable)",
     "Demand for main route + extension vs extension only, two running regimes, 2022–2050, AM and PM, zone by zone."),
    ("reports", "Reports",
     "Peak-hour factors for the charts, maps, the alternatives report, the comprehensive report in English and Hebrew, the decision deck."),
    ("sensitivity", "Sensitivities and alternative runs",
     "The same notebooks with other settings: 2026 car skim, LRT headway, bus competition, bus wait rule, out-of-vehicle weights, slower buses, TAZ bus construction. Executed copies go to the scratch folder."),
    ("validation", "Validation and diagnostics",
     "Tests against smart cards, road counts, the phone-based matrix and the Ministry of Transport guideline. Evidence, not products."),
]
STAGE_KEYS = [k for k, _, _ in STAGES]


@dataclass
class Step:
    id: str
    stage: str
    title: str
    path: str                                   # notebook or script, repository-relative
    step_no: str = ""                            # METHODOLOGY step number
    section: str = ""                            # METHODOLOGY section
    needs: tuple[str, ...] = ()                  # ids of the steps whose outputs this one reads
    inputs: tuple[str, ...] = ()                 # Input/ files it must have (LFS pointers are detected at check time)
    soft_inputs: tuple[str, ...] = ()            # inputs it can do without (dry run, or a check that is skipped)
    outputs: tuple[str, ...] = ()                # key files it writes, for --skip-done and the check
    env: dict[str, str] = field(default_factory=dict)   # the environment of this run
    knobs: tuple[str, ...] = ()                  # environment variables the notebook reads (documentation)
    optional: bool = False
    cached: bool = False
    inplace: bool = True
    out_notebook: str = ""
    restore: tuple[str, ...] = ()
    minutes: float = 1
    note: str = ""
    packages: tuple[str, ...] = ()               # import names beyond BASE_PACKAGES
    args: tuple[str, ...] = ()                   # script arguments

    @property
    def kind(self) -> str:
        return "notebook" if self.path.endswith(".ipynb") else "script"

    def __post_init__(self) -> None:
        if self.stage not in STAGE_KEYS:
            raise ValueError(f"{self.id}: unknown stage {self.stage!r}")


# ---------------------------------------------------------------- inputs ----
NB = "notebooks/current/"
DG = "notebooks/diagnostics/"
THS_TRIPS = "Input/THS_2017-2018/trips_ths_2017.xlsx"
THS_PERSONS = ("Input/THS_2017-2018/PersonsFin2.csv", "Input/THS_2017-2018/HHfinal.csv", "Input/THS_2017-2018/ACTIVITIES_DEC18_corrected.csv")
KEYS = "Input/Matrices/1270_02_09_2021_TAZ_North_keys.csv"
TAZ2636 = "Input/TAZ_2636_Keys.xlsx"
SUBMX = "Input/Submatrix_tazs.xlsx"
CORR_V2 = "Input/Corridor_TAZ_Agg_V2.xlsx"
ZONAL, ZONAL25 = "Input/Zonal_2020.csv", "Input/Zonal_BU_2025.csv"
TAZKEYS, SZLOC, GSNEW = "Input/taz_keys_from_shapefile.csv", "Input/sz_localities.csv", "Input/TAZ_GSnew.csv"
TAZ_SHP = "Input/TAZ_North/TAZ_North.shp"
GTFS = "Input/GTFS/israel-public-transportation.zip"
STREETS = "Input/BusSpeedData/Streets/Streets.shp"
BUS_SPEED = "Input/BusSpeedData/std_202605.csv"
CAR_SPEED = "Input/CarSpeedData/GoogleSpeed_202605/GoogleSpeed.shp"
EMME = "Input/Network_with_Counts/Emme_Links_Final_Res 2026-09-23.shp"
TRAIN = "Input/Matrices/Train_mtx_table.csv"
CELLULAR = "Input/Matrices/AvgDayHourlyTrips201819_1270_weekday_v1.csv"
HH_WEIGHTS = "Input/Matrices/households_with_weights.csv"
BUSPROB = "Input/6_9_BusProbability_ByTAZ.xlsx"
HF_LINE, HF_STATIONS = "Input/GeneralHalufa/hf_lrt_3.shp", "Input/GeneralHalufa/station_hf_lrt_3.geojson"
MAIN_LINE, MAIN_STOPS = "Input/Main_Nofit/Main_Nofit 2026-10-05.shp", "Input/Main_Nofit/Main_Nofit_StopsID.csv"
DEMOG = tuple(f"Input/Demographic_Forecast/Zonal_{s}.csv" for s in ("BU_2040", "BU_2050", "HS_2040", "HS_2050"))
RAVKAV_2022 = tuple(f"Input/BusRavKav/May_2022/trips_table_2022-05-{d}.csv" for d in ("03", "17", "24", "31"))
RAVKAV_2025 = ("Input/BusRavKav/2025/Buses_RavKav.csv", "Input/BusRavKav/2025/Metronit_RavKav_Data.csv",
               "Input/BusRavKav/2025/Rail_RavKav_Data.csv", "Input/BusRavKav/Stops_In_North/stops_in_taz_north.csv")
GEO = ("geopandas", "shapely", "pyproj")
SURVEY_KEYS = (THS_TRIPS, KEYS, TAZ2636, SUBMX, ZONAL, TAZKEYS)

# figures the default runs draw that an alternative run of the same notebook redraws (METHODOLOGY §9)
FIG_26 = ("Output/figures/gc_first_fill_trunk_v2.png", "Output/figures/gc_bus_gtfs_vs_survey.png")
FIG_31 = ("Output/figures/skims_logit_car_vs_transit.png", "Output/figures/skims_trunk_link_flows_bus_vs_lrt.png")
FIG_32 = ("Output/figures/lrt_capture_forecast_2040_2050.png",)

CAR_NETWORK_KNOBS = ("CAR_SOURCE", "BUS_WAIT_RULE", "LRT_HEADWAY")
S31_KNOBS = ("GC_SOURCE_DIR", "LRT_HEADWAY", "BUS_COMPETITION", "OVT_TAG", "W_WALK", "W_WALK_LRT", "W_WAIT",
             "TRANSFER_PEN", "BRT_LRT_TRANSFER_PEN", "STATION_ACCESS_UG", "STATION_ACCESS_GR")


def _mot_period_copies(stem: str, title: str, needs: tuple[str, ...], inputs: tuple[str, ...], periods=("PM", "MD"),
                       source: str | None = None, packages: tuple[str, ...] = ()) -> list[Step]:
    """A Ministry-of-Transport validation notebook run on the PM / midday windows into notebooks/diagnostics/periods/."""
    src = source or f"{DG}{stem}.ipynb"
    return [Step(id=f"mot_{stem.split('_')[2].lower()}_{p.lower()}", stage="validation", section="6ar",
                 title=f"{title}, {'PM 16:00–19:00' if p == 'PM' else 'midday 09:00–15:00'}", path=src,
                 needs=needs, inputs=inputs, env={"NOFIT_PERIOD": p}, knobs=("NOFIT_PERIOD",), optional=True,
                 out_notebook=f"{DG}periods/{stem}_{p}.ipynb", packages=packages, minutes=1.5) for p in periods]


# ---------------------------------------------------------------- the steps, in run order ----
STEPS: list[Step] = [
    # ---- upstream: raw records -> the matrices the chain starts from (committed outputs) ----
    Step("s05", "upstream", "Survey trips file extracted by day and mode (area matrices, study-area zone matrices)",
         f"{NB}THS_2017_trips_matrices.ipynb", "5", "6c",
         inputs=(THS_TRIPS, KEYS, TAZ2636, GSNEW), soft_inputs=(CELLULAR,),
         outputs=("Output/ths2017/matrix_avg_ALL.csv", "Output/ths2017/study_taz/matrix_avg_ALL_taz.csv"),
         optional=True, minutes=3, note="First-generation product; the chain reads the study-area legend it left under Output/ths2017/study_taz/."),
    Step("s07", "upstream", "Trips per resident in the morning peak (≈ 0.83)", f"{NB}THS_2017_trip_generation.ipynb", "7", "6e",
         inputs=(THS_TRIPS, KEYS, TAZ2636, GSNEW), outputs=("Output/ths2017/trip_generation_summary.csv",), optional=True),
    Step("s08", "upstream", "May 2022 RavKav records → average-Tuesday morning bus journey matrix by zone, boardings and alightings",
         f"{NB}BusRavKav_matrix.ipynb", "8", "6f", inputs=RAVKAV_2022 + (TAZ_SHP,),
         outputs=("Output/bus/bus_od_taz_avg.csv", "Output/bus/bus_boardings_alightings_taz.csv", "Output/bus/bus_stops_taz.csv"),
         optional=True, minutes=1, packages=GEO, note="The four trip tables are 1.9 GB on LFS. Step 15 reads bus_od_taz_avg.csv as the calibration prior (RavKav's own alightings)."),
    Step("s08p", "upstream", "Step 8 for the PM-peak and midday windows", f"{NB}BusRavKav_matrix_periods.ipynb", "—", "6ar",
         needs=("s08",), inputs=RAVKAV_2022,
         outputs=("Output/bus/periods/bus_od_taz_avg_PM.csv", "Output/bus/periods/bus_od_taz_avg_MD.csv", "Output/bus/periods/bus_hourly_journeys_2022.csv"),
         optional=True, minutes=1),
    Step("s09", "upstream", "RavKav volumes × on-board survey destinations (comparison only since 23 Sep 2026)",
         f"{NB}BusOnBoard_matrix.ipynb", "9", "6g", needs=("s08", "s05"), inputs=(BUSPROB, SUBMX),
         outputs=("Output/bus/bus_od_taz_new.csv", "Output/bus/bus_od_area_new_filtered.csv"), optional=True,
         note="Step 15 still reads bus_od_taz_new.csv for the on-board comparison columns."),
    Step("s10", "upstream", "2019 rail smart-card station-to-station matrix (its composite transit matrix is historical)",
         f"{NB}Transit_complete_matrix.ipynb", "10", "6h", needs=("s09",), inputs=(TRAIN, SUBMX),
         outputs=("Output/train/train_od_taz_6_9.csv", "Output/train/train_od_area.csv"), optional=True),

    # ---- base year 2022 ----
    Step("s15", "base_year", "Survey-only car and transit matrices; bus calibrated to RavKav per origin × segment",
         f"{NB}THS_2017_two_mode_matrix.ipynb", "15", "6m", needs=("s08", "s09"), inputs=SURVEY_KEYS + (SZLOC,),
         outputs=("Output/ths2017/two_mode/car_taz.csv", "Output/ths2017/two_mode/bus_calibrated_taz.csv", "Output/ths2017/two_mode/bus_survey_taz.csv"),
         knobs=("NOFIT_PERIOD",), minutes=2),
    Step("s16", "base_year", "Grows to 2022; splits into car / bus / taxi-type / rail layers", f"{NB}THS_2017_three_mode_2022.ipynb", "16", "6n",
         needs=("s15", "s10"), inputs=(KEYS, TRAIN, SUBMX, ZONAL, ZONAL25, TAZKEYS),
         outputs=tuple(f"Output/ths2017/three_mode_2022/{m}_2022_taz.csv" for m in ("car", "bus", "taxi", "rail")),
         knobs=("NOFIT_PERIOD",), minutes=2),
    Step("s17", "base_year", "Potential movements along the line, link by link, three hours", f"{NB}Corridor_flow_profile_survey_2022.ipynb", "17", "6o",
         needs=("s16",), outputs=("Output/ths2017/three_mode_2022/corridor_link_flows_transit_2022.csv", "Output/ths2017/three_mode_2022/corridor_link_flows_total_2022.csv")),
    Step("s18", "base_year", "The survey-based transit profile against the smart-card one", f"{NB}Corridor_profile_hybrid_vs_ticketing.ipynb", "18", "6p",
         needs=("s17", "s15", "s08", "s10"), inputs=(KEYS, SUBMX, TAZKEYS), outputs=("Output/figures/corridor_profile_hybrid_vs_ticketing.png",),
         note="Comparison: evidence, not a product."),
    Step("s20", "base_year", "Peak hour and peak-hour factors from the survey's departure times", f"{NB}Corridor_peak_hour_2022.ipynb", "20", "6r",
         needs=("s16", "s17"), inputs=SURVEY_KEYS,
         outputs=("Output/ths2017/three_mode_2022/peak_hour_factors.csv", "Output/ths2017/three_mode_2022/corridor_link_flows_peak_hour_2022.csv")),
    Step("s22", "base_year", "The deliverable car / transit / total matrices for 2022 (778 zones) with their manifest", f"{NB}Final_matrices_2022.ipynb", "22", "6t",
         needs=("s16",), inputs=(SUBMX,),
         outputs=("Output/final_2022/car_2022_taz.csv", "Output/final_2022/transit_2022_taz.csv", "Output/final_2022/total_2022_taz.csv",
                  "Output/final_2022/final_2022_long.csv.gz", "Output/final_2022/MANIFEST.csv")),
    Step("s36", "validation", "The car layer against road counts on six closed cordons", f"{DG}Car_cordon_counts_validation.ipynb", "36", "6ah",
         needs=("s16", "s20"), inputs=(EMME, TAZ_SHP, THS_TRIPS, SZLOC),
         outputs=("Output/validation/car_cordon_counts.csv", "Output/validation/car_cordon_crossing_links.csv", "Output/validation/car_cordon_count_hourly_profile.csv"),
         optional=True, packages=GEO, note="Runs here, before step 27, because step 27 reads its cordon table for the peak-hour comparison."),
    Step("s34", "upstream", "The 2025 smart-card extracts → boardings by stop and zone, bus + Metronit OD, rail OD, peak factors",
         f"{NB}RavKav_2025_boardings_matrix.ipynb", "34", "6af", needs=("s08", "s09", "s10", "s16"),
         inputs=RAVKAV_2025 + (BUSPROB, CORR_V2, SUBMX, TAZ_SHP), soft_inputs=(GTFS,),
         outputs=("Output/ravkav_2025/bus_od_taz_2025.csv", "Output/ravkav_2025/boardings_by_taz_2025.csv", "Output/ravkav_2025/boarding_hour_peak_factors_2025.csv"),
         optional=True, minutes=5, packages=GEO, note="3.3 GB on LFS. Step 27 reads its peak factors; the validation reads its OD tables."),

    # ---- PM and midday base matrices (NOFIT_PERIOD) ----
    Step("s15_pm", "periods", "Step 15 on the PM window 16:00–19:00", f"{NB}THS_2017_two_mode_matrix.ipynb", "15", "6ar",
         needs=("s08p", "s09"), inputs=SURVEY_KEYS + (SZLOC,), env={"NOFIT_PERIOD": "PM"}, knobs=("NOFIT_PERIOD",), optional=True,
         out_notebook=f"{NB}periods/THS_2017_two_mode_matrix_PM.ipynb", outputs=("Output/ths2017/two_mode_pm/car_taz.csv",), minutes=2),
    Step("s16_pm", "periods", "Step 16 on the PM window (the PM 2022 layers of the alternatives)", f"{NB}THS_2017_three_mode_2022.ipynb", "16", "6ar",
         needs=("s15_pm", "s10"), inputs=(KEYS, TRAIN, SUBMX, ZONAL, ZONAL25, TAZKEYS), env={"NOFIT_PERIOD": "PM"}, knobs=("NOFIT_PERIOD",), optional=True,
         out_notebook=f"{NB}periods/THS_2017_three_mode_2022_PM.ipynb",
         outputs=tuple(f"Output/ths2017/three_mode_2022_pm/{m}_2022_taz.csv" for m in ("car", "bus", "rail")), minutes=2),
    Step("s15_md", "periods", "Step 15 on the midday window 09:00–15:00", f"{NB}THS_2017_two_mode_matrix.ipynb", "15", "6ar",
         needs=("s08p", "s09"), inputs=SURVEY_KEYS + (SZLOC,), env={"NOFIT_PERIOD": "MD"}, knobs=("NOFIT_PERIOD",), optional=True,
         out_notebook=f"{NB}periods/THS_2017_two_mode_matrix_MD.ipynb", outputs=("Output/ths2017/two_mode_md/car_taz.csv",), minutes=2),
    Step("s16_md", "periods", "Step 16 on the midday window", f"{NB}THS_2017_three_mode_2022.ipynb", "16", "6ar",
         needs=("s15_md", "s10"), inputs=(KEYS, TRAIN, SUBMX, ZONAL, ZONAL25, TAZKEYS), env={"NOFIT_PERIOD": "MD"}, knobs=("NOFIT_PERIOD",), optional=True,
         out_notebook=f"{NB}periods/THS_2017_three_mode_2022_MD.ipynb", outputs=("Output/ths2017/three_mode_2022_md/car_2022_taz.csv",), minutes=2),

    # ---- forecast ----
    Step("s23", "forecast", "Grows the 2022 matrices to BU / HS × 2040 / 2050", f"{NB}Forecast_matrices_TAZ_2040_2050.ipynb", "23", "6u",
         needs=("s22", "s17"), inputs=(KEYS, SUBMX, TAZ_SHP, ZONAL, ZONAL25, TAZKEYS), soft_inputs=DEMOG,
         outputs=("Output/forecast_taz/BU_2050/transit_BU_2050_taz.csv", "Output/forecast_taz/BU_2050/car_BU_2050_taz.csv", "Output/forecast_taz/summary_by_class.csv"),
         packages=GEO, minutes=2, note="Without the four Zonal_*.csv forecasts (LFS) the notebook makes a dry run into Output/forecast_taz/dry_run/."),
    Step("demog", "forecast", "BU vs HS forecasts compared by area", f"{NB}Demographic_scenario_comparison.ipynb", "—", "—",
         inputs=DEMOG + (SUBMX,), outputs=("Output/demographics/scenario_comparison_area.csv",), optional=True),

    # ---- corridor aggregation and the LRT line ----
    Step("s27", "corridor_lrt", "Peak-hour factors per route and direction on the 25-area V2 aggregation", f"{NB}Corridor_peak_hour_V2_routes.ipynb", "27", "6y",
         needs=("s20", "s34", "s36"), inputs=SURVEY_KEYS + (CORR_V2,),
         outputs=("Output/corridor_v2/peak_hour_factors_v2.csv", "Output/corridor_v2/peak_hour_factors_v2_applied.csv"),
         note="Runs before step 24, which reads its factors; reads the committed cordon counts (step 36) and 2025 boarding factors (step 34)."),
    Step("s24", "corridor_lrt", "Potential movements on the V2 aggregation: three routes and a tree network", f"{NB}Corridor_flow_profile_V2_routes.ipynb", "24", "6v",
         needs=("s27", "s16"), inputs=(CORR_V2, SUBMX, ZONAL),
         outputs=("Output/corridor_v2/car_2022_area_v2.csv", "Output/corridor_v2/transit_2022_area_v2.csv", "Output/corridor_v2/corridor_v2_network_link_flows.csv", "Output/corridor_v2/area_legend_v2.csv")),
    Step("s28", "corridor_lrt", "Survey vs smart-card transit profiles on the V2 routes", f"{NB}Corridor_profile_V2_survey_vs_ticketing.ipynb", "28", "6z",
         needs=("s24", "s15", "s08", "s10"), inputs=(CORR_V2,), outputs=("Output/corridor_v2/corridor_v2_survey_vs_ticketing.csv",), note="Comparison: evidence, not a product."),
    Step("s25", "corridor_lrt", "The drawn extension → 24 stations and station-to-station times (several running regimes)", f"{NB}LRT_line_stations_travel_time.ipynb", "25", "6w",
         inputs=(HF_LINE, HF_STATIONS, CORR_V2, TAZ_SHP, ZONAL), soft_inputs=(GTFS,),
         outputs=("Output/lrt_v2/lrt_stations_hf_lrt_3.csv", "Output/lrt_v2/lrt_area_representative_station.csv", "Output/lrt_v2/lrt_station_times_all_underground.csv", "Output/lrt_v2/lrt_area_ivt_all_underground.csv"),
         packages=GEO),

    # ---- level of service ----
    Step("s29", "los", "Bus and Metronit level of service per zone from the national timetable; timetable skim between areas", f"{NB}GTFS_bus_LOS_TAZ.ipynb", "29", "6aa",
         inputs=(CORR_V2, TAZ_SHP), soft_inputs=(GTFS,),
         outputs=("Output/gtfs/bus_los_taz.csv", "Output/gtfs/bus_direct_skim_area_v2.csv", "Output/gtfs/stops_study_area.csv", "Output/gtfs/stop_times_study_area_am_trips.csv.gz"),
         packages=GEO, minutes=8, note="Without the GTFS archive (181 MB on LFS) the notebook makes a dry run into Output/gtfs/dry_run/."),
    Step("s30", "los", "Timetable trips routed over measured May 2026 bus speeds → observed in-vehicle times", f"{NB}GTFS_bus_observed_times.ipynb", "30", "6ab",
         needs=("s29",), inputs=(BUS_SPEED, STREETS, CORR_V2),
         outputs=("Output/gtfs/bus_observed_skim_area_v2.csv", "Output/gtfs/bus_segments_observed.csv", "Output/gtfs/bus_trips_observed.csv.gz"),
         packages=GEO, minutes=5, note="The bus speed file is 311 MB on LFS."),
    Step("s26", "los", "Generalized-cost components per mode between the 25 areas, with a gap inventory", f"{NB}GC_data_inventory_and_skims.ipynb", "26", "6x",
         needs=("s24", "s25", "s29", "s30"), inputs=SURVEY_KEYS + (CORR_V2, TAZ_SHP, STREETS, BUS_SPEED),
         outputs=("Output/gc/gc_area_v2_car.csv", "Output/gc/gc_area_v2_bus.csv", "Output/gc/gc_area_v2_lrt_all_underground.csv", "Output/gc/gc_components_area_v2_long.csv", "Output/gc/gc_data_inventory.csv"),
         knobs=CAR_NETWORK_KNOBS, packages=GEO, minutes=4),
    Step("s43", "los", "May 2026 car speed network clipped to the study area", f"{NB}Car_speed_network_North.ipynb", "43", "6am",
         inputs=(CAR_SPEED, STREETS, TAZ_SHP), soft_inputs=(EMME,),
         outputs=("Output/car_speed/GoogleSpeed_202605_North.gpkg", "Output/car_speed/car_speed_hourly_summary_north.csv"),
         packages=GEO + ("pyogrio", "shapefile")),

    # ---- LRT capture ----
    Step("s31", "capture", "Complete skims per mode; the pivoted LRT capture model between the 25 areas (central 4,250 trips)", f"{NB}Mode_skims_and_flow_comparison.ipynb", "31", "6ac",
         needs=("s24", "s25", "s26", "s27", "s29"), inputs=(CORR_V2, ZONAL),
         outputs=("Output/skims/pair_flows_and_skims_2022.csv", "Output/skims/lrt_capture_scenarios.csv", "Output/skims/skim_bus_gc.csv", "Output/skims/skim_car_gc.csv"),
         knobs=S31_KNOBS, minutes=3),
    Step("s32", "capture", "The same capture on the 2040 / 2050 sets", f"{NB}LRT_capture_forecast_2040_2050.ipynb", "32", "6ad",
         needs=("s31", "s23"), inputs=(CORR_V2,), outputs=("Output/skims/forecast/lrt_capture_scenarios_forecast.csv", "Output/skims/forecast/lrt_boardings_forecast.csv"),
         knobs=("SK_DIR",)),
    Step("s33", "capture", "Person-level logit on the survey: estimates λ (0.035) with car availability held constant", f"{NB}Mode_choice_person_level.ipynb", "33", "6ae",
         needs=("s31",), inputs=(THS_TRIPS,) + THS_PERSONS + (TAZ2636, KEYS, CORR_V2),
         outputs=("Output/mode_choice/lambda_summary.csv", "Output/mode_choice/lambda_estimates.csv"),
         knobs=("SK_DIR", "SKIM_DIR"), packages=("statsmodels",), minutes=1),
    Step("s37", "capture", "Car times between the 25 areas at 2026 speeds, against the survey's times", f"{NB}Car_skim_2026_network.ipynb", "37", "6an",
         needs=("s43", "s25", "s26", "s31"), inputs=(STREETS, CORR_V2, TAZ_SHP),
         outputs=("Output/gc/car_ivt_network_area_v2.csv", "Output/gc/car_network_vs_survey_summary.csv"), packages=GEO + ("pyogrio",)),
    Step("s44", "capture", "Car and transit level of service for every zone pair (781 zones), aggregated to the 25 areas", f"{NB}LOS_skims_TAZ_and_V2.ipynb", "44", "6ao",
         needs=("s43", "s29", "s30", "s31", "s37"), inputs=(STREETS, CORR_V2, TAZ_SHP, ZONAL),
         outputs=("Output/los/car_los_taz.csv.gz", "Output/los/transit_los_taz.csv.gz", "Output/los/los_area_v2_pairs.csv"), packages=GEO + ("pyogrio",), minutes=1.5),
    Step("s39", "capture", "The capture run zone by zone (diagnostic; not adopted)", f"{NB}LRT_capture_TAZ.ipynb", "39", "6ap",
         needs=("s44", "s31", "s22", "s24", "s26", "s29"), inputs=(CORR_V2, ZONAL),
         outputs=("Output/skims/taz/lrt_capture_scenarios_taz.csv",), knobs=("BUS_TAZ_SOURCE",), minutes=0.5),

    # ---- sensitivities and alternative runs (executed copies to the scratch folder) ----
    Step("v26_net", "sensitivity", "Step 26 on the May 2026 car skim (CAR_SOURCE=network) → Output/skims/car_network/", f"{NB}GC_data_inventory_and_skims.ipynb", "26", "6x",
         needs=("s26", "s37"), inputs=SURVEY_KEYS + (CORR_V2, TAZ_SHP, STREETS, BUS_SPEED), env={"CAR_SOURCE": "network"}, knobs=CAR_NETWORK_KNOBS,
         outputs=("Output/skims/car_network/gc_components_area_v2_long.csv",), optional=True, inplace=False, restore=FIG_26, packages=GEO, minutes=4),
    Step("v31_net", "sensitivity", "Step 31 on the 2026 car skim (GC_SOURCE_DIR=Output/skims/car_network)", f"{NB}Mode_skims_and_flow_comparison.ipynb", "31", "6ac",
         needs=("v26_net",), inputs=(CORR_V2, ZONAL), env={"GC_SOURCE_DIR": "Output/skims/car_network"}, knobs=S31_KNOBS,
         outputs=("Output/skims/car_network/lrt_capture_scenarios.csv",), optional=True, inplace=False, restore=FIG_31, minutes=3),
    Step("v32_net", "sensitivity", "Step 32 on the 2026 car skim", f"{NB}LRT_capture_forecast_2040_2050.ipynb", "32", "6ad",
         needs=("v31_net", "s23"), inputs=(CORR_V2,), env={"SK_DIR": "Output/skims/car_network"}, knobs=("SK_DIR",),
         outputs=("Output/skims/car_network/forecast/lrt_capture_scenarios_forecast.csv",), optional=True, inplace=False, restore=FIG_32),
    Step("v33_net", "sensitivity", "Step 33 on the 2026 car skim (λ 0.040 vs 0.035)", f"{NB}Mode_choice_person_level.ipynb", "33", "6ae",
         needs=("v31_net",), inputs=(THS_TRIPS,) + THS_PERSONS + (TAZ2636, KEYS, CORR_V2), env={"SK_DIR": "Output/skims/car_network"}, knobs=("SK_DIR", "SKIM_DIR"),
         outputs=("Output/mode_choice/car_network/lambda_summary.csv", "Output/figures/mode_choice_person_level_by_segment_car_network.png"), optional=True, inplace=False, packages=("statsmodels",)),
    Step("v26_wait", "sensitivity", "Step 26 with the bus wait on the busiest single line (BUS_WAIT_RULE=best_line)", f"{NB}GC_data_inventory_and_skims.ipynb", "26", "6x",
         needs=("s26",), inputs=SURVEY_KEYS + (CORR_V2, TAZ_SHP, STREETS, BUS_SPEED), env={"BUS_WAIT_RULE": "best_line"}, knobs=CAR_NETWORK_KNOBS,
         outputs=("Output/skims/bus_wait_best_line/gc_components_area_v2_long.csv",), optional=True, inplace=False, restore=FIG_26, packages=GEO, minutes=4),
    Step("v31_wait", "sensitivity", "Step 31 on the best-line bus wait", f"{NB}Mode_skims_and_flow_comparison.ipynb", "31", "6ac",
         needs=("v26_wait",), inputs=(CORR_V2, ZONAL), env={"GC_SOURCE_DIR": "Output/skims/bus_wait_best_line"}, knobs=S31_KNOBS,
         outputs=("Output/skims/bus_wait_best_line/lrt_capture_scenarios.csv",), optional=True, inplace=False, restore=FIG_31, minutes=3),
    Step("v26_h75", "sensitivity", "Step 26 with a 7.5-minute LRT headway → Output/skims/lrt_headway_7.5/", f"{NB}GC_data_inventory_and_skims.ipynb", "26", "6x",
         needs=("s26",), inputs=SURVEY_KEYS + (CORR_V2, TAZ_SHP, STREETS, BUS_SPEED), env={"LRT_HEADWAY": "7.5"}, knobs=CAR_NETWORK_KNOBS,
         outputs=("Output/skims/lrt_headway_7.5/gc_components_area_v2_long.csv",), optional=True, inplace=False, restore=FIG_26, packages=GEO, minutes=4),
    Step("v31_h75", "sensitivity", "Step 31 with a 7.5-minute LRT headway", f"{NB}Mode_skims_and_flow_comparison.ipynb", "31", "6ac",
         needs=("v26_h75",), inputs=(CORR_V2, ZONAL), env={"LRT_HEADWAY": "7.5", "GC_SOURCE_DIR": "Output/skims/lrt_headway_7.5"}, knobs=S31_KNOBS,
         outputs=("Output/skims/lrt_headway_7.5/lrt_capture_scenarios.csv",), optional=True, inplace=False, restore=FIG_31, minutes=3),
    Step("v26_h10", "sensitivity", "Step 26 with a 10-minute LRT headway → Output/skims/lrt_headway_10/", f"{NB}GC_data_inventory_and_skims.ipynb", "26", "6x",
         needs=("s26",), inputs=SURVEY_KEYS + (CORR_V2, TAZ_SHP, STREETS, BUS_SPEED), env={"LRT_HEADWAY": "10"}, knobs=CAR_NETWORK_KNOBS,
         outputs=("Output/skims/lrt_headway_10/gc_components_area_v2_long.csv",), optional=True, inplace=False, restore=FIG_26, packages=GEO, minutes=4),
    Step("v31_h10", "sensitivity", "Step 31 with a 10-minute LRT headway", f"{NB}Mode_skims_and_flow_comparison.ipynb", "31", "6ac",
         needs=("v26_h10",), inputs=(CORR_V2, ZONAL), env={"LRT_HEADWAY": "10", "GC_SOURCE_DIR": "Output/skims/lrt_headway_10"}, knobs=S31_KNOBS,
         outputs=("Output/skims/lrt_headway_10/lrt_capture_scenarios.csv",), optional=True, inplace=False, restore=FIG_31, minutes=3),
    Step("v31_trunc", "sensitivity", "Step 31 without the parallel trunk bus (BUS_COMPETITION=truncated) → Output/skims/bus_truncated/", f"{NB}Mode_skims_and_flow_comparison.ipynb", "31", "6ac",
         needs=("s31",), inputs=(CORR_V2, ZONAL), env={"BUS_COMPETITION": "truncated"}, knobs=S31_KNOBS,
         outputs=("Output/skims/bus_truncated/lrt_capture_scenarios.csv",), optional=True, inplace=False, restore=FIG_31, minutes=3),
    Step("ovt_chain", "sensitivity", "Steps 31 → 33 on every out-of-vehicle parameter set of Output/ovt_research/parameter_sets.csv", "tools/ovt_run_chain.py", "—", "6al",
         needs=("s31", "s33"), inputs=(CORR_V2, ZONAL, THS_TRIPS) + THS_PERSONS + (TAZ2636, KEYS),
         outputs=("Output/skims/ovt_empirical_central/lrt_capture_scenarios.csv", "Output/mode_choice/ovt_empirical_central/lambda_summary.csv"),
         optional=True, packages=("statsmodels", "nbformat", "nbclient"), minutes=30, note="Seven sets × (3 + 1) minutes; executed copies go to OVT_NB_OUT (default /tmp/ovt_nb)."),
    Step("ovt_summary", "sensitivity", "The OVT reruns collected into one table", "tools/ovt_chain_summary.py", "—", "6al",
         needs=("ovt_chain",), outputs=("Output/ovt_research/chain_results.csv",), optional=True),
    Step("ovt_evidence", "sensitivity", "The OVT literature extracts consolidated into one evidence table", "tools/ovt_build_evidence_table.py", "—", "6al",
         outputs=("Output/ovt_research/evidence_table.csv",), optional=True),
    Step("ovt_screen", "sensitivity", "Screen of the capture's sensitivity to the OVT weights on the saved skims (writes nothing)", "tools/ovt_sensitivity_screen.py", "—", "6al",
         needs=("s31",), optional=True),
    Step("v39_apw", "sensitivity", "Step 39 with the hand-over's bus construction (BUS_TAZ_SOURCE=area_plus_walk)", f"{NB}LRT_capture_TAZ.ipynb", "39", "6ap",
         needs=("s39",), inputs=(CORR_V2, ZONAL), env={"BUS_TAZ_SOURCE": "area_plus_walk"}, knobs=("BUS_TAZ_SOURCE",),
         outputs=("Output/skims/taz/bus_area_plus_walk/lrt_capture_scenarios_taz.csv",), optional=True, inplace=False, minutes=0.5),

    # ---- the uncertainty analysis, which reads the sensitivity folders above ----
    Step("s40", "capture", "Which assumptions move the capture most (factorial and tornado)", f"{NB}LRT_capture_uncertainty.ipynb", "40", "6ak",
         needs=("s31", "v26_h75", "v31_h75", "v26_h10", "v31_h10", "v31_trunc", "ovt_chain"),
         outputs=("Output/skims/uncertainty/lrt_capture_tornado.csv", "Output/skims/uncertainty/lrt_capture_factorial.csv"),
         note="Reads the committed sensitivity folders under Output/skims/ (headway, bus competition, OVT sets); the two truncated cells at headway 7.5 and 10 were one-off runs copied by hand (§6ak)."),

    # ---- the LRT alternatives ----
    Step("gtfs45", "alternatives", "Study-area stop times of the GTFS day for the AM and PM windows, rail and Metronit trips", "tools/gtfs_extract_periods.py", "45", "6aq",
         needs=("s29",), inputs=(GTFS,),
         outputs=("Output/gtfs/stop_times_study_area_am_trips_v45.csv.gz", "Output/gtfs/stop_times_study_area_pm_trips_v45.csv.gz", "Output/gtfs/stop_times_study_area_rail_day.csv.gz"),
         cached=True, minutes=4, note="Committed; rerun only with a new feed (skipped while its outputs exist unless --force)."),
    Step("s45", "alternatives", "THE DELIVERABLE: LRT demand for main + extension vs extension only, two regimes, 2022–2050, AM and PM", f"{NB}LRT_alternatives_demand.ipynb", "45", "6aq",
         needs=("s22", "s23", "s25", "s29", "s30", "s43", "gtfs45", "s16_pm"), inputs=(MAIN_LINE, MAIN_STOPS, CORR_V2, STREETS, TAZ_SHP, ZONAL), soft_inputs=(GTFS,),
         outputs=("Output/alternatives/demand_summary.csv", "Output/alternatives/time_on_route.csv", "Output/alternatives/stations_main_ext.csv", "Output/alternatives/skims_summary.csv"),
         knobs=("ALT_OUT", "BUS_SLOWDOWN"), packages=GEO + ("pyogrio",), minutes=3),

    # ---- the slower-bus sensitivity of step 45, read by the comprehensive report ----
    Step("v45_slow", "sensitivity", "Step 45 with slower buses in the forecast years → Output/alternatives_bus_slow/", f"{NB}LRT_alternatives_demand.ipynb", "45", "6aq",
         needs=("s45",), inputs=(MAIN_LINE, MAIN_STOPS, CORR_V2, STREETS, TAZ_SHP, ZONAL),
         env={"BUS_SLOWDOWN": "BU_2040:1.10,BU_2050:1.20,HS_2040:1.10,HS_2050:1.20", "ALT_OUT": "Output/alternatives_bus_slow"}, knobs=("ALT_OUT", "BUS_SLOWDOWN"),
         outputs=("Output/alternatives_bus_slow/demand_summary.csv",), optional=True, inplace=False, packages=GEO + ("pyogrio",), minutes=3),

    # ---- reports ----
    Step("r_phf", "reports", "Peak-hour factors for the charts: step 27's method on the PM window beside the AM values", "tools/peak_hour_factors_periods.py", "—", "6aq",
         needs=("s27", "s45"), inputs=SURVEY_KEYS + (CORR_V2,),
         outputs=("Output/corridor_v2/peak_hour_factors_v2_pm.csv", "Output/alternatives/peak_hour_factors.csv"), minutes=2),
    Step("r_maps", "reports", "Maps of time, demand, line loads and differences for the alternatives (peak hour)", "tools/build_alternatives_maps.py", "—", "6aq",
         needs=("s45", "r_phf"), inputs=(TAZ_SHP,), outputs=("Output/figures/alternatives/map_diff_main_vs_ext_AM_BU_2040.png",), packages=GEO, minutes=1.5),
    Step("r_alt", "reports", "The alternatives workbook and Word report", "tools/build_alternatives_report.py", "—", "6aq",
         needs=("s45", "r_maps"), inputs=(CORR_V2,), outputs=("Output/alternatives/LRT_alternatives_matrices.xlsx", "reports/LRT_Alternatives_Demand_Report.docx"), packages=("docx",)),
    Step("r_comp", "reports", "The comprehensive report for decision-makers (English) and its charts", "tools/build_comprehensive_report.py", "—", "—",
         needs=("s45", "r_phf", "r_maps", "s33", "v33_net", "v45_slow"),
         outputs=("reports/Nofit_LRT_Extension_Comprehensive_Report.docx", "Output/figures/comprehensive/areaflow_lrt_AM_2022.png"), packages=("docx",), minutes=1,
         note="Also reads the committed slower-bus run (Output/alternatives_bus_slow/) and the λ on the 2026 car skim (Output/mode_choice/car_network/)."),
    Step("r_comp_he", "reports", "The same report in simple Hebrew", "tools/build_comprehensive_report_he.py", "—", "—",
         needs=("r_comp",), outputs=("reports/Nofit_LRT_Extension_Comprehensive_Report_HE.docx",), packages=("docx",), minutes=1),
    Step("r_deck", "reports", "The decision deck, English and Hebrew (self-contained HTML)", "tools/build_decision_deck.py", "—", "—",
         needs=("r_comp", "r_comp_he"), outputs=("reports/Nofit_LRT_Extension_Decision_Deck.html", "reports/Nofit_LRT_Extension_Decision_Deck_HE.html"), packages=("docx",)),

    # ---- validation and diagnostics ----
    Step("t_metrics", "validation", "Hand-checked tests of the validation statistics module", "tools/test_validation_metrics.py", "—", "6ar", optional=True, minutes=0.1),
    Step("s12", "validation", "Cosine and GEH tests: survey vs phone-based vs hybrid matrices", f"{DG}THS_2017_cosine_GEH_tests.ipynb", "12", "6j",
         needs=("s05",), inputs=(THS_TRIPS, KEYS, TAZ2636, SUBMX, GSNEW, CELLULAR), outputs=("Output/ths2017/tests/cosine_geh_summary.csv",), optional=True, minutes=2),
    Step("s13", "validation", "Kolmogorov–Smirnov tests of the same matrices", f"{DG}THS_2017_KS_tests.ipynb", "13", "6k",
         needs=("s05",), inputs=(THS_TRIPS, KEYS, TAZ2636, SUBMX, TAZ_SHP, CELLULAR), optional=True, packages=GEO, minutes=2),
    Step("s14", "validation", "Structural similarity (MSSIM) tests of the same matrices", f"{DG}THS_2017_MSSIM_tests.ipynb", "14", "6l",
         needs=("s05",), inputs=(THS_TRIPS, KEYS, TAZ2636, SUBMX, TAZ_SHP, CELLULAR), optional=True, packages=GEO, minutes=2),
    Step("s19", "validation", "Regression test: the historical hybrid does not conserve its superzone blocks (committed outputs only)", f"{DG}Hybrid_superzone_conservation_test.ipynb", "19", "6q",
         inputs=(SUBMX,), outputs=("Output/ths2017/tests/hybrid_sz_conservation_summary.csv",), optional=True),
    Step("s21", "validation", "Car and transit destination structure compared (PCA within the survey)", f"{DG}THS_2017_PCA_car_vs_transit.ipynb", "21", "6s",
         needs=("s17",), inputs=SURVEY_KEYS + (CORR_V2, SZLOC), optional=True),
    Step("s35", "validation", "The similarity tests on today's products: the survey matches RavKav's own alightings", f"{DG}THS_vs_RavKav_2025_tests.ipynb", "35", "6ag",
         needs=("s34", "s15", "s16", "s22", "s08", "s09"), inputs=SURVEY_KEYS + (CORR_V2, TAZ_SHP), soft_inputs=(CELLULAR,), optional=True, packages=GEO, minutes=4),
    Step("s41", "validation", "The 2025 taps chained into journeys; the transfer tag checked", f"{DG}RavKav_2025_own_alightings.ipynb", "41", "6ai",
         needs=("s08",), inputs=RAVKAV_2025[:3], outputs=("Output/figures/ravkav_2025_own_alighting_distance.png",), optional=True, minutes=5, note="Reads the 3.3 GB 2025 extracts."),
    Step("s42", "validation", "All-or-nothing assignment of the car layer onto the road network", f"{DG}Car_AON_assignment_2022.ipynb", "42", "6aj",
         needs=("s16",), inputs=(EMME,), outputs=("Output/validation/car_aon_link_flows.csv",), optional=True, packages=GEO, minutes=1,
         note="Superseded by the guideline's T11 (MOT stage 4), kept as record."),
    Step("mot_stage1", "validation", "MoT guideline, stage 1: inputs and trip-length distributions (AM)", f"{DG}MOT_Validation_Stage1_Inputs_Distribution.ipynb", "—", "6ar",
         needs=("s15", "s16", "s08", "s34"), inputs=SURVEY_KEYS + THS_PERSONS[:2] + (GSNEW, TAZ_SHP, CELLULAR), outputs=("Output/validation_mot/summary_stage1.csv",),
         optional=True, knobs=("NOFIT_PERIOD",), packages=GEO, minutes=2),
    *_mot_period_copies("MOT_Validation_Stage1_Inputs_Distribution", "MoT stage 1", ("s15_pm", "s16_pm", "s15_md", "s16_md", "s08p"),
                        SURVEY_KEYS + THS_PERSONS[:2] + (GSNEW, TAZ_SHP, CELLULAR), packages=GEO),
    Step("mot_stage1c", "validation", "MoT guideline, stage 1c: bus coverage by period", f"{DG}MOT_Validation_Stage1c_Bus_coverage_by_period.ipynb", "—", "6ar",
         needs=("s08p", "s15"), inputs=(THS_TRIPS, KEYS, TAZ2636), outputs=("Output/validation_mot/summary_stage1c.csv",), optional=True),
    Step("mot_stage1d", "validation", "MoT guideline, stage 1d: zones, population and trip rates (AM)", f"{DG}MOT_Validation_Stage1d_Zones_Population_Rates.ipynb", "—", "6ar",
         needs=("s15", "s16"), inputs=SURVEY_KEYS + THS_PERSONS[:2] + (HH_WEIGHTS, CORR_V2, GSNEW, TAZ_SHP, ZONAL25, SZLOC),
         outputs=("Output/validation_mot/summary_stage1d.csv",), optional=True, knobs=("NOFIT_PERIOD",), packages=GEO),
    *_mot_period_copies("MOT_Validation_Stage1d_Zones_Population_Rates", "MoT stage 1d", ("s15_pm", "s16_pm", "s15_md", "s16_md"),
                        SURVEY_KEYS + THS_PERSONS[:2] + (HH_WEIGHTS, CORR_V2, GSNEW, TAZ_SHP, ZONAL25, SZLOC), packages=GEO),
    Step("mot_stage2", "validation", "MoT guideline, stage 2: timing profiles against counts and smart cards", f"{DG}MOT_Validation_Stage2_Timing.ipynb", "—", "6ar",
         needs=("s15", "s34", "s36"), inputs=(THS_TRIPS, KEYS, TAZ2636, ZONAL), outputs=("Output/validation_mot/summary_stage2.csv",), optional=True),
    Step("mot_stage2b", "validation", "MoT guideline, stage 2b: timing by period", f"{DG}MOT_Validation_Stage2b_Timing_periods.ipynb", "—", "6ar",
         needs=("s08p", "s15", "s36"), inputs=(THS_TRIPS, KEYS, TAZ2636, ZONAL), outputs=("Output/validation_mot/summary_stage2b.csv",), optional=True),
    Step("mot_stage2c", "validation", "MoT guideline, stage 2c: mode split, occupancy and convergence (AM)", f"{DG}MOT_Validation_Stage2c_Mode_Occupancy_Convergence.ipynb", "—", "6ar",
         needs=("s15", "s16", "s34"), inputs=SURVEY_KEYS + (CORR_V2, GSNEW, ZONAL25, SZLOC), outputs=("Output/validation_mot/summary_stage2c.csv",),
         optional=True, knobs=("NOFIT_PERIOD",)),
    *_mot_period_copies("MOT_Validation_Stage2c_Mode_Occupancy_Convergence", "MoT stage 2c", ("s15_pm", "s16_pm", "s15_md", "s16_md", "s34"),
                        SURVEY_KEYS + (CORR_V2, GSNEW, ZONAL25, SZLOC)),
    Step("mot_stage3", "validation", "MoT guideline, stage 3: transit counts (bus origins, rail, Metronit, running times)", f"{DG}MOT_Validation_Stage3_Counts_Transit.ipynb", "—", "6ar",
         needs=("s16", "s20", "s34", "s30", "s26", "s36"), inputs=(THS_TRIPS, KEYS, TAZ_SHP, ZONAL), outputs=("Output/validation_mot/summary_stage3.csv",), optional=True, packages=GEO),
    *_mot_period_copies("MOT_Validation_Stage3b_Counts", "MoT stage 3b: transit counts", ("s16_pm", "s16_md", "s08p", "s34", "s36"),
                        (THS_TRIPS, KEYS, TAZ_SHP, ZONAL), source=f"{DG}MOT_Validation_Stage3b_Counts_periods.ipynb", packages=GEO),
    Step("mot_stage4", "validation", "MoT guideline, stage 4: link volumes of the car layer on the road network (AM)", f"{DG}MOT_Validation_Stage4_Link_volumes.ipynb", "—", "6ar",
         needs=("s16", "s20", "s36"), inputs=(EMME, SUBMX, TAZ_SHP, THS_TRIPS), outputs=("Output/validation_mot/summary_stage4.csv",),
         optional=True, knobs=("NOFIT_PERIOD",), packages=GEO, minutes=1),
    *_mot_period_copies("MOT_Validation_Stage4_Link_volumes", "MoT stage 4", ("s16_pm", "s16_md", "s36"), (EMME, SUBMX, TAZ_SHP, THS_TRIPS), packages=GEO),
    Step("mot_buspattern", "validation", "Bus destination pattern: RavKav vs on-board survey", f"{DG}Bus_destination_pattern_RavKav_vs_OnBoard.ipynb", "—", "6ar",
         needs=("s08", "s09", "s15"), inputs=(THS_TRIPS, KEYS, TAZ2636, TAZ_SHP, ZONAL), outputs=("Output/validation_mot/summary_busPattern.csv",), optional=True, packages=GEO),
    Step("mot_workbook", "validation", "The validation workbook: one sheet per test plus the summary against the guideline", "tools/build_validation_workbook.py", "—", "6ar",
         needs=("mot_stage1", "mot_stage1c", "mot_stage1d", "mot_stage2", "mot_stage2b", "mot_stage2c", "mot_stage3", "mot_stage4", "mot_buspattern"),
         outputs=("Output/validation_mot/validation_workbook.xlsx",), optional=True, minutes=0.2),
]

_BY_ID = {s.id: s for s in STEPS}
if len(_BY_ID) != len(STEPS):
    dup = [s.id for s in STEPS if [t.id for t in STEPS].count(s.id) > 1]
    raise ValueError(f"duplicate step ids: {sorted(set(dup))}")


def by_id(step_id: str) -> Step:
    try:
        return _BY_ID[step_id]
    except KeyError:
        raise KeyError(f"unknown step {step_id!r}; python3 -m pipeline list shows the ids") from None


def run_order() -> list[Step]:
    """The steps in run order (the manifest order, which the test checks against ``needs``)."""
    return list(STEPS)


def stage_steps(stage: str) -> list[Step]:
    return [s for s in STEPS if s.stage == stage]
