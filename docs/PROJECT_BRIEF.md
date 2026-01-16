# bg_ai — Project Brief

## One-liner
A Python learning playground to simulate any kind of board/turn-based game with agents (players) using policies (strategies), producing deterministic results and a complete event trace that enables replay and analysis.

## Purpose
bg_ai provides a clean, extensible core for:
- implementing many different games (simultaneous, turn-based, initiative-based, multi-step turns)
- experimenting with strategies/policies
- running reproducible matches and simulations
- capturing a full event trace for debugging, analytics, and future automation

## Core Principles

### Determinism (hard requirement)
- Same seed + same setup ⇒ same match result and same event trace (within defined version constraints).
- Randomness may exist anywhere (engine/game/policy), but must flow through a seeded RNG (or a seed generated at initialization and recorded).

### Event trace (first-class)
- The engine emits events for everything needed to understand and reproduce a match:
  - game events
  - engine events
  - decision/policy events
  - randomness/seed events as needed for determinism

### Hybrid truth model (canonical events + optional snapshots)
- Events are the canonical source of truth for replay/debugging.
- State snapshots may be optionally stored as performance optimizations.
- Replay must support reconstructing state from initial setup + events without invoking agents/policies.

## Definitions / Vocabulary
- **Game**: a ruleset/type (e.g., Chess, RPS).
- **Match**: one complete playthrough instance of a Game.
- **Simulation**: orchestration layer for running many matches (tournaments/experiments).
- **Tick**: universal engine step. Games may additionally define Turn/Round/Phase as game-specific concepts.
- **Agent (Player)**: participant in a match; uses a Policy to choose actions.
- **Policy (Strategy)**: decision logic that suggests the next action.
- **Event**: immutable record of a meaningful occurrence (decision requested, action chosen, state updated, RNG used, etc.).
- **Replay**: reconstructing match state by applying events from an initial state (optionally from a snapshot + remaining events).

## MVP Scope
Must have:
- core engine capable of running at least one example game end-to-end
- deterministic execution with a fixed seed
- in-memory event log captured for the match
- export of event log (e.g., JSON/JSONL)
- replay mode that rebuilds state from initial setup + event list (no policy execution)
- hard-coded configuration through main.py (CLI later)

Example starting games:
- start with a simple game (e.g., RPS)
- architecture must support additional game types (turn-based, initiative, multi-step turns)

## Non-goals (Not Now)
- multiplayer networking / online play
- real-time (frame-based) games
- GUI editors for games/policies (a simple match viewer may exist later)
- parallel/distributed compute
- auto hyperparameter tuning
- complex plugin marketplace system

## Maybe Soon
- a storage layer (JSONL/SQLite) for matches, events, metadata, and derived stats
- analytics/query helpers: action ratios, win rates, policy usage per match/tournament, etc.

## Success Criteria
- adding a new policy does not require changing game logic
- adding a new game does not require changing the engine core (beyond registering the new game)
- same seed reproduces the same outcome and trace
- any match can be replayed from stored events (and optional snapshots)
