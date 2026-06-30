"""``uv run typecheck`` — mypy on the application package only.

Tests intentionally not type-checked here because they require
fixtures that fight mypy. Add ``tests`` to the targets in pyproject
when coverage of test code is desired.
"""

from __future__ import annotations

import sys

from scripts._common import banner, run


def main() -> int:
    banner("mypy type check")
    return run((sys.executable, "-m", "mypy", "app"))


if __name__ == "__main__":
    raise SystemExit(main())
