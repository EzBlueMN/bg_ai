# bg_ai — Features & Acceptance Criteria

This document defines the product features as behaviors, not implementation details.
Vocabulary: Game / Match / Simulation / Tick.

## F0 — Core Vocabulary & Interfaces (foundation)
**Goal:** A consistent conceptual model across all games.

Acceptance Criteria:
- A "Game" is a ruleset/type, and a "Match" is a single playthrough instance.
- Engine exposes a universal Tick loop that works for:
  - simultaneous-move games
  - alternating-turn games
  - initiative/variable-turn-order games
  - multi-step turns (phase-like structure inside the game)
- Policies and Games remain decoupled: policies do not mutate game state directly.

---

## F1 — Deterministic RNG (hard requirement)
**Goal:** Any randomness can be used anywhere, but deterministically.

Acceptance Criteria:
- Match can be started with an explicit seed.
- If no seed is provided, the engine generates one and records it as an event.
- All randomness used by engine/game/policy can be routed through a controlled RNG source.
- Same seed + same setup + same code version ⇒ same event trace and same outcome.

Notes:
- Determinism is validated via regression tests (repeat run equality).

---

## F2 — Event System (first-class trace)
**Goal:** Capture a complete, structured event log for every match.

Acceptance Criteria:
- Engine emits a match event stream containing:
  - match lifecycle (match_start, match_end)
  - tick boundaries (tick_start, tick_end)
  - decision lifecycle (decision_requested, decision_provided)
  - action application (action_applied / resolution events)
  - RNG/seed events as needed (seed_set, rng_used optional)
- Events are ordered, timestamped/logical-indexed, and serializable.
- Events include enough data to replay the match deterministically without invoking agents/policies.

---

## F3 — Replay (no agent required)
**Goal:** Rebuild match state from initial setup + event log.

Acceptance Criteria:
- Replay can run in a "no-agent" mode:
  - takes initial state/setup + event list
  - applies events to rebuild the same final state/outcome
- Replay outputs match result identical to the original run.
- Replay does not call policies.

---

## F4 — Minimal Match Runner (Phase 3 slice)
**Goal:** A minimal, working end-to-end match execution.

Acceptance Criteria:
- `main.py` can run a match (hard-coded configuration initially).
- At least one example game works end-to-end (start with RPS).
- Output includes:
  - final result summary (winner/draw/score)
  - event count
  - optional path to exported event log

---

## F5 — Export / Import of Event Logs
**Goal:** Persist match traces and reload them later.

Acceptance Criteria:
- Events can be exported to disk (JSON or JSONL).
- Export includes match metadata:
  - game id/name
  - seed
  - participating agents/policies identifiers
  - version info (optional but recommended)
- Exported trace can be imported and replayed successfully.

---

## F6 — Simulation/Tournament Orchestration (Milestone 3)
**Goal:** Run multiple matches and aggregate results.

Acceptance Criteria:
- A Simulation can run N matches with:
  - same configuration
  - or a set of configurations (round-robin)
- Aggregated stats are produced:
  - win rate per agent/policy
  - action distribution (where applicable)
- Simulation results can reference stored match logs.

---

## F7 — Stats & Query Layer (Maybe Soon)
**Goal:** Policies can query historical and aggregate info safely.

Acceptance Criteria:
- Provide a query interface that can answer:
  - R:P:S ratio for a player/policy (for RPS-like games)
  - win rate of a player/policy in current simulation
  - results for a player across a tournament
- Policy can request stats via a read-only API (no direct DB coupling).
- Default implementation works without a DB (in-memory), DB can come later.

Non-goals for stats:
- No heavyweight analytics stack required in MVP.
