from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from bg_ai.games.base import MatchResult

from .types import FingersAction, MatchingFingersState


@dataclass(frozen=True, slots=True)
class MatchingFingersGame:
    """Matching Fingers game.

    One match is exactly one simultaneous reveal by two actors.

    Config (game_config):
      - actors: list[str] (default ["A", "B"])  # exactly 2 actors
      - same_winner: str (default actors[0])
      - different_winner: str (default actors[1])
    """

    game_id: str = "matching_fingers_v1"

    def initial_state(self, rng: Any, config: Dict[str, Any]) -> MatchingFingersState:
        actors = config.get("actors", ["A", "B"])
        if not isinstance(actors, list) or len(actors) != 2:
            raise ValueError("MatchingFingers requires config['actors'] to be a list of exactly 2 actor ids")

        a_id = str(actors[0])
        b_id = str(actors[1])

        same_winner = str(config.get("same_winner", a_id))
        different_winner = str(config.get("different_winner", b_id))

        if same_winner not in (a_id, b_id):
            raise ValueError("same_winner must be one of the configured actor ids")
        if different_winner not in (a_id, b_id):
            raise ValueError("different_winner must be one of the configured actor ids")
        if same_winner == different_winner:
            raise ValueError("same_winner and different_winner must be different actor ids")

        return MatchingFingersState(
            actors=(a_id, b_id),
            same_winner=same_winner,
            different_winner=different_winner,
        )

    def current_actor_ids(self, state: MatchingFingersState) -> List[str]:
        if state.is_done():
            return []
        return [state.actors[0], state.actors[1]]

    def legal_actions(self, state: MatchingFingersState, actor_id: str) -> Optional[List[FingersAction]]:
        if actor_id not in state.actors:
            raise ValueError(f"Unknown actor_id for MatchingFingers: {actor_id!r}")
        return [FingersAction.ONE, FingersAction.TWO]

    def apply_actions(
        self,
        state: MatchingFingersState,
        actions_by_actor: Dict[str, Any],
        rng: Any,
    ) -> Tuple[MatchingFingersState, List[Dict[str, Any]]]:
        if state.is_done():
            return state, []

        a_id, b_id = state.actors
        a = actions_by_actor.get(a_id)
        b = actions_by_actor.get(b_id)

        # Live play provides FingersAction enums; replay provides wire strings.
        # Note: FingersAction is a `str` Enum, so check enum type before checking `str`.
        if not isinstance(a, FingersAction) and isinstance(a, str):
            a = FingersAction.from_wire(a)
        if not isinstance(b, FingersAction) and isinstance(b, str):
            b = FingersAction.from_wire(b)

        if not isinstance(a, FingersAction) or not isinstance(b, FingersAction):
            raise ValueError(f"Invalid MatchingFingers actions: {a_id}={a!r}, {b_id}={b!r}")

        if a == b:
            winner = state.same_winner
        else:
            winner = state.different_winner

        state.last_a = a
        state.last_b = b
        state.last_winner = winner
        state.done = True

        domain_payloads = [
            {
                "game": self.game_id,
                "actors": [a_id, b_id],
                "actions": {a_id: a.to_wire(), b_id: b.to_wire()},
                "winner": winner,
                "same_winner": state.same_winner,
                "different_winner": state.different_winner,
            }
        ]
        return state, domain_payloads

    def is_terminal(self, state: MatchingFingersState) -> bool:
        return state.is_done()

    def result(self, state: MatchingFingersState) -> MatchResult:
        a_id, b_id = state.actors
        return MatchResult(
            outcome="done",
            details={
                "game_id": self.game_id,
                "actors": [a_id, b_id],
                "actions": {
                    a_id: (state.last_a.to_wire() if state.last_a else None),
                    b_id: (state.last_b.to_wire() if state.last_b else None),
                },
                "winner": state.last_winner,
                "same_winner": state.same_winner,
                "different_winner": state.different_winner,
            },
        )
