import random

from core.events.event_bus import EventBus


class Simulation:
    def __init__(self, game, agents, seed: int, event_bus: EventBus | None = None):
        self.game = game
        self.agents = agents
        self.rng = random.Random(seed)
        self.event_bus = event_bus or EventBus()

    def run(self):
        self.event_bus.emit(Event(
            type="simulation_started",
            payload={
                "agents": [agent.player_id for agent in self.agents]
            },
            timestamp=datetime.utcnow()
        ))
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
