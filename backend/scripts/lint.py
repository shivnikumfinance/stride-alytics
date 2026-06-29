"""``uv run lint`` — ruff lint, fail fast.

Usage:
    uv run lint            # ruff check on backend/
    uv run lint --fix      # autofix what's safe, then re-check
"""

from __future__ import annotations

import sys

from scripts._common import banner, run


def main() -> int:
    banner("ruff lint")
    args = [sys.executable, "-m", "ruff", "check", "."]
    if "--fix" in sys.argv[1:]:
        args.insert(-1, "--fix")
    return run(tuple(args))


if __name__ == "__main__":
    raise SystemExit(main())