from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from bg_ai.games.base import MatchResult

from .types import RPSAction, RPSState, beats


@dataclass(frozen=True, slots=True)
class RPSGame:
    """
    Rock Paper Scissors (RPS) game.

    Config (game_config):
      - rounds: int (default 3)
      - actors: list[str] (default ["A","B"])  # MVP assumes exactly 2 actors
    """
    game_id: str = "rps_v1"

    def initial_state(self, rng: Any, config: Dict[str, Any]) -> RPSState:
        rounds = int(config.get("rounds", 3))
        actors = config.get("actors", ["A", "B"])
        if not isinstance(actors, list) or len(actors) != 2:
            raise ValueError("RPS requires config['actors'] to be a list of exactly 2 actor ids")

        if rounds <= 0:
            raise ValueError("rounds must be > 0")

        # No randomness needed for base RPS state, but rng is provided for consistency.
        return RPSState(rounds_total=rounds)

    def current_actor_ids(self, state: RPSState) -> List[str]:
        # Two-player simultaneous decision each round.
        if state.is_done():
            return []
        return ["A", "B"]

    def legal_actions(self, state: RPSState, actor_id: str) -> Optional[List[RPSAction]]:
        if actor_id not in ("A", "B"):
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

        a = actions_by_actor.get("A")
        b = actions_by_actor.get("B")
        if not isinstance(a, RPSAction) or not isinstance(b, RPSAction):
            raise ValueError(f"Invalid RPS actions: A={a!r}, B={b!r}")

        # Determine winner of the round
        winner: Optional[str]
        if a == b:
            winner = None
        elif beats(a, b):
            winner = "A"
        else:
            winner = "B"

        # Update scores
        if winner == "A":
            state.score_a += 1
        elif winner == "B":
            state.score_b += 1

        state.last_a = a
        state.last_b = b
        state.last_winner = winner
        state.round_index += 1

        # Domain event payload (engine will wrap it)
        domain_payloads = [
            {
                "game": self.game_id,
                "round": state.round_index,  # 1-based after increment
                "A": a.to_wire(),
                "B": b.to_wire(),
                "winner": winner,
                "score_a": state.score_a,
                "score_b": state.score_b,
            }
        ]
        return state, domain_payloads

    def is_terminal(self, state: RPSState) -> bool:
        return state.is_done()

    def result(self, state: RPSState) -> MatchResult:
        if state.score_a > state.score_b:
            winner = "A"
        elif state.score_b > state.score_a:
            winner = "B"
        else:
            winner = None

        return MatchResult(
            outcome="done",
            details={
                "game_id": self.game_id,
                "rounds": state.rounds_total,
                "score_a": state.score_a,
                "score_b": state.score_b,
                "winner": winner,
            },
        )
