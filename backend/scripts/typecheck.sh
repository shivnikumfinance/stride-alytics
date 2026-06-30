#!/usr/bin/env bash
# =============================================================================
# typecheck.sh — thin wrapper around `uv run typecheck` (mypy).
#
# Usage:
#   bash scripts/typecheck.sh
#
# Windows / PowerShell users use scripts/typecheck.ps1.
# =============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

exec uv run typecheck "$@"
