from __future__ import annotations

import io
from contextlib import redirect_stdout
from pathlib import Path
from typing import Callable


CURRENT_ADR = "0001"
MAX_SLICES_FOR_CURRENT_ADR = 8

# -------------------------
# Helpers
# -------------------------

def _repo_root() -> Path:
    # This file is at: test_ADR/ADR0001.py
    # Repo root assumed: parent of test_ADR/
    return Path(__file__).resolve().parent.parent

def _ensure_src_on_syspath() -> None:
    """
    Ensure <repo_root>/src is on sys.path so imports like `import bg_ai` work
    when running this ADR runner from the terminal.
    """
    import sys

    src_path = str(_repo_root() / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

_ensure_src_on_syspath()

def _run_module(module: str) -> str:
    """
    Run a Python module like: python -m <module>, capturing stdout.
    This matches real module execution semantics (run as __main__).
    """
    import runpy

    buf = io.StringIO()
    with redirect_stdout(buf):
        runpy.run_module(module, run_name="__main__")
    return buf.getvalue()

def _assert(condition: bool, msg: str) -> None:
    if not condition:
        raise AssertionError(msg)


# -------------------------
# Slice tests (S1..S8)
# -------------------------

def test_s1() -> None:
    """
    S1: validate `python -m bg_ai.cli.main` prints OK.
    """
    out = _run_module("bg_ai.cli.main").strip()
    _assert(out == "OK", f"S1 failed: expected 'OK', got {out!r}")
    print("S1 OK")


def test_s2() -> None:
    """
    S2: validate deterministic RNG forks.
    """
    from bg_ai.engine.rng import RNG

    r = RNG.from_seed(123)
    a1 = r.fork("policy:A").randint(1, 999)
    a2 = r.fork("policy:A").randint(1, 999)
    b = r.fork("policy:B").randint(1, 999)

    _assert(a1 == a2, "S2 failed: same fork scope did not reproduce same first value")
    _assert(a1 != b, "S2 warning/fail: different scopes produced same value (unlikely)")

    print("S2 OK")


def test_s3() -> None:
    """
    S3: validate Event + InMemoryEventSink store events in order.
    """
    from bg_ai.events.model import Event
    from bg_ai.events.sink import InMemoryEventSink

    s = InMemoryEventSink()
    s.emit(Event(match_id="m1", idx=0, tick=0, type="match_start", payload={}))
    s.emit(Event(match_id="m1", idx=1, tick=0, type="tick_start", payload={"tick": 0}))

    _assert(len(s) == 2, f"S3 failed: expected 2 events, got {len(s)}")
    evs = s.events()
    _assert(evs[1].type == "tick_start", f"S3 failed: wrong event order/type: {evs[1].type!r}")

    print("S3 OK")


def test_s4() -> None:
    """
    S4: validate JSONL export/import round-trip.
    """
    from bg_ai.events.model import Event
    from bg_ai.events.sink import InMemoryEventSink
    from bg_ai.events.codecs_jsonl import export_events_jsonl, import_events_jsonl

    s = InMemoryEventSink()
    s.emit(Event(match_id="m1", idx=0, tick=0, type="match_start", payload={}))
    s.emit(Event(match_id="m1", idx=1, tick=0, type="tick_start", payload={"tick": 0}))

    path = export_events_jsonl(_repo_root() / "runs" / "test_adr0001.jsonl", s.events())
    loaded = import_events_jsonl(path)

    _assert(len(loaded) == 2, f"S4 failed: expected 2 loaded events, got {len(loaded)}")
    _assert(loaded[1].payload["tick"] == 0, "S4 failed: payload mismatch after import")

    print("S4 OK")


def test_s5() -> None:
    """
    S5: validate MatchRunner emits lifecycle + tick events for a no-action game.
    """
    from bg_ai.engine.match_runner import MatchRunner, MatchConfig
    from bg_ai.events.sink import InMemoryEventSink
    from bg_ai.games.base import MatchResult

    class NoActionGame:
        game_id = "no_action_v1"

        def initial_state(self, rng, config):
            return {"ticks_left": 3}

        def current_actor_ids(self, state):
            # No actions required in S5
            return []

        def apply_actions(self, state, actions_by_actor, rng):
            raise NotImplementedError

        def is_terminal(self, state):
            # Each tick consumes one step; terminal after 3 ticks.
            state["ticks_left"] -= 1
            return state["ticks_left"] <= 0

        def result(self, state):
            return MatchResult(outcome="done", details={"reason": "completed"})

    sink = InMemoryEventSink()
    runner = MatchRunner()
    cfg = MatchConfig(game_config={}, seed=123, max_ticks=100)

    match_id, result = runner.run_match(NoActionGame(), sink, cfg)

    events = sink.events()
    _assert(result.outcome == "done", f"S5 failed: expected outcome 'done', got {result.outcome!r}")
    _assert(events[0].type == "seed_set", f"S5 failed: first event should be seed_set, got {events[0].type!r}")
    _assert(events[1].type == "match_start", f"S5 failed: second event should be match_start, got {events[1].type!r}")
    _assert(events[-1].type == "match_end", f"S5 failed: last event should be match_end, got {events[-1].type!r}")

    # With 3 ticks: seed_set + match_start + 3*(tick_start+tick_end) + match_end = 9
    tick_starts = [e for e in events if e.type == "tick_start"]
    tick_ends = [e for e in events if e.type == "tick_end"]

    _assert(len(tick_starts) == len(tick_ends),
            f"S5 failed: tick_start/tick_end mismatch: {len(tick_starts)} vs {len(tick_ends)}")

    expected_total = 2 + (2 * len(tick_starts)) + 1  # seed_set + match_start + 2 per tick + match_end
    _assert(len(events) == expected_total, f"S5 failed: expected {expected_total} events, got {len(events)}")

    print("S5 OK")


def test_s6() -> None:
    """
    S6: validate decision wiring:
    - decision_requested / decision_provided emitted
    - actions_applied emitted
    - match runs without terminal errors
    """
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
            # no domain events in this test
            return state, []

        def is_terminal(self, state):
            return state["ticks_left"] <= 0

        def result(self, state):
            return MatchResult(outcome="done", details={"last_action": state["last_action"]})

    sink = InMemoryEventSink()
    runner = MatchRunner()
    cfg = MatchConfig(game_config={}, seed=123, max_ticks=100)

    agents = {"A": Agent(actor_id="A", policy=FixedPolicy("X"))}

    match_id, result = runner.run_match(OneActorGame(), sink, cfg, agents_by_id=agents)

    events = sink.events()
    types = [e.type for e in events]

    _assert("decision_requested" in types, "S6 failed: missing decision_requested")
    _assert("decision_provided" in types, "S6 failed: missing decision_provided")
    _assert("actions_applied" in types, "S6 failed: missing actions_applied")
    _assert(result.outcome == "done", f"S6 failed: expected outcome 'done', got {result.outcome!r}")
    _assert(result.details.get("last_action") == "X", f"S6 failed: expected last_action 'X', got {result.details!r}")

    # There should be exactly 3 decisions for 3 ticks (one actor per tick)
    dp = [e for e in events if e.type == "decision_provided"]
    _assert(len(dp) == 3, f"S6 failed: expected 3 decision_provided events, got {len(dp)}")

    print("S6 OK")

def test_s7() -> None:
    """
    S7: validate RPS end-to-end:
    - 2 actors (A,B), simultaneous decisions per tick
    - scores update correctly
    - result winner computed
    - decision events count matches rounds * 2
    """
    from bg_ai.agents.agent import Agent
    from bg_ai.engine.match_runner import MatchRunner, MatchConfig
    from bg_ai.events.sink import InMemoryEventSink
    from bg_ai.games.rock_paper_scissors.game import RPSGame
    from bg_ai.policies.fixed_policy import FixedPolicy

    sink = InMemoryEventSink()
    runner = MatchRunner()

    # 3 rounds, A always Rock, B always Scissors -> A wins all rounds
    cfg = MatchConfig(game_config={"rounds": 3, "actors": ["A", "B"]}, seed=123, max_ticks=100)

    agents = {
        "A": Agent(actor_id="A", policy=FixedPolicy("R")),
        "B": Agent(actor_id="B", policy=FixedPolicy("S")),
    }

    match_id, result = runner.run_match(RPSGame(), sink, cfg, agents_by_id=agents)

    _assert(result.outcome == "done", f"S7 failed: expected outcome 'done', got {result.outcome!r}")
    _assert(result.details.get("winner") == "A", f"S7 failed: expected winner 'A', got {result.details!r}")
    _assert(result.details.get("score_a") == 3, f"S7 failed: expected score_a=3, got {result.details!r}")
    _assert(result.details.get("score_b") == 0, f"S7 failed: expected score_b=0, got {result.details!r}")

    events = sink.events()
    dp = [e for e in events if e.type == "decision_provided"]
    _assert(len(dp) == 6, f"S7 failed: expected 6 decision_provided events (3 rounds * 2 actors), got {len(dp)}")

    # Optional: ensure at least one domain_event was emitted
    de = [e for e in events if e.type == "domain_event"]
    _assert(len(de) >= 1, "S7 failed: expected at least one domain_event")

    print("S7 OK")

def test_s8() -> None:
    """
    S8: validate replay without policies:
    - run live match (RPS)
    - export JSONL
    - import JSONL
    - replay events
    - replay result matches live result
    """
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

    match_id, live_result = runner.run_match(RPSGame(), sink, cfg, agents_by_id=agents)

    # Export/import
    path = export_events_jsonl(_repo_root() / "runs" / "test_s8_rps.jsonl", sink.events())
    loaded_events = import_events_jsonl(path)

    # Replay (no agents/policies)
    replayer = Replayer()
    replay_result = replayer.replay(RPSGame(), loaded_events, ReplayConfig(game_config={"rounds": 3, "actors": ["A", "B"]}))

    _assert(live_result.details == replay_result.details, f"S8 failed: live != replay\nlive={live_result.details}\nreplay={replay_result.details}")

    print("S8 OK")


# -------------------------
# Dispatch (generic runner)
# -------------------------

def test_slice(index: int) -> None:
    table: dict[int, Callable[[], None]] = {
        1: test_s1,
        2: test_s2,
        3: test_s3,
        4: test_s4,
        5: test_s5,
        6: test_s6,
        7: test_s7,
        8: test_s8,
    }

    if index not in table:
        raise ValueError(f"Invalid slice index: {index}")

    table[index]()


def main() -> None:
    print(f"Running ADR {CURRENT_ADR} slice tests (1..{MAX_SLICES_FOR_CURRENT_ADR})")

    for i in range(1, MAX_SLICES_FOR_CURRENT_ADR + 1):
        try:
            test_slice(i)
        except Exception as e:
            print(f"S{i} FAILED: {e}")
            raise

    print("All requested slice tests completed.")


if __name__ == "__main__":
    main()
