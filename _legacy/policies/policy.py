import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import List


class Policy(ABC):

    @abstractmethod
    def choose(self, state, legal_actions):
        pass
