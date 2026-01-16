from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional


RPSAction = Literal["R", "P", "S"]  # Rock, Paper, Scissors
ActorId = str


def beats(a: RPSAction, b: RPSAction) -> bool:
    return (a == "R" and b == "S") or (a == "P" and b == "R") or (a == "S" and b == "P")


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
