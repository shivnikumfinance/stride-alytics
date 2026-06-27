#!/usr/bin/env bash
# =============================================================================
# migrate-to-uv.sh
#
# One-shot script to migrate a legacy requirements.txt project to
# pyproject.toml managed by uv (Astral).
#
# Prerequisites:
#   - uv installed (pip install uv or https://docs.astral.sh/uv/#installation)
#   - An existing backend/ directory with requirements.txt
#
# Usage:
#   cd backend && bash scripts/migrate-to-uv.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "=== Checking prerequisites ==="
if ! command -v uv &> /dev/null; then
    echo "ERROR: 'uv' not found. Install it first:"
    echo "  pip install uv"
    echo "  or visit https://docs.astral.sh/uv/#installation"
    exit 1
fi
echo "uv version: $(uv --version)"

if [ ! -f "requirements.txt" ]; then
    echo "ERROR: No requirements.txt found in $(pwd)"
    exit 1
fi

echo ""
echo "=== 1. Detected dependencies from requirements.txt ==="
cat requirements.txt

echo ""
echo "=== 2. Ensuring pyproject.toml exists ==="
if [ ! -f "pyproject.toml" ]; then
    echo "pyproject.toml not found — creating one from template..."
    cat > pyproject.toml << 'PYPROJECT'
[project]
name = "stride-alytics-backend"
version = "0.1.0"
description = "StrideAlytics platform — backend API"
requires-python = ">=3.10"
dependencies = []

[dependency-groups]
dev = []

[tool.hatch.build.targets.wheel]
packages = ["app/"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
PYPROJECT
    echo "pyproject.toml created."
else
    echo "pyproject.toml already exists — skipping creation."
fi

echo ""
echo "=== 3. Generating uv.lock (resolving dependencies) ==="
uv lock
echo "uv.lock generated successfully."

echo ""
echo "=== 4. Syncing virtual environment ==="
uv sync --frozen --no-dev
echo "All packages installed."

echo ""
echo "=== 5. Verification ==="
echo "Checking that the app can import its main module..."
uv run python -c "from app.main import app; print('✓ FastAPI app loaded successfully')"

echo ""
echo "=== 6. Cleanup ==="
if [ -f "requirements.txt" ]; then
    echo "Removing legacy requirements.txt..."
    rm requirements.txt
    echo "✓ requirements.txt deleted."
fi

echo ""
echo "============================================"
echo " Migration complete!                         "
echo "--------------------------------------------"
echo " New files:                                  "
echo "   pyproject.toml  — project config + deps   "
echo "   uv.lock          — deterministic lock     "
echo "   .venv/           — virtual environment    "
echo "                                              "
echo " Removed:                                    "
echo "   requirements.txt  — (legacy, deleted)      "
echo "                                              "
echo " Next steps:                                 "
echo "   cd backend                                 "
echo "   uv run uvicorn app.main:app --reload       "
echo "============================================"