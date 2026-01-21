from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from bg_ai.games.base import MatchResult
from bg_ai.games.phases.ids import PhaseId
from bg_ai.games.phases.rules import PhaseRules

from .rules import CHOOSE_RULES, END_RULES, RESOLVE_RULES
from .types import (
    BuyPlayAction,
    BuyPlayMemory,
    BuyPlayState,
    PHASE_CHOOSE,
    PHASE_END,
    PHASE_RESOLVE,
)


@dataclass(frozen=True, slots=True)
class BuyPlayGame:
    """
    S25: Dispatcher-pattern version.
    The Game delegates phase behavior to PhaseRules objects.
    """
    game_id: str = "buy_play_v1"

    phase_rules_by_id: Dict[PhaseId, PhaseRules] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "phase_rules_by_id",
            {
                PHASE_CHOOSE: CHOOSE_RULES,
                PHASE_RESOLVE: RESOLVE_RULES,
                PHASE_END: END_RULES,
            },
        )

    def _rules(self, phase: PhaseId) -> PhaseRules:
        try:
            return self.phase_rules_by_id[phase]
        except KeyError as e:
            raise ValueError(f"Unknown phase: {phase!r}") from e

    def initial_state(self, rng: Any, config: Dict[str, Any]) -> BuyPlayState:
        actors = config.get("actors", ["A", "B"])
        if not isinstance(actors, list) or len(actors) != 2:
            raise ValueError("BuyPlay requires config['actors'] to be a list of exactly 2 actor ids")

        a_id = str(actors[0])
        b_id = str(actors[1])

        max_turns = int(config.get("max_turns", 3))
        if max_turns <= 0:
            raise ValueError("BuyPlay requires config['max_turns'] > 0")

        mem = BuyPlayMemory(
            actors=(a_id, b_id),
            coins_by_actor={a_id: 0, b_id: 0},
            points_by_actor={a_id: 0, b_id: 0},
            turn=0,
            max_turns=max_turns,
        )
        return BuyPlayState(phase=PHASE_CHOOSE, memory=mem, pending=None)

    def current_actor_ids(self, state: BuyPlayState) -> List[str]:
        return self._rules(state.phase).current_actor_ids(state)

    def legal_actions(self, state: BuyPlayState, actor_id: str) -> Optional[List[BuyPlayAction]]:
        if state.phase == PHASE_END:
            return []
        return self._rules(state.phase).legal_actions(state, actor_id)  # type: ignore[return-value]

    def apply_actions(
        self,
        state: BuyPlayState,
        actions_by_actor: Dict[str, Any],
        rng: Any,
    ) -> Tuple[BuyPlayState, List[Dict[str, Any]]]:
        if state.phase == PHASE_END:
            return state, []
        # MatchRunner passes RNG; keep signature Any here but delegate expects RNG.
        rules = self._rules(state.phase)
        return rules.apply_actions(state, actions_by_actor, rng)  # type: ignore[arg-type]

    def is_terminal(self, state: BuyPlayState) -> bool:
        return state.phase == PHASE_END

    def result(self, state: BuyPlayState) -> MatchResult:
        a_id, b_id = state.memory.actors
        a_points = int(state.memory.points_by_actor.get(a_id, 0))
        b_points = int(state.memory.points_by_actor.get(b_id, 0))

        winner: Optional[str]
        if a_points == b_points:
            winner = None
        elif a_points > b_points:
            winner = a_id
        else:
            winner = b_id

        return MatchResult(
            outcome="done",
            details={
                "game_id": self.game_id,
                "actors": [a_id, b_id],
                "winner": winner,
                "turn": int(state.memory.turn),
                "max_turns": int(state.memory.max_turns),
                "coins_by_actor": dict(state.memory.coins_by_actor),
                "points_by_actor": dict(state.memory.points_by_actor),
            },
        )
