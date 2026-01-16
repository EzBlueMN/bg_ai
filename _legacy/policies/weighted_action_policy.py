from enum import Enum
from typing import Union, List

from _legacy.policies.policy import Policy


class WeightedActionPolicy(Policy):
    def __init__(self, actions: Union[List[Enum], Enum], weights: List[float] = None, seed=None):
        if isinstance(actions, type) and issubclass(actions, Enum):
            actions = list(actions)

        self.actions = actions

        if weights is None:
            # default: uniform weights
            weights = [1.0 for _ in actions]

        if len(weights) != len(actions):
            raise ValueError("weights and actions must have the same length")

        if any(w < 0 for w in weights):
            raise ValueError("All weights must be non-negative")

        self.weights = weights
        self.rng = random.Random(seed)

    def choose(self, state, legal_actions):
        # only consider legal actions
        valid_actions = [a for a in self.actions if a in legal_actions]
        valid_weights = [
            self.weights[self.actions.index(a)] for a in valid_actions
        ]
        # normalize automatically
        total = sum(valid_weights)
        probs = [w / total for w in valid_weights]
        # pick one
        return self.rng.choices(valid_actions, weights=probs, k=1)[0]