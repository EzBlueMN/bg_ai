# ADR 0005 — Phase-Driven Game Rule Modeling

## Status
Proposed (planned)

## Context
Simple games (RPS, Matching Fingers) work well with a single “apply_actions” step.

However, many board/card games require multiple phases and sub-steps such as:
- init/setup
- choose role / buy resources
- execute actions
- resolve outcomes
- cleanup / next turn

If we keep growing games using a single monolithic `apply_actions` and a single `legal_actions` method,
we will end up with large `if/elif` blocks and poor separation of concerns.

We want:
- explicit multi-phase support
- legal actions depending on phase + memory
- better OOP structure so game logic is composed instead of hardcoded

## Decision (proposed)
Keep the existing engine-facing `Game` interface unchanged.

Inside a game implementation, introduce a Phase-driven pattern:

1) **State wrapper has explicit phase + memory**
- `state.phase`: enum-like identifier (e.g. BUY, PLAY, RESOLVE, END)
- `state.memory`: data needed by the game (resources, board, etc.)
- optional `state.pending`: partial selections for multi-step decisions

2) **Phase objects (rules)**
Create phase rule objects that define:
- `current_actor_ids(state)`
- `legal_actions(state, actor_id)`
- `apply_actions(state, actions_by_actor, rng) -> (state, domain_payloads)`
- transition rules (phase changes)

3) **Game delegates**
Game becomes a dispatcher:
- `phase_impl = phases[state.phase]`
- methods call into the phase implementation

## Non-goals (ADR0005)
- Hidden-information / private state
- Parameterized actions (moves with coordinates)
- Chance/decks abstraction
- Tournament systems

## Consequences
Pros:
- clean separation of multi-step game rules
- legal actions naturally depend on phase
- policies can reason on phase via `ctx.state.phase`
- avoids large if/elif chains

Cons:
- more boilerplate for simple games
- requires a consistent internal convention across games

## Follow-ups (future ADRs)
- Parameterized actions (dataclass actions)
- Public vs private state exposure
- Chance/deck mechanics with deterministic event tracing
