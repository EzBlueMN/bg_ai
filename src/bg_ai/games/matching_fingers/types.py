from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from bg_ai.games.action_enum import ActionEnum


class FingersAction(ActionEnum):
    ONE = "1"
    TWO = "2"


ActorId = str


@dataclass
class MatchingFingersState:
    """Single-round matching fingers state.

    Each player reveals 1 or 2 fingers.
    If both reveal the same number: `same_winner` wins.
    If different: `different_winner` wins.
    """

    actors: tuple[str, str] = ("A", "B")
    same_winner: ActorId = "A"
    different_winner: ActorId = "B"

    done: bool = False
    last_a: Optional[FingersAction] = None
    last_b: Optional[FingersAction] = None
    last_winner: Optional[ActorId] = None

    def is_done(self) -> bool:
        return self.done
