from __future__ import annotations

from dataclasses import dataclass

from bg_ai.policies.base import DecisionContext

from .types import BuyPlayAction, PHASE_CHOOSE, PHASE_RESOLVE


def _is_buy_play_state(obj: object) -> bool:
    # Runtime-safe check (avoid isinstance on subscripted generics).
    return hasattr(obj, "phase") and hasattr(obj, "memory")


@dataclass(frozen=True, slots=True)
class GreedyBuyPlayPolicy:
    """
    Greedy policy:
    - CHOOSE:
        - if coins >= 1: BOTH (convert 1 action into +1 point, keep coins)
        - else: BUY
    - RESOLVE: PASS (required sync step)
    """
    def decide(self, ctx: DecisionContext) -> object:
        st = ctx.state
        if not _is_buy_play_state(st):
            return BuyPlayAction.PASS

        if st.phase == PHASE_CHOOSE:
            coins = int(st.memory.coins_by_actor.get(ctx.actor_id, 0))
            if coins >= 1:
                return BuyPlayAction.BOTH
            return BuyPlayAction.BUY

        if st.phase == PHASE_RESOLVE:
            return BuyPlayAction.PASS

        return BuyPlayAction.PASS


@dataclass(frozen=True, slots=True)
class ConservativeBuyPlayPolicy:
    """
    Conservative policy:
    - CHOOSE:
        - BUY until coins >= target_coins
        - then PLAY (spend 1 coin for 1 point)
    - RESOLVE: PASS
    """
    target_coins: int = 2

    def decide(self, ctx: DecisionContext) -> object:
        st = ctx.state
        if not _is_buy_play_state(st):
            return BuyPlayAction.PASS

        if st.phase == PHASE_CHOOSE:
            coins = int(st.memory.coins_by_actor.get(ctx.actor_id, 0))
            if coins < int(self.target_coins):
                return BuyPlayAction.BUY

            if coins >= 1:
                return BuyPlayAction.PLAY
            return BuyPlayAction.BUY

        if st.phase == PHASE_RESOLVE:
            return BuyPlayAction.PASS

        return BuyPlayAction.PASS
