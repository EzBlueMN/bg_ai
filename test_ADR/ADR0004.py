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
    from bg_ai.agents.agent import Agent
    from bg_ai.engine.match_runner import MatchConfig, MatchRunner
    from bg_ai.events.sink import InMemoryEventSink
    from bg_ai.games.rock_paper_scissors.game import RPSGame
    from bg_ai.games.rock_paper_scissors.types import RPSAction
    from bg_ai.policies.fixed_policy import FixedPolicy
    from bg_ai.stats.memory_store import InMemoryStatsStore

    store = InMemoryStatsStore()
    runner = MatchRunner()

    # Match 1: A=ROCK, B=SCISSORS => A wins
    sink1 = InMemoryEventSink()
    cfg = MatchConfig(game_config={"actors": ["A", "B"]}, seed=123, max_ticks=100)
    agents1 = {
        "A": Agent("A", FixedPolicy(RPSAction.ROCK)),
        "B": Agent("B", FixedPolicy(RPSAction.SCISSORS)),
    }
    _mid1, res1 = runner.run_match(RPSGame(), sink1, cfg, agents_by_id=agents1)
    store.ingest_match(result=res1, events=sink1.events())

    # Match 2: A=PAPER, B=PAPER => draw
    sink2 = InMemoryEventSink()
    agents2 = {
        "A": Agent("A", FixedPolicy(RPSAction.PAPER)),
        "B": Agent("B", FixedPolicy(RPSAction.PAPER)),
    }
    _mid2, res2 = runner.run_match(RPSGame(), sink2, cfg, agents_by_id=agents2)
    store.ingest_match(result=res2, events=sink2.events())

    q = store.query()

    # Action counts (wire values)
    assert q.action_counts("A") == {"R": 1, "P": 1}
    assert q.action_counts("B") == {"S": 1, "P": 1}

    # Records
    assert q.record("A") == {"wins": 1, "losses": 0, "draws": 1, "total": 2}
    assert q.record("B") == {"wins": 0, "losses": 1, "draws": 1, "total": 2}

    # Win rate (wins/total)
    assert q.win_rate("A") == 0.5
    assert q.win_rate("B") == 0.0



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
