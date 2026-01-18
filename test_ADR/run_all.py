from __future__ import annotations

import argparse
import importlib
import re
from pathlib import Path
from types import ModuleType
from typing import List, Tuple


def _test_adr_dir() -> Path:
    return Path(__file__).resolve().parent


def _find_adr_modules() -> List[Tuple[int, str]]:
    """
    Finds test_ADR/ADRXXXX.py files, returns sorted list of (num, module_name).
    """
    items: List[Tuple[int, str]] = []
    pat = re.compile(r"^ADR(\d{4})\.py$")
    for p in _test_adr_dir().iterdir():
        m = pat.match(p.name)
        if not m:
            continue
        num = int(m.group(1))
        items.append((num, f"test_ADR.ADR{m.group(1)}"))
    return sorted(items, key=lambda t: t[0])


def _is_deprecated(mod: ModuleType) -> bool:
    return getattr(mod, "STATUS", "active").strip().lower() == "deprecated"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-deprecated", action="store_true", default=False)
    ap.add_argument("--continue-on-failure", action="store_true", default=False)
    args = ap.parse_args()

    failures: List[str] = []

    for _, module_name in _find_adr_modules():
        mod = importlib.import_module(module_name)

        if _is_deprecated(mod) and not args.include_deprecated:
            print(f"Skipping {module_name} (deprecated)")
            continue

        print("")
        print("=" * 60)
        print(f"RUN {module_name}")
        print("=" * 60)

        try:
            if not hasattr(mod, "main"):
                raise RuntimeError(f"{module_name} has no main()")
            mod.main()  # type: ignore[attr-defined]
        except Exception as e:
            failures.append(f"{module_name}: {e}")
            print(f"{module_name} FAILED: {e}")
            if not args.continue_on_failure:
                raise

    if failures:
        raise SystemExit("Failures:\n" + "\n".join(failures))

    print("")
    print("All ADR runners completed successfully.")


if __name__ == "__main__":
    main()
