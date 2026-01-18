from __future__ import annotations

import io
import runpy
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def ensure_src_on_syspath() -> None:
    """
    Ensure <repo_root>/src is on sys.path so imports like `import bg_ai` work
    when running this ADR runner from the terminal.
    """
    import sys

    src_path = str(repo_root() / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


def run_module_capture_stdout(module: str) -> str:
    """
    Run a Python module like: python -m <module>, capturing stdout.
    This matches real module execution semantics (run as __main__).
    """
    buf = io.StringIO()
    with redirect_stdout(buf):
        runpy.run_module(module, run_name="__main__")
    return buf.getvalue()


@dataclass(frozen=True)
class AdrMeta:
    adr: str
    starting_slice: int
    last_slice: int
    status: str = "active"  # "active" or "deprecated"


def run_slices(
    *,
    meta: AdrMeta,
    slice_tests: Dict[int, Callable[[], None]],
    fail_fast: bool = True,
) -> None:
    """
    Runs slice tests keyed by GLOBAL slice number (e.g. 13, 14, ...).
    Ensures all slices in [starting_slice..last_slice] exist.
    """
    ensure_src_on_syspath()

    print(f"Running ADR {meta.adr} slice tests (S{meta.starting_slice}..S{meta.last_slice})")
    print(f"Status: {meta.status}")

    missing = [s for s in range(meta.starting_slice, meta.last_slice + 1) if s not in slice_tests]
    if missing:
        raise AssertionError(f"Missing slice test functions for slices: {missing}")

    for s in range(meta.starting_slice, meta.last_slice + 1):
        try:
            slice_tests[s]()
            print(f"S{s} OK")
        except Exception as e:
            print(f"S{s} FAILED: {e}")
            if fail_fast:
                raise

    print("All requested slice tests completed.")
