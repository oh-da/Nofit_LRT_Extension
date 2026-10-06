"""The Nofit LRT extension demand chain as one pipeline.

``pipeline/steps.py`` is the manifest: every notebook and script of the chain, in run order, with its
stage, the steps whose outputs it reads, the inputs it needs (and which of them are Git LFS files), the
key outputs it writes, the environment variables that select its alternative runs, and the METHODOLOGY
section that explains it.  ``pipeline/runner.py`` executes a selection of steps in that order,
``pipeline/checks.py`` tells which inputs and packages are missing before anything runs, and
``pipeline/cli.py`` is the command line (``python3 -m pipeline --help``).

The notebooks and scripts themselves are unchanged: each still runs on its own with ``jupyter nbconvert``
or ``python3`` exactly as METHODOLOGY.md §9 lists them.  The package only puts that listing into one
machine-readable place and runs it.
"""
from .steps import STAGES, STEPS, Step, by_id, run_order  # noqa: F401

__all__ = ["STAGES", "STEPS", "Step", "by_id", "run_order"]
