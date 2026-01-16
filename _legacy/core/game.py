from abc import ABC, abstractmethod
from _legacy.core.state import State
from _legacy.core.action import Action

class Game(ABC):

    @abstractmethod
    def initial_state(self, seed: int) -> State:
        pass

    @abstractmethod
    def legal_actions(self, state: State, player_id: int) -> list[Action]:
        pass

    @abstractmethod
    def next_state(
        self,
        state: State,
        actions: dict[int, Action],
        rng
    ) -> State:
        pass

    @abstractmethod
    def evaluate_terminal(self, state: State):
        pass
