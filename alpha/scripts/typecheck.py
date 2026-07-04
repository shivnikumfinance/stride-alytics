"""Alpha project typecheck script - runs mypy."""

import subprocess


def main() -> int:
    """Run mypy type checker on the app directory."""
    print("Running typecheck...")
    result = subprocess.run(
        ["mypy", "app"],
        cwd=".",
    )
    return result.returncode