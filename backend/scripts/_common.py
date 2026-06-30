"""Shared helpers for the backend developer-experience scripts.

These are intentionally tiny — no third-party imports. Each script in
this directory has a ``main()`` and exits non-zero on failure so that
``uv run verify`` and the pre-commit hook can never disagree on
failure semantics.

Usage from a script:

    from scripts._common import banner, run, step

    def main() -> int:
        banner("Backend verify")
        if not step("ruff", lambda: run(("python", "-m", "ruff", "check", "."))):
            return 1
        return 0
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path


def project_root() -> Path:
    """Find the backend/ directory by walking up from CWD.

    Robust whether the script is run from source (``uv run lint``,
    ``python scripts/lint.py``) or from an installed wheel where
    ``scripts/_common.py`` lives in site-packages.
    """
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "app").is_dir() and (candidate / "pyproject.toml").is_file():
            return candidate
    # Fallback: assume CWD itself is the project root.
    return cwd


def banner(title: str) -> None:
    """Print a section header so multi-step runs are readable."""
    bar = "=" * max(0, 60 - len(title) - 2)
    print(f"\n=== {title} {bar}", flush=True)


def run(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> int:
    """Run ``cmd`` and stream its output. Returns the exit code.

    When ``check=True`` (default), a non-zero exit raises
    ``SystemExit``. When ``check=False``, the caller is expected to
    inspect the returned code.
    """
    printable = " ".join(cmd)
    print(f"$ {printable}", flush=True)
    completed = subprocess.run(  # noqa: S603 — intentional subprocess
        list(cmd),
        cwd=cwd or project_root(),
        env={**os.environ, **(env or {})},
        check=False,
    )
    if check and completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return completed.returncode


def step(name: str, fn: Callable[[], int]) -> bool:
    """Run a verification step. Returns True on success, False on failure.

    A failing step is logged but does NOT raise — the caller decides
    whether to abort the chain (``return 1``) or continue collecting
    failures. This is how ``verify`` shows "ruff: FAIL, mypy: FAIL"
    in a single run instead of stopping at the first failure.
    """
    banner(name)
    try:
        rc = fn()
    except SystemExit as exc:
        rc = int(exc.code) if exc.code is not None else 1
    except Exception as exc:  # noqa: BLE001 — last-resort guard for the chain
        print(f"!! {name} raised {type(exc).__name__}: {exc}", file=sys.stderr)
        rc = 1
    status = "OK " if rc == 0 else "FAIL"
    print(f"-- {status}  {name} (exit {rc})", flush=True)
    return rc == 0


def clean_caches() -> int:
    """Remove __pycache__ + ruff/pytest/mypy caches. Mirrors pre-commit step."""
    patterns = ("__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache")
    removed = 0
    for pattern in patterns:
        for path in project_root().rglob(pattern):
            if path.is_dir():
                import shutil

                shutil.rmtree(path, ignore_errors=True)
                removed += 1
    print(f"removed {removed} cache directories", flush=True)
    return 0


def import_smoke() -> int:
    """Verify the FastAPI app + every public service import cleanly.

    This is the same check the pre-commit hook runs. Catches the
    "declarative_base() missing" / circular import / typo class of
    bug before the test suite even starts.
    """
    code = "import app.main, app.services, app.api.v1.router;" " print('OK: backend imports clean')"
    return run((sys.executable, "-c", code))


# Kept as an alias for back-compat with callers that already use the name.
BACKEND_ROOT = project_root()
