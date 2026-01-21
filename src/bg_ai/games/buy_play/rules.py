from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from bg_ai.engine.rng import RNG
from bg_ai.games.phases.rules import PhaseRules

from .types import (
    BuyPlayAction,
    BuyPlayPending,
    BuyPlayState,
    PHASE_CHOOSE,
    PHASE_END,
    PHASE_RESOLVE,
)


@dataclass(frozen=True, slots=True)
class ChoosePhaseRules(PhaseRules):
    def current_actor_ids(self, state: BuyPlayState) -> List[str]:
        if state.phase == PHASE_END:
            return []
        a_id, b_id = state.memory.actors
        return [a_id, b_id]

    def legal_actions(self, state: BuyPlayState, actor_id: str) -> List[BuyPlayAction]:
        if actor_id not in state.memory.actors:
            raise ValueError(f"Unknown actor_id for BuyPlay: {actor_id!r}")

        coins = int(state.memory.coins_by_actor.get(actor_id, 0))
        actions: List[BuyPlayAction] = [BuyPlayAction.BUY, BuyPlayAction.PASS]
        if coins >= 1:
            actions.extend([BuyPlayAction.PLAY, BuyPlayAction.BOTH])
        return actions

    def apply_actions(
        self,
        state: BuyPlayState,
        actions_by_actor: Dict[str, Any],
        rng: RNG,
    ) -> Tuple[BuyPlayState, List[Dict[str, Any]]]:
        a_id, b_id = state.memory.actors

        def _coerce(v: Any) -> BuyPlayAction:
            if isinstance(v, BuyPlayAction):
                return v
            if isinstance(v, str):
                return BuyPlayAction.from_wire(v)
            raise ValueError(f"Invalid action type: {v!r}")

        if a_id not in actions_by_actor or b_id not in actions_by_actor:
            raise ValueError("BuyPlay requires actions for both actors each tick")

        a_act = _coerce(actions_by_actor[a_id])
        b_act = _coerce(actions_by_actor[b_id])

        a_legal = self.legal_actions(state, a_id)
        b_legal = self.legal_actions(state, b_id)
        if a_act not in a_legal:
            raise ValueError(f"Illegal action for {a_id} in CHOOSE: {a_act}")
        if b_act not in b_legal:
            raise ValueError(f"Illegal action for {b_id} in CHOOSE: {b_act}")

        state.pending = BuyPlayPending(actions_by_actor={a_id: a_act, b_id: b_act})
        state.phase = PHASE_RESOLVE

        return state, [
            {
                "game": "buy_play_v1",
                "phase": PHASE_CHOOSE,
                "type": "mode_selected",
                "turn": int(state.memory.turn),
                "actions": {a_id: a_act.to_wire(), b_id: b_act.to_wire()},
            }
        ]


@dataclass(frozen=True, slots=True)
class ResolvePhaseRules(PhaseRules):
    def current_actor_ids(self, state: BuyPlayState) -> List[str]:
        if state.phase == PHASE_END:
            return []
        a_id, b_id = state.memory.actors
        return [a_id, b_id]

    def legal_actions(self, state: BuyPlayState, actor_id: str) -> List[BuyPlayAction]:
        if actor_id not in state.memory.actors:
            raise ValueError(f"Unknown actor_id for BuyPlay: {actor_id!r}")
        return [BuyPlayAction.PASS]

    def apply_actions(
        self,
        state: BuyPlayState,
        actions_by_actor: Dict[str, Any],
        rng: RNG,
    ) -> Tuple[BuyPlayState, List[Dict[str, Any]]]:
        a_id, b_id = state.memory.actors

        def _coerce(v: Any) -> BuyPlayAction:
            if isinstance(v, BuyPlayAction):
                return v
            if isinstance(v, str):
                return BuyPlayAction.from_wire(v)
            raise ValueError(f"Invalid action type: {v!r}")

        if a_id not in actions_by_actor or b_id not in actions_by_actor:
            raise ValueError("BuyPlay requires actions for both actors each tick")

        a_act = _coerce(actions_by_actor[a_id])
        b_act = _coerce(actions_by_actor[b_id])

        if a_act is not BuyPlayAction.PASS or b_act is not BuyPlayAction.PASS:
            raise ValueError("In RESOLVE phase, only PASS is legal (sync step)")

        if state.pending is None:
            raise ValueError("RESOLVE phase requires pending actions from CHOOSE")

        chosen = state.pending.actions_by_actor

        for actor in (a_id, b_id):
            act = chosen[actor]
            coins = int(state.memory.coins_by_actor.get(actor, 0))
            points = int(state.memory.points_by_actor.get(actor, 0))

            if act is BuyPlayAction.BUY:
                coins += 1
            elif act is BuyPlayAction.PLAY:
                coins -= 1
                points += 1
            elif act is BuyPlayAction.BOTH:
                coins -= 1
                coins += 1
                points += 1
            elif act is BuyPlayAction.PASS:
                pass
            else:
                raise ValueError(f"Unknown chosen action: {act}")

            state.memory.coins_by_actor[actor] = coins
            state.memory.points_by_actor[actor] = points

        state.pending = None
        state.memory.turn += 1

        if state.memory.turn >= state.memory.max_turns:
            state.phase = PHASE_END
        else:
            state.phase = PHASE_CHOOSE

        return state, [
            {
                "game": "buy_play_v1",
                "phase": PHASE_RESOLVE,
                "type": "turn_resolved",
                "turn": int(state.memory.turn),
                "coins_by_actor": dict(state.memory.coins_by_actor),
                "points_by_actor": dict(state.memory.points_by_actor),
                "last_actions": {a_id: chosen[a_id].to_wire(), b_id: chosen[b_id].to_wire()},
            }
        ]


@dataclass(frozen=True, slots=True)
class EndPhaseRules(PhaseRules):
    def current_actor_ids(self, state: BuyPlayState) -> List[str]:
        return []

    def legal_actions(self, state: BuyPlayState, actor_id: str) -> List[Any]:
        return []

    def apply_actions(
        self,
        state: BuyPlayState,
        actions_by_actor: Dict[str, Any],
        rng: RNG,
    ) -> Tuple[BuyPlayState, List[Dict[str, Any]]]:
        return state, []


CHOOSE_RULES = ChoosePhaseRules()
RESOLVE_RULES = ResolvePhaseRules()
END_RULES = EndPhaseRules()
