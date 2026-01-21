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
    cfg = MatchConfig(game_config={"actors": ["A", "B"]}, seed=123, max_ticks=100)

    # Match 1: A=ROCK, B=SCISSORS => A wins
    sink1 = InMemoryEventSink()
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

    # Action counts (wire values)
    assert store.action_counts("A") == {"R": 1, "P": 1}
    assert store.action_counts("B") == {"S": 1, "P": 1}

    # Records
    assert store.record("A") == {"wins": 1, "losses": 0, "draws": 1, "total": 2}
    assert store.record("B") == {"wins": 0, "losses": 1, "draws": 1, "total": 2}

    # Win rate (wins/total)
    assert store.win_rate("A") == 0.5
    assert store.win_rate("B") == 0.0




def test_s19() -> None:
    from dataclasses import dataclass

    from bg_ai.agents.agent import Agent
    from bg_ai.engine.match_runner import MatchConfig, MatchRunner
    from bg_ai.events.sink import InMemoryEventSink
    from bg_ai.games.rock_paper_scissors.game import RPSGame
    from bg_ai.games.rock_paper_scissors.types import RPSAction
    from bg_ai.policies.base import DecisionContext
    from bg_ai.stats.base import StatsQuery
    from bg_ai.stats.memory_store import InMemoryStatsStore

    @dataclass(frozen=True, slots=True)
    class _StatsAwarePolicy:
        stats: StatsQuery

        def decide(self, ctx: DecisionContext) -> object:
            # S19 acceptance: ctx.stats is the object we injected
            assert ctx.stats is self.stats
            return RPSAction.ROCK

    runner = MatchRunner()
    cfg = MatchConfig(game_config={"actors": ["A", "B"]}, seed=123, max_ticks=100)

    # Provide a real query handle (store itself is a StatsQuery in S18 MVP)
    store = InMemoryStatsStore()

    sink = InMemoryEventSink()
    agents = {
        "A": Agent("A", _StatsAwarePolicy(store)),
        "B": Agent("B", _StatsAwarePolicy(store)),
    }

    _mid, res = runner.run_match(RPSGame(), sink, cfg, agents_by_id=agents, stats_query=store)
    assert res.outcome == "done"


def test_s20() -> None:
    # S20: run multiple matches sequentially, updating stats after each match.
    from bg_ai.agents.agent import Agent
    from bg_ai.games.rock_paper_scissors.game import RPSGame
    from bg_ai.games.rock_paper_scissors.types import RPSAction
    from bg_ai.policies.fixed_policy import FixedPolicy
    from bg_ai.sim.sim_runner import SimConfig, SimRunner
    from bg_ai.stats.memory_store import InMemoryStatsStore

    store = InMemoryStatsStore()
    runner = SimRunner()

    config = SimConfig(
        game_config={"actors": ["A", "B"]},
        num_matches=2,
        seed=123,
        max_ticks=100,
    )

    agents = {
        "A": Agent("A", FixedPolicy(RPSAction.ROCK)),
        "B": Agent("B", FixedPolicy(RPSAction.SCISSORS)),
    }

    sim_res = runner.run_matches(
        game=RPSGame(),
        config=config,
        agents_by_id=agents,
        stats_store=store,
        stats_query=store,
    )

    assert len(sim_res.match_results) == 2

    # Stable assertions: 2 matches => 2 decisions each actor => 2 total actions each
    assert store.action_counts("A") == {"R": 2}
    assert store.action_counts("B") == {"S": 2}

    assert store.record("A") == {"wins": 2, "losses": 0, "draws": 0, "total": 2}
    assert store.record("B") == {"wins": 0, "losses": 2, "draws": 0, "total": 2}


def test_s21() -> None:
    """
    S21: ADR0004 integration assertions:
    - StatsStore exists and can ingest match results
    - MatchRunner provides ctx.stats to policies (S19)
    - SimRunner updates stats across multiple matches (S20)
    """
    from dataclasses import dataclass

    from bg_ai.agents.agent import Agent
    from bg_ai.games.rock_paper_scissors.game import RPSGame
    from bg_ai.games.rock_paper_scissors.types import RPSAction
    from bg_ai.policies.base import DecisionContext
    from bg_ai.sim.sim_runner import SimConfig, SimRunner
    from bg_ai.stats.base import StatsQuery
    from bg_ai.stats.memory_store import InMemoryStatsStore

    store = InMemoryStatsStore()

    @dataclass(frozen=True, slots=True)
    class _StatsAwarePolicy:
        expected_stats: StatsQuery
        action: RPSAction

        def decide(self, ctx: DecisionContext) -> object:
            # S21: the DecisionContext.stats object is the injected one
            assert ctx.stats is self.expected_stats
            return self.action

    agents = {
        "A": Agent("A", _StatsAwarePolicy(store, RPSAction.ROCK)),
        "B": Agent("B", _StatsAwarePolicy(store, RPSAction.SCISSORS)),
    }

    sim_res = SimRunner().run_matches(
        game=RPSGame(),
        config=SimConfig(game_config={"actors": ["A", "B"]}, num_matches=3, seed=100, max_ticks=100),
        agents_by_id=agents,
        stats_store=store,
        stats_query=store,
    )

    assert len(sim_res.match_results) == 3

    # RPS: A always ROCK, B always SCISSORS => A always wins
    assert store.record("A") == {"wins": 3, "losses": 0, "draws": 0, "total": 3}
    assert store.record("B") == {"wins": 0, "losses": 3, "draws": 0, "total": 3}

    # Action counts: 3 matches => each actor decided 3 times
    assert store.action_counts("A") == {"R": 3}
    assert store.action_counts("B") == {"S": 3}



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
