# Architecture

This document describes the current architecture of bg_ai and the design intent for upcoming milestones.

---

## Top-level concepts

### Game
A `Game` defines match rules:
- how to create initial state
- who must act at each step
- what actions are legal
- how actions update state
- when the match ends
- how to compute final result

**Note:** A match is **one execution** of a Game under a given configuration.

### MatchRunner
`MatchRunner` executes a single match:
- builds initial state
- requests decisions from policies via DecisionContext
- applies actions
- emits trace events
- returns MatchResult

### Event model (current)
All runtime signals are emitted as `Event` objects:
- `match_id`: string id for grouping events
- `idx`: global index for ordering events inside a match
- `tick`: logical time step (integer)
- `type`: string
- `payload`: dict, must be JSON-serializable

### Replay
Replay runs a Game by reusing event streams:
- decisions are taken from recorded events
- outcome should match original run (determinism invariant)

### Typed Actions
Actions are represented with `ActionEnum` subclasses per game:
- type-safe in code
- wire-safe in events via string values

Example:
- `RPSAction.ROCK` instead of `"R"`

### Series (multi-match aggregation)
SeriesRunner executes multiple matches and aggregates:
- BestOfN
- FirstToN
It also supports minimal series-level events.

### Stats / Query
Stats are updated after each completed match:
- in-memory store ingests match result + decision_provided events
- policies can access stats through `DecisionContext.stats`

---

## Current module map (important packages)

- `bg_ai.engine/`
  - match runner (single match execution)

- `bg_ai.events/`
  - event model
  - sinks (in-memory sink)
  - JSONL codecs
  - pretty printing helpers

- `bg_ai.games/`
  - Game definitions and game-specific types

- `bg_ai.policies/`
  - policy interfaces and implementations

- `bg_ai.series/`
  - series formats (BestOfN / FirstToN)
  - series runner
  - series ids

- `bg_ai.stats/`
  - stats query interface
  - in-memory store

- `bg_ai.sim/`
  - sim runner (runs N matches, updates stats)

---

## Design constraints / invariants
1) Determinism and replay correctness are foundational
2) Event payloads must be JSON-safe (strings, numbers, lists, dicts)
3) Game logic must remain pure-ish: state + actions + rng ⇒ next state
4) Slice-based development must stay monotonic across ADRs

---

## Next architecture direction (planned)

### ADR0005: Phase-driven games
Goal: support multi-step games without giant if/elif logic.

Proposed internal game pattern:
- `state.phase`: explicit enum representing the current rule step
- `state.memory`: game memory (resources, board, hand, etc.)
- game delegates legal/action logic to phase objects (“phase rules”)

This does NOT require changing MatchRunner or the `Game` interface.
