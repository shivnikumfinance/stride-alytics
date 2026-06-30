# Backend — Folder Conventions

**Layer:** `backend/**` (FastAPI / Python)
**Sibling docs:** [BACKEND-CODING-STANDARDS.md](./BACKEND-CODING-STANDARDS.md),
[../api-flow/API-FLOW.md](../api-flow/API-FLOW.md).

---

## 1. Canonical layout

```
backend/
├── app/
│   ├── main.py                       # FastAPI app factory + lifespan
│   ├── config.py                     # Settings (pydantic-settings)
│   ├── database.py                   # SQLAlchemy Base + engine
│   │
│   ├── api/
│   │   ├── middleware/               # auth, logging, error_handler
│   │   └── v1/
│   │       ├── router.py             # ONLY place that sets prefix="/api/v1"
│   │       ├── endpoints/            # one file per resource, exposes `router`
│   │       │   └── __init__.py       # re-export every endpoint module
│   │       └── schemas/              # one file per resource, Pydantic models
│   │           └── __init__.py       # re-export every model
│   │
│   ├── services/                     # pure business logic — no FastAPI imports
│   │   └── __init__.py               # re-export public symbols
│   │
│   ├── models/                       # SQLAlchemy ORM — DB shape only
│   │   └── __init__.py               # re-export every model
│   │
│   └── utils/                        # logger, validators, helpers, constants
│
├── tests/                            # pytest, mirrors app/ structure
├── scripts/                          # developer-experience entry points +
│   │                                 # cross-platform wrappers (.sh + .ps1)
├── pyproject.toml
└── .env.example
```

## 2. Adding a new resource — file checklist

1. `app/models/<name>.py` — SQLAlchemy ORM. Re‑export from `models/__init__.py`.
2. `app/api/v1/schemas/<name>.py` — Pydantic models. Re‑export from `schemas/__init__.py`.
3. `app/services/<name>.py` — pure business logic. Re‑export from `services/__init__.py`.
4. `app/api/v1/endpoints/<name>.py` — thin adapter exposing `router`.
   Re‑export from `endpoints/__init__.py`.
5. Register the endpoint in `app/api/v1/router.py` with the right `prefix=` and `tags=`.

## 3. Naming rules

| Thing | Rule | Example |
|-------|------|---------|
| Folder | lowercase, snake_case for multi‑word | `app/api/v1/endpoints/` |
| File | snake_case | `ticker_service.py` |
| ORM class | PascalCase, singular | `Portfolio` |
| Pydantic | PascalCase | `TickerEnvelope`, `LoginRequest` |
| Test file | `test_<area>.py` | `test_screener.py` |

## 4. Hard prohibitions

- ❌ `endpoints/` modules containing `httpx`, business logic, or hard‑coded URLs.
- ❌ `services/` modules importing `from fastapi import ...`.
- ❌ Duplicating the URL prefix `/api/v1` outside `api/v1/router.py`.
- ❌ Putting Pydantic models in `models/` or ORM models in `schemas/`.

## 5. The `scripts/` folder

Both one‑off CLIs **and** the developer verify chain live here:

```
scripts/
├── _common.py                # shared helpers (banner, run, step, project_root)
├── lint.py                   # `uv run lint`
├── format.py                 # `uv run format`
├── typecheck.py              # `uv run typecheck`
├── test.py                   # `uv run test`
├── verify.py                 # `uv run verify`
├── migrate-to-uv.sh          # legacy one-shot (unchanged)
├── migrate-to-uv.ps1
├── verify.{sh,ps1}           # thin wrapper — delegates to `uv run verify`
├── lint.{sh,ps1}
├── format.{sh,ps1}
├── typecheck.{sh,ps1}
└── test.{sh,ps1}
```

Every script exposes a `main() -> int` returning the process exit code
so they can be composed into `verify`. The shell wrappers exist only
for discoverability — they always delegate to the Python entry point
so there is one source of truth.

When adding a new developer command: add `_common.py`'s helpers,
drop a `<name>.py`, register it in `pyproject.toml
[project.scripts]`, then add the matching `<name>.{sh,ps1}` shells.

---

## See also

- [BACKEND-CODING-STANDARDS.md](./BACKEND-CODING-STANDARDS.md)
- [../api-flow/API-FLOW.md](../api-flow/API-FLOW.md) §2 — backend checklist
- [../../03-FOLDER-STRUCTURE.md](../../03-FOLDER-STRUCTURE.md)
