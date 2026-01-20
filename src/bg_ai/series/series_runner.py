from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from bg_ai.agents.agent import Agent
from bg_ai.engine.match_runner import MatchConfig, MatchRunner
from bg_ai.events.model import Event
from bg_ai.events.sink import EventSink, InMemoryEventSink
from bg_ai.games.base import Game, MatchResult

from .formats import MatchFormat, SeriesScore
from .ids import new_series_id


@dataclass(frozen=True, slots=True)
class SeriesConfig:
    game_config: Dict[str, Any]
    seed: Optional[int] = None
    max_matches: int = 1_000  # safety guard


@dataclass(frozen=True, slots=True)
class SeriesResult:
    outcome: str
    series_id: str
    winner: Optional[str]
    wins_by_actor: Dict[str, int]
    draws: int
    match_results: List[MatchResult]


class SeriesRunner:
    """
    Runs multiple *single-match* games sequentially and aggregates results.

    S15:
      - supports BestOfN / FirstToN stopping conditions
      - returns SeriesResult (wins/draws + per-match results)

    S15.1 (Option A):
      - optional series-level EventSink
      - emits: series_start, series_match_completed, series_end

    Event envelope rule for series-level events:
      - Event.match_id == series_id
      - Event.tick == -1
      - Event.idx monotonic within the series
    """

    def __init__(self) -> None:
        self._match_runner = MatchRunner()

    def run_series(
        self,
        *,
        game: Game,
        match_format: MatchFormat,
        config: SeriesConfig,
        agents_by_id: Dict[str, Agent],
        series_sink: Optional[EventSink] = None,
    ) -> SeriesResult:
        series_id = new_series_id()

        actors = config.game_config.get("actors")
        if not isinstance(actors, list) or len(actors) != 2:
            raise ValueError("Series requires config.game_config['actors'] to be a list of exactly 2 actor ids")

        a_id = str(actors[0])
        b_id = str(actors[1])

        wins_by_actor: Dict[str, int] = {a_id: 0, b_id: 0}
        draws = 0
        match_results: List[MatchResult] = []

        # Series-level events
        sidx = 0
        if series_sink is not None:
            series_sink.emit(
                Event(
                    match_id=series_id,
                    idx=sidx,
                    tick=-1,
                    type="series_start",
                    payload={
                        "series_id": series_id,
                        "game_id": game.game_id,
                        "format": match_format.__class__.__name__,
                        "game_config": dict(config.game_config),
                    },
                )
            )
            sidx += 1

        for match_index in range(config.max_matches):
            score = SeriesScore(wins_by_actor=dict(wins_by_actor), draws=draws)
            if match_format.is_done(score=score, game_config=config.game_config):
                break

            match_sink = InMemoryEventSink()
            match_cfg = MatchConfig(
                game_config=dict(config.game_config),
                seed=(None if config.seed is None else int(config.seed) + match_index),
                max_ticks=10_000,
            )

            match_id, result = self._match_runner.run_match(
                game,
                match_sink,
                match_cfg,
                agents_by_id=agents_by_id,
            )

            match_results.append(result)

            winner = result.details.get("winner")
            if winner is None:
                draws += 1
            elif winner == a_id:
                wins_by_actor[a_id] += 1
            elif winner == b_id:
                wins_by_actor[b_id] += 1
            else:
                raise RuntimeError(
                    f"Unexpected winner id {winner!r} (expected {a_id!r} or {b_id!r} or None)"
                )

            if series_sink is not None:
                series_sink.emit(
                    Event(
                        match_id=series_id,
                        idx=sidx,
                        tick=-1,
                        type="series_match_completed",
                        payload={
                            "series_id": series_id,
                            "match_index": match_index,
                            "match_id": match_id,
                            "winner": winner,
                            "wins_by_actor": dict(wins_by_actor),
                            "draws": int(draws),
                            "match_result": dict(result.details),
                        },
                    )
                )
                sidx += 1

        final_score = SeriesScore(wins_by_actor=dict(wins_by_actor), draws=draws)
        series_winner = match_format.winner(score=final_score, game_config=config.game_config)

        if series_sink is not None:
            series_sink.emit(
                Event(
                    match_id=series_id,
                    idx=sidx,
                    tick=-1,
                    type="series_end",
                    payload={
                        "series_id": series_id,
                        "winner": series_winner,
                        "wins_by_actor": dict(wins_by_actor),
                        "draws": int(draws),
                        "matches_played": len(match_results),
                    },
                )
            )

        return SeriesResult(
            outcome="done",
            series_id=series_id,
            winner=series_winner,
            wins_by_actor=dict(wins_by_actor),
            draws=int(draws),
            match_results=list(match_results),
        )
