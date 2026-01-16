from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from .model import Event


class EventSink(Protocol):
    def emit(self, event: Event) -> None:
        ...


@dataclass
class InMemoryEventSink:
    """
    MVP sink: stores events in-memory in insertion order.
    """
    _events: List[Event]

    def __init__(self) -> None:
        self._events = []

    def emit(self, event: Event) -> None:
        self._events.append(event)

    def events(self) -> List[Event]:
        # Return a shallow copy to avoid accidental mutation.
        return list(self._events)

    def __len__(self) -> int:
        return len(self._events)
