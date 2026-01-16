from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Union

from .model import Event


PathLike = Union[str, Path]


def export_events_jsonl(path: PathLike, events: Iterable[Event]) -> Path:
    """
    Export events to JSONL (one JSON object per line).
    Returns the resolved Path written to.
    """
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8", newline="\n") as f:
        for ev in events:
            f.write(json.dumps(ev.to_dict(), ensure_ascii=False, separators=(",", ":")))
            f.write("\n")

    return p


def import_events_jsonl(path: PathLike) -> List[Event]:
    """
    Import events from JSONL (one JSON object per line).
    Skips empty/whitespace lines.
    """
    p = Path(path).expanduser().resolve()
    events: List[Event] = []

    with p.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_no} in {p}: {e}") from e
            events.append(Event.from_dict(obj))

    return events
