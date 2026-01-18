from __future__ import annotations

from typing import Callable, Dict

from test_ADR._adr_common import AdrMeta, run_slices

ADR = "0003"
STARTING_SLICE = 13
LAST_SLICE = 17
STATUS = "active"  # set "deprecated" if you intentionally stop maintaining this ADR


# -------------------------
# Slice tests (GLOBAL slice numbers)
# -------------------------

def test_s13() -> None:
    # TODO: implement validation for S13
    # Example:
    # - import your ActionEnum / RPSAction
    # - assert wire encoding/decoding works
    pass


def test_s14() -> None:
    # TODO: implement validation for S14
    pass


def test_s15() -> None:
    # TODO: implement validation for S15
    pass


def test_s16() -> None:
    # TODO: implement validation for S16
    pass


def test_s17() -> None:
    # TODO: implement validation for S17
    pass


SLICE_TESTS: Dict[int, Callable[[], None]] = {
    13: test_s13,
    14: test_s14,
    15: test_s15,
    16: test_s16,
    17: test_s17,
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
