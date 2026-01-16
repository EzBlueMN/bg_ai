from src.bg_ai._legacy.core import State

class RPSState(State):
    def __init__(self, moves=None):
        self.moves = moves or {}

    def is_terminal(self) -> bool:
        return len(self.moves) == 2

    def __hash__(self):
        return hash(tuple(sorted(self.moves.items())))

    def __eq__(self, other):
        return isinstance(other, RPSState) and self.moves == other.moves
