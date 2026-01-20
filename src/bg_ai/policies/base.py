from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

from bg_ai.stats.base import StatsQuery

from bg_ai.engine.rng import RNG


JSONValue = Any
JSONDict = Dict[str, JSONValue]


@dataclass(frozen=True, slots=True)
class DecisionContext:
    match_id: str
    tick: int
    actor_id: str
    state: Any
    legal_actions: List[Any]
    rng: RNG
    game_id: str
    stats: StatsQuery


class Policy(Protocol):
    def decide(self, ctx: DecisionContext) -> Any:
        ...
