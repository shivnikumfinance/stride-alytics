"""``uv run dev`` — watch backend files and re-run verify on change.

A lightweight, dependency-free file watcher that re-runs the full
``verify`` pipeline whenever a tracked backend file changes. Use this
while iterating so that lint / type-check / test / coverage drift
shows up the moment you save, before CI yells at you.

Why not a heavyweight tool? We already use ``watchdog`` is overkill
for a single-tree watcher with debounce; stdlib is enough. This file
imports only from the standard library and ``scripts.verify`` so we
stay aligned with the rest of the verify chain.

Usage:

    uv run dev              # watch backend/, run verify on change
    uv run dev --once       # single run, then exit (CI smoke)
    uv run dev --quiet      # suppress per-run banner (only show failures)

Environment:

    DEV_DEBOUNCE_MS    override default 750 ms debounce (lower = snappier,
                       higher = fewer redundant runs during multi-file
                       refactors)
"""

from __future__ import annotations

import os
import sys
import time
from collections.abc import Iterable
from pathlib import Path

from scripts._common import project_root

# ---------------------------------------------------------------------------
# File-scope configuration
# ---------------------------------------------------------------------------

# Directories we watch. Anything outside is ignored even if it's under
# the backend/ root (caches, virtualenv, coverage artifacts, etc.).
_WATCH_DIRS: tuple[str, ...] = ("app", "scripts", "tests")

# Suffixes that should trigger a verify re-run. Adding a new code-bearing
# file type? Add it here so the watcher knows to react.
_WATCH_SUFFIXES: tuple[str, ...] = (
    ".py",  # Python source — primary trigger
    ".sql",  # Schema / function / view files
    ".toml",  # pyproject.toml changes (e.g. dependency or mypy config)
    ".txt",  # requirements*.txt if present
)

# Files at the project root that should also trigger a re-run, even
# though they are not under any _WATCH_DIRS.
_ROOT_WATCH_FILES: tuple[str, ...] = (
    "pyproject.toml",
    "uv.lock",
    "Dockerfile",
    "render.yaml",
)

# Paths to always exclude — caches, virtualenv, coverage, build output.
_EXCLUDE_SUBSTRINGS: tuple[str, ...] = (
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".coverage",
    "dist",
    "build",
    ".git",
)

# Default debounce window in milliseconds. 750 ms is long enough to
# coalesce a multi-file refactor save into a single run, short enough
# to feel instant to the developer.
_DEFAULT_DEBOUNCE_MS = 750


def _iter_watch_paths(root: Path) -> Iterable[Path]:
    """Yield every file under ``root`` that the watcher should react to.

    Walks the watch directories once at startup and at every poll cycle.
    This is O(n) per scan but n is small (<10k files for the current
    backend) and avoids the inotify event-queue pitfalls on Windows.
    """
    for rel in _WATCH_DIRS:
        base = root / rel
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            rel_str = str(path)
            if any(token in rel_str for token in _EXCLUDE_SUBSTRINGS):
                continue
            if path.suffix not in _WATCH_SUFFIXES:
                # Root-level files (e.g. pyproject.toml) are matched by
                # _ROOT_WATCH_FILES below; for nested files we only
                # react to known code-bearing suffixes.
                continue
            yield path

    # Root-level files: only watch the explicitly allowlisted names.
    for name in _ROOT_WATCH_FILES:
        candidate = root / name
        if candidate.is_file():
            yield candidate


def _snapshot(root: Path) -> dict[Path, float]:
    """Return ``{path: mtime}`` for every watched file.

    Using ``mtime`` instead of file contents keeps each scan cheap and
    avoids reading Python source into memory just to compare it.
    """
    return {p: p.stat().st_mtime for p in _iter_watch_paths(root)}


def _print_banner(message: str) -> None:
    """Print a watcher-style banner to stdout (always visible)."""
    print(f"\n>>> {message}", flush=True)


def _run_verify(quiet: bool) -> int:
    """Run ``scripts.verify.main()`` in-process and return its exit code.

    In-process is intentional — re-importing subprocess is wasteful and
    we'd lose the colored banner. The verify script already handles its
    own output, so we just need to forward the exit code.

    ``scripts.verify`` forwards its own ``sys.argv[1:]`` to pytest, so
    we must scrub dev's own flags (``--once``, ``--quiet``) out of
    ``sys.argv`` before delegating. Otherwise ``uv run dev --once``
    would pass ``--once`` through to pytest.
    """
    import contextlib
    import io

    from scripts import verify

    dev_only_flags = {"--once", "--quiet", "-h", "--help"}
    saved_argv = sys.argv[:]
    sys.argv = [sys.argv[0]] + [a for a in sys.argv[1:] if a not in dev_only_flags]
    try:
        if quiet:
            with (
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                return int(verify.main())
        return int(verify.main())
    finally:
        sys.argv = saved_argv


def _watch(debounce_ms: int, quiet: bool) -> int:
    """Run the watch loop. Returns the exit code of the last verify run."""
    root = project_root()
    _print_banner(f"watching {root}  (Ctrl+C to stop)")
    _print_banner("initial verify run")
    last_rc = _run_verify(quiet=quiet)
    _print_banner(
        "ready — save a file to re-run"
        if last_rc == 0
        else "ready — failures present, save a file to re-run"
    )

    snapshot = _snapshot(root)
    last_change_at: float | None = None

    # Poll interval — 250 ms gives a snappy feel without burning CPU.
    poll_interval_s = 0.25
    debounce_s = debounce_ms / 1000.0

    try:
        while True:
            time.sleep(poll_interval_s)
            current = _snapshot(root)
            if current == snapshot:
                # Nothing changed; reset the debounce timer if we were
                # mid-wait so we don't fire spuriously.
                last_change_at = None
                continue
            snapshot = current
            now = time.monotonic()
            if last_change_at is None:
                last_change_at = now
                continue
            # Wait until the debounce window has elapsed since the FIRST
            # change in the current burst. This coalesces a multi-file
            # save into one verify run.
            if now - last_change_at < debounce_s:
                continue
            last_change_at = None
            _print_banner("change detected — re-running verify")
            last_rc = _run_verify(quiet=quiet)
            _print_banner(
                "ready — save a file to re-run"
                if last_rc == 0
                else "ready — failures present, save a file to re-run"
            )
    except KeyboardInterrupt:
        _print_banner("stopped")
        return last_rc


def main() -> int:
    """CLI entry point. Parses a minimal flag set without argparse so
    we keep zero runtime dependencies."""
    args = sys.argv[1:]
    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0
    once = "--once" in args
    quiet = "--quiet" in args or os.environ.get("DEV_QUIET") == "1"

    debounce_ms = _DEFAULT_DEBOUNCE_MS
    env_override = os.environ.get("DEV_DEBOUNCE_MS")
    if env_override and env_override.isdigit():
        debounce_ms = int(env_override)

    root = project_root()
    if not (root / "app").is_dir():
        print(
            f"!! dev must be run from the backend/ directory (missing {root / 'app'})",
            file=sys.stderr,
        )
        return 2

    if once:
        _print_banner("single-run mode")
        return _run_verify(quiet=quiet)

    return _watch(debounce_ms=debounce_ms, quiet=quiet)


if __name__ == "__main__":
    raise SystemExit(main())
