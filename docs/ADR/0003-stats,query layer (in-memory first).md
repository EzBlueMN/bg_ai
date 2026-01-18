# ADR 0003 — Stats/Query Layer (In-Memory First)

**Status:** Proposed
**Date:** 2026-01-16
**Related:** ADR 0001 (Event-traced deterministic architecture)
**Supersedes:** ADR 0002 (renumbered; see ADR 0002 for match formats + typed actions)

---

## Context

We want policies and experiments to access **cross-match** information such as:

* R:P:S ratios for a player
* win rate of a player
* results by opponent, tournament, or policy
* “previous games” and “history” beyond the current match

MVP already supports:

* deterministic execution
* full event logging
* replay without policies

Now we need a **Stats/Query layer** that:

* can be updated after each match
* can answer questions during later matches (or later in the same simulation)
* does not force a DB immediately
* keeps determinism and separation of concerns

---

## Decision

### Truth model

**Hybrid (C)**:

* Canonical record remains the **event stream** (events are the source of truth)
* Stats store is a **derived view** built from match results and/or events

### Storage strategy (phase 1)

**In-memory aggregator + export (optional)**

* `StatsStore` is updated incrementally after a match completes.
* `StatsQuery` is a read-only interface for policies and simulations.

A future ADR may add:

* SQLite-backed store
* incremental rebuild from JSONL event logs
* schema versioning and migrations

---

## Design

### New core interfaces

#### `StatsQuery` (read-only)

Examples of supported queries (MVP subset):

* `action_distribution(player_id, game_id=None) -> dict[action, count]`
* `win_rate(player_id, game_id=None) -> float`
* `head_to_head(player_id, opponent_id, game_id=None) -> {wins, losses, draws}`

Policies receive a `stats: StatsQuery` handle via `DecisionContext` (optional for MVP, but wired in).

#### `StatsStore` (mutable)

* updated by the simulation loop or match runner wrapper
* provides `query()` returning a `StatsQuery` view

### What gets stored

Minimum derived data:

* match outcomes (winner, scores, draw)
* actions selected per actor (from decision_provided events) **or** summary counts emitted by the game
* metadata (policy name, game_id, seed, timestamps optional)

### Determinism rule

Stats queries must not introduce nondeterminism:

* querying existing deterministic data is OK
* using wall-clock timestamps or random sampling is not OK unless explicitly controlled

---

## Consequences

### Pros

* Fast to implement
* No DB complexity
* Works for policy “memory” and tournament-level analysis
* Can later be rebuilt from events or exported summaries

### Cons

* In-memory only (lost between runs unless exported)
* Requires explicit update step after matches
* Query set will expand over time (need careful API evolution)

---

## Notes

* The Stats layer is intentionally separate from replay:
  replay reconstructs a match; stats summarize many matches.
* A future ADR can define a stable schema and storage (SQLite/Parquet/etc.).
