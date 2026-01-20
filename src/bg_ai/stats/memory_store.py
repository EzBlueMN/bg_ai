from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from bg_ai.events.model import Event
from bg_ai.games.base import MatchResult

from .base import StatsQuery, StatsStore


@dataclass
class _PlayerRecord:
    wins: int = 0
    losses: int = 0
    draws: int = 0


@dataclass
class InMemoryStatsStore(StatsStore, StatsQuery):
    """
    S18 MVP:
    - action counts from decision_provided events (payload: actor_id, action wire str)
    - win/loss/draw from result.details:
        - winner: actor_id or None
        - actors: list[str] (expected for our games)
    """
    _action_counts: Dict[str, Dict[str, int]] = field(default_factory=dict)
    _records: Dict[str, _PlayerRecord] = field(default_factory=dict)

    def ingest_match(self, *, result: MatchResult, events: List[Event]) -> None:
        # 1) Action counts
        for e in events:
            if e.type != "decision_provided":
                continue
            actor_id = str(e.payload.get("actor_id"))
            action = e.payload.get("action")
            if action is None:
                continue
            action_wire = str(action)

            per_actor = self._action_counts.setdefault(actor_id, {})
            per_actor[action_wire] = int(per_actor.get(action_wire, 0)) + 1

            self._records.setdefault(actor_id, _PlayerRecord())

        # 2) W/L/D (game-agnostic but assumes result has 'actors' + 'winner')
        details = result.details or {}
        actors = details.get("actors")
        winner = details.get("winner", None)

        if not isinstance(actors, list) or len(actors) == 0:
            return

        actor_ids = [str(a) for a in actors]
        for a in actor_ids:
            self._records.setdefault(a, _PlayerRecord())

        if winner is None:
            for a in actor_ids:
                self._records[a].draws += 1
            return

        winner_id = str(winner)
        for a in actor_ids:
            if a == winner_id:
                self._records[a].wins += 1
            else:
                self._records[a].losses += 1

    def query(self) -> StatsQuery:
        return self

    def action_counts(self, actor_id: str) -> Dict[str, int]:
        return dict(self._action_counts.get(actor_id, {}))

    def record(self, actor_id: str) -> Dict[str, int]:
        r = self._records.get(actor_id) or _PlayerRecord()
        total = int(r.wins + r.losses + r.draws)
        return {
            "wins": int(r.wins),
            "losses": int(r.losses),
            "draws": int(r.draws),
            "total": total,
        }

    def win_rate(self, actor_id: str) -> float:
        rec = self.record(actor_id)
        total = rec["total"]
        if total <= 0:
            return 0.0
        return float(rec["wins"]) / float(total)
