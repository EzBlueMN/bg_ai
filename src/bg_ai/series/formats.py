from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True, slots=True)
class SeriesScore:
    """Score tracked across many matches."""
    wins_by_actor: Dict[str, int]
    draws: int = 0

    def wins(self, actor_id: str) -> int:
        return int(self.wins_by_actor.get(actor_id, 0))


class MatchFormat:
    """Stop condition + aggregation rules for a series."""
    def is_done(self, *, score: SeriesScore, game_config: dict) -> bool:
        raise NotImplementedError

    def winner(self, *, score: SeriesScore, game_config: dict) -> Optional[str]:
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class BestOfN(MatchFormat):
    n: int

    def __post_init__(self) -> None:
        if self.n <= 0:
            raise ValueError("BestOfN.n must be > 0")
        if self.n % 2 == 0:
            raise ValueError("BestOfN.n must be odd (e.g. 1,3,5,...)")

    def is_done(self, *, score: SeriesScore, game_config: dict) -> bool:
        actors = game_config.get("actors")
        if not isinstance(actors, list) or len(actors) != 2:
            raise ValueError("Series requires game_config['actors'] to be a list of exactly 2 actor ids")

        a, b = str(actors[0]), str(actors[1])
        needed = (self.n // 2) + 1
        return score.wins(a) >= needed or score.wins(b) >= needed

    def winner(self, *, score: SeriesScore, game_config: dict) -> Optional[str]:
        actors = game_config.get("actors")
        a, b = str(actors[0]), str(actors[1])
        needed = (self.n // 2) + 1

        if score.wins(a) >= needed:
            return a
        if score.wins(b) >= needed:
            return b
        return None


@dataclass(frozen=True, slots=True)
class FirstToN(MatchFormat):
    n: int

    def __post_init__(self) -> None:
        if self.n <= 0:
            raise ValueError("FirstToN.n must be > 0")

    def is_done(self, *, score: SeriesScore, game_config: dict) -> bool:
        actors = game_config.get("actors")
        if not isinstance(actors, list) or len(actors) != 2:
            raise ValueError("Series requires game_config['actors'] to be a list of exactly 2 actor ids")

        a, b = str(actors[0]), str(actors[1])
        return score.wins(a) >= self.n or score.wins(b) >= self.n

    def winner(self, *, score: SeriesScore, game_config: dict) -> Optional[str]:
        actors = game_config.get("actors")
        a, b = str(actors[0]), str(actors[1])

        if score.wins(a) >= self.n:
            return a
        if score.wins(b) >= self.n:
            return b
        return None
