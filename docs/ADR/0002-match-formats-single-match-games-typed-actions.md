# ADR 0002 — Match Formats, Single-Match Games, and Typed Actions

**Status:** Proposed
**Date:** 2026-01-18
**Related:** ADR 0001 (Event-traced deterministic architecture)

---

## Context

Today, at least one game (RPS) embeds multi-round logic directly in its game state (round counters and cumulative score).
Policies also return raw action tokens (ex: "R"), which makes code less type-safe and harder to extend across games.

We want:

1) Games to represent the minimal unit of play:
   - RPS should be a single round (one simultaneous action per player, one outcome).
2) A generic way to play multiple matches for a game:
   - best_of_X
   - first_to_X
   - play_for_duration (if/when we introduce deterministic simulated time)
   - later: tournaments, swiss, etc.
3) Typed actions:
   - prefer RPSAction.ROCK instead of "R"
   - allow each game to define its own action enum
   - still have a common concept for “Action” used by generic code.
4) Add a second simple game to validate separation:
   - Matching Fingers: each player reveals 1 or 2 fingers.
     - If same -> Player A wins
     - If different -> Player B wins
   (Exact “who wins on same/different” should be part of the game rules/config.)

---

## Decision

### 1) Move multi-match concerns out of Game

Introduce a generic “format” layer that runs many single-match games.

Terminology:

- **Game**: rules + state transition for a single match.
- **Match**: one execution of a Game from initial state to terminal state.
- **Series**: multiple matches of the same Game aggregated under a format.

New concepts:

- `MatchFormat` (strategy): defines stop condition and aggregation rules.
- `SeriesRunner` (engine helper): repeatedly runs MatchRunner + applies MatchFormat.

This removes the need for “rounds_total”, “round_index”, and “scoreboard across rounds” from individual games like RPS.

### 2) Require single-match Game implementations

Games should not embed “best-of” or multi-round logic in game state.
They may still emit rich per-match result payloads (winner, draw, actions, etc.).

### 3) Use Enum-based actions with a reusable base

Define a reusable base for per-game action enums:

- `ActionEnum` = common base for game action enums.
- Each game defines `XxxAction(ActionEnum)` (e.g. `RPSAction`, `FingersAction`).

The event stream should store a stable “wire” representation of actions:

- default: store `action.value` (string) in `decision_provided.payload["action"]`
- decoders should accept older shapes if we need backward compatibility.

### 4) Policies are game-specific, generic policies can be adapted

Policies should be typed per game action space.

Example intent:

- `RPSPolicy` returns `RPSAction`
- A generic policy implementation can still exist, but must be wrapped/adapted to a specific game.

---

## Design

### MatchFormat

A MatchFormat defines:

- `is_done(series_state) -> bool`
- `update(series_state, match_result) -> None`
- `winner(series_state) -> optional[winner_id]` (or equivalent)

MVP formats:

- BestOfN
- FirstToN

Later (optional):

- PlayForDuration (requires deterministic simulated time model)
- Tournament formats (separate ADR)

### SeriesRunner

SeriesRunner responsibilities:

- Creates a new match with fresh match_id each time
- Runs MatchRunner for that match
- Feeds the match result into MatchFormat
- Emits series-level events (optional in MVP):
  - series_start
  - series_match_completed
  - series_end

### Typed actions

Introduce `ActionEnum` base.

Wire format rules:

- Live run:
  - policy returns `ActionEnum` instance
  - engine logs `action.value` in the event payload
- Replay:
  - decoder maps wire string back to the game’s action enum

Compatibility:

- If older logs stored different shapes (ex: raw string tokens already match `.value`), decoding remains easy.

---

## Consequences

### Pros

- Clear separation:
  - games stay minimal and reusable
  - series/tournament logic becomes generic
- Stronger typing for actions and policies
- Adding a new game becomes easier and more consistent

### Cons / Costs

- Refactor required:
  - RPS must become single-round
  - example scripts must change
- Replay/event payload compatibility needs careful handling if old logs exist
- Adds one more layer (SeriesRunner / MatchFormat) to understand

---

## Follow-ups

- ADR 0003 (Stats/Query Layer) should be updated to reference Series/Format as a source of “cross-match” boundaries.
- Implement a second game (Matching Fingers) to validate that the abstractions do not leak RPS assumptions.
