## Milestone: 1 — ADR0001 (S1-S8) - Plan (MVP)

**Goal:** Build a fresh MVP implementation based on the current architecture.
**Approach:** Greenfield MVP (new code aligned with ADR/ARCHITECTURE), legacy code is ignored for implementation.
**Priority:** Determinism + Events + Replay (no policies during replay).

---

## 0) MVP Definition of Done

The MVP is complete when all of the following are true:

1) A match can run end-to-end for at least one game (RPS).
2) Determinism works:
   - Same seed + same config ⇒ same event trace + same match result
3) A full event log is produced during the match.
4) Event log can be exported to disk.
5) Replay works without calling policies:
   - Initial setup + events ⇒ same final result
6) A single entrypoint (initially hard-coded `main.py`) runs:
   - live match
   - replay from exported log

---

## 1) Implementation strategy

### Fresh code (no legacy integration)
- We implement the MVP from scratch using the new architecture.
- We do not attempt to modify old repo code to fit the new design.

### Minimal dependencies
- Standard library only for MVP.
- No DB, no networking, no GUI, no parallelism.

### Default choices for MVP
- Event export format: **JSONL** (1 event per line)
- Replay mode: **Lenient replay** (strict validation optional later)
- Policies: basic examples only (Random + Fixed)
- Configuration: hard-coded in `main.py` (CLI later)

---

## 2) Target MVP folder structure

This is the structure we will create first:

bg_ai/
init.py

cli/
main.py

engine/
init.py
match_runner.py
rng.py
ids.py

events/
init.py
model.py
sink.py
codecs_jsonl.py

games/
init.py
base.py
rock_paper_scissors/
init.py
game.py
types.py

agents/
init.py
agent.py

policies/
init.py
base.py
random_policy.py
fixed_policy.py

replay/
init.py
replayer.py

tests/
test_determinism_rps.py
test_replay_rps.py

docs/
PROJECT_BRIEF.md
FEATURES.md
ARCHITECTURE.md
PLAN.md
ADR/
0001-event-traced-deterministic-architecture.md


---

## 3) Work slices (MVP)

Each slice is designed to be small, testable, and incremental.

---

### Slice S1 — Repo bootstrap + entrypoint

**Goal:** Establish a runnable skeleton with the target folder structure.

**Files to create**
- `bg_ai/` package + subpackages
- `bg_ai/cli/main.py`

**Acceptance criteria**
- Running `python -m bg_ai.cli.main` works and prints "OK".

**How to verify**
- Command:
  - `python -m bg_ai.cli.main`

---

### Slice S2 — Deterministic RNG service (F1)

**Goal:** Implement a deterministic RNG service that supports scoped forks.

**Files**
- `bg_ai/engine/rng.py`

**Acceptance criteria**
- Root RNG created from a seed produces deterministic numbers.
- Forked RNG streams are stable and independent:
  - adding new forks does not change other streams

**How to verify**
- Add a small test or demo call in `main.py`
- Add unit test if desired later (recommended)

---

### Slice S3 — Event model + in-memory sink (F2 partial)

**Goal:** Define canonical event envelopes and an event sink that collects events.

**Files**
- `bg_ai/events/model.py`
- `bg_ai/events/sink.py`

**Acceptance criteria**
- Events contain:
  - match_id, idx, tick, type, payload
- In-memory sink stores events in order and supports `.emit()`

---

### Slice S4 — JSONL export/import codec (F5 partial)

**Goal:** Export a list of events to JSONL and load it back.

**Files**
- `bg_ai/events/codecs_jsonl.py`

**Acceptance criteria**
- Export produces 1 JSON object per line.
- Import restores the same event list (same fields, same order).

**How to verify**
- `main.py` writes a file like:
  - `runs/rps_match_001.jsonl`
- You can load it back and count events.

---

### Slice S5 — Game base contract + MatchRunner emits lifecycle/tick events (F0 + F2 partial)

**Goal:** Implement the match execution loop (Tick-based) and emit key engine events.

**Files**
- `bg_ai/games/base.py`
- `bg_ai/engine/match_runner.py`
- `bg_ai/engine/ids.py`

**Events required (minimum)**
- `seed_set`
- `match_start`
- `tick_start`
- `tick_end`
- `match_end`

**Acceptance criteria**
- MatchRunner can run a match loop even before full actions exist.
- Events are emitted with increasing `idx`.

---

### Slice S6 — Decision events + basic Agent/Policy wiring (F2 + F4 partial)

**Goal:** Policies produce actions during live play and decisions are recorded.

**Files**
- `bg_ai/policies/base.py`
- `bg_ai/policies/random_policy.py`
- `bg_ai/policies/fixed_policy.py`
- `bg_ai/agents/agent.py`

**Events required**
- `decision_requested`
- `decision_provided` (must store the chosen action)

**Acceptance criteria**
- For each actor required by the game per tick:
  - decision_requested emitted
  - policy called once
  - decision_provided emitted with action payload

---

### Slice S7 — RPS game end-to-end with actions applied (F4)

**Goal:** Implement a complete working example game.

**Files**
- `bg_ai/games/rock_paper_scissors/types.py`
- `bg_ai/games/rock_paper_scissors/game.py`

**Acceptance criteria**
- RPS can run for N rounds.
- End result produced (win/loss/draw counts or final winner).
- Events include:
  - decisions
  - actions applied/resolution for each tick

**How to verify**
- Run match from `main.py`, see summary + event count.

---

### Slice S8 — Replay (no policies) (F3)

**Goal:** Rebuild match state from initial setup + recorded decisions.

**Files**
- `bg_ai/replay/replayer.py`

**Replay rules**
- Replayer must NOT instantiate agents or call policies.
- It reads recorded `decision_provided` events and applies them via the game.

**Acceptance criteria**
- Live match result == replayed match result
- Replay runs deterministically and produces same final outcome

---

## 4) Testing plan (MVP)

### Test T1 — Determinism
**File:** `tests/test_determinism_rps.py`

Acceptance criteria:
- Run match twice with same seed and same config
- event logs are identical (or at least equivalent by idx/type/payload)
- final results identical

### Test T2 — Replay
**File:** `tests/test_replay_rps.py`

Acceptance criteria:
- Run match live → export events
- Import events → replay
- replay result equals live result

---

## 5) Post-MVP planned extensions (not part of MVP)

These are intentionally delayed:
- strict replay validation (compare domain events)
- snapshots (performance)
- tournaments/simulation layer
- stats/query service + SQLite store
- CLI arguments / config files
- GUI

---

## 6) Execution instructions (MVP)

### Run a live match
- `python -m bg_ai.cli.main`

### Run replay
- `python -m bg_ai.cli.main --replay runs/<file>.jsonl`
(added later when CLI exists; for MVP can be hard-coded)

---

## 7) Notes / rules during implementation

- Do not add complexity unless required by an acceptance criteria.
- Do not let policies mutate game state directly.
- Do not allow unseeded randomness.
- If something is unclear, prefer adding an event to make behavior observable.

## Milestone : Readability / Developer Onboarding (insert between S8 and S9)

### Goal (Definition of Done)
Before starting ADR0002 (Stats/Query), we add a human-friendly layer so a developer can:
1) Understand what ADR0001 built without reading all code first
2) Know where to start and how the system flows
3) Run a simple example from PyCharm and see readable output (events + summary)
4) Use examples as the “living documentation” instead of relying on the ADR tests

---

### Slice S9 — Developer README + Project Map (Docs)

**Create**
- `docs/README_DEV.md` (main onboarding entrypoint)
- `docs/MAP.md` (navigation map: “if you want X, read Y”)

**Acceptance Criteria**
- README includes:
  - What the project is (1 paragraph)
  - How to run the simplest demo (one script)
  - Key vocabulary (Game/Match/Tick/Event/Replay/Agent/Policy)
  - “Follow the flow” (file → file)
- MAP includes:
  - “Start here” reading order
  - Links to key files
  - Debug pointers (if X fails, look at Y)

---

### Slice S10 — ADR0001 Implementation Notes (Docs)

**Create**
- `docs/IMPLEMENTATION/ADR0001.md`

**Acceptance Criteria**
- Explains:
  - What was implemented (S1–S8)
  - What was intentionally NOT implemented
  - Key invariants
  - Event types emitted and when
  - Replay assumptions + limitations
  - Where to extend next (Stats layer entrypoint)

---

### Slice S11 — Executable Examples (PyCharm-friendly)

**Create**
- `examples/adr0001_rps_live_and_replay.py`
- `examples/adr0001_no_action_game.py`

**Acceptance Criteria**
- Running each example produces:
  - clear printed summary
  - event count + top event types
  - live result vs replay result comparison (for RPS example)

---

### Slice S12 — Pretty Event Printing Helpers

**Create**
- `src/bg_ai/events/pretty.py`

**Acceptance Criteria**
- Provide helpers:
  - `format_event(ev) -> str`
  - `print_events(events, limit=...)`
  - `summarize_event_types(events) -> dict[type, count]`
- Examples use these helpers instead of raw event dumps

---

## Milestone: ADR0002 (S13-116) — Stats/Query Layer (In-Memory)

### Goal (Definition of Done)

1. A `StatsStore` can ingest completed matches (result + events).
2. A `StatsQuery` can answer at least:

   * action distribution for a player (R/P/S counts)
   * win rate for a player (wins/total, draws supported)
3. `DecisionContext` includes an optional `stats` handle.
4. A demo run (or ADR test) proves:

   * run N matches
   * store is updated
   * queries return expected numbers

---

### Slice S13 — Stats interfaces + in-memory implementation

**Create**

* `src/bg_ai/stats/__init__.py`
* `src/bg_ai/stats/base.py` (Protocols: StatsQuery, StatsStore)
* `src/bg_ai/stats/memory_store.py` (InMemoryStatsStore)

**Acceptance criteria**

* Can record:

  * per-player action counts
  * per-player wins/losses/draws (game-agnostic)
* Query methods return deterministic results.

---

### Slice S14 — Wire StatsQuery into DecisionContext (optional for policies)

**Update**

* `src/bg_ai/policies/base.py` (DecisionContext gains `stats` field, default None)
* `src/bg_ai/engine/match_runner.py` (accept optional `stats_query` or `stats_store.query()`)

**Acceptance criteria**

* Policies can read `ctx.stats` if provided.
* Existing tests still pass when stats is None.

---

### Slice S15 — Simulation helper to run multiple matches + update store

**Create**

* `src/bg_ai/sim/__init__.py`
* `src/bg_ai/sim/sim_runner.py`

**Acceptance criteria**

* Runs M matches sequentially, updating stats after each match:

  * `store.ingest_match(game_id, agents, result, events)`
* Returns final stats store.

---

### Slice S16 — ADR runner test_s9+ (or ADR0002 runner)

**Update**

* Either extend `test_ADR/ADR0001.py` with:

  * `test_s9()` (stats aggregation)
  * `test_s10()` (stats wired into context)
* Or create:

  * `test_ADR/ADR0002.py` (recommended for clarity)

**Acceptance criteria**

* After 3 RPS matches (fixed policies), assert:

  * action_distribution(A)["R"] == expected
  * win_rate(A) == expected

---
