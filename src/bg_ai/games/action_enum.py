from __future__ import annotations

from enum import Enum
from typing import Any, Type, TypeVar


TActionEnum = TypeVar("TActionEnum", bound="ActionEnum")


class ActionEnum(str, Enum):
    """Base class for game-specific action enums.

    This gives us two things:
    1) Type-safe actions in code (policies return enum members)
    2) A stable *wire format* for logging/replay (events store strings)
    """

    def to_wire(self) -> str:
        """Stable string representation for event payloads (JSON-safe)."""
        return str(self.value)

    @classmethod
    def from_wire(cls: Type[TActionEnum], wire: Any) -> TActionEnum:
        """Decode the wire string back into the enum member."""
        return cls(str(wire))
