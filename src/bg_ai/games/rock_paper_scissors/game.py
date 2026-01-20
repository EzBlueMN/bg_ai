from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from bg_ai.games.base import MatchResult

from .types import RPSAction, RPSState, beats


@dataclass(frozen=True, slots=True)
class RPSGame:
    """
    Rock Paper Scissors (RPS) game.

    ADR0003/S14: single-round game (one match = one round).

    Config (game_config):
      - actors: list[str] (default ["A","B"])  # exactly 2 actors
    """
    game_id: str = "rps_v1"

    def initial_state(self, rng: Any, config: Dict[str, Any]) -> RPSState:
        actors = config.get("actors", ["A", "B"])
        if not isinstance(actors, list) or len(actors) != 2:
            raise ValueError("RPS requires config['actors'] to be a list of exactly 2 actor ids")

        # No randomness needed for base RPS state, but rng is provided for consistency.
        return RPSState(actors=(str(actors[0]), str(actors[1])))

    def current_actor_ids(self, state: RPSState) -> List[str]:
        # Two-player simultaneous decision (single round).
        if state.is_done():
            return []
        return [state.actors[0], state.actors[1]]

    def legal_actions(self, state: RPSState, actor_id: str) -> Optional[List[RPSAction]]:
        if actor_id not in state.actors:
            raise ValueError(f"Unknown actor_id for RPS: {actor_id!r}")
        return [RPSAction.ROCK, RPSAction.PAPER, RPSAction.SCISSORS]

    def apply_actions(
        self,
        state: RPSState,
        actions_by_actor: Dict[str, Any],
        rng: Any,
    ) -> Tuple[RPSState, List[Dict[str, Any]]]:
        if state.is_done():
            return state, []

        a_id, b_id = state.actors
        a = actions_by_actor.get(a_id)
        b = actions_by_actor.get(b_id)

        # Live play provides RPSAction enums; replay provides wire strings.
        # Note: RPSAction is a `str` Enum, so check enum type before checking `str`.
        if not isinstance(a, RPSAction) and isinstance(a, str):
            a = RPSAction.from_wire(a)
        if not isinstance(b, RPSAction) and isinstance(b, str):
            b = RPSAction.from_wire(b)

        if not isinstance(a, RPSAction) or not isinstance(b, RPSAction):
            raise ValueError(f"Invalid RPS actions: {a_id}={a!r}, {b_id}={b!r}")

        # Determine winner of the round
        winner: Optional[str]
        if a == b:
            winner = None
        elif beats(a, b):
            winner = a_id
        else:
            winner = b_id

        state.last_a = a
        state.last_b = b
        state.last_winner = winner
        state.done = True

        domain_payloads = [
            {
                "game": self.game_id,
                "actors": [a_id, b_id],
                "actions": {
                    a_id: a.to_wire(),
                    b_id: b.to_wire(),
                },
                "winner": winner,
            }
        ]
        return state, domain_payloads

    def is_terminal(self, state: RPSState) -> bool:
        return state.is_done()

    def result(self, state: RPSState) -> MatchResult:
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
            },
        )
