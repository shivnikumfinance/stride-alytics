"""``uv run format`` — black formatter.

Usage:
    uv run format           # black --check (CI mode, fails on drift)
    uv run format --write   # apply formatting in place
"""

from __future__ import annotations

import sys

from scripts._common import banner, run


def main() -> int:
    banner("black format")
    write = "--write" in sys.argv[1:]
    args = [sys.executable, "-m", "black", "."]
    if not write:
        args.insert(-1, "--check")
    return run(tuple(args))


if __name__ == "__main__":
    raise SystemExit(main())