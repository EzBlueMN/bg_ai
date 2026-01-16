from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bg_ai.policies.base import DecisionContext, Policy


@dataclass(frozen=True, slots=True)
class FixedPolicy(Policy):
    """
    Always returns a fixed action.
    """
    action: Any

    def decide(self, ctx: DecisionContext) -> Any:
        return self.action
