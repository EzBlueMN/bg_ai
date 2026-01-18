from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict

from test_ADR._adr_common import AdrMeta, run_module_capture_stdout, repo_root, run_slices

ADR = "0001"
STARTING_SLICE = 1
LAST_SLICE = 8
STATUS = "active"


def _runs_dir() -> Path:
    p = repo_root() / "runs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _assert(condition: bool, msg: str) -> None:
    if not condition:
        raise AssertionError(msg)


# -------------------------
# Slice tests (GLOBAL S1..S8)
# -------------------------

def test_s1() -> None:
    out = run_module_capture_stdout("bg_ai.cli.main").strip()
    _assert(out == "OK", f"S1 failed: expected 'OK', got {out!r}")


def test_s2() -> None:
    from bg_ai.engine.rng import RNG

    r = RNG.from_seed(123)
    a1 = r.fork("policy:A").randint(1, 999)
    a2 = r.fork("policy:A").randint(1, 999)
    b = r.fork("policy:B").randint(1, 999)

    _assert(a1 == a2, "S2 failed: same fork scope did not reproduce same first value")
    _assert(a1 != b, "S2 warning/fail: different scopes produced same value (unlikely)")


def test_s3() -> None:
    from bg_ai.events.model import Event
    from bg_ai.events.sink import InMemoryEventSink

    s = InMemoryEventSink()
    s.emit(Event(match_id="m1", idx=0, tick=0, type="match_start", payload={}))
    s.emit(Event(match_id="m1", idx=1, tick=0, type="tick_start", payload={"tick": 0}))

    _assert(len(s) == 2, f"S3 failed: expected 2 events, got {len(s)}")
    evs = s.events()
    _assert(evs[1].type == "tick_start", f"S3 failed: wrong event order/type: {evs[1].type!r}")


def test_s4() -> None:
    from bg_ai.events.model import Event
    from bg_ai.events.sink import InMemoryEventSink
    from bg_ai.events.codecs_jsonl import export_events_jsonl, import_events_jsonl

    s = InMemoryEventSink()
    s.emit(Event(match_id="m1", idx=0, tick=0, type="match_start", payload={}))
    s.emit(Event(match_id="m1", idx=1, tick=0, type="tick_start", payload={"tick": 0}))

    path = export_events_jsonl(_runs_dir() / "test_adr0001.jsonl", s.events())
    loaded = import_events_jsonl(path)

    _assert(len(loaded) == 2, f"S4 failed: expected 2 loaded events, got {len(loaded)}")
    _assert(loaded[1].payload["tick"] == 0, "S4 failed: payload mismatch after import")


def test_s5() -> None:
    from bg_ai.engine.match_runner import MatchRunner, MatchConfig
    from bg_ai.events.sink import InMemoryEventSink
    from bg_ai.games.base import MatchResult

    class NoActionGame:
        game_id = "no_action_v1"

        def initial_state(self, rng, config):
            return {"ticks_left": 3}

        def current_actor_ids(self, state):
            return []

        def apply_actions(self, state, actions_by_actor, rng):
            raise NotImplementedError

        def is_terminal(self, state):
            state["ticks_left"] -= 1
            return state["ticks_left"] <= 0

        def result(self, state):
            return MatchResult(outcome="done", details={"reason": "completed"})

    sink = InMemoryEventSink()
    runner = MatchRunner()
    cfg = MatchConfig(game_config={}, seed=123, max_ticks=100)

    _, result = runner.run_match(NoActionGame(), sink, cfg)

    events = sink.events()
    _assert(result.outcome == "done", f"S5 failed: expected outcome 'done', got {result.outcome!r}")
    _assert(events[0].type == "seed_set", f"S5 failed: first event should be seed_set, got {events[0].type!r}")
    _assert(events[1].type == "match_start", f"S5 failed: second event should be match_start, got {events[1].type!r}")
    _assert(events[-1].type == "match_end", f"S5 failed: last event should be match_end, got {events[-1].type!r}")

    tick_starts = [e for e in events if e.type == "tick_start"]
    tick_ends = [e for e in events if e.type == "tick_end"]

    _assert(len(tick_starts) == len(tick_ends),
            f"S5 failed: tick_start/tick_end mismatch: {len(tick_starts)} vs {len(tick_ends)}")

    expected_total = 2 + (2 * len(tick_starts)) + 1
    _assert(len(events) == expected_total, f"S5 failed: expected {expected_total} events, got {len(events)}")


def test_s6() -> None:
    from bg_ai.agents.agent import Agent
    from bg_ai.engine.match_runner import MatchRunner, MatchConfig
    from bg_ai.events.sink import InMemoryEventSink
    from bg_ai.games.base import MatchResult
    from bg_ai.policies.fixed_policy import FixedPolicy

    class OneActorGame:
        game_id = "one_actor_v1"

        def initial_state(self, rng, config):
            return {"ticks_left": 3, "last_action": None}

        def current_actor_ids(self, state):
            return ["A"]

        def legal_actions(self, state, actor_id):
            return ["X", "Y"]

        def apply_actions(self, state, actions_by_actor, rng):
            state["last_action"] = actions_by_actor["A"]
            state["ticks_left"] -= 1
            return state, []

        def is_terminal(self, state):
            return state["ticks_left"] <= 0

        def result(self, state):
            return MatchResult(outcome="done", details={"last_action": state["last_action"]})

    sink = InMemoryEventSink()
    runner = MatchRunner()
    cfg = MatchConfig(game_config={}, seed=123, max_ticks=100)

    agents = {"A": Agent(actor_id="A", policy=FixedPolicy("X"))}

    _, result = runner.run_match(OneActorGame(), sink, cfg, agents_by_id=agents)

    events = sink.events()
    types = [e.type for e in events]

    _assert("decision_requested" in types, "S6 failed: missing decision_requested")
    _assert("decision_provided" in types, "S6 failed: missing decision_provided")
    _assert("actions_applied" in types, "S6 failed: missing actions_applied")
    _assert(result.outcome == "done", f"S6 failed: expected outcome 'done', got {result.outcome!r}")
    _assert(result.details.get("last_action") == "X", f"S6 failed: expected last_action 'X', got {result.details!r}")

    dp = [e for e in events if e.type == "decision_provided"]
    _assert(len(dp) == 3, f"S6 failed: expected 3 decision_provided events, got {len(dp)}")


def test_s7() -> None:
    # NOTE: this will need updating when RPS becomes single-round + enums (ADR0002).
    from bg_ai.agents.agent import Agent
    from bg_ai.engine.match_runner import MatchRunner, MatchConfig
    from bg_ai.events.sink import InMemoryEventSink
    from bg_ai.games.rock_paper_scissors.game import RPSGame
    from bg_ai.policies.fixed_policy import FixedPolicy

    sink = InMemoryEventSink()
    runner = MatchRunner()

    cfg = MatchConfig(game_config={"rounds": 3, "actors": ["A", "B"]}, seed=123, max_ticks=100)

    agents = {
        "A": Agent(actor_id="A", policy=FixedPolicy("R")),
        "B": Agent(actor_id="B", policy=FixedPolicy("S")),
    }

    _, result = runner.run_match(RPSGame(), sink, cfg, agents_by_id=agents)

    _assert(result.outcome == "done", f"S7 failed: expected outcome 'done', got {result.outcome!r}")
    _assert(result.details.get("winner") == "A", f"S7 failed: expected winner 'A', got {result.details!r}")
    _assert(result.details.get("score_a") == 3, f"S7 failed: expected score_a=3, got {result.details!r}")
    _assert(result.details.get("score_b") == 0, f"S7 failed: expected score_b=0, got {result.details!r}")

    events = sink.events()
    dp = [e for e in events if e.type == "decision_provided"]
    _assert(len(dp) == 6, f"S7 failed: expected 6 decision_provided events, got {len(dp)}")


def test_s8() -> None:
    # NOTE: this will need updating when RPS becomes single-round + enums (ADR0002).
    from bg_ai.agents.agent import Agent
    from bg_ai.engine.match_runner import MatchRunner, MatchConfig
    from bg_ai.events.sink import InMemoryEventSink
    from bg_ai.events.codecs_jsonl import export_events_jsonl, import_events_jsonl
    from bg_ai.games.rock_paper_scissors.game import RPSGame
    from bg_ai.policies.fixed_policy import FixedPolicy
    from bg_ai.replay.replayer import Replayer, ReplayConfig

    sink = InMemoryEventSink()
    runner = MatchRunner()

    cfg = MatchConfig(game_config={"rounds": 3, "actors": ["A", "B"]}, seed=123, max_ticks=100)
    agents = {
        "A": Agent(actor_id="A", policy=FixedPolicy("R")),
        "B": Agent(actor_id="B", policy=FixedPolicy("S")),
    }

    _, live_result = runner.run_match(RPSGame(), sink, cfg, agents_by_id=agents)

    path = export_events_jsonl(_runs_dir() / "test_s8_rps.jsonl", sink.events())
    loaded_events = import_events_jsonl(path)

    replayer = Replayer()
    replay_result = replayer.replay(
        RPSGame(),
        loaded_events,
        ReplayConfig(game_config={"rounds": 3, "actors": ["A", "B"]}),
    )

    _assert(
        live_result.details == replay_result.details,
        f"S8 failed: live != replay\nlive={live_result.details}\nreplay={replay_result.details}",
    )


SLICE_TESTS: Dict[int, Callable[[], None]] = {
    1: test_s1,
    2: test_s2,
    3: test_s3,
    4: test_s4,
    5: test_s5,
    6: test_s6,
    7: test_s7,
    8: test_s8,
}


def main() -> None:
    meta = AdrMeta(adr=ADR, starting_slice=STARTING_SLICE, last_slice=LAST_SLICE, status=STATUS)
    run_slices(meta=meta, slice_tests=SLICE_TESTS, fail_fast=True)


if __name__ == "__main__":
    main()
