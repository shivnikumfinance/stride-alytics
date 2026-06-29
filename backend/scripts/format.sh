#!/usr/bin/env bash
# =============================================================================
# format.sh — thin wrapper around `uv run format` (black).
#
# Usage:
#   bash scripts/format.sh           # black --check (CI mode)
#   bash scripts/format.sh --write   # apply formatting in place
#
# Windows / PowerShell users use scripts/format.ps1.
# =============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

exec uv run format "$@"
