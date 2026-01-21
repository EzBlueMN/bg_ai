# ADR 0001 — Event-traced deterministic architecture

## Status
Accepted (implemented)

## Context
We need a foundation for:
- deterministic simulation runs
- traceable execution
- replay correctness
- future policy experiments

## Decision
Implement a match engine that emits events while running:
- events include match_id, idx, tick, type, payload
- payloads must stay JSON-serializable
- event streams can be exported/imported as JSONL
- replay uses recorded decision events to reproduce results

## Consequences
Pros:
- deterministic reproducibility enables testing and debugging
- replay enables auditing and experiment analysis
- events allow later derived stats/query layers

Cons:
- event schema discipline must be maintained
- policy and game logic must stay deterministic given RNG

## Notes
This ADR is the base for:
- ADR0003 typed actions (wire-safe)
- ADR0004 stats ingestion from event streams
