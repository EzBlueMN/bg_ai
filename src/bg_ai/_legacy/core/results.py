class Outcome:
    def __init__(self, rewards: dict[int, float]):
        """
        rewards: {player_id: reward}
        """
        self.rewards = rewards
