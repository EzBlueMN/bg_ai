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
    from bg_ai.agents.agent import Agent
    from bg_ai.engine.match_runner import MatchConfig, MatchRunner
    from bg_ai.events.codecs_jsonl import export_events_jsonl, import_events_jsonl
    from bg_ai.events.sink import InMemoryEventSink
    from bg_ai.games.action_enum import ActionEnum
    from bg_ai.games.rock_paper_scissors.game import RPSGame
    from bg_ai.games.rock_paper_scissors.types import RPSAction
    from bg_ai.policies.fixed_policy import FixedPolicy

    # 1) Enum basics
    assert issubclass(RPSAction, ActionEnum)
    assert RPSAction.ROCK.to_wire() == "R"
    assert RPSAction.from_wire("P") is RPSAction.PAPER

    # 2) Running a match with enum actions must still work.
    sink = InMemoryEventSink()
    runner = MatchRunner()
    cfg = MatchConfig(game_config={"actors": ["A", "B"]}, seed=123, max_ticks=100)


    agents = {
        "A": Agent(actor_id="A", policy=FixedPolicy(RPSAction.ROCK)),
        "B": Agent(actor_id="B", policy=FixedPolicy(RPSAction.SCISSORS)),
    }

    _, result = runner.run_match(RPSGame(), sink, cfg, agents_by_id=agents)
    assert result.outcome == "done"

    # 3) Event payloads must be JSON-serializable (enums should not leak into payloads)
    decision_events = [e for e in sink.events() if e.type == "decision_provided"]
    assert decision_events, "Expected decision_provided events"
    assert all(isinstance(e.payload["action"], str) for e in decision_events)

    applied = [e for e in sink.events() if e.type == "actions_applied"]
    assert applied, "Expected actions_applied events"
    assert all(isinstance(v, str) for v in applied[-1].payload["actions"].values())

    # 4) JSONL export/import roundtrip should work
    out_path = export_events_jsonl("runs/adr0003_s13_enum_actions.jsonl", sink.events())
    loaded = import_events_jsonl(out_path)
    assert len(loaded) == len(sink.events())



def test_s14() -> None:
    from bg_ai.agents.agent import Agent
    from bg_ai.engine.match_runner import MatchConfig, MatchRunner
    from bg_ai.events.sink import InMemoryEventSink
    from bg_ai.games.rock_paper_scissors.game import RPSGame
    from bg_ai.games.rock_paper_scissors.types import RPSAction
    from bg_ai.policies.fixed_policy import FixedPolicy

    sink = InMemoryEventSink()
    runner = MatchRunner()

    # S14: RPS is single-round, so there is no "rounds" in config.
    cfg = MatchConfig(game_config={"actors": ["A", "B"]}, seed=123, max_ticks=100)

    agents = {
        "A": Agent(actor_id="A", policy=FixedPolicy(RPSAction.ROCK)),
        "B": Agent(actor_id="B", policy=FixedPolicy(RPSAction.SCISSORS)),
    }

    _, result = runner.run_match(RPSGame(), sink, cfg, agents_by_id=agents)
    assert result.outcome == "done"
    assert result.details.get("winner") == "A"

    # Exactly one tick worth of decisions: 2 actors => 2 decision_provided
    decision_events = [e for e in sink.events() if e.type == "decision_provided"]
    assert len(decision_events) == 2

    # Terminal after one actions_applied
    applied = [e for e in sink.events() if e.type == "actions_applied"]
    assert len(applied) == 1



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
