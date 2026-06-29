"""``uv run test`` — pytest with sensible defaults.

Forwards any extra args to pytest, so ``uv run test -k greeks -x``
works as expected.
"""

from __future__ import annotations

import sys

from scripts._common import banner, run


def main() -> int:
    banner("pytest")
    args = [sys.executable, "-m", "pytest", "tests", *sys.argv[1:]]
    return run(tuple(args))


if __name__ == "__main__":
    raise SystemExit(main())