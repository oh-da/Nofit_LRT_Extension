"""Execute pipeline steps in run order.

A notebook step is executed with ``nbclient`` (the same engine as ``jupyter nbconvert --execute``) with the
repository root as working directory, and the executed notebook is written back in place (the committed
convention), to a named copy (``Step.out_notebook``, the PM / midday copies under ``periods/``) or to the
scratch folder (alternative runs, which must not replace the committed default run).  A script step runs
with the current Python interpreter.  Every run writes ``=== START / OK / FAILED <id>`` lines to the
console and to ``pipeline/logs/run_<timestamp>.log``, plus one CSV row per step.
"""
from __future__ import annotations

import csv
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from . import checks
from .steps import ROOT, STEPS, Step, by_id, run_order

LOG_DIR = ROOT / "pipeline" / "logs"
DEFAULT_SCRATCH = LOG_DIR / "executed"


class StepFailed(RuntimeError):
    pass


@dataclass
class Result:
    step: Step
    status: str          # OK | FAILED | SKIPPED (done) | SKIPPED (dry run) | SKIPPED (inputs)
    seconds: float
    detail: str = ""


# ---------------------------------------------------------------- selection ----

def select(stages: Sequence[str] = (), only: Sequence[str] = (), start: str | None = None, stop: str | None = None,
           with_optional: bool = False, with_deps: bool = False) -> list[Step]:
    """Resolve a command-line selection into steps, in run order.

    ``stages`` keeps the steps of those stages; ``only`` keeps the named steps (optional ones included);
    ``start`` / ``stop`` keep the slice of the run order between the two ids (inclusive).  With no
    criterion every step is selected.  Optional steps are dropped unless ``with_optional`` or named in
    ``only``.  ``with_deps`` adds the transitive ``needs`` of the selection; those are marked so that the
    runner skips them when their outputs already exist (the committed products).
    """
    order = run_order()
    ids = [s.id for s in order]
    for s in order:
        s._dep_only = False  # type: ignore[attr-defined]  # reset the mark of an earlier selection in this process
    for sid in list(only) + [x for x in (start, stop) if x]:
        by_id(sid)  # raises on an unknown id
    picked: set[str] = set()
    if not (stages or only or start or stop):
        picked = set(ids)
    if stages:
        picked |= {s.id for s in order if s.stage in stages}
    if start or stop:
        i0 = ids.index(start) if start else 0
        i1 = ids.index(stop) if stop else len(ids) - 1
        picked |= set(ids[i0:i1 + 1])
    if not with_optional:
        picked = {sid for sid in picked if not by_id(sid).optional}
    picked |= set(only)
    deps: set[str] = set()
    if with_deps:
        frontier = list(picked)
        while frontier:
            s = by_id(frontier.pop())
            for n in s.needs:
                if n not in picked and n not in deps:
                    deps.add(n); frontier.append(n)
    chosen = [s for s in order if s.id in picked or s.id in deps]
    for s in chosen:
        s._dep_only = s.id in deps  # type: ignore[attr-defined]
    return chosen


# ---------------------------------------------------------------- execution ----

def _env_for(step: Step, extra: dict[str, str]) -> dict[str, str]:
    env = dict(os.environ)
    env.setdefault("MPLBACKEND", "Agg")
    env["PYTHONUNBUFFERED"] = "1"
    env.update(step.env)
    env.update(extra)
    return env


def execute_notebook(step: Step, env: dict[str, str], scratch: Path, timeout: int, kernel: str, log) -> Path:
    """Run one notebook and return the path of the executed copy."""
    try:
        import nbformat
        from nbclient import NotebookClient
    except ImportError:  # fall back to the jupyter command line
        return _execute_with_nbconvert(step, env, scratch, timeout, log)
    src = ROOT / step.path
    if step.out_notebook:
        dst = ROOT / step.out_notebook
    elif step.inplace:
        dst = src
    else:
        dst = scratch / f"{step.id}_{src.stem}.ipynb"
    dst.parent.mkdir(parents=True, exist_ok=True)
    nb = nbformat.read(src, as_version=4)
    # the notebooks read os.environ at run time; the kernel inherits the process environment
    saved = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    try:
        client = NotebookClient(nb, timeout=timeout, kernel_name=kernel, resources={"metadata": {"path": str(ROOT)}},
                                allow_errors=False, record_timing=True)
        client.execute()
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        nbformat.write(nb, dst)  # keep whatever executed, also after a failure, for diagnosis
    return dst


def _execute_with_nbconvert(step: Step, env: dict[str, str], scratch: Path, timeout: int, log) -> Path:
    jupyter = shutil.which("jupyter")
    if not jupyter:
        raise StepFailed("neither nbclient nor the jupyter command line is installed: pip install nbformat nbclient ipykernel")
    src = ROOT / step.path
    cmd = [jupyter, "nbconvert", "--to", "notebook", "--execute", f"--ExecutePreprocessor.timeout={timeout}"]
    if step.out_notebook:
        dst = ROOT / step.out_notebook
        cmd += ["--output-dir", str(dst.parent), "--output", dst.name]
    elif step.inplace:
        dst = src; cmd += ["--inplace"]
    else:
        dst = scratch / f"{step.id}_{src.stem}.ipynb"
        cmd += ["--output-dir", str(dst.parent), "--output", dst.name]
    dst.parent.mkdir(parents=True, exist_ok=True)
    log(f"    $ {' '.join(cmd + [str(src)])}")
    r = subprocess.run(cmd + [str(src)], cwd=ROOT, env=env)
    if r.returncode:
        raise StepFailed(f"jupyter nbconvert exited with {r.returncode}")
    return dst


def execute_script(step: Step, env: dict[str, str], log) -> None:
    cmd = [sys.executable, str(ROOT / step.path)] + list(step.args)
    log(f"    $ {' '.join(os.path.relpath(c, ROOT) if c.startswith(str(ROOT)) else c for c in cmd)}")
    r = subprocess.run(cmd, cwd=ROOT, env=env)
    if r.returncode:
        raise StepFailed(f"{step.path} exited with {r.returncode}")


def restore_files(paths: Iterable[str], log) -> None:
    paths = list(paths)
    if not paths:
        return
    log(f"    git checkout -- {' '.join(paths)}")
    subprocess.run(["git", "checkout", "--", *paths], cwd=ROOT, check=False)


# ---------------------------------------------------------------- the run ----

def run(steps: Sequence[Step], *, dry_run: bool = False, skip_done: bool = False, force: bool = False,
        keep_going: bool = False, check_inputs: bool = True, scratch: Path | None = None, timeout: int = 3000,
        kernel: str = "python3", extra_env: dict[str, str] | None = None, log_name: str | None = None) -> list[Result]:
    """Run the given steps in order and return one Result per step."""
    extra_env = dict(extra_env or {})
    scratch = Path(scratch) if scratch else DEFAULT_SCRATCH
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = log_name or time.strftime("run_%Y%m%d_%H%M%S")
    log_path, csv_path = LOG_DIR / f"{stamp}.log", LOG_DIR / f"{stamp}.csv"
    log_file = open(log_path, "a", encoding="utf-8")

    def log(msg: str) -> None:
        line = f"{time.strftime('%H:%M:%S')} {msg}"
        print(line, flush=True); log_file.write(line + "\n"); log_file.flush()

    results: list[Result] = []
    log(f"pipeline run of {len(steps)} step(s); log {log_path.relative_to(ROOT)}; " + ("DRY RUN" if dry_run else f"scratch {scratch}"))
    with open(csv_path, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["id", "status", "seconds", "path", "detail", "finished"])
        for step in steps:
            t0 = time.time()
            dep_only = getattr(step, "_dep_only", False)
            label = f"{step.id} ({step.path})" + (" [dependency]" if dep_only else "")
            try:
                if (skip_done or dep_only or (step.cached and not force)) and step.outputs and checks.outputs_present(step):
                    res = Result(step, "SKIPPED (done)", 0.0, "outputs present")
                    log(f"--- SKIP  {label}: outputs present"); results.append(res)
                    w.writerow([step.id, res.status, 0, step.path, res.detail, time.strftime("%Y-%m-%d %H:%M:%S")]); continue
                if check_inputs:
                    problems = checks.input_problems(step)
                    if problems:
                        msg = "; ".join(problems)
                        if dry_run:
                            log(f"--- WARN  {label}: {msg}")
                        else:
                            raise StepFailed("inputs: " + msg)
                    pk = checks.missing_packages(step)
                    if pk:
                        msg = "missing packages: pip install " + " ".join(pk)
                        if dry_run:
                            log(f"--- WARN  {label}: {msg}")
                        else:
                            raise StepFailed(msg)
                env = _env_for(step, extra_env)
                shown = {k: v for k, v in {**step.env, **extra_env}.items()}
                if dry_run:
                    res = Result(step, "SKIPPED (dry run)", 0.0, " ".join(f"{k}={v}" for k, v in shown.items()))
                    log(f"=== PLAN  {label}" + (f"  env {res.detail}" if shown else "") + (f"  -> {step.out_notebook}" if step.out_notebook else "" if step.inplace or step.kind != 'notebook' else "  -> scratch copy"))
                    results.append(res); w.writerow([step.id, res.status, 0, step.path, res.detail, ""]); continue
                log(f"=== START {label}" + (f"  env {' '.join(f'{k}={v}' for k, v in shown.items())}" if shown else ""))
                if step.kind == "notebook":
                    out = execute_notebook(step, env, scratch, timeout, kernel, log)
                    log(f"    executed copy: {os.path.relpath(out, ROOT)}")
                else:
                    execute_script(step, env, log)
                restore_files(step.restore, log)
                dt = time.time() - t0
                res = Result(step, "OK", dt); results.append(res)
                log(f"=== OK    {label} in {dt:,.0f} s")
            except Exception as e:  # noqa: BLE001 - any failure of the step is reported, not hidden
                dt = time.time() - t0
                detail = str(e).strip().splitlines()[-1] if str(e).strip() else type(e).__name__
                res = Result(step, "FAILED", dt, detail); results.append(res)
                log(f"=== FAILED {label} after {dt:,.0f} s: {detail}")
                w.writerow([step.id, res.status, round(dt), step.path, detail, time.strftime("%Y-%m-%d %H:%M:%S")])
                if not keep_going:
                    log("stopping at the first failure (use --keep-going to continue with the remaining steps)")
                    break
                continue
            w.writerow([step.id, res.status, round(res.seconds), step.path, res.detail, time.strftime("%Y-%m-%d %H:%M:%S")])
    n_ok = sum(r.status == "OK" for r in results); n_fail = sum(r.status == "FAILED" for r in results)
    n_skip = sum(r.status.startswith("SKIPPED") for r in results)
    log(f"done: {n_ok} ok, {n_fail} failed, {n_skip} skipped; {sum(r.seconds for r in results)/60:,.1f} min")
    log_file.close()
    return results
