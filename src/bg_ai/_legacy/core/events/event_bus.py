# core/events/event_bus.py
from typing import List
from .event import Event

class EventBus:
    def __init__(self):
        self._events: List[Event] = []

    def emit(self, event: Event):
        self._events.append(event)

    def get_events(self) -> List[Event]:
        return list(self._events)

    def clear(self):
        self._events.clear()
