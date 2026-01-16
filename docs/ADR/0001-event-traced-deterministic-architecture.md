# ADR 0001 — Event-Traced, Deterministic Simulation Architecture for `bg_ai`

**Status:** Proposed (ready to accept)
**Date:** 2026-01-16
**Decision drivers:** Determinism, full event trace, replay without agents/policies, support for many game types, clean separation of concerns, future stats/DB layer.

---

## Context

The current repo already contains the *seed* of a useful architecture:

* A `core.Game` abstraction with `initial_state`, `legal_actions`, `next_state`, `evaluate_terminal`.
* A `core.State` base class with `is_terminal`, hashing, equality.
* An `Agent` that delegates decision-making to a `Policy`.
* A minimal `Simulation` loop that collects actions from agents and advances game state.

However, many planned modules are placeholders or incomplete (e.g., match/tournament/persistence/tests), and there is no first-class event system, no canonical replay mechanism, and randomness usage is inconsistent across policies.

We want to **prioritize the new architecture** over existing structure, while **preserving working concepts** (Game/State/Action/Agent/Policy) and making room for refactoring.

---

## Decision

We adopt an architecture built around:

1. **Hybrid truth model (A)**

   * Live runs mutate state normally for simplicity and performance.
   * **Events are the canonical record** used for replay/debug/audit.
   * Optional state snapshots may be introduced later for speed, but are not required for correctness.

2. **Deterministic RNG service with scoped substreams**

   * Randomness may be used anywhere (engine/game/policy) but must flow through a controlled RNG service.
   * The engine provides stable scoped RNG forks (e.g., `game`, `policy:<actor_id>`) to reduce accidental nondeterminism due to call-order changes.

3. **First-class event trace**

   * Every match produces a structured event log including:

     * lifecycle (match start/end)
     * tick boundaries (tick start/end)
     * decision lifecycle (requested/provided)
     * action application / resolution
     * seed recording (and optional RNG usage instrumentation)
   * Events are serializable and exportable.

4. **Replay without agents/policies**

   * The system must reconstruct state from initial setup + recorded events, without invoking policy logic.
   * Replay can be lenient (state rebuild) or strict (validate emitted events match recorded events).

5. **Vocabulary standardization**

   * **Game** = ruleset/type
   * **Match** = one playthrough instance of a Game
   * **Simulation** = orchestration of many matches (tournaments/experiments)
   * **Tick** = universal engine step; games may optionally define turn/round/phase internally

6. **Stats/query layer as a read-only service**

   * Policies may query cross-match or tournament context (e.g., action ratios, win rate) through a read-only interface.
   * Initial implementation can be in-memory; DB (e.g., SQLite/JSONL) is optional and can be added later without leaking storage concerns into policies.

---

## Proposed module boundaries (target structure)

This structure is designed to support all required features and to keep responsibilities clean. Exact filenames can evolve, but the boundaries should remain stable.

```
bg_ai/
  engine/              # match execution + deterministic services
    match_runner.py
    tick_loop.py
    rng.py
    ids.py

  events/              # event model, sinks, import/export
    model.py
    sink.py
    codecs_jsonl.py

  games/               # game implementations + shared base protocol
    base.py
    rock_paper_scissors/
      game.py
      types.py
      rules.py

  agents/              # agent wrapper around policy
    base.py
    agent.py

  policies/            # strategies (decision logic)
    base.py
    random.py
    fixed.py
    weighted.py

  replay/              # rebuild state from events (no policies)
    replayer.py
    validator.py

  sim/                 # multi-match orchestration (tournament/experiments)
    simulation.py
    tournament.py
    results.py

  stats/               # query interface + implementations
    query.py
    in_memory.py
    sqlite_store.py    # optional later

  cli/                 # CLI entrypoints (GUI may come later)
    main.py

  docs/
    PROJECT_BRIEF.md
    FEATURES.md
    ARCHITECTURE.md
    ADR/
      0001-event-traced-deterministic-architecture.md
```

Notes:

* Existing concepts in `core/` will be migrated into these boundaries (e.g., `core/game.py` → `games/base.py` or similar).
* The current `match/`, `tournament/`, and `persistance/` placeholders will be replaced by the above separation (or removed if redundant).

---

## Key abstractions (conceptual contracts)

### Game contract

A Game owns:

* initial state creation (seeded)
* which actor(s) must act now
* how to apply actions to transition state
* terminal detection and result evaluation

To support all game types, the engine expects the Game to:

* request one or many actors per tick (turn-based vs simultaneous)
* accept a batch of actions for the current tick

### Agent and Policy

* **Agent** is a player identity + wiring (policy assignment, optional memory hook later).
* **Policy** is strategy logic: given a decision context, produce an action.

Decision context contains:

* state view (public/private as needed)
* legal actions (if provided by game)
* RNG handle (scoped)
* stats query service (read-only)
* match metadata (tick index, seed, actor id, etc.)

### RNG

* Single deterministic root RNG per match.
* Forked/scoped RNG streams per subsystem to stabilize determinism.

### Events (canonical record)

* Events are immutable, ordered, and serializable.
* Each event has an envelope containing:

  * `match_id`, `idx` (monotonic), `tick`
  * `type` (string)
  * `payload` (JSON-serializable dict)
  * optional metadata: schema version, timestamps

Minimum required event types:

* `seed_set` (always recorded, even when seed is provided)
* `match_start`, `match_end`
* `tick_start`, `tick_end`
* `decision_requested`, `decision_provided` (must include chosen action)
* `actions_applied` and/or domain resolution events

### Replay

* Uses the same Game transition logic, but consumes recorded actions from events.
* Does not call policies.
* Optional strict validation compares reconstructed events to recorded events.

### Stats/query layer

* Policies query via `StatsQuery` interface (read-only).
* Implementation can aggregate from completed matches/events.
* Optional persistence (SQLite/JSONL) can back the query service later.

---

## Consequences

### Benefits

* Enables deterministic experimentation and debugging.
* Event logs become a powerful artifact: replay, audit, analytics, visualization hooks.
* Clean layering: games don’t know about policies; policies don’t know about storage.
* Supports “any game type” by modeling decisions per tick as a set of required actors.

### Costs / tradeoffs

* Requires upfront design of event schemas and versioning strategy.
* Replay correctness depends on recording the right minimal set of canonical events (especially chosen actions and seed).
* Additional structure (engine/events/replay/stats) increases initial complexity vs a single simulation loop.

### Compatibility/migration

* Existing `Game`, `State`, `Action`, `Agent`, `Policy`, and `Simulation` concepts are preserved conceptually.
* Naming and module placement will change to match boundaries above.
* Current RPS can be used as the first “golden” game to validate:

  * determinism
  * event trace completeness
  * replay correctness

---

## Follow-up ADRs (recommended)

* ADR 0002: Event schema and versioning strategy (JSONL, schema version field, compatibility rules)
* ADR 0003: RNG scoping strategy (fork naming, determinism guarantees, optional RNG instrumentation events)
* ADR 0004: Replay strictness levels (lenient vs strict validation and when to use which)
* ADR 0005: Stats/query layer design (in-memory first, optional SQLite store)

---

## Acceptance criteria for this ADR

This ADR is considered successfully implemented when:

1. A match run produces a deterministic event log given a fixed seed.
2. The match can be replayed from initial setup + events without invoking policies.
3. The architecture allows adding a new game and a new policy without changing engine internals.
4. The project vocabulary is consistently used across docs and code (Game/Match/Simulation/Tick).
