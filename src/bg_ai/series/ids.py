from __future__ import annotations

import uuid


def new_series_id() -> str:
    """Create a unique series id."""
    return uuid.uuid4().hex
