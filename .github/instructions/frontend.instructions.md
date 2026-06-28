---
description: "StrideAlytics frontend rules (React / Vite / TypeScript) — applies to frontend/src/**. Reads docs/TECHNICAL/RULES/frontend/* and the cross-cutting api-flow/API-FLOW.md."
applyTo: "frontend/src/**"
---

# StrideAlytics — Frontend Rules

**Authoritative sources (read before editing):**
- [`docs/TECHNICAL/RULES/frontend/FRONTEND-CODING-STANDARDS.md`](../../docs/TECHNICAL/RULES/frontend/FRONTEND-CODING-STANDARDS.md)
- [`docs/TECHNICAL/RULES/frontend/FRONTEND-FOLDER-CONVENTIONS.md`](../../docs/TECHNICAL/RULES/frontend/FRONTEND-FOLDER-CONVENTIONS.md)
- [`docs/TECHNICAL/RULES/frontend/FRONTEND-DATA-FLOW.md`](../../docs/TECHNICAL/RULES/frontend/FRONTEND-DATA-FLOW.md)
- [`docs/TECHNICAL/RULES/api-flow/API-FLOW.md`](../../docs/TECHNICAL/RULES/api-flow/API-FLOW.md) — cross-cutting

If a planned change conflicts with any of the above, **stop and surface the conflict before writing code**.

## Hard prohibitions (the agent MUST refuse)

- ❌ `import.meta.env.VITE_API_URL` outside `src/api/client.ts`.
- ❌ Template-literal URL construction (`` `${API_BASE}/api/v1/foo` ``) anywhere.
- ❌ Raw `fetch(...)` in components, stores, or hooks (use `src/api/endpoints.ts`).
- ❌ Inline `interface Foo {...}` inside `src/api/endpoints.ts` for a wire shape (move to `src/types/<name>.ts`).
- ❌ Domain types living inside `api/endpoints.ts`.
- ❌ `any` (use `unknown` + narrowing or a proper type).

## Adding a new frontend endpoint — file checklist

1. `frontend/src/types/<name>.ts` mirroring backend Pydantic 1:1 + `export *` from `types/index.ts`.
2. `frontend/src/api/endpoints.ts` — add a `xApi` block that uses `client`.
3. If polling / caching / fallback is needed → `frontend/src/api/services/<name>.service.ts`.
4. Component / store / hook imports the service or wrapper — never raw `fetch`.

## Reference docs

- [`docs/TECHNICAL/LAYERS/01-FRONTEND-LAYER.md`](../../docs/TECHNICAL/LAYERS/01-FRONTEND-LAYER.md)
- [`docs/TECHNICAL/RULES/api-flow/API-FLOW.md`](../../docs/TECHNICAL/RULES/api-flow/API-FLOW.md)
- [`docs/TECHNICAL/RULES/README.md`](../../docs/TECHNICAL/RULES/README.md)

## Before declaring the task done — verification checklist

If the change **added, moved, or renamed** any file under `frontend/src/**`,
you MUST run these checks before saying "done". The pre-commit hook runs them
too, but don't wait for it — catch the issue before staging.

```bash
cd frontend
npm run clean         # wipe dist/, .vite/, node_modules/.cache, tsconfig.tsbuildinfo
npm run type-check    # tsc --noEmit
npm run build:prod    # clean + tsc + vite build (production)
```

Or in one shot: `npm run prebuild:prod && npm run build:prod`.
The pre-commit hook runs the same sequence on every commit.

Both must exit `0`. If either fails:

1. Read the error carefully — it points at the file/line.
2. If `tsc` says it's fine but Pylance complains in the editor, **trust tsc**
   and restart the TS server (`Ctrl+Shift+P` → "TypeScript: Restart TS Server").
3. If `tsc` agrees with Pylance, fix the actual error before declaring done.

Do **not**:

- ❌ Delete a working import just because Pylance shows a phantom `Cannot find module` error. Restart the TS server first.
- ❌ Add a new file and immediately commit it without running `npm run type-check` + `npm run build:prod`.
- ❌ Use `// @ts-ignore` or `as any` to silence type errors — fix the type.

See [docs/TECHNICAL/RULES/frontend/FRONTEND-CODING-STANDARDS.md § 8](../../docs/TECHNICAL/RULES/frontend/FRONTEND-CODING-STANDARDS.md) for the full rationale.
