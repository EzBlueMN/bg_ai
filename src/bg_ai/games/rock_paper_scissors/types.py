from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from bg_ai.games.action_enum import ActionEnum


class RPSAction(ActionEnum):
    ROCK = "R"
    PAPER = "P"
    SCISSORS = "S"


ActorId = str


def beats(a: RPSAction, b: RPSAction) -> bool:
    return (
        (a is RPSAction.ROCK and b is RPSAction.SCISSORS)
        or (a is RPSAction.PAPER and b is RPSAction.ROCK)
        or (a is RPSAction.SCISSORS and b is RPSAction.PAPER)
    )


@dataclass
class RPSState:
    """Single-match RPS state.

    ADR0003/S14: RPS is one round (one simultaneous action per actor),
    with multi-match aggregation handled by the generic series/format layer.
    """

    actors: tuple[str, str] = ("A", "B")
    done: bool = False
    last_a: Optional[RPSAction] = None
    last_b: Optional[RPSAction] = None
    last_winner: Optional[ActorId] = None  # actor id or None for draw

    def is_done(self) -> bool:
        return self.done
