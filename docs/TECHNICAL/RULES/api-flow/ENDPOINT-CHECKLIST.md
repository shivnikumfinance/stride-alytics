# Endpoint Checklist — Adding a New API Resource

**One‑page checklist pulled from [API-FLOW.md](./API-FLOW.md).** Use this
during PR review or when planning a new resource.

---

## Backend (5 files)

- [ ] `backend/app/models/<name>.py` — SQLAlchemy ORM
- [ ] `backend/app/api/v1/schemas/<name>.py` — Pydantic models
- [ ] `backend/app/services/<name>.py` — pure business logic (no `fastapi`)
- [ ] `backend/app/api/v1/endpoints/<name>.py` — thin adapter (no `httpx`)
- [ ] `backend/app/api/v1/router.py` — register with `include_router(...)`

Re‑exports:
- [ ] `models/__init__.py`
- [ ] `schemas/__init__.py`
- [ ] `services/__init__.py`
- [ ] `endpoints/__init__.py`

## Frontend (3 files)

- [ ] `frontend/src/types/<name>.ts` — wire shape mirroring backend 1:1
- [ ] `frontend/src/api/endpoints.ts` — `xApi` block using `client`
- [ ] Optional: `frontend/src/api/services/<name>.service.ts` for polling/cache

Re‑exports:
- [ ] `frontend/src/types/index.ts` — `export * from "./<name>"`

## Common violations — quick reference

| Bad | Fix |
|-----|-----|
| `httpx` inside `endpoints/` | Move into `services/` |
| `BaseModel` declared inline in endpoint | Move into `schemas/` |
| `import.meta.env` outside `client.ts` | Delete; use `client` |
| `fetch(...)` in a component | Use `xApi` |
| Wire shape `interface` in `endpoints.ts` | Move into `types/<name>.ts` |
| `/api/v1/...` in `include_router(prefix=...)` | Drop the prefix |

---

## See also

- [API-FLOW.md](./API-FLOW.md) — full rule doc
- [../backend/BACKEND-FOLDER-CONVENTIONS.md](../backend/BACKEND-FOLDER-CONVENTIONS.md)
- [../frontend/FRONTEND-FOLDER-CONVENTIONS.md](../frontend/FRONTEND-FOLDER-CONVENTIONS.md)
