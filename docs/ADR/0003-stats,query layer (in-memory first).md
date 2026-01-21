# ADR 0003 — Stats / Query layer (in-memory first)

## Status
Accepted (implemented)

## Context
We want policies to become “smarter” by using historical information:
- win/loss record
- action frequencies
- eventually opponent modeling

We also want analysis tooling:
- experiment summaries
- behavior debugging

## Decision
1) Create an in-memory stats store:
- ingest match results + event stream
- compute action counts from decision_provided events
- compute win/loss/draw from match results

2) Expose stats through DecisionContext:
- `ctx.stats` provides a query interface

3) Provide a SimRunner:
- runs N matches sequentially
- updates stats store after each match

## Consequences
Pros:
- policies can use stats without global singletons
- tests can validate stats incrementally after matches
- adds minimal stateful learning capabilities

Cons:
- current store is in-memory only
- richer query interfaces may require schema/versioning later
