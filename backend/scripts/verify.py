"""``uv run verify`` — the full backend quality gate.

Mirrors the pre-commit hook so editor, CLI, and CI can never disagree.
Runs every step regardless of failures so you see all problems in a
single run.

Order matters — earlier steps are cheap and catch the most common
mistakes; later steps are slower and assume earlier ones passed.

  1. clean caches       — fast, ensures no stale .pyc
  2. ruff lint          — fast, catches unused imports + style
  3. mypy typecheck     — medium, catches real type bugs
  4. import smoke       — fast, catches missing Base / circular imports
  5. pytest             — slow, the actual contract test

Exit codes:
  0   — every step passed
  1   — at least one step failed (summary printed)
  2   — invocation error (e.g. cwd not backend/)
"""

from __future__ import annotations

import sys

from scripts._common import (
    banner,
    clean_caches,
    import_smoke,
    project_root,
    step,
)


def main() -> int:
    root = project_root()
    if not (root / "app").is_dir():
        print(
            f"!! verify must be run from the backend/ directory "
            f"(missing {root / 'app'})",
            file=sys.stderr,
        )
        return 2

    banner(f"verify  ({root})")
    results: list[tuple[str, bool]] = []

    # ``step()`` returns bool: True on success, False on failure.
    # The individual script ``main()`` functions return int (0 = success).

    # --- 1. clean caches ---
    results.append(("clean caches", step("clean caches", clean_caches)))

    # --- 2. ruff lint ---
    from scripts.lint import main as lint_main

    results.append(("ruff lint", step("ruff lint", lint_main)))

    # --- 3. mypy ---
    from scripts.typecheck import main as typecheck_main

    results.append(("mypy", step("mypy", typecheck_main)))

    # --- 4. import smoke ---
    results.append(("import smoke", step("import smoke", import_smoke)))

    # --- 5. pytest ---
    from scripts.test import main as test_main

    results.append(("pytest", step("pytest", test_main)))

    # --- summary ---
    banner("summary")
    width = max(len(name) for name, _ in results)
    failed = [name for name, ok in results if not ok]
    for name, ok in results:
        marker = "OK  " if ok else "FAIL"
        print(f"  {marker}  {name:<{width}}")
    print()
    if failed:
        print(f"!! {len(failed)} step(s) failed: {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"OK   all {len(results)} steps passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())