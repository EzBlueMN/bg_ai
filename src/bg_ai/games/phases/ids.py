from __future__ import annotations

# S22:
# PhaseId is intentionally a simple wire-safe identifier.
# We keep it as `str` so phases remain easy to serialize + compare.
PhaseId = str
