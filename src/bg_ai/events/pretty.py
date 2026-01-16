from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List, Optional

from bg_ai.events.model import Event


def format_event(ev: Event) -> str:
    """
    Compact human-readable one-line event.
    """
    return f"idx={ev.idx:04d} tick={ev.tick:04d} type={ev.type} payload={ev.payload}"


def summarize_event_types(events: Iterable[Event]) -> Dict[str, int]:
    """
    Count event types.
    """
    c = Counter(ev.type for ev in events)
    return dict(c)


def print_events(events: List[Event], limit: int = 50) -> None:
    """
    Print up to `limit` events in order.
    """
    for ev in events[:limit]:
        print(format_event(ev))
    if len(events) > limit:
        print(f"... ({len(events) - limit} more events)")


def print_event_summary(events: Iterable[Event]) -> None:
    """
    Print sorted counts by event type.
    """
    counts = summarize_event_types(events)
    for k in sorted(counts.keys()):
        print(f"{k}: {counts[k]}")
