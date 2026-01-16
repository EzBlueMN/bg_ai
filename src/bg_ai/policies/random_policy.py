from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bg_ai.policies.base import DecisionContext, Policy


@dataclass(frozen=True, slots=True)
class RandomPolicy(Policy):
    def decide(self, ctx: DecisionContext) -> Any:
        return ctx.rng.choice(ctx.legal_actions)
