"""Alpha project test script - runs pytest."""

import subprocess


def main() -> int:
    """Run pytest on the tests directory."""
    print("Running tests...")
    result = subprocess.run(
        ["pytest", "tests", "-v"],
        cwd=".",
    )
    return result.returncode