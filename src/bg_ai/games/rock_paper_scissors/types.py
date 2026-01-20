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
    rounds_total: int
    round_index: int = 0
    score_a: int = 0
    score_b: int = 0
    last_a: Optional[RPSAction] = None
    last_b: Optional[RPSAction] = None
    last_winner: Optional[ActorId] = None  # "A", "B", or None for draw

    def is_done(self) -> bool:
        return self.round_index >= self.rounds_total
