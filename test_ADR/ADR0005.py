from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict

CURRENT_ADR = "0005"
STARTING_SLICE = 22
LAST_SLICE = 27
STATUS = "active"


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _ensure_src_on_syspath() -> None:
    import sys

    src_path = str(_repo_root() / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


_ensure_src_on_syspath()


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


def test_s22() -> None:
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

    p: PhaseId = "CHOOSE_ACTION"
    assert isinstance(p, str)

    rules: PhaseRules = DummyRules()
    state0 = {"phase": p}
    assert rules.current_actor_ids(state0) == ["A", "B"]
    assert rules.legal_actions(state0, "A") == ["X"]

    rng = RNG.from_seed(123)
    state1, payloads = rules.apply_actions(state0, {"A": "X"}, rng)
    assert state1 == state0
    assert isinstance(payloads, list) and len(payloads) == 1


def test_s23() -> None:
    from dataclasses import dataclass
    from bg_ai.games.phases.state import PhaseState

    @dataclass(frozen=True, slots=True)
    class Memory:
        coins: int

    @dataclass(frozen=True, slots=True)
    class Pending:
        chosen: str

    st = PhaseState[Memory, Pending](phase="INIT", memory=Memory(coins=3), pending=None)
    assert st.phase == "INIT"
    assert st.memory.coins == 3
    assert st.pending is None

    st2 = PhaseState[Memory, Pending](phase="CHOOSE", memory=st.memory, pending=Pending(chosen="BUY"))
    assert st2.phase == "CHOOSE"
    assert st2.pending is not None and st2.pending.chosen == "BUY"


def test_s24() -> None:
    from dataclasses import dataclass

    from bg_ai.agents.agent import Agent
    from bg_ai.engine.match_runner import MatchConfig, MatchRunner
    from bg_ai.events.sink import InMemoryEventSink
    from bg_ai.games.buy_play.game import BuyPlayGame
    from bg_ai.games.buy_play.types import BuyPlayAction, PHASE_CHOOSE, PHASE_RESOLVE
    from bg_ai.policies.base import DecisionContext

    @dataclass(frozen=True, slots=True)
    class PhaseAwarePolicy:
        choose_action: BuyPlayAction

        def decide(self, ctx: DecisionContext) -> object:
            if getattr(ctx.state, "phase", None) == PHASE_CHOOSE:
                return self.choose_action
            if getattr(ctx.state, "phase", None) == PHASE_RESOLVE:
                return BuyPlayAction.PASS
            return BuyPlayAction.PASS

    sink = InMemoryEventSink()
    runner = MatchRunner()
    cfg = MatchConfig(game_config={"actors": ["A", "B"], "max_turns": 1}, seed=123, max_ticks=50)

    agents = {
        "A": Agent("A", PhaseAwarePolicy(BuyPlayAction.BUY)),
        "B": Agent("B", PhaseAwarePolicy(BuyPlayAction.PASS)),
    }

    _mid, res = runner.run_match(BuyPlayGame(), sink, cfg, agents_by_id=agents)

    assert res.details["coins_by_actor"] == {"A": 1, "B": 0}
    assert res.details["points_by_actor"] == {"A": 0, "B": 0}
    assert res.details["turn"] == 1
    assert res.details["winner"] is None

    applied = [e for e in sink.events() if e.type == "actions_applied"]
    assert len(applied) == 2


def test_s25() -> None:
    # S25: BuyPlay uses dispatcher pattern and exposes phase_rules_by_id.
    from dataclasses import dataclass

    from bg_ai.agents.agent import Agent
    from bg_ai.engine.match_runner import MatchConfig, MatchRunner
    from bg_ai.events.sink import InMemoryEventSink
    from bg_ai.games.buy_play.game import BuyPlayGame
    from bg_ai.games.buy_play.rules import ChoosePhaseRules, ResolvePhaseRules
    from bg_ai.games.buy_play.types import BuyPlayAction, PHASE_CHOOSE, PHASE_RESOLVE
    from bg_ai.policies.base import DecisionContext

    game = BuyPlayGame()
    assert hasattr(game, "phase_rules_by_id")
    assert isinstance(game.phase_rules_by_id[PHASE_CHOOSE], ChoosePhaseRules)
    assert isinstance(game.phase_rules_by_id[PHASE_RESOLVE], ResolvePhaseRules)

    # Also verify legal_actions differs by phase via delegation
    st = game.initial_state(rng=None, config={"actors": ["A", "B"], "max_turns": 1})
    assert st.phase == PHASE_CHOOSE
    assert BuyPlayAction.PASS in (game.legal_actions(st, "A") or [])
    assert BuyPlayAction.BUY in (game.legal_actions(st, "A") or [])

    @dataclass(frozen=True, slots=True)
    class PhaseAwarePolicy:
        choose_action: BuyPlayAction

        def decide(self, ctx: DecisionContext) -> object:
            if getattr(ctx.state, "phase", None) == PHASE_CHOOSE:
                return self.choose_action
            if getattr(ctx.state, "phase", None) == PHASE_RESOLVE:
                return BuyPlayAction.PASS
            return BuyPlayAction.PASS

    sink = InMemoryEventSink()
    runner = MatchRunner()
    cfg = MatchConfig(game_config={"actors": ["A", "B"], "max_turns": 1}, seed=123, max_ticks=50)

    agents = {
        "A": Agent("A", PhaseAwarePolicy(BuyPlayAction.BUY)),
        "B": Agent("B", PhaseAwarePolicy(BuyPlayAction.PASS)),
    }

    _mid, res = runner.run_match(game, sink, cfg, agents_by_id=agents)
    assert res.details["coins_by_actor"] == {"A": 1, "B": 0}

    applied = [e for e in sink.events() if e.type == "actions_applied"]
    assert len(applied) == 2

def test_s26() -> None:
    # S26: Policies for phase-driven gameplay.
    from bg_ai.agents.agent import Agent
    from bg_ai.engine.match_runner import MatchConfig, MatchRunner
    from bg_ai.events.sink import InMemoryEventSink
    from bg_ai.games.buy_play import BuyPlayGame, ConservativeBuyPlayPolicy, GreedyBuyPlayPolicy

    sink = InMemoryEventSink()
    runner = MatchRunner()

    # 2 turns: Greedy should get 1 point on turn 2 via BOTH
    # Conservative (target_coins=2) will BUY both turns and score 0 points.
    cfg = MatchConfig(game_config={"actors": ["A", "B"], "max_turns": 2}, seed=123, max_ticks=200)

    agents = {
        "A": Agent("A", GreedyBuyPlayPolicy()),
        "B": Agent("B", ConservativeBuyPlayPolicy(target_coins=2)),
    }

    _mid, res = runner.run_match(BuyPlayGame(), sink, cfg, agents_by_id=agents)

    assert res.details["points_by_actor"] == {"A": 1, "B": 0}
    assert res.details["winner"] == "A"

    # We should still see 2 phases per turn => 4 actions_applied events for 2 turns.
    applied = [e for e in sink.events() if e.type == "actions_applied"]
    assert len(applied) == 4


SLICE_TESTS: Dict[int, Callable[[], None]] = {
    22: test_s22,
    23: test_s23,
    24: test_s24,
    25: test_s25,
    26: test_s26,
}


def main() -> None:
    _run_slices(SLICE_TESTS, fail_fast=True)


if __name__ == "__main__":
    main()
