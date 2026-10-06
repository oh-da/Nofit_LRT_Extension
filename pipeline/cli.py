"""Command line of the pipeline:  python3 -m pipeline <command> [options]

  list     the steps in run order (--stage, --all)
  graph    the dependency graph as a Mermaid flowchart (--all includes the optional steps)
  check    which inputs are missing or still Git LFS pointers, which packages are not installed
  run      execute a selection of steps in run order
  doc      write docs/PIPELINE.md from the manifest

Selections (check, run):  --stage KEY [KEY ...]   --only ID [ID ...]   --from ID --to ID   --with-optional   --with-deps
With no selection the default chain is meant: every non-optional step from the base year to the reports.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import checks, runner
from .steps import ROOT, STAGE_KEYS, STAGES, STEPS, Step, run_order


def _add_selection(p: argparse.ArgumentParser) -> None:
    p.add_argument("--stage", nargs="+", choices=STAGE_KEYS, default=(), metavar="KEY", help="steps of these stages: " + " ".join(STAGE_KEYS))
    p.add_argument("--only", nargs="+", default=(), metavar="ID", help="exactly these steps (optional ones included)")
    p.add_argument("--from", dest="start", metavar="ID", help="first step of a slice of the run order")
    p.add_argument("--to", dest="stop", metavar="ID", help="last step of the slice")
    p.add_argument("--with-optional", action="store_true", help="include the optional steps of the selection")
    p.add_argument("--with-deps", action="store_true", help="add the steps the selection needs; those are skipped when their outputs exist")


def _selected(a: argparse.Namespace) -> list[Step]:
    return runner.select(a.stage, a.only, a.start, a.stop, a.with_optional, a.with_deps)


def cmd_list(a: argparse.Namespace) -> int:
    steps = [s for s in run_order() if (not a.stage or s.stage in a.stage) and (a.all or not s.optional)]
    print(f"{'id':<14} {'step':<5} {'stage':<13} {'kind':<9} {'min':>5}  {'path':<66} needs")
    for s in steps:
        flags = ("optional " if s.optional else "") + ("cached " if s.cached else "") + ("" if s.inplace or s.kind != "notebook" else "scratch ")
        print(f"{s.id:<14} {s.step_no:<5} {s.stage:<13} {s.kind:<9} {s.minutes:>5g}  {s.path:<66} {','.join(s.needs)}" + (f"   [{flags.strip()}]" if flags else ""))
        if a.verbose:
            print(f"{'':<14} {s.title}" + (f"  — {s.note}" if s.note else ""))
            if s.env:
                print(f"{'':<14} env: " + " ".join(f"{k}={v}" for k, v in s.env.items()))
    print(f"\n{len(steps)} steps, about {sum(s.minutes for s in steps):,.0f} minutes of run time" + ("" if a.all else " (optional steps hidden; --all shows them)"))
    return 0


def mermaid(include_optional: bool = False, stages: tuple[str, ...] = ()) -> str:
    steps = [s for s in run_order() if (include_optional or not s.optional) and (not stages or s.stage in stages)]
    ids = {s.id for s in steps}
    out = ["flowchart TB"]
    for key, title, _ in STAGES:
        group = [s for s in steps if s.stage == key]
        if not group:
            continue
        out.append(f'    subgraph {key} ["{title}"]')
        for s in group:
            label = f"{s.id}: " + (Path(s.path).stem if s.kind == "notebook" else Path(s.path).name)
            out.append(f'        {s.id}["{label}"]')
        out.append("    end")
    for s in steps:
        for n in s.needs:
            if n in ids:
                out.append(f"    {n} --> {s.id}")
    return "\n".join(out)


def cmd_graph(a: argparse.Namespace) -> int:
    print(mermaid(a.all, tuple(a.stage)))
    return 0


def cmd_check(a: argparse.Namespace) -> int:
    steps = _selected(a)
    lines, blocked = checks.report(steps)
    print("\n".join(lines))
    print(f"\n{len(steps) - blocked} of {len(steps)} selected steps can run now" + ("" if not blocked else f"; {blocked} are blocked by missing inputs or packages"))
    return 1 if blocked else 0


def cmd_run(a: argparse.Namespace) -> int:
    steps = _selected(a)
    if not steps:
        print("nothing selected"); return 1
    extra = {}
    for kv in a.env:
        if "=" not in kv:
            print(f"--env expects NAME=value, got {kv!r}"); return 2
        k, v = kv.split("=", 1); extra[k] = v
    results = runner.run(steps, dry_run=a.dry_run, skip_done=a.skip_done, force=a.force, keep_going=a.keep_going,
                         check_inputs=not a.no_input_check, scratch=a.scratch, timeout=a.timeout, kernel=a.kernel, extra_env=extra)
    return 1 if any(r.status == "FAILED" for r in results) else 0


def cmd_doc(a: argparse.Namespace) -> int:
    from .doc import write_doc
    path = write_doc(Path(a.out) if a.out else None)
    print(f"written {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python3 -m pipeline", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list", help="the steps in run order"); p.set_defaults(func=cmd_list)
    p.add_argument("--stage", nargs="+", choices=STAGE_KEYS, default=(), metavar="KEY")
    p.add_argument("--all", action="store_true", help="include the optional steps")
    p.add_argument("-v", "--verbose", action="store_true", help="titles, notes and environments")

    p = sub.add_parser("graph", help="Mermaid dependency graph"); p.set_defaults(func=cmd_graph)
    p.add_argument("--stage", nargs="+", choices=STAGE_KEYS, default=(), metavar="KEY")
    p.add_argument("--all", action="store_true", help="include the optional steps")

    p = sub.add_parser("check", help="inputs and packages of a selection"); p.set_defaults(func=cmd_check); _add_selection(p)

    p = sub.add_parser("run", help="execute a selection in run order"); p.set_defaults(func=cmd_run); _add_selection(p)
    p.add_argument("--dry-run", action="store_true", help="print the plan, run nothing")
    p.add_argument("--skip-done", action="store_true", help="skip steps whose listed outputs all exist")
    p.add_argument("--force", action="store_true", help="run cached steps even when their outputs exist")
    p.add_argument("--keep-going", action="store_true", help="continue with the remaining steps after a failure")
    p.add_argument("--no-input-check", action="store_true", help="do not stop on missing inputs or packages before a step")
    p.add_argument("--scratch", type=Path, help=f"folder for executed copies of alternative runs (default {runner.DEFAULT_SCRATCH.relative_to(ROOT)})")
    p.add_argument("--timeout", type=int, default=3000, help="cell timeout in seconds (default 3000)")
    p.add_argument("--kernel", default="python3", help="Jupyter kernel name (default python3)")
    p.add_argument("--env", nargs="+", default=(), metavar="NAME=value", help="environment for every selected step, e.g. NOFIT_PERIOD=PM")

    p = sub.add_parser("doc", help="write docs/PIPELINE.md"); p.set_defaults(func=cmd_doc)
    p.add_argument("--out", help="another output path")

    a = ap.parse_args(argv)
    try:
        return a.func(a)
    except KeyError as e:
        print(e.args[0] if e.args else e, file=sys.stderr); return 2


if __name__ == "__main__":
    sys.exit(main())
