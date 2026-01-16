from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Tuple


JSONValue = Any
JSONDict = Dict[str, JSONValue]


@dataclass(frozen=True, slots=True)
class MatchResult:
    """
    MVP match result.

    Games can extend this later, but keep it JSON-friendly.
    """
    outcome: str  # e.g. "ongoing", "done"
    details: JSONDict


class Game(Protocol):
    """
    Game ruleset contract (conceptual).
    Concrete games define their own State and Action structures, but the engine
    interacts with them through this interface.
    """
    game_id: str

    def initial_state(self, rng: Any, config: JSONDict) -> Any:
        ...

    def current_actor_ids(self, state: Any) -> List[str]:
        """
        Returns the actor ids that must provide actions now.
        - simultaneous games: many actors
        - turn-based: one actor
        - no-action phases: can be empty
        """
        ...

    def legal_actions(self, state: Any, actor_id: str) -> Optional[List[Any]]:
        """
        Return legal actions for actor_id.

        - If you return None: engine treats it as "game does not provide legal action list".
        - For MVP, most games should return a list.
        """
        ...


    def apply_actions(self, state: Any, actions_by_actor: Dict[str, Any], rng: Any) -> Tuple[Any, List[JSONDict]]:
        """
        Apply a batch of actions for the current tick and return:
        (new_state, domain_events_payloads)

        Domain events are game-specific payload dicts; the engine will wrap them
        in canonical event envelopes.
        """
        ...

    def is_terminal(self, state: Any) -> bool:
        ...

    def result(self, state: Any) -> MatchResult:
        ...
