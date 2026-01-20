from __future__ import annotations

from typing import Dict, List, Protocol

from bg_ai.events.model import Event
from bg_ai.games.base import MatchResult


class StatsQuery(Protocol):
    def action_counts(self, actor_id: str) -> Dict[str, int]:
        """Returns action->count for this actor (wire action values)."""
        ...

    def record(self, actor_id: str) -> Dict[str, int]:
        """Returns {wins, losses, draws, total}."""
        ...

    def win_rate(self, actor_id: str) -> float:
        """wins/total (draws count toward total). Returns 0.0 if total==0."""
        ...


class StatsStore(Protocol):
    def ingest_match(self, *, result: MatchResult, events: List[Event]) -> None:
        """Update internal stats from a completed match (result + event stream)."""
        ...

    def query(self) -> StatsQuery:
        """Return a query handle (often self for in-memory)."""
        ...
