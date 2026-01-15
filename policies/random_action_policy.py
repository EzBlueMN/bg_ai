from policies.policy import Policy


class RandomPolicy(Policy):
    def choose(self, state, legal_actions, seed):
        rng = random.Random(seed)
        return rng.choice(legal_actions)