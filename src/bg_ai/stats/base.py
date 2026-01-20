from __future__ import annotations

from typing import Dict, Protocol


class StatsQuery(Protocol):
    def action_counts(self, actor_id: str) -> Dict[str, int]:
        ...

    def record(self, actor_id: str) -> Dict[str, int]:
        ...

    def win_rate(self, actor_id: str) -> float:
        ...


class NullStatsQuery(StatsQuery):
    """Default stats query when none is provided."""
    def action_counts(self, actor_id: str) -> Dict[str, int]:
        return {}

    def record(self, actor_id: str) -> Dict[str, int]:
        return {"wins": 0, "losses": 0, "draws": 0, "total": 0}

    def win_rate(self, actor_id: str) -> float:
        return 0.0
