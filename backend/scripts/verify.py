"""``uv run verify`` — the full backend quality gate.

Mirrors the pre-commit hook so editor, CLI, and CI can never disagree.
Runs every step regardless of failures so you see all problems in a
single run.

Order matters — earlier steps are cheap and catch the most common
mistakes; later steps are slower and assume earlier ones passed.

  1. clean caches       — fast, ensures no stale .pyc
  2. ruff lint          — fast, catches unused imports + style
  3. black --check      — fast, catches formatting drift
  4. mypy --strict      — medium, catches real type bugs
  5. import smoke       — fast, catches missing Base / circular imports
  6. pytest + coverage  — slow, contract test + coverage gate

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
    run,
    step,
)


def _pytest_with_coverage() -> int:
    """Run pytest with coverage enabled. Coverage fails the run if under
    ``[tool.coverage.report] fail_under``.

    Uses the project's pyproject.toml — no extra config file required.
    Forward any extra args (e.g. ``-k greeks``) to pytest by appending
    to ``sys.argv``.
    """
    args = [
        sys.executable,
        "-m",
        "pytest",
        "tests",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-config=pyproject.toml",
        *sys.argv[1:],
    ]
    return run(tuple(args))


def main() -> int:
    root = project_root()
    if not (root / "app").is_dir():
        print(
            f"!! verify must be run from the backend/ directory " f"(missing {root / 'app'})",
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

    # --- 3. black format check ---
    from scripts.format import main as format_main

    results.append(("black --check", step("black --check", format_main)))

    # --- 4. mypy (strict) ---
    from scripts.typecheck import main as typecheck_main

    results.append(("mypy --strict", step("mypy --strict", typecheck_main)))

    # --- 5. import smoke ---
    results.append(("import smoke", step("import smoke", import_smoke)))

    # --- 6. pytest + coverage ---
    results.append(
        (
            "pytest + coverage",
            step("pytest + coverage", _pytest_with_coverage),
        )
    )

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
