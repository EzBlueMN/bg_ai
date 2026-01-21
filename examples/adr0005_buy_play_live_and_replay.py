from __future__ import annotations

from pathlib import Path

from bg_ai.agents.agent import Agent
from bg_ai.engine.match_runner import MatchConfig, MatchRunner
from bg_ai.events.codecs_jsonl import export_events_jsonl, import_events_jsonl
from bg_ai.events.sink import InMemoryEventSink
from bg_ai.games.buy_play import BuyPlayGame, ConservativeBuyPlayPolicy, GreedyBuyPlayPolicy
from bg_ai.replay.replayer import ReplayConfig, Replayer


def main() -> None:
    game = BuyPlayGame()
    runner = MatchRunner()

    cfg = MatchConfig(
        game_config={"actors": ["A", "B"], "max_turns": 3},
        seed=123,
        max_ticks=500,
    )

    agents = {
        "A": Agent("A", GreedyBuyPlayPolicy()),
        "B": Agent("B", ConservativeBuyPlayPolicy(target_coins=2)),
    }

    sink = InMemoryEventSink()
    match_id, result = runner.run_match(game, sink, cfg, agents_by_id=agents)

    print("=" * 60)
    print("LIVE RESULT")
    print("=" * 60)
    print("match_id:", match_id)
    print("details:", result.details)

    out_dir = Path("runs") / "adr0005"
    out_dir.mkdir(parents=True, exist_ok=True)

    events_path = out_dir / f"{match_id}.jsonl"
    export_events_jsonl(events_path, sink.events())

    # Load back from disk and replay
    events = import_events_jsonl(events_path)
    replay_res = Replayer().replay(game, events, ReplayConfig(game_config=dict(cfg.game_config)))

    print("=" * 60)
    print("REPLAY RESULT")
    print("=" * 60)
    print("details:", replay_res.details)

    ok = replay_res.details == result.details
    print("replay_matches_live:", ok)
    if not ok:
        raise SystemExit("Replay result does not match live result")


if __name__ == "__main__":
    main()
