# docs/README_DEV.md

# bg_ai — Developer README (Onboarding)

This document explains what was built so far (ADR0001) and how to run it.

If you are new to the repo, start here.

---

## 1) What is bg_ai?

`bg_ai` is a Python project for running board games / simulations as deterministic matches.

A match:

* runs tick-by-tick
* calls policies to produce actions (live run)
* records everything as an event stream
* can be replayed later without policies (using only events)

---

## 2) Quick start (what to run first)

### Option A — Run the ADR slice runner

This validates that all MVP slices (S1–S8) still work.

```
python -m test_ADR.ADR0001
```

You should see:

* `S1 OK`
* ...
* `S8 OK`

### Option B — Run the CLI hello

```
python -m bg_ai.cli.main
```

Expected:

```
OK
```

Note: The CLI currently only prints `OK` (MVP bootstrap).
Readability milestone later adds runnable demos in `/examples`.

---

## 3) Core vocabulary (mental model)

* Game: a ruleset implementation (ex: Rock Paper Scissors)
* Match: one playthrough instance of a Game
* Tick: one engine step (universal unit of progress)
* Agent: a player identity + a policy
* Policy: decision logic that selects an action
* Event: canonical record emitted by the engine (and domain) during a match
* Replay: reconstruct the match result from events without calling policies

---

## 4) How the runtime works (high level)

### Live match

1. MatchRunner creates/records the seed
2. Game creates initial state
3. For each tick:

   * engine asks the game which actors must act
   * policies choose actions (one per actor)
   * engine records decisions as events
   * engine applies actions to the game state
4. Game declares terminal
5. engine emits `match_end` with the result

### Replay

Replay uses:

* `seed_set` event
* all `decision_provided` events
* game `apply_actions(...)`

Replay does NOT use:

* agents
* policies

---

## 5) Where the important code is

### Match execution (engine)

* `src/bg_ai/engine/match_runner.py`

### Deterministic RNG

* `src/bg_ai/engine/rng.py`

### Event model + storage

* `src/bg_ai/events/model.py`
* `src/bg_ai/events/sink.py`
* `src/bg_ai/events/codecs_jsonl.py`

### Game contract

* `src/bg_ai/games/base.py`

### Example game

* `src/bg_ai/games/rock_paper_scissors/game.py`

### Replay

* `src/bg_ai/replay/replayer.py`

### Policies + agents

* `src/bg_ai/policies/`
* `src/bg_ai/agents/`

---

## 6) Event types (MVP)

Engine events:

* `seed_set`
* `match_start`
* `tick_start`
* `decision_requested`
* `decision_provided`
* `actions_applied`
* `domain_event` (optional payload from game)
* `tick_end`
* `match_end`

---

## 7) Known limitations (intentional for MVP)

* No simulation/tournament runner module yet
* No stats/query layer yet (ADR0002)
* No strict replay validation yet
* No CLI arguments/config system yet
* Event schema is minimal (versioning comes later)

---

## 8) Recommended reading order

1. `docs/PROJECT_BRIEF.md`
2. `docs/FEATURES.md`
3. `docs/ARCHITECTURE.md`
4. `src/bg_ai/engine/match_runner.py`
5. `src/bg_ai/games/rock_paper_scissors/game.py`
6. `src/bg_ai/replay/replayer.py`

Also see:

* `docs/MAP.md`
* `docs/IMPLEMENTATION/ADR0001.md` (added in S10)
