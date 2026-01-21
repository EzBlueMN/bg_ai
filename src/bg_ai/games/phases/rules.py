from __future__ import annotations

from typing import Any, Dict, List, Protocol, Tuple

from bg_ai.engine.rng import RNG


class PhaseRules(Protocol):
    """
    S22:
    A PhaseRules object owns the rules for a specific "phase" of a game.

    Important:
    - We keep this generic on purpose (state type is Any)
    - Game implementations will delegate to PhaseRules based on state.phase
    """

    def current_actor_ids(self, state: Any) -> List[str]:
        """
        Return the actors required to act in this phase.
        For simultaneous phases, return multiple actor ids.
        """
        ...

    def legal_actions(self, state: Any, actor_id: str) -> List[Any]:
        """
        Return the legal actions for this actor in this phase.
        For now actions can be ActionEnum or any other domain type.
        """
        ...

    def apply_actions(
        self,
        state: Any,
        actions_by_actor: Dict[str, Any],
        rng: RNG,
    ) -> Tuple[Any, List[Dict[str, Any]]]:
        """
        Apply actions and return:
        - new_state
        - domain_payloads: list[dict] to be emitted as domain_event payloads
        """
        ...
