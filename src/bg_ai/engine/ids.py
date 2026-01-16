from __future__ import annotations

import uuid


def new_match_id() -> str:
    """
    Create a unique match id.
    """
    return uuid.uuid4().hex
