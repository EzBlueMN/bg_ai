from __future__ import annotations

from bg_ai.agents.agent import Agent
from bg_ai.engine.match_runner import MatchRunner, MatchConfig
from bg_ai.events.codecs_jsonl import export_events_jsonl, import_events_jsonl
from bg_ai.events.sink import InMemoryEventSink
from bg_ai.games.rock_paper_scissors.game import RPSGame
from bg_ai.policies.fixed_policy import FixedPolicy
from bg_ai.replay.replayer import Replayer, ReplayConfig


def main() -> None:
    # Live match
    sink = InMemoryEventSink()
    runner = MatchRunner()

    cfg = MatchConfig(game_config={"rounds": 3, "actors": ["A", "B"]}, seed=123, max_ticks=100)

    agents = {
        "A": Agent(actor_id="A", policy=FixedPolicy("R")),
        "B": Agent(actor_id="B", policy=FixedPolicy("S")),
    }

    match_id, live_result = runner.run_match(RPSGame(), sink, cfg, agents_by_id=agents)

    print("=== RPS LIVE ===")
    print("match_id:", match_id)
    print("live_result:", live_result.details)
    print("events:", len(sink.events()))

    # Export events
    path = export_events_jsonl("runs/example_rps_live.jsonl", sink.events())
    print("exported:", path)

    # Import events
    loaded_events = import_events_jsonl(path)
    print("imported events:", len(loaded_events))

    # Replay
    replayer = Replayer()
    replay_result = replayer.replay(
        RPSGame(),
        loaded_events,
        ReplayConfig(game_config={"rounds": 3, "actors": ["A", "B"]}),
    )

    print("=== RPS REPLAY ===")
    print("replay_result:", replay_result.details)

    print("=== CHECK ===")
    print("live == replay ?", live_result.details == replay_result.details)

    # Small event summary
    counts = {}
    for e in loaded_events:
        counts[e.type] = counts.get(e.type, 0) + 1

    # print("event counts:")
    # for k in sorted(counts.keys()):
    #     print(f"  {k}: {counts[k]}")
    from bg_ai.events.pretty import print_event_summary

    print("event summary:")
    print_event_summary(loaded_events)

if __name__ == "__main__":
    main()
