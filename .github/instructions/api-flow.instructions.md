---
description: "StrideAlytics cross-cutting API flow rule — endpoint ↔ service ↔ schema separation and centralized URL construction. Fires whenever the edit touches API endpoints, services, schemas, axios/fetch calls, or wire-shape types. Layer-specific files handle layer-specific prohibitions."
applyTo: "{backend/app/api/**,backend/app/services/**,frontend/src/api/**,frontend/src/types/**,frontend/src/components/**,frontend/src/store/**,frontend/src/hooks/**,frontend/src/pages/**}"
---

# StrideAlytics — API Flow Rule (cross-cutting)

**Authoritative source:** [`docs/TECHNICAL/RULES/api-flow/API-FLOW.md`](../../docs/TECHNICAL/RULES/api-flow/API-FLOW.md).
**One‑page checklist:** [`docs/TECHNICAL/RULES/api-flow/ENDPOINT-CHECKLIST.md`](../../docs/TECHNICAL/RULES/api-flow/ENDPOINT-CHECKLIST.md).
**Rules index:** [`docs/TECHNICAL/RULES/README.md`](../../docs/TECHNICAL/RULES/README.md).

Read those docs before doing anything described below.

This instruction is the **cross‑cutting** companion to the per‑layer files:

- Backend edits → also see [`.github/instructions/backend.instructions.md`](./backend.instructions.md)
- Frontend edits → also see [`.github/instructions/frontend.instructions.md`](./frontend.instructions.md)
- Database edits → also see [`.github/instructions/database.instructions.md`](./database.instructions.md)

## When this rule applies

Any task that touches:

- `from fastapi import ...`, `@router.get`, `@router.post`, endpoint / service / schema files.
- `import axios`, `client.get`, `client.post`, `fetch(`, anything under `frontend/src/api/**` or `frontend/src/components/**` data fetching.
- Wire-shape types under `frontend/src/types/**` or `backend/app/api/v1/schemas/**`.
- `import.meta.env`, `VITE_API_URL`, `process.env.API_URL`.

## Mandatory checks before editing

1. **Have you read `docs/TECHNICAL/RULES/api-flow/API-FLOW.md`?** If not, read it first.
2. **Have you read the per-layer instruction for the file you're editing?** (backend / frontend / database)
3. **Are you touching the right layer?** See the layering table in `API-FLOW.md §1`.
4. **Are you duplicating a URL, env-var read, or schema definition that already lives elsewhere?** Stop and reuse the existing one.

## Cross-cutting prohibitions

### Backend
- ❌ `from fastapi import ...` inside `app/services/*.py`.
- ❌ `httpx` / `requests` / `aiohttp` calls inside `app/api/v1/endpoints/*.py`.
- ❌ Hard-coded external URLs inside `app/api/v1/endpoints/*.py`.
- ❌ Inline `class Foo(BaseModel)` or `class Foo:` inside an endpoint module.
- ❌ `app/api/v1/router.py` prefixing with `/api/v1/...` (the parent already owns it).

### Frontend
- ❌ `import.meta.env.VITE_API_URL` outside `src/api/client.ts`.
- ❌ Template-literal URL construction anywhere.
- ❌ Raw `fetch(...)` in components, stores, or hooks (use `src/api/endpoints.ts`).
- ❌ Inline `interface Foo {...}` inside `src/api/endpoints.ts` for a wire shape (move it to `src/types/<name>.ts`).
- ❌ Domain types living inside `api/endpoints.ts`.

## How to surface a conflict

If the user asks for something that violates the rule (e.g. "add a `fetch` to the Header component"), do not silently comply. Instead:

1. Quote the relevant section of `docs/TECHNICAL/RULES/api-flow/API-FLOW.md`.
2. Propose the layer-correct alternative.
3. Implement the alternative unless the user explicitly overrides after seeing the conflict.
