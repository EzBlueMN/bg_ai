from __future__ import annotations

from typing import Callable, Dict

from test_ADR._adr_common import AdrMeta, run_slices

ADR = "0005"
STARTING_SLICE = 22
LAST_SLICE = 27
STATUS = "active"


def test_s22() -> None:
    # TODO: phase primitives
    raise NotImplementedError


def test_s23() -> None:
    # TODO: phase state wrapper
    raise NotImplementedError


def test_s24() -> None:
    # TODO: example game baseline
    raise NotImplementedError


def test_s25() -> None:
    # TODO: dispatcher pattern
    raise NotImplementedError


def test_s26() -> None:
    # TODO: policies
    raise NotImplementedError


def test_s27() -> None:
    # TODO: example module + replay smoke test
    raise NotImplementedError


SLICE_TESTS: Dict[int, Callable[[], None]] = {
    22: test_s22,
    23: test_s23,
    24: test_s24,
    25: test_s25,
    26: test_s26,
    27: test_s27,
}


def main() -> None:
    meta = AdrMeta(adr=ADR, starting_slice=STARTING_SLICE, last_slice=LAST_SLICE, status=STATUS)
    run_slices(meta=meta, slice_tests=SLICE_TESTS, fail_fast=True)


if __name__ == "__main__":
    main()
