from src.bg_ai._legacy.policies.policy import Policy


class ForceActionPolicy(Policy):
    def __init__(self, forced_action:Enum):
        self.action = forced_action

    def choose(self, state, legal_actions):
        return self.action
