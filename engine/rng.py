from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Iterable, Sequence, TypeVar

T = TypeVar("T")


def _derive_seed(parent_seed: int, scope: str) -> int:
    """
    Deterministically derive a child seed from (parent_seed, scope).

    This makes substreams stable and reduces accidental nondeterminism caused by
    changing the order of random calls elsewhere.
    """
    msg = f"{parent_seed}:{scope}".encode("utf-8")
    digest = hashlib.sha256(msg).digest()
    # Use first 8 bytes as an unsigned 64-bit int, then fold into Python int.
    return int.from_bytes(digest[:8], "big", signed=False)


@dataclass
class RNG:
    """
    Deterministic RNG with scoped forks.

    - Root RNG is created from a seed.
    - fork(scope) returns a new RNG whose sequence is stable for that scope.
    """
    seed: int
    _r: random.Random

    @classmethod
    def from_seed(cls, seed: int) -> "RNG":
        if not isinstance(seed, int):
            raise TypeError(f"seed must be int, got {type(seed).__name__}")
        return cls(seed=seed, _r=random.Random(seed))

    def fork(self, scope: str) -> "RNG":
        if not isinstance(scope, str) or not scope:
            raise ValueError("scope must be a non-empty string")
        child_seed = _derive_seed(self.seed, scope)
        return RNG.from_seed(child_seed)

    # ---- Common helpers (wrap stdlib Random) ----

    def random(self) -> float:
        return self._r.random()

    def randint(self, a: int, b: int) -> int:
        return self._r.randint(a, b)

    def choice(self, seq: Sequence[T]) -> T:
        if not seq:
            raise ValueError("choice() cannot be called on an empty sequence")
        return self._r.choice(seq)

    def shuffle(self, x: list[T]) -> None:
        self._r.shuffle(x)

    def sample(self, population: Sequence[T], k: int) -> list[T]:
        return self._r.sample(population, k)

    def uniform(self, a: float, b: float) -> float:
        return self._r.uniform(a, b)

    def randrange(self, *args: int) -> int:
        return self._r.randrange(*args)

    def getrandbits(self, k: int) -> int:
        return self._r.getrandbits(k)
