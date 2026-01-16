from __future__ import annotations

from bg_ai.engine.match_runner import MatchRunner, MatchConfig
from bg_ai.events.sink import InMemoryEventSink
from bg_ai.games.base import MatchResult


class NoActionGame:
    """
    Minimal game that requires no actions.
    Useful to understand the engine lifecycle + tick events.
    """
    game_id = "no_action_v1"

    def initial_state(self, rng, config):
        return {"ticks_left": 3}

    def current_actor_ids(self, state):
        return []

    def legal_actions(self, state, actor_id):
        return None

    def apply_actions(self, state, actions_by_actor, rng):
        raise NotImplementedError("NoActionGame never applies actions")

    def is_terminal(self, state):
        # Decrement here so we can see ticks happen
        state["ticks_left"] -= 1
        return state["ticks_left"] <= 0

    def result(self, state):
        return MatchResult(outcome="done", details={"reason": "completed"})


def main() -> None:
    sink = InMemoryEventSink()
    runner = MatchRunner()
    cfg = MatchConfig(game_config={}, seed=123, max_ticks=100)

    match_id, result = runner.run_match(NoActionGame(), sink, cfg, agents_by_id=None)

    print("=== NO ACTION GAME ===")
    print("match_id:", match_id)
    print("result:", result)
    print("events:", len(sink.events()))

    # Print event types in order
    print("event types:")
    # for e in sink.events():
    #     print(f"  idx={e.idx:02d} tick={e.tick:02d} type={e.type}")
    from bg_ai.events.pretty import print_events, print_event_summary

    print("event summary:")
    print_event_summary(sink.events())

    print("first events:")
    print_events(sink.events(), limit=50)

if __name__ == "__main__":
    main()
