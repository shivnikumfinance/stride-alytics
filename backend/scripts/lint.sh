#!/usr/bin/env bash
# =============================================================================
# lint.sh — thin wrapper around `uv run lint`.
#
# Usage:
#   bash scripts/lint.sh           # ruff check
#   bash scripts/lint.sh --fix     # auto-fix what's safe
#
# Windows / PowerShell users use scripts/lint.ps1.
# =============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

exec uv run lint "$@"
