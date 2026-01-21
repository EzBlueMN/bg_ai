# bg_ai — Project Brief

## One-line summary
bg_ai is a deterministic, event-traced simulation framework for turn-based games, designed to support reproducible experiments, replay, and policy-driven agents.

## What bg_ai is (current scope)
- A minimal engine to run **matches** (single-game executions) with:
  - deterministic RNG
  - structured events (JSONL export/import)
  - replay to reproduce match results
- A framework to plug in **Games** and **Policies**
- A growing set of “toy games” used as architecture validation
- A stats/query layer (in-memory first) for policy context and analysis

## What bg_ai is NOT (yet)
- A full multi-agent RL training framework
- A full game DSL / data-driven game definition language
- A complete tournament manager (Swiss, brackets, etc.)
- Hidden-information / partially observable game engine (planned later)

## Core invariants (do not break)
1) **Determinism**: same seed + same policies ⇒ same results/events
2) **Replay correctness**: replaying recorded events reproduces the match outcome
3) **Events are JSON-serializable**: payloads must remain wire-safe
4) **Stable module layout**: src-layout, imports always `from bg_ai...`
5) **Slice numbering monotonic**: slices never reset across ADRs

## Current implemented milestones (high-level)
- ADR0001: deterministic match engine + event tracing + replay
- ADR0002: repo usability + runner patterns for ADR tests
- ADR0003: typed actions + single-match games + series runner + series events
- ADR0004: stats/query (in-memory) + DecisionContext.stats + SimRunner

## Next milestone (planned)
- ADR0005: phase-driven game rule modeling (multi-phase games without giant if/elif)
