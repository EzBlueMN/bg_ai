from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

from .ids import PhaseId

MemoryT = TypeVar("MemoryT")
PendingT = TypeVar("PendingT")


@dataclass(slots=True)
class PhaseState(Generic[MemoryT, PendingT]):
    """
    S23:
    Generic state wrapper for phase-driven games.

    - phase: current phase identifier
    - memory: game-specific memory (resources/board/hand/etc.)
    - pending: optional partial selection used for multi-step phases
    """
    phase: PhaseId
    memory: MemoryT
    pending: Optional[PendingT] = None
