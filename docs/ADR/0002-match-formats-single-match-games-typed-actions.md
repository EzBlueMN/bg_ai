# ADR 0002 — Match formats, single-match games, typed actions

## Status
Accepted (implemented)

## Context
Initial games like RPS were evolving into multi-round logic inside the game.
This caused:
- duplicated concepts (rounds vs match vs series)
- limited composition of “multiple matches”
- unclear boundaries between game rules and match orchestration

## Decision
1) Treat each game implementation as a **single-match game**:
   - one match produces one result
2) Add typed actions with wire-safe serialization:
   - `ActionEnum` base
   - game-specific enums (RPSAction, FingersAction)
3) Introduce match formats using a series runner:
   - BestOfN
   - FirstToN
4) Add optional series-level events (minimal):
   - series_start / series_match_completed / series_end

## Consequences
Pros:
- clean separation between game logic and multi-match orchestration
- policies can use strong types (enums) while logs remain JSON-friendly
- series results are easy to compute

Cons:
- larger games will need parameterized actions later (not only enums)
