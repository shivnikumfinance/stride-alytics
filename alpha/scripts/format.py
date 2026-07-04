"""Alpha project format script - runs ruff formatter and black."""

import subprocess


def main() -> int:
    """Run ruff format and black on the app directory."""
    print("Running formatters...")
    result1 = subprocess.run(
        ["ruff", "format", "app"],
        cwd=".",
    )
    result2 = subprocess.run(
        ["black", "app"],
        cwd=".",
    )
    return max(result1.returncode, result2.returncode)