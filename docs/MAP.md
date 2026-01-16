# docs/MAP.md

# bg_ai — Map (Where to look)

This file answers: "Where do I go in the repo to understand or change X?"

---

## Start here (reading order)

1. `docs/README_DEV.md`
2. `docs/PROJECT_BRIEF.md`
3. `docs/FEATURES.md`
4. `docs/ARCHITECTURE.md`
5. `docs/ADR/` (decisions and tradeoffs)

Then code:
6) `src/bg_ai/engine/match_runner.py`
7) `src/bg_ai/games/base.py`
8) `src/bg_ai/games/rock_paper_scissors/game.py`
9) `src/bg_ai/replay/replayer.py`

---

## I want to...

### Run a match (live)

* `src/bg_ai/engine/match_runner.py`

### Add a new game

Start with:

* `src/bg_ai/games/base.py` (Game contract)

Then follow the example:

* `src/bg_ai/games/rock_paper_scissors/game.py`

### Add a new policy

* `src/bg_ai/policies/base.py`
* `src/bg_ai/policies/random_policy.py`
* `src/bg_ai/policies/fixed_policy.py`

### Understand how decisions are recorded

* `src/bg_ai/engine/match_runner.py`
  Search for:
* `decision_requested`
* `decision_provided`

### Export / import event logs

* `src/bg_ai/events/codecs_jsonl.py`

### Replay without policies

* `src/bg_ai/replay/replayer.py`

---

## Debug map (if something is wrong)

### "Match never ends"

* check `Game.is_terminal(...)`
* check `MatchConfig.max_ticks`

### "Replay result differs from live result"

* check the event stream includes all `decision_provided`
* check game `apply_actions(...)` uses only:

  * provided actions
  * deterministic RNG fork (`game:apply:<tick>`)

### "Imports are broken"

If you use `src/` layout:

* ensure `src/` is marked as Sources Root (PyCharm)
* run modules from repo root:

  * `python -m ...`
* ADR runner adds `src/` to `sys.path`

---

## Validation tools

### ADR0001 slice runner

Validates end-to-end MVP slices:

```
python -m test_ADR.ADR0001
```
