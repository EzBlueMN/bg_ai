from __future__ import annotations

from bg_ai.agents.agent import Agent
from bg_ai.engine.match_runner import MatchConfig
from bg_ai.games.buy_play import BuyPlayGame, ConservativeBuyPlayPolicy, GreedyBuyPlayPolicy
from bg_ai.series.formats import BestOfN
from bg_ai.series.series_runner import SeriesRunner


def main() -> None:
    game = BuyPlayGame()

    # Each match = 3 turns of the Buy/Play game
    match_cfg = MatchConfig(
        game_config={"actors": ["A", "B"], "max_turns": 3},
        seed=123,
        max_ticks=500,
    )

    agents = {
        "A": Agent("A", GreedyBuyPlayPolicy()),
        "B": Agent("B", ConservativeBuyPlayPolicy(target_coins=2)),
    }

    series_runner = SeriesRunner()

    series_id, series_result = series_runner.run_series(
        game=game,
        match_config=match_cfg,
        agents_by_id=agents,
        series_format=BestOfN(3),
    )

    print("=" * 60)
    print("BUY/PLAY — BEST OF 3")
    print("=" * 60)
    print("series_id:", series_id)
    print("series_result:", series_result)

    # Useful quick inspection
    if hasattr(series_result, "details"):
        print("details:", series_result.details)


if __name__ == "__main__":
    main()
