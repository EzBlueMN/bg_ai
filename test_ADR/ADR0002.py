from __future__ import annotations

from typing import Callable, Dict

from test_ADR._adr_common import AdrMeta, run_slices

ADR = "0002"
STARTING_SLICE = 9
LAST_SLICE = 12
STATUS = "active"  # set "deprecated" if you intentionally stop maintaining this ADR


# -------------------------
# Slice tests (GLOBAL slice numbers)
# -------------------------

def test_s9() -> None:
    # TODO: implement validation for S9
    # Example:
    # - import your ActionEnum / RPSAction
    # - assert wire encoding/decoding works
    pass


def test_s10() -> None:
    # TODO: implement validation for S10
    pass


def test_s11() -> None:
    # TODO: implement validation for S11
    pass


def test_s12() -> None:
    # TODO: implement validation for S12
    pass

SLICE_TESTS: Dict[int, Callable[[], None]] = {
    9: test_s9,
    10: test_s10,
    11: test_s11,
    12: test_s12,
}


def main() -> None:
    meta = AdrMeta(
        adr=ADR,
        starting_slice=STARTING_SLICE,
        last_slice=LAST_SLICE,
        status=STATUS,
    )
    run_slices(meta=meta, slice_tests=SLICE_TESTS, fail_fast=True)


if __name__ == "__main__":
    main()
