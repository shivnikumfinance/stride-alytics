"""Alpha project verify script - runs all verification steps."""

import subprocess


def main() -> int:
    """Run all verification steps: lint, typecheck, test."""
    print("Running verify (lint, typecheck, test)...")
    
    lint_result = subprocess.run(["uv", "run", "lint"], cwd=".", capture_output=True)
    if lint_result.returncode != 0:
        print("Lint failed")
        return lint_result.returncode
    
    typecheck_result = subprocess.run(["uv", "run", "typecheck"], cwd=".", capture_output=True)
    if typecheck_result.returncode != 0:
        print("Typecheck failed")
        return typecheck_result.returncode
    
    test_result = subprocess.run(["uv", "run", "test"], cwd=".", capture_output=True)
    if test_result.returncode != 0:
        print("Tests failed")
        return test_result.returncode
    
    print("All verification steps passed!")
    return 0