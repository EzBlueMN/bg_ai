from src.bg_ai._legacy.core import Simulation
from src.bg_ai._legacy.agents import Agent
from src.bg_ai._legacy.games.rock_paper_scissors.rps_action import RPSMove
from src.bg_ai._legacy.policies.policy import ForceActionPolicy, WeightedActionPolicy
from src.bg_ai._legacy.games.rock_paper_scissors.rps_game import RockPaperScissorsGame
from src.bg_ai._legacy.policies.policy import ForceActionPolicy, WeightedActionPolicy


def run_experiment(n_games=100_000):
    game = RockPaperScissorsGame()

    stats = {0: 0, 1: 0, "draw": 0}

    for i in range(n_games):
        agents = [
            Agent(ForceActionPolicy(RPSMove.ROCK), player_id=0),
            Agent(WeightedActionPolicy(RPSMove, [3,1,2]), player_id=1),
        ]

        sim = Simulation(game, agents, seed=i)
        outcome = sim.run()

        r0 = outcome.rewards[0]
        if r0 == 1:
            stats[0] += 1
        elif r0 == -1:
            stats[1] += 1
        else:
            stats["draw"] += 1

    print("Results:")
    for k, v in stats.items():
        print(f"{k}: {v / n_games:.3f}")

if __name__ == "__main__":
    run_experiment()
