from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

from bg_ai.agents.agent import Agent
from bg_ai.engine.match_runner import MatchConfig, MatchRunner
from bg_ai.events.sink import InMemoryEventSink
from bg_ai.games.base import Game, MatchResult
from bg_ai.stats.base import StatsQuery


class StatsStore(Protocol):
    def ingest_match(self, *, result: MatchResult, events: List[Any]) -> None:
        ...


@dataclass(frozen=True, slots=True)
class SimConfig:
    game_config: Dict[str, Any]
    num_matches: int
    seed: Optional[int] = None
    max_ticks: int = 10_000


@dataclass(frozen=True, slots=True)
class SimResult:
    match_results: List[MatchResult]


class SimRunner:
    """
    S20:
    - Runs M matches sequentially
    - Updates stats store after each match (store.ingest_match(result, events))
    - Passes stats_query into policies via MatchRunner (S19)
    """

    def __init__(self) -> None:
        self._match_runner = MatchRunner()

    def run_matches(
        self,
        *,
        game: Game,
        config: SimConfig,
        agents_by_id: Dict[str, Agent],
        stats_store: StatsStore,
        stats_query: StatsQuery,
    ) -> SimResult:
        if config.num_matches <= 0:
            raise ValueError("SimConfig.num_matches must be > 0")

        results: List[MatchResult] = []

        for i in range(config.num_matches):
            sink = InMemoryEventSink()

            match_cfg = MatchConfig(
                game_config=dict(config.game_config),
                seed=(None if config.seed is None else int(config.seed) + i),
                max_ticks=int(config.max_ticks),
            )

            _match_id, result = self._match_runner.run_match(
                game,
                sink,
                match_cfg,
                agents_by_id=agents_by_id,
                stats_query=stats_query,
            )

            # Update stats after each match
            stats_store.ingest_match(result=result, events=sink.events())

            results.append(result)

        return SimResult(match_results=results)
