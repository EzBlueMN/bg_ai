from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from bg_ai.games.action_enum import ActionEnum
from bg_ai.games.phases import PhaseId, PhaseState


class BuyPlayAction(ActionEnum):
    BUY = "BUY"
    PLAY = "PLAY"
    BOTH = "BOTH"
    PASS = "PASS"


# Phase identifiers (wire-safe strings)
PHASE_CHOOSE: PhaseId = "CHOOSE"
PHASE_RESOLVE: PhaseId = "RESOLVE"
PHASE_END: PhaseId = "END"


@dataclass(slots=True)
class BuyPlayMemory:
    """
    Public memory for the Buy/Play game.
    """
    actors: tuple[str, str]
    coins_by_actor: Dict[str, int]
    points_by_actor: Dict[str, int]
    turn: int
    max_turns: int


@dataclass(slots=True)
class BuyPlayPending:
    """
    Pending selection captured during CHOOSE, resolved in RESOLVE.
    """
    actions_by_actor: Dict[str, BuyPlayAction]


BuyPlayState = PhaseState[BuyPlayMemory, BuyPlayPending]
