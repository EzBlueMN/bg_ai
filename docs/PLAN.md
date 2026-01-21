# Plan

Slice numbers are global and monotonic: S1, S2, S3, ... forever.

Rule:
- Every slice belongs to exactly one ADR.
- Docs-only milestones still get an ADR number and a lightweight ADR runner.

---

## ADR0001 — Event-traced deterministic architecture (S1–S8)
Status: done

- S1: deterministic RNG seed + event id baseline
- S2: event sink + in-memory storage
- S3: JSONL export/import
- S4: replay baseline
- S5: reproducible replays
- S6: determinism checks
- S7: RPS demo execution
- S8: RPS replay validation

---

## ADR0002 — Project usability + developer onboarding (S9–S12)
Status: done

- S9: ADR runner patterns
- S10: run_all ADR harness
- S11: docs structure conventions
- S12: minimal onboarding improvements

---

## ADR0003 — Match formats, single-match games, typed actions (S13–S17)
Status: done

- S13: ActionEnum base + typed actions for RPS
- S14: RPS becomes single-round match
- S15: SeriesRunner + BestOfN / FirstToN
- S15.1: series-level events (series_start/match_completed/end)
- S16: Matching Fingers game (single-round)
- S17: example module covering RPS series + Fingers series

---

## ADR0004 — Stats/Query layer (in-memory first) (S18–S21)
Status: done

- S18: InMemoryStatsStore MVP + tests
- S19: DecisionContext.stats wiring + tests
- S20: SimRunner runs N matches and updates stats after each match
- S21: ADR0004 integration test (stats + ctx.stats + sim)

---

## ADR0005 — Phase-driven game rule modeling (S22–S27)
Status: planned

Goal:
- Enable multi-phase games (buy/play/resolve/etc.) with clean separation of rules.

Principle:
- Keep the engine-facing `Game` interface unchanged.
- Implement phase logic inside games via Phase rule objects (OOP dispatcher).

Non-goals (ADR0005):
- hidden information / private state
- parameterized actions for grid-based games
- chance/decks abstraction
- tournament formats

### S22 — Phase model primitives (protocols + ids)
Deliverables:
- `bg_ai/games/phases/` package
- `PhaseId` type (string or Enum-like)
- `PhaseRules` Protocol:
  - `current_actor_ids(state) -> list[str]`
  - `legal_actions(state, actor_id) -> list[ActionEnum]`
  - `apply_actions(state, actions_by_actor, rng) -> (state, domain_payloads)`
Acceptance:
- Unit tests validate a dummy PhaseRules object can be called and returns expected shapes.

### S23 — Phase-driven state wrapper (generic)
Deliverables:
- `PhaseState` generic-ish container:
  - `phase`
  - `memory`
  - optional `pending`
Acceptance:
- Minimal helper functions:
  - `is_terminal` convention based on phase or a `done` flag in memory

### S24 — Example game: Buy/Play/Both/Pass (single-turn, multi-phase)
Game concept:
- Each match is a fixed number of turns (or “first to X points” later via SeriesRunner).
- Each turn has phases:
  1) CHOOSE_MODE (players choose BUY/PLAY/BOTH/PASS)
  2) RESOLVE (apply resource/point updates)
  3) NEXT_TURN (advance turn counter, go back to CHOOSE_MODE) or END

Deliverables:
- `bg_ai/games/buy_play/` (name can change later)
- `ActionEnum` for mode selection
- Memory includes:
  - coins_by_actor
  - points_by_actor
  - turn
  - max_turns (from config)
Acceptance:
- Deterministic outcomes for fixed policies.

### S25 — Dispatcher pattern inside the example game
Deliverables:
- Game delegates to PhaseRules objects:
  - `ChooseModeRules`
  - `ResolveRules`
  - `NextTurnRules` (or integrated into Resolve)
Acceptance:
- `legal_actions` differs by phase (e.g., PLAY illegal if coins==0, depending on chosen rule)
- Policies can branch on `ctx.state.phase`.

### S26 — Policies for phase-driven gameplay
Deliverables:
- 2 policies:
  - greedy (prefer PLAY/BOTH when possible)
  - conservative (prefer BUY until threshold)
Acceptance:
- Tests verify policies see phase and make expected decisions.

### S27 — ADR0005 test module + example
Deliverables:
- `test_ADR/ADR0005.py` runs S22..S27
- `examples/adr0005_buy_play_phase_game.py`
Acceptance:
- Replay works for at least one match of the example game.
