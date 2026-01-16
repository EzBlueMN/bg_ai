from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


JSONValue = Any  # MVP: keep flexible; later can tighten to JSON-serializable unions.
JSONDict = Dict[str, JSONValue]


@dataclass(frozen=True, slots=True)
class Event:
    """
    Canonical event envelope.

    idx is a monotonic sequence number within a match.
    tick is the engine tick index (0..N).
    type is a stable string identifier (e.g., "match_start", "decision_provided").
    payload must be JSON-serializable (enforced later; flexible in MVP).
    """
    match_id: str
    idx: int
    tick: int
    type: str
    payload: JSONDict
    schema_version: int = 1
    timestamp_ms: Optional[int] = None  # optional; do not rely on for determinism

    def to_dict(self) -> JSONDict:
        d: JSONDict = {
            "match_id": self.match_id,
            "idx": self.idx,
            "tick": self.tick,
            "type": self.type,
            "payload": self.payload,
            "schema_version": self.schema_version,
        }
        if self.timestamp_ms is not None:
            d["timestamp_ms"] = self.timestamp_ms
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Event":
        # Minimal validation for MVP
        return cls(
            match_id=str(d["match_id"]),
            idx=int(d["idx"]),
            tick=int(d["tick"]),
            type=str(d["type"]),
            payload=dict(d.get("payload") or {}),
            schema_version=int(d.get("schema_version", 1)),
            timestamp_ms=(int(d["timestamp_ms"]) if "timestamp_ms" in d and d["timestamp_ms"] is not None else None),
        )
