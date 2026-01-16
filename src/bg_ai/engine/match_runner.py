from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Any, Dict, Optional

from bg_ai.agents.agent import Agent
from bg_ai.engine.ids import new_match_id
from bg_ai.engine.rng import RNG
from bg_ai.events.model import Event
from bg_ai.events.sink import EventSink
from bg_ai.games.base import Game, MatchResult
from bg_ai.policies.base import DecisionContext


@dataclass(frozen=True, slots=True)
class MatchConfig:
    game_config: Dict[str, Any]
    seed: Optional[int] = None
    max_ticks: int = 10_000  # safety guard


class MatchRunner:
    """
    Runs a match tick-by-tick and emits canonical engine events.

    S6 adds:
    - agent/policy decision wiring
    - decision_requested / decision_provided events
    - actions_applied events
    """

    def run_match(
        self,
        game: Game,
        sink: EventSink,
        config: MatchConfig,
        agents_by_id: Optional[Dict[str, Agent]] = None,
    ) -> tuple[str, MatchResult]:
        match_id = new_match_id()

        seed = config.seed if config.seed is not None else secrets.randbits(64)
        rng = RNG.from_seed(int(seed))

        idx = 0
        tick = 0

        sink.emit(Event(match_id=match_id, idx=idx, tick=0, type="seed_set", payload={"seed": int(seed)}))
        idx += 1

        sink.emit(Event(match_id=match_id, idx=idx, tick=0, type="match_start", payload={"game_id": game.game_id}))
        idx += 1

        state = game.initial_state(rng.fork("game:init"), dict(config.game_config))

        while True:
            if game.is_terminal(state):
                break
            if tick >= config.max_ticks:
                raise RuntimeError(f"max_ticks reached ({config.max_ticks}); possible infinite match loop")

            sink.emit(Event(match_id=match_id, idx=idx, tick=tick, type="tick_start", payload={"tick": tick}))
            idx += 1

            actor_ids = game.current_actor_ids(state)
            actions_by_actor: Dict[str, Any] = {}

            # If the game requests actions, we must have agents for those actors.
            if actor_ids:
                if not agents_by_id:
                    raise RuntimeError("Game requested actions but no agents_by_id were provided.")

                for actor_id in actor_ids:
                    if actor_id not in agents_by_id:
                        raise RuntimeError(f"Missing agent for actor_id={actor_id!r}")

                    legal = game.legal_actions(state, actor_id)
                    if legal is None:
                        raise RuntimeError("This game returned legal_actions=None; MVP expects a list.")

                    sink.emit(
                        Event(
                            match_id=match_id,
                            idx=idx,
                            tick=tick,
                            type="decision_requested",
                            payload={"actor_id": actor_id},
                        )
                    )
                    idx += 1

                    agent = agents_by_id[actor_id]
                    ctx = DecisionContext(
                        match_id=match_id,
                        tick=tick,
                        actor_id=actor_id,
                        state=state,
                        legal_actions=list(legal),
                        rng=rng.fork(f"policy:{actor_id}:{tick}"),
                        game_id=game.game_id,
                    )
                    action = agent.policy.decide(ctx)

                    sink.emit(
                        Event(
                            match_id=match_id,
                            idx=idx,
                            tick=tick,
                            type="decision_provided",
                            payload={"actor_id": actor_id, "action": action},
                        )
                    )
                    idx += 1

                    actions_by_actor[actor_id] = action

                # Apply actions for this tick
                state, domain_payloads = game.apply_actions(state, actions_by_actor, rng.fork(f"game:apply:{tick}"))

                sink.emit(
                    Event(
                        match_id=match_id,
                        idx=idx,
                        tick=tick,
                        type="actions_applied",
                        payload={"actions": actions_by_actor},
                    )
                )
                idx += 1

                # Optional: game-domain events (payloads are game-defined dicts)
                for payload in domain_payloads:
                    sink.emit(
                        Event(
                            match_id=match_id,
                            idx=idx,
                            tick=tick,
                            type="domain_event",
                            payload=dict(payload),
                        )
                    )
                    idx += 1

            sink.emit(Event(match_id=match_id, idx=idx, tick=tick, type="tick_end", payload={"tick": tick}))
            idx += 1

            tick += 1

        result = game.result(state)
        sink.emit(
            Event(
                match_id=match_id,
                idx=idx,
                tick=tick,
                type="match_end",
                payload={"outcome": result.outcome, "result": result.details},
            )
        )
        idx += 1

        return match_id, result
