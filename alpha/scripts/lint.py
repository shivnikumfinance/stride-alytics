"""Alpha project lint script - runs ruff linter."""

import subprocess
import sys


def main() -> int:
    """Run ruff linter on the app directory."""
    print("Running linter...")
    result = subprocess.run(
        ["ruff", "check", "app"],
        cwd=".",
    )
    return result.returncode