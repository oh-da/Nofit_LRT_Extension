"""Checks of the pipeline manifest and a smoke test of the runner.  Run:  python3 tools/test_pipeline.py

1. Every step's notebook or script exists; ids are unique; every `needs` names a known step that comes
   EARLIER in the manifest (the list order is the run order); stages are known; paths of outputs are
   repository-relative; environments are strings.
2. The command line works: list, graph, check, run --dry-run, and doc into a temporary file.
3. The runner executes a throw-away notebook (when nbclient and a kernel are installed) and a throw-away
   script, with the environment of the step reaching the code, and writes its log.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from pipeline import STAGES, STEPS, by_id, run_order  # noqa: E402
from pipeline import checks, cli, runner  # noqa: E402
from pipeline.steps import STAGE_KEYS, Step  # noqa: E402

failures = 0


def check(cond: bool, msg: str) -> None:
    global failures
    if not cond:
        failures += 1
        print("FAIL", msg)


# 1. the manifest ---------------------------------------------------------------------------------------
ids = [s.id for s in STEPS]
check(len(ids) == len(set(ids)), "duplicate ids")
seen: set[str] = set()
for s in run_order():
    check((ROOT / s.path).exists(), f"{s.id}: {s.path} does not exist")
    check(s.stage in STAGE_KEYS, f"{s.id}: unknown stage {s.stage}")
    for n in s.needs:
        check(n in ids, f"{s.id} needs unknown step {n}")
        check(n in seen, f"{s.id} needs {n}, which comes later in the run order")
    for o in s.outputs:
        check(o.startswith(("Output/", "reports/", "notebooks/")), f"{s.id}: output {o} is not under Output/, reports/ or notebooks/")
    for i in s.inputs + s.soft_inputs:
        check(i.startswith("Input/"), f"{s.id}: input {i} is not under Input/")
    for k, v in s.env.items():
        check(isinstance(k, str) and isinstance(v, str), f"{s.id}: env {k}={v!r} must be strings")
    if s.out_notebook:
        check(s.out_notebook.endswith(".ipynb") and s.out_notebook != s.path, f"{s.id}: out_notebook {s.out_notebook}")
    check(s.minutes > 0, f"{s.id}: minutes must be positive")
    seen.add(s.id)
# the chain's default run reaches the deliverable and the reports
default = [s.id for s in STEPS if not s.optional]
for must in ("s15", "s16", "s22", "s23", "s27", "s24", "s25", "s29", "s30", "s26", "s43", "s31", "s37", "s44", "s45", "r_comp", "r_comp_he", "r_deck"):
    check(must in default, f"{must} must be in the default run")
check([k for k, _, _ in STAGES] == STAGE_KEYS, "stage keys out of order")
# every stage of the deliverable's needs comes earlier in the run order
pos = {s.id: i for i, s in enumerate(STEPS)}
for s in STEPS:
    for n in s.needs:
        check(pos[n] < pos[s.id], f"{n} must run before {s.id}")

# 2. the command line -------------------------------------------------------------------------------
import contextlib, io  # noqa: E402

def run_cli(*args: str) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cli.main(list(args))
    return rc, buf.getvalue()

rc, out = run_cli("list", "--all"); check(rc == 0 and "s45" in out and "mot_workbook" in out, "list --all")
rc, out = run_cli("list"); check(rc == 0 and "mot_workbook" not in out, "list hides optional steps")
rc, out = run_cli("graph", "--all"); check(rc == 0 and out.startswith("flowchart") and "s31 --> s45" not in out and "s22 --> s45" in out, "graph")
rc, out = run_cli("check", "--only", "s22"); check("s22" in out, "check")
rc, out = run_cli("run", "--dry-run", "--only", "s31", "s45"); check(rc == 0 and "PLAN  s31" in out and "PLAN  s45" in out, "run --dry-run")
rc, out = run_cli("run", "--dry-run", "--stage", "reports"); check(rc == 0 and out.count("PLAN") == 6, f"dry run of the reports stage: {out.count('PLAN')} steps")
sel = runner.select(only=["s45"], with_deps=True)
check([s.id for s in sel][-1] == "s45" and "s22" in [s.id for s in sel] and "s16_pm" in [s.id for s in sel], "select --with-deps")
check(all(getattr(s, "_dep_only", False) for s in sel if s.id != "s45"), "dependencies are marked")
try:
    by_id("nope"); check(False, "unknown id must raise")
except KeyError:
    pass
with tempfile.TemporaryDirectory() as td:
    rc, out = run_cli("doc", "--out", f"{td}/PIPELINE.md")
    text = Path(td, "PIPELINE.md").read_text(encoding="utf-8")
    check(rc == 0 and "## The steps, in run order" in text and "`s45`" in text and "```mermaid" in text, "doc")

# 3. the runner on throw-away steps --------------------------------------------------------------------
with tempfile.TemporaryDirectory(dir=ROOT / "pipeline") as td:
    td_rel = os.path.relpath(td, ROOT)
    marker = Path(td) / "marker.txt"
    script = Path(td) / "hello.py"
    script.write_text("import os, pathlib\npathlib.Path(os.environ['MARKER']).write_text('env ' + os.environ.get('PIPELINE_TEST', '?'))\n", encoding="utf-8")
    st = Step("t_script", "validation", "throw-away script", f"{td_rel}/hello.py", env={"MARKER": str(marker), "PIPELINE_TEST": "ok"}, optional=True)
    res = runner.run([st], check_inputs=False, log_name="test_pipeline")
    check(res[0].status == "OK" and marker.read_text() == "env ok", f"script step: {res[0].status} {res[0].detail}")
    try:
        import nbformat
        from nbclient import NotebookClient  # noqa: F401
        from jupyter_client.kernelspec import KernelSpecManager
        have_kernel = "python3" in KernelSpecManager().find_kernel_specs()
    except Exception:
        nbformat = None; have_kernel = False
    if nbformat and have_kernel:
        nb = nbformat.v4.new_notebook()
        nb.cells = [nbformat.v4.new_code_cell("import os, pathlib\nassert os.path.exists('METHODOLOGY.md'), 'cwd must be the repository root'\n"
                                              "pathlib.Path(os.environ['MARKER']).write_text('nb ' + os.environ['PIPELINE_TEST'])\nprint('ran')")]
        nb_path = Path(td) / "t.ipynb"; nbformat.write(nb, nb_path)
        st = Step("t_nb", "validation", "throw-away notebook", f"{td_rel}/t.ipynb", env={"MARKER": str(marker), "PIPELINE_TEST": "nb-ok"}, optional=True, inplace=False)
        res = runner.run([st], check_inputs=False, scratch=Path(td) / "scratch", log_name="test_pipeline")
        check(res[0].status == "OK" and marker.read_text() == "nb nb-ok", f"notebook step: {res[0].status} {res[0].detail}")
        executed = Path(td) / "scratch" / "t_nb_t.ipynb"
        check(executed.exists() and "ran" in executed.read_text(encoding="utf-8"), "executed copy written to scratch with its outputs")
        check("PIPELINE_TEST" not in os.environ, "the step environment is removed after the run")
        # a failing notebook is reported, not raised
        nb.cells = [nbformat.v4.new_code_cell("raise RuntimeError('boom')")]; nbformat.write(nb, nb_path)
        res = runner.run([st], check_inputs=False, scratch=Path(td) / "scratch", log_name="test_pipeline")
        check(res[0].status == "FAILED" and "boom" in res[0].detail, f"failing notebook: {res[0].status} {res[0].detail}")
    else:
        print("note: nbclient or the python3 kernel is not installed; the notebook smoke test was skipped")
    # input check: an LFS pointer blocks the step before it runs
    ptr = Path(td) / "pointer.csv"; ptr.write_bytes(b"version https://git-lfs.github.com/spec/v1\noid sha256:0\nsize 1\n")
    check(checks.is_lfs_pointer(ptr) and checks.input_state(os.path.relpath(ptr, ROOT)) == "lfs pointer", "LFS pointer detection")
    st = Step("t_blocked", "validation", "blocked", f"{td_rel}/hello.py", inputs=(os.path.relpath(ptr, ROOT),), optional=True)
    res = runner.run([st], log_name="test_pipeline")
    check(res[0].status == "FAILED" and "LFS pointer" in res[0].detail, f"blocked by pointer: {res[0].status} {res[0].detail}")
for f in (runner.LOG_DIR / "test_pipeline.log", runner.LOG_DIR / "test_pipeline.csv"):
    f.unlink(missing_ok=True)

print("all pipeline tests passed" if not failures else f"{failures} failure(s)")
sys.exit(1 if failures else 0)
