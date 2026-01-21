# ADR 0004 — Stats / Query Layer (In-Memory First)

## Status
Accepted (implemented)

## Context
We want policies and experiments to have access to “history” across matches:
- win/loss/draw record
- action frequency (per actor)
- basic behavior summaries

We also want to keep the engine deterministic and replayable.

Before this ADR:
- matches produced results + events
- but there was no persistent aggregation layer
- policies had no shared query interface for stats

## Decision
We introduce an in-memory stats/query layer:

1) **StatsQuery interface**
A minimal read-only interface:
- `action_counts(actor_id) -> {wire_action: count}`
- `record(actor_id) -> {wins, losses, draws, total}`
- `win_rate(actor_id) -> float`

2) **InMemoryStatsStore**
A concrete implementation that supports:
- ingestion from a completed match:
  - `ingest_match(result, events)`
- action counts derived from:
  - `decision_provided` events (`payload.actor_id`, `payload.action`)
- W/L/D derived from:
  - `MatchResult.details["winner"]`
  - `MatchResult.details["actors"]`

3) **DecisionContext.stats**
MatchRunner wires a `stats_query` object into policies:
- `ctx.stats` becomes available inside `Policy.decide(ctx)`
- default behavior is safe (NullStatsQuery / empty stats)

4) **SimRunner**
A higher-level runner that:
- executes N matches sequentially
- updates the stats store after each match
- passes the query object into MatchRunner so policies see updated stats

## Consequences
Pros:
- policies can use cross-match stats without globals
- reproducible experiments remain possible
- minimal and easy to test

Cons / limitations:
- current store is in-memory only
- relies on match result schema providing:
  - `actors` list
  - `winner` id or None
- richer analytics (opponent modeling, per-phase stats, etc.) is future work

## Notes
This ADR does not define:
- persistent storage
- statistics versioning
- event schema evolution rules
