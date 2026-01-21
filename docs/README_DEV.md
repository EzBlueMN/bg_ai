# Developer README

## Repo layout
This repo uses src-layout.

- Python package root:
  - `src/bg_ai/`
- Docs:
  - `docs/`
- ADR test runners:
  - `test_ADR/`
- Examples:
  - `examples/`
- Runtime artifacts:
  - `runs/`

Import rule:
- Always import using:
  - `from bg_ai...`

---

## Running tests
Run all ADR runners:
- `python -m test_ADR.run_all`

Run a specific ADR:
- `python -m test_ADR.ADR0001`
- `python -m test_ADR.ADR0003`
- `python -m test_ADR.ADR0004`

---

## Running examples
Example modules live in `examples/`.

Run from repo root:
- `python -m examples.adr0003_series_rps_and_fingers`

---

## Determinism expectations
- If you run the same match with the same seed and the same policies, you should get the same result.
- Replay should reproduce the final result based on recorded decision events.

---

## Workflow notes
- Slice numbers are global and monotonic.
- Avoid refactors unless explicitly allowed (refactor policy).
- Prefer module execution (`python -m ...`).
