class Agent:
    def __init__(self, policy, player_id: int):
        self.policy = policy
        self.player_id = player_id

    def select_action(self, state, legal_actions):
        return self.policy.choose(state, legal_actions)

    def on_episode_end(self, outcome):
        pass
