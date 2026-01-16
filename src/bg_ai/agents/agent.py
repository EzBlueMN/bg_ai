from __future__ import annotations

from dataclasses import dataclass

from bg_ai.policies.base import Policy


@dataclass(frozen=True, slots=True)
class Agent:
    actor_id: str
    policy: Policy
