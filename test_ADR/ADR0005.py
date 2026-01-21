from __future__ import annotations

import io
from contextlib import redirect_stdout
from pathlib import Path
from typing import Callable, Dict

CURRENT_ADR = "0005"
STARTING_SLICE = 22
LAST_SLICE = 27
STATUS = "active"


# -------------------------
# Helpers
# -------------------------

def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _ensure_src_on_syspath() -> None:
    import sys

    src_path = str(_repo_root() / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


_ensure_src_on_syspath()


def _assert(condition: bool, msg: str) -> None:
    if not condition:
        raise AssertionError(msg)


def _run_slices(slice_tests: Dict[int, Callable[[], None]], fail_fast: bool = True) -> None:
    print("=" * 60)
    print(f"RUN test_ADR.ADR{CURRENT_ADR}")
    print("=" * 60)
    print(f"Running ADR {CURRENT_ADR} slice tests (S{STARTING_SLICE}..S{LAST_SLICE})")
    print(f"Status: {STATUS}")

    for s in range(STARTING_SLICE, LAST_SLICE + 1):
        if s not in slice_tests:
            print(f"S{s} SKIP (not defined)")
            continue

        try:
            slice_tests[s]()
            print(f"S{s} OK")
        except Exception as e:
            print(f"S{s} FAILED: {e}")
            if fail_fast:
                raise

    print("All requested slice tests completed.")


# -------------------------
# Slice tests
# -------------------------

def test_s22() -> None:
    """
    S22:
    - PhaseId exists
    - PhaseRules Protocol exists and is structurally usable
    """
    from bg_ai.engine.rng import RNG
    from bg_ai.games.phases.ids import PhaseId
    from bg_ai.games.phases.rules import PhaseRules

    class DummyRules:
        def current_actor_ids(self, state):
            return ["A", "B"]

        def legal_actions(self, state, actor_id: str):
            return ["X"]

        def apply_actions(self, state, actions_by_actor, rng: RNG):
            return state, [{"type": "dummy", "actions": dict(actions_by_actor)}]

    # phase id is wire-safe str
    p: PhaseId = "CHOOSE_ACTION"
    _assert(isinstance(p, str), "S22 failed: PhaseId must be str-compatible")

    # structural typing check (runtime)
    rules: PhaseRules = DummyRules()
    state0 = {"phase": p}
    _assert(rules.current_actor_ids(state0) == ["A", "B"], "S22 failed: current_actor_ids mismatch")
    _assert(rules.legal_actions(state0, "A") == ["X"], "S22 failed: legal_actions mismatch")

    rng = RNG.from_seed(123)
    state1, payloads = rules.apply_actions(state0, {"A": "X"}, rng)
    _assert(state1 == state0, "S22 failed: apply_actions returned wrong state")
    _assert(isinstance(payloads, list) and len(payloads) == 1, "S22 failed: domain payload shape mismatch")


def test_s23() -> None:
    pass


def test_s24() -> None:
    pass


def test_s25() -> None:
    pass


def test_s26() -> None:
    pass


def test_s27() -> None:
    pass


SLICE_TESTS: Dict[int, Callable[[], None]] = {
    22: test_s22,
    23: test_s23,
    24: test_s24,
    25: test_s25,
    26: test_s26,
    27: test_s27,
}


def main() -> None:
    _run_slices(SLICE_TESTS, fail_fast=True)


if __name__ == "__main__":
    main()
