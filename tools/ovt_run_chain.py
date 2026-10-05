"""Run the step-31 / step-33 chain for every OVT parameter set in Output/ovt_research/parameter_sets.csv.

Usage:  python3 tools/ovt_run_chain.py [--sets name,name] [--skip-33]
Needs nbformat, nbclient, ipykernel and the notebooks' own dependencies (pandas, scipy, matplotlib, openpyxl,
statsmodels) plus the pulled LFS inputs (Input/Corridor_TAZ_Agg_V2.xlsx, Input/TAZ_2636_Keys.xlsx,
Input/THS_2017-2018/* -- see tools/lfs_pull.py). Each set runs Mode_skims_and_flow_comparison.ipynb with
OVT_TAG=<set> and the set's weights in the environment (outputs in Output/skims/ovt_<set>/), then
Mode_choice_person_level.ipynb with SKIM_DIR=Output/skims/ovt_<set> (outputs in Output/mode_choice/ovt_<set>/).
Executed notebooks are written to the scratch directory given by OVT_NB_OUT (default /tmp/ovt_nb), never into
notebooks/. Afterwards run tools/ovt_chain_summary.py. Background: docs/OVT_WEIGHTS_RESEARCH_PLAN.md §5.6.
"""
import argparse, csv, os, sys, time
from pathlib import Path
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
PARAMS = ("W_WALK", "W_WALK_LRT", "W_WAIT", "TRANSFER_PEN", "BRT_LRT_TRANSFER_PEN", "STATION_ACCESS_UG", "STATION_ACCESS_GR")
NB31 = ROOT / "notebooks/current/Mode_skims_and_flow_comparison.ipynb"
NB33 = ROOT / "notebooks/current/Mode_choice_person_level.ipynb"


def run(nb_path, env, out_path):
    os.environ.update(env)
    try:
        nb = nbformat.read(nb_path, as_version=4)
        t = time.time()
        NotebookClient(nb, timeout=1800, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}).execute()
        nbformat.write(nb, out_path)
        return time.time() - t
    finally:
        for k in env:
            os.environ.pop(k, None)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sets", help="comma-separated subset of set names")
    ap.add_argument("--skip-33", action="store_true", help="only rerun step 31")
    a = ap.parse_args()
    os.environ.setdefault("MPLBACKEND", "Agg")
    scratch = Path(os.environ.get("OVT_NB_OUT", "/tmp/ovt_nb")); scratch.mkdir(parents=True, exist_ok=True)
    sets = list(csv.DictReader(open(ROOT / "Output/ovt_research/parameter_sets.csv", encoding="utf-8")))
    if a.sets:
        want = a.sets.split(","); sets = [s for s in sets if s["set"] in want]
    for s in sets:
        tag = s["set"]
        env = {"OVT_TAG": tag, **{p: s[p] for p in PARAMS}}
        print(f"== {tag}: " + ", ".join(f"{p}={s[p]}" for p in PARAMS), flush=True)
        dt = run(NB31, env, scratch / f"step31_{tag}.ipynb")
        print(f"   step 31 done in {dt:.0f} s -> Output/skims/ovt_{tag}/", flush=True)
        if not a.skip_33:
            dt = run(NB33, {"SKIM_DIR": f"Output/skims/ovt_{tag}"}, scratch / f"step33_{tag}.ipynb")
            print(f"   step 33 done in {dt:.0f} s -> Output/mode_choice/ovt_{tag}/", flush=True)
    print("all sets done; now: python3 tools/ovt_chain_summary.py")


if __name__ == "__main__":
    main()
