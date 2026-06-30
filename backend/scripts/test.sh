#!/usr/bin/env bash
# =============================================================================
# test.sh — thin wrapper around `uv run test` (pytest).
#
# Forwards extra args to pytest, so `bash scripts/test.sh -k greeks -x` works.
#
# Usage:
#   bash scripts/test.sh
#   bash scripts/test.sh tests/test_services.py -v
#
# Windows / PowerShell users use scripts/test.ps1.
# =============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

exec uv run test "$@"
