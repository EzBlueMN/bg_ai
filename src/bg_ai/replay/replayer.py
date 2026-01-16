from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from bg_ai.engine.rng import RNG
from bg_ai.events.model import Event
from bg_ai.games.base import Game, MatchResult


@dataclass(frozen=True, slots=True)
class ReplayConfig:
    """
    MVP replay config.
    """
    game_config: Dict[str, Any]


class Replayer:
    """
    Rebuild match outcome from events WITHOUT calling policies.

    MVP replay uses:
    - seed_set for RNG seed
    - decision_provided events for actions per tick per actor
    - game.apply_actions to advance state
    """

    def replay(self, game: Game, events: List[Event], config: ReplayConfig) -> MatchResult:
        if not events:
            raise ValueError("Cannot replay: empty event list")

        # All events should share the same match_id, but we don't strictly enforce in MVP.
        seed = self._extract_seed(events)
        rng = RNG.from_seed(seed)

        state = game.initial_state(rng.fork("game:init"), dict(config.game_config))

        # Group actions by tick
        actions_by_tick: Dict[int, Dict[str, Any]] = {}
        for ev in events:
            if ev.type == "decision_provided":
                actor_id = ev.payload.get("actor_id")
                action = ev.payload.get("action")
                if not isinstance(actor_id, str):
                    raise ValueError(f"decision_provided missing/invalid actor_id: {ev.payload!r}")
                actions_by_tick.setdefault(ev.tick, {})[actor_id] = action

        # Apply ticks in ascending order
        for tick in sorted(actions_by_tick.keys()):
            actions = actions_by_tick[tick]
            state, _domain_payloads = game.apply_actions(state, actions, rng.fork(f"game:apply:{tick}"))

        return game.result(state)

    @staticmethod
    def _extract_seed(events: List[Event]) -> int:
        for ev in events:
            if ev.type == "seed_set":
                seed = ev.payload.get("seed")
                if isinstance(seed, int):
                    return seed
                # allow string seeds if ever serialized oddly
                if isinstance(seed, str) and seed.isdigit():
                    return int(seed)
                raise ValueError(f"seed_set has invalid seed: {ev.payload!r}")
        raise ValueError("Cannot replay: missing seed_set event")
