# Backend — Coding Standards

**Layer:** `backend/**` (FastAPI / Python)
**Sibling docs:** [BACKEND-FOLDER-CONVENTIONS.md](./BACKEND-FOLDER-CONVENTIONS.md),
[../api-flow/API-FLOW.md](../api-flow/API-FLOW.md) (cross‑cutting endpoint ↔ service ↔ schema rule).

---

## 1. Naming

| Construct | Convention | Example |
|-----------|------------|---------|
| Class | PascalCase | `ScreenerService`, `GreeksCalculator` |
| Function / variable | snake_case | `calculate_greeks`, `user_portfolio` |
| Constant | UPPER_SNAKE_CASE | `API_BASE_URL`, `MAX_RETRIES`, `FREE_TIER_LIMIT` |
| Private | leading underscore | `_internal_helper`, `_cache_key` |
| Boolean | `is_` / `has_` / `can_` prefix | `is_loading`, `has_error`, `can_access` |
| Pydantic model | PascalCase, ends in `Request` / `Response` / noun | `LoginRequest`, `TickerEnvelope` |
| SQLAlchemy ORM | PascalCase, singular | `Portfolio`, `Trade`, `Option` |
| Module | snake_case | `screener_service.py`, `ticker_service.py` |
| Router variable | `router` (always) | `router = APIRouter()` |

## 2. Imports — required order

```python
# stdlib
from datetime import datetime
from typing import List, Optional

# third-party
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import structlog

# local
from app.database.client import supabase
from app.services.screener import ScreenerFilters
from app.api.v1.schemas.screener import ScreenerQuery
```

## 3. Service class / module pattern

```python
class ScreenerService:
    """Screener business logic. NO FastAPI imports."""

    def __init__(self, db_client):
        self.db = db_client

    async def filter_options(self, filters: dict) -> List[dict]:
        """Docstring: what + Args + Returns + Raises."""
        log.info("Filtering options", filters=filters)
        try:
            return await self._build_query(filters).execute()
        except Exception as exc:
            log.error("Filter failed", error=str(exc))
            raise
```

- Use `structlog` (`log = get_logger(__name__)`), never `print`.
- Functions either return plain types **or** Pydantic models — never a raw dict at the service boundary.
- Async by default; never block the event loop with sync I/O.

## 4. Pydantic schemas

- One file per resource under `app/api/v1/schemas/<name>.py`.
- Use `Field(...)` for descriptions on every public field.
- Re‑export every public model from `schemas/__init__.py`.
- Wire shape only — no DB / network calls in Pydantic validators.

## 5. Endpoints (thin adapter rule)

```python
@router.post("/run", response_model=ScreenerResponse)
async def run(payload: ScreenerQuery, current_user = Depends(get_current_user)):
    result = await run_screener(payload)        # delegate to service
    return ScreenerResponse(**result)           # wrap in response_model
```

- No `httpx`/`requests`/`aiohttp` in endpoint files.
- No business logic, no constants, no fallback data.
- All endpoints in `app/api/v1/endpoints/<name>.py`.
- Router prefix lives **only** in `app/api/v1/router.py` — endpoint files use relative paths.

## 6. Error handling

- Services raise **domain exceptions** (`class ScreenerError(Exception)`); the global `error_handler` middleware translates to HTTP.
- Do not raise `HTTPException` from inside `app/services/`.
- Always log the exception with `log.exception(...)` before re‑raising.

## 7. Tests

- File: `tests/test_<area>.py`.
- One pytest fixture per external dependency in `tests/conftest.py`.
- Mock `httpx.AsyncClient` and Supabase; never hit the network in unit tests.

## 8. Hard prohibitions

- ❌ `from fastapi import ...` inside `app/services/`.
- ❌ `print(...)` for logging.
- ❌ `from app.api.v1.endpoints import ...` inside `app/services/`.
- ❌ Bare `except:` without re‑raise.
- ❌ `# noqa` without a justification comment.

---

## 9. Before you finish — the verify chain

Run these commands locally before pushing a branch or opening a PR.
Each is implemented as a Python entry point (registered in
`pyproject.toml [project.scripts]`) and exposed via thin shell
wrappers for discoverability:

| What | Python entry point | Bash | PowerShell |
|------|--------------------|------|------------|
| Full gate (lint → mypy → smoke → tests) | `uv run verify` | `bash scripts/verify.sh` | `.\scripts\verify.ps1` |
| Ruff lint (pass `--fix` to autofix) | `uv run lint [--fix]` | `bash scripts/lint.sh` | `.\scripts\lint.ps1` |
| mypy on `app/` | `uv run typecheck` | `bash scripts/typecheck.sh` | `.\scripts\typecheck.ps1` |
| pytest (forward args) | `uv run test [-k ...]` | `bash scripts/test.sh` | `.\scripts\test.ps1` |
| black (pass `--write` to apply) | `uv run format [--write]` | `bash scripts/format.sh` | `.\scripts\format.ps1` |

The pre-commit hook runs the same chain (clean caches → ruff →
black --check → mypy → import smoke → pytest) so an editor that says
"OK" matches CI exactly. Any of these commands exit non‑zero if a
step fails — never suppress a verify failure with `--no-verify`.

`backend/.vscode/tasks.json` exposes the same commands as
Ctrl+Shift+B tasks; the default task is **Verify**.

Type stubs the project depends on (`scipy-stubs`, `types-python-jose`)
live in `[dependency-groups].dev` so a fresh `uv sync` installs them
automatically.

---

## See also

- [BACKEND-FOLDER-CONVENTIONS.md](./BACKEND-FOLDER-CONVENTIONS.md)
- [../api-flow/API-FLOW.md](../api-flow/API-FLOW.md)
- [../LAYERS/03-BACKEND-LAYER.md](../../LAYERS/03-BACKEND-LAYER.md)
