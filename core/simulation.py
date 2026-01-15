import random

class Simulation:
    def __init__(self, game, agents, seed: int):
        self.game = game
        self.agents = agents
        self.rng = random.Random(seed)

    def run(self):
        state = self.game.initial_state(
            seed=self.rng.randint(0, 1_000_000_000)
        )

        while not state.is_terminal():
            actions = {}
            for agent in self.agents:
                legal = self.game.legal_actions(state, agent.player_id)
                actions[agent.player_id] = agent.select_action(state, legal)

            state = self.game.next_state(state, actions, self.rng)

        outcome = self.game.evaluate_terminal(state)

        for agent in self.agents:
            agent.on_episode_end(outcome)

        return outcome
