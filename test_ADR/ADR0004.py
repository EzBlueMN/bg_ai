from __future__ import annotations

from typing import Callable, Dict

from test_ADR._adr_common import AdrMeta, run_slices

ADR = "0004"
STARTING_SLICE = 18
LAST_SLICE = 21
STATUS = "active"  # set "deprecated" if you intentionally stop maintaining this ADR


# -------------------------
# Slice tests (GLOBAL slice numbers)
# -------------------------

def test_s18() -> None:
    # TODO: implement validation for S18
    # Example:
    # - import your ActionEnum / RPSAction
    # - assert wire encoding/decoding works
    pass


def test_s19() -> None:
    # TODO: implement validation for S19
    pass


def test_s20() -> None:
    # TODO: implement validation for S20
    pass


def test_s21() -> None:
    # TODO: implement validation for S21
    pass


SLICE_TESTS: Dict[int, Callable[[], None]] = {
    18: test_s18,
    19: test_s19,
    20: test_s20,
    21: test_s21,
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
