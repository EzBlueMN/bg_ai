# core/events/event.py
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

@dataclass(frozen=True)
class Event:
    type: str
    payload: Dict[str, Any]
    timestamp: datetime
