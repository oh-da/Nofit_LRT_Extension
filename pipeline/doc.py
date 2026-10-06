"""Write docs/PIPELINE.md from the manifest, so the document and the runner never disagree."""
from __future__ import annotations

from pathlib import Path

from .cli import mermaid
from .steps import ROOT, STAGES, Step, run_order

DOC = ROOT / "docs" / "PIPELINE.md"

INTRO = """# The pipeline, start to finish

> Generated from `pipeline/steps.py` by `python3 -m pipeline doc`. Edit the manifest, not this file.

The demand estimate for the Nofit LRT extension is a chain of Jupyter notebooks and Python scripts. Each
one reads committed inputs under `Input/` and the outputs of earlier steps under `Output/`, and writes its
own outputs back under `Output/` (or `reports/`). This document lists the whole chain in one place, in run
order, with what every step needs and produces. The methods and results are in
[METHODOLOGY.md](../METHODOLOGY.md); the step numbers and section references below are its.

## How to run it

```bash
pip install pandas numpy scipy matplotlib openpyxl pyshp shapely pyproj geopandas pyogrio statsmodels python-docx nbformat nbclient ipykernel
python3 -m pipeline check                      # which inputs are still LFS pointers, which packages are missing
python3 -m pipeline check --stage base_year    # the same for one stage
python3 -m pipeline run --dry-run              # the plan: every default step, in order, with its environment
python3 -m pipeline run                        # the default chain, base year to reports (about {default_minutes:,.0f} minutes plus the GTFS and smart-card steps)
python3 -m pipeline run --stage los capture    # two stages
python3 -m pipeline run --from s31 --to s45    # a slice of the run order
python3 -m pipeline run --only s31 --env LRT_HEADWAY=7.5   # one notebook with another setting (executed copy in place: use a v* step for a scratch copy)
python3 -m pipeline run --only v26_h75 v31_h75  # the committed sensitivity run of that setting (executed copies go to pipeline/logs/executed/)
python3 -m pipeline run --skip-done            # skip every step whose listed outputs already exist
python3 -m pipeline run --with-optional --stage validation   # the Ministry of Transport validation
python3 -m pipeline list --all -v              # every step with its title, note and environment
python3 -m pipeline graph --all                # the dependency graph (Mermaid)
```

Every run appends `=== START / OK / FAILED <id>` lines to `pipeline/logs/run_<timestamp>.log` and one row
per step to the CSV beside it. Executed notebooks replace the committed ones (the repository convention:
executed notebooks are committed), except the alternative runs (`v*` steps), whose executed copies go to
the scratch folder so the committed default run stays intact, and the PM / midday runs, which go to the
`periods/` copies. A failure stops the run unless `--keep-going` is given; the notebook as far as it got
is written out for diagnosis.

Before a step runs, its inputs are checked: a file still in Git LFS pointer form stops the run with the
`git lfs pull --include=...` (or `python3 tools/lfs_pull.py ...`) command that fetches it. `--skip-done`
skips a step whose listed outputs all exist, so a partial rerun needs no bookkeeping. Step ids that are
only *needed* by the selection (`--with-deps`) are skipped in the same way.

**Default chain and optional steps.** The default run (no `--with-optional`) covers the base year, the
forecast, the corridor and LRT line, the level of service, the capture, the alternatives and the reports:
everything that produces a product the reports quote. The optional steps are the upstream rebuilds of
committed products from the raw smart-card files (gigabytes on LFS), the PM / midday matrices, the
sensitivities, and the validation. The dependency graph records them all; `--with-deps` pulls a needed
optional step in and skips it when its committed outputs are present.

## The stages

| # | Stage | Steps | What it does |
|---|---|---|---|
{stage_table}

```mermaid
{graph}
```

Arrows read "is read by": a step comes after everything it needs. Optional steps are shown with
`python3 -m pipeline graph --all`.

## The steps, in run order
"""

STEP_HEADER = """
### {n}. {title}

{what}

| id | Step | § | Notebook / script | Needs | Inputs | Key outputs | Minutes |
|---|---|---|---|---|---|---|---|
"""

KNOBS = """
## Environment variables that select alternative runs

A notebook reads these from the environment and, when any of them moves from its default, writes to a
tagged folder so the committed default run is never overwritten. The `v*` steps above set them exactly as
METHODOLOGY §9 does; `--env NAME=value` sets them for an ad-hoc run.

| Variable | Read by | Default | Alternatives and effect |
|---|---|---|---|
| `NOFIT_PERIOD` | steps 15, 16, the MoT validation | `AM` (06:00–09:00) | `PM` (16:00–19:00), `MD` (09:00–15:00): the window of the survey trips and the RavKav prior; outputs to `*_pm` / `*_md` folders |
| `CAR_SOURCE` | step 26 | `survey` | `network`: car in-vehicle time from the May 2026 network skim of step 37 → `Output/skims/car_network/` |
| `BUS_WAIT_RULE` | step 26 | `half_headway` | `best_line`: wait on the single busiest line-direction → `Output/skims/bus_wait_best_line/` |
| `LRT_HEADWAY` | steps 26, 31 | `5.0` minutes | `7.5`, `10`: the trunk's headway → `Output/skims/lrt_headway_<h>/` |
| `GC_SOURCE_DIR` | step 31 | `Output/gc` | an alternate step-26 folder; step 31 then writes beside it |
| `BUS_COMPETITION` | step 31 | `full` | `truncated`: the parallel trunk bus removed → `Output/skims/bus_truncated/` |
| `OVT_TAG`, `W_WALK`, `W_WALK_LRT`, `W_WAIT`, `TRANSFER_PEN`, `BRT_LRT_TRANSFER_PEN`, `STATION_ACCESS_UG`, `STATION_ACCESS_GR` | step 31 | the central set (§6al) | another out-of-vehicle parameter set, tagged → `Output/skims/ovt_<tag>/` (`tools/ovt_run_chain.py` runs all seven) |
| `SK_DIR` / `SKIM_DIR` | steps 32, 33 | `Output/skims` | an alternate step-31 folder (the two names are synonyms in step 33) → `Output/mode_choice/<tag>/` |
| `BUS_TAZ_SOURCE` | step 39 | `los` | `area_plus_walk`: the hand-over's bus construction → `Output/skims/taz/bus_area_plus_walk/` |
| `ALT_OUT`, `BUS_SLOWDOWN` | step 45 | `Output/alternatives`, no slowdown | another output folder; bus time factors per scenario-year, e.g. `BU_2040:1.10,BU_2050:1.20,...` |
| `OVT_NB_OUT` | `tools/ovt_run_chain.py` | `/tmp/ovt_nb` | where that script writes its executed copies |

## Git LFS inputs

Every file directly under `Input/` and most sub-folders are Git LFS pointers until pulled.
`python3 -m pipeline check [selection]` lists exactly which files a selection needs and prints the pull
command. Without the git-lfs client, `tools/lfs_pull.py` fetches single files; restore the pointers before
committing (`git checkout -- Input/ && git clean -fdq Input/`).
"""


def _md(s: str) -> str:
    return s.replace("|", "\\|")


def _inputs(step: Step) -> str:
    items = [Path(p).name for p in step.inputs] + [f"({Path(p).name})" for p in step.soft_inputs]
    return ", ".join(f"`{i}`" if not i.startswith("(") else f"(`{i[1:-1]}`)" for i in items) if items else "—"


def _outputs(step: Step) -> str:
    return ", ".join(f"`{o}`" for o in step.outputs) if step.outputs else "—"


def render() -> str:
    order = run_order()
    default_minutes = sum(s.minutes for s in order if not s.optional)
    rows = []
    for i, (key, title, what) in enumerate(STAGES, 1):
        n_all = sum(s.stage == key for s in order); n_opt = sum(s.stage == key and s.optional for s in order)
        rows.append(f"| {i} | **{title}** (`{key}`) | {n_all}" + (f" ({n_opt} optional)" if n_opt else "") + f" | {what} |")
    text = INTRO.format(default_minutes=default_minutes, stage_table="\n".join(rows), graph=mermaid(False))
    for i, (key, title, what) in enumerate(STAGES, 1):
        group = [s for s in order if s.stage == key]
        text += STEP_HEADER.format(n=i, title=title, what=what)
        for s in group:
            flags = []
            if s.optional: flags.append("optional")
            if s.cached: flags.append("rerun only with a new input")
            if s.env: flags.append("env " + " ".join(f"`{k}={v}`" for k, v in s.env.items()))
            if s.out_notebook: flags.append(f"writes `{s.out_notebook}`")
            elif s.kind == "notebook" and not s.inplace: flags.append("executed copy to scratch")
            name = f"`{s.path}`" + (f"<br>*{', '.join(flags)}*" if flags else "")
            text += (f"| `{s.id}` | {s.step_no} | {s.section} | {name} | {', '.join(f'`{n}`' for n in s.needs) or '—'} | "
                     f"{_inputs(s)} | {_outputs(s)} | {s.minutes:g} |\n")
            text += f"| | | | *{_md(s.title)}*" + (f" {_md(s.note)}" if s.note else "") + " | | | | |\n"
    text += KNOBS
    return text


def write_doc(path: Path | None = None) -> Path:
    path = path or DOC
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(), encoding="utf-8")
    return path
