from abc import ABC, abstractmethod

class State(ABC):
    """Immutable snapshot of a game."""

    @abstractmethod
    def is_terminal(self) -> bool:
        pass

    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass
