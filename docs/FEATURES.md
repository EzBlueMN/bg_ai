# Features

This file is a status-oriented overview of bg_ai capabilities.

Legend:
- ✅ implemented
- 🟡 planned
- ❌ out of scope (for now)

---

## Engine / Runtime
- ✅ Deterministic match execution (seeded RNG)
- ✅ Tick-based execution loop
- ✅ Stable event emission (match_id, idx, tick, type, payload)
- ✅ JSONL export/import for events
- ✅ Replay reproduces results

## Policies / Agents
- ✅ Agent wrapper (`Agent(actor_id, policy)`)
- ✅ Policy interface (`decide(ctx)`)
- ✅ DecisionContext passed into policies
- ✅ Typed actions via `ActionEnum` (wire-safe strings)

## Games
- ✅ Game interface supports:
  - initial_state
  - current_actor_ids
  - legal_actions
  - apply_actions
  - is_terminal
  - result
- ✅ Rock Paper Scissors (single-round match)
- ✅ Matching Fingers (single-round match)

## Match Formats / Multi-match execution
- ✅ SeriesRunner (BestOfN, FirstToN)
- ✅ Series-level events (Option A):
  - series_start
  - series_match_completed
  - series_end

## Stats / Query
- ✅ InMemoryStatsStore
- ✅ Stats ingest from match result + decision events
- ✅ ctx.stats wired into DecisionContext
- ✅ SimRunner runs N matches and updates stats after each match

---

## Planned next
- 🟡 Phase-driven games (phase + memory + phase rules objects)
- 🟡 Parameterized actions (dataclass actions for moves like “from→to”)
- 🟡 Public/private state separation (hidden information)
- 🟡 Chance/decks as deterministic event-traced transformations
- 🟡 Tournament formats (Swiss, bracket)

---

## Explicitly out of scope (for now)
- ❌ Full JSON-defined game rules engine / DSL
- ❌ Neural training pipeline / PPO/etc.
