"""What a step needs before it can run: its input files (pulled from Git LFS, not pointers), the Python
packages it imports, and, for ``--skip-done``, whether its outputs are already there.
"""
from __future__ import annotations

import glob
import importlib.util
import os
from pathlib import Path

from .steps import BASE_PACKAGES, ROOT, Step

LFS_HEADER = b"version https://git-lfs"

# import name -> pip name, where they differ
PIP_NAME = {"docx": "python-docx", "shapefile": "pyshp", "sklearn": "scikit-learn", "yaml": "pyyaml"}


def is_lfs_pointer(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            return f.read(40).startswith(LFS_HEADER)
    except OSError:
        return False


def _exists(rel: str) -> bool:
    """A path exists; a shapefile may be given by any of its parts; a glob may match."""
    p = ROOT / rel
    if p.exists():
        return True
    if any(ch in rel for ch in "*?["):
        return bool(glob.glob(str(p)))
    return False


def input_state(rel: str) -> str:
    """'ok', 'missing' or 'lfs pointer' for one input path."""
    p = ROOT / rel
    if not _exists(rel):
        return "missing"
    if p.is_file() and is_lfs_pointer(p):
        return "lfs pointer"
    if p.is_dir():
        files = [f for f in p.rglob("*") if f.is_file()]
        if files and all(is_lfs_pointer(f) for f in files):
            return "lfs pointer"
    return "ok"


def input_problems(step: Step) -> list[str]:
    """Human-readable problems with the step's required inputs (empty when all are usable)."""
    out = []
    for rel in step.inputs:
        st = input_state(rel)
        if st != "ok":
            out.append(f"{rel} is {'an LFS pointer (not pulled)' if st == 'lfs pointer' else 'missing'}")
    return out


def soft_input_problems(step: Step) -> list[str]:
    return [f"{rel} is {input_state(rel)}" for rel in step.soft_inputs if input_state(rel) != "ok"]


def lfs_pull_commands(paths: list[str]) -> list[str]:
    """The two ways to pull a list of LFS pointer files: the git-lfs client, or tools/lfs_pull.py."""
    if not paths:
        return []
    files = sorted(set(paths))
    return [f'git lfs pull --include="{",".join(files)}"',
            f"python3 tools/lfs_pull.py {' '.join(files)}"]


def missing_packages(step: Step) -> list[str]:
    """pip names of the packages the step imports that are not installed."""
    names = list(BASE_PACKAGES) + list(step.packages)
    if step.kind == "notebook":
        names += ["nbformat", "nbclient", "ipykernel"]
    missing = [n for n in dict.fromkeys(names) if importlib.util.find_spec(n) is None]
    return [PIP_NAME.get(n, n) for n in missing]


def outputs_present(step: Step) -> bool:
    return bool(step.outputs) and all(_exists(o) for o in step.outputs)


def missing_outputs(step: Step) -> list[str]:
    return [o for o in step.outputs if not _exists(o)]


def report(steps: list[Step]) -> tuple[list[str], int]:
    """Lines describing the readiness of the given steps and the number of steps that cannot run."""
    lines: list[str] = []
    pointers: list[str] = []
    blocked = 0
    pk_all: set[str] = set()
    for s in steps:
        probs = input_problems(s)
        soft = soft_input_problems(s)
        pk = missing_packages(s)
        pk_all |= set(pk)
        for rel in s.inputs:
            if input_state(rel) == "lfs pointer":
                p = ROOT / rel
                pointers += [os.path.relpath(f, ROOT) for f in p.rglob("*") if f.is_file()] if p.is_dir() else [rel]
        status = "ready" if not probs and not pk else "blocked"
        blocked += status == "blocked"
        outs = missing_outputs(s)
        lines.append(f"{s.id:<14} {status:<8} {s.path}" + ("" if not outs else f"   (outputs missing: {len(outs)} of {len(s.outputs)})"))
        for p_ in probs:
            lines.append(f"    - {p_}")
        for p_ in soft:
            lines.append(f"    ~ optional input: {p_}")
        if pk:
            lines.append(f"    - packages: pip install {' '.join(pk)}")
    if pointers:
        lines.append("")
        lines.append("LFS files to pull for this selection:")
        lines += ["    " + c for c in lfs_pull_commands(pointers)]
    if pk_all:
        lines.append("")
        lines.append("Python packages to install for this selection:  pip install " + " ".join(sorted(pk_all)))
    return lines, blocked
