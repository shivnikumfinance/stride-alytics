---
description: "StrideAlytics backend rules (FastAPI / Python) — applies to backend/**. Reads docs/TECHNICAL/RULES/backend/* and the cross-cutting api-flow/API-FLOW.md."
applyTo: "backend/**"
---

# StrideAlytics — Backend Rules

**Authoritative sources (read before editing):**
- [`docs/TECHNICAL/RULES/backend/BACKEND-CODING-STANDARDS.md`](../../docs/TECHNICAL/RULES/backend/BACKEND-CODING-STANDARDS.md)
- [`docs/TECHNICAL/RULES/backend/BACKEND-FOLDER-CONVENTIONS.md`](../../docs/TECHNICAL/RULES/backend/BACKEND-FOLDER-CONVENTIONS.md)
- [`docs/TECHNICAL/RULES/backend/BACKEND-DATA-FLOW.md`](../../docs/TECHNICAL/RULES/backend/BACKEND-DATA-FLOW.md)
- [`docs/TECHNICAL/RULES/api-flow/API-FLOW.md`](../../docs/TECHNICAL/RULES/api-flow/API-FLOW.md) — cross-cutting

If a planned change conflicts with any of the above, **stop and surface the conflict before writing code**.

## Hard prohibitions (the agent MUST refuse)

- ❌ `from fastapi import ...` inside `app/services/*.py`.
- ❌ `httpx` / `requests` / `aiohttp` calls inside `app/api/v1/endpoints/*.py`.
- ❌ Hard-coded external URLs inside `app/api/v1/endpoints/*.py`.
- ❌ Inline `class Foo(BaseModel)` or `class Foo:` inside an endpoint module.
- ❌ `app/api/v1/router.py` prefixing with `/api/v1/...` (the parent already owns it).
- ❌ `print(...)` for logging — use `log = get_logger(__name__)`.
- ❌ Bare `except:` without re-raise.

## Adding a new backend resource — file checklist

1. `backend/app/models/<name>.py` (SQLAlchemy ORM) + re-export from `models/__init__.py`.
2. `backend/app/api/v1/schemas/<name>.py` (Pydantic) + re-export from `schemas/__init__.py`.
3. `backend/app/services/<name>.py` (pure business logic) + re-export from `services/__init__.py`.
4. `backend/app/api/v1/endpoints/<name>.py` (thin adapter) + re-export from `endpoints/__init__.py`.
5. Register in `backend/app/api/v1/router.py` with `include_router(...)` and correct `prefix=` / `tags=`.

## Reference docs

- [`docs/TECHNICAL/LAYERS/03-BACKEND-LAYER.md`](../../docs/TECHNICAL/LAYERS/03-BACKEND-LAYER.md)
- [`docs/TECHNICAL/RULES/api-flow/API-FLOW.md`](../../docs/TECHNICAL/RULES/api-flow/API-FLOW.md)
- [`docs/TECHNICAL/RULES/README.md`](../../docs/TECHNICAL/RULES/README.md)
