from core.game import Game
from core.results import Outcome
from games.rock_paper_scissors.rps_state import RPSState
from games.rock_paper_scissors.rps_action import RPSMove

class RockPaperScissorsGame(Game):

    def initial_state(self, seed: int):
        return RPSState()

    def legal_actions(self, state, player_id):
        return list(RPSMove)

    def next_state(self, state, actions, rng):
        return RPSState(actions)

    def evaluate_terminal(self, state):
        p0 = state.moves[0]
        p1 = state.moves[1]

        if p0 == p1:
            return Outcome({0: 0, 1: 0})

        wins = {
            RPSMove.ROCK: RPSMove.SCISSORS,
            RPSMove.SCISSORS: RPSMove.PAPER,
            RPSMove.PAPER: RPSMove.ROCK,
        }

        if wins[p0] == p1:
            return Outcome({0: 1, 1: -1})
        else:
            return Outcome({0: -1, 1: 1})
