#!/usr/bin/env bash
# =============================================================================
# verify.sh — thin wrapper around `uv run verify`.
#
# Forwards any extra args to verify.
#
# Usage:
#   bash scripts/verify.sh
#   bash scripts/verify.sh --quiet
#
# Windows / PowerShell users use scripts/verify.ps1.
# =============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

exec uv run verify "$@"
