# StrideAlytics — Rules

**Authoritative source for coding & layer rules. Layer-scoped so each Copilot
instruction only loads the rules it needs.**

If you're an agent: read the file whose `applyTo` glob matched your edit.
If you're a human: pick the doc for the layer you're touching (or the
cross-cutting `api-flow/` folder for end-to-end API changes).

---

## Folder map

```
docs/TECHNICAL/RULES/
├── README.md                                ← you are here
│
├── api-flow/                                ← cross-cutting: backend ⇄ frontend contract
│   ├── API-FLOW.md                          endpoint ↔ service ↔ schema layering,
│   │                                          URL rules, response envelope, auth,
│   │                                          pagination, versioning, data contracts
│   ├── ENDPOINT-CHECKLIST.md                one-page checklist for adding a resource
│   └── DATA-FLOW-RULES.md                   ⚠ DEPRECATED — content folded into the
│                                              per-layer docs. See banner at top of file.
│                                              Future TODOs tracked at the bottom.
│
├── backend/                                 ← applies to backend/**
│   ├── BACKEND-CODING-STANDARDS.md          Python/FastAPI naming, imports, services
│   ├── BACKEND-FOLDER-CONVENTIONS.md        backend layout rules
│   └── BACKEND-DATA-FLOW.md                 backend request/response patterns,
│                                              transactions, PII, auth flow
│
├── frontend/                                ← applies to frontend/src/**
│   ├── FRONTEND-CODING-STANDARDS.md         TS/React/Vite/Tailwind naming, imports, hooks
│   ├── FRONTEND-FOLDER-CONVENTIONS.md       frontend layout rules
│   └── FRONTEND-DATA-FLOW.md                frontend data fetching, caching, retries,
│                                              rate-limit headers
│
├── database/                                ← applies to database/**
│   ├── DATABASE-CODING-STANDARDS.md         SQL style, naming, numeric data
│   ├── DATABASE-FOLDER-CONVENTIONS.md       migrations/rls/seeds layout
│   ├── DATABASE-MIGRATIONS.md               migration ordering + rollbacks
│   └── DATABASE-RLS-POLICIES.md             RLS authoring rules
│
└── mobile/                                  ← planned (parity TODO)
    └── MOBILE-PARITY-TODO.md                mobile/** rules + Copilot instruction — tracked here
```

## Picking the right doc

| You're editing… | Read first |
|-----------------|------------|
| `backend/app/api/v1/**` | [api-flow/API-FLOW.md](api-flow/API-FLOW.md), [backend/BACKEND-CODING-STANDARDS.md](backend/BACKEND-CODING-STANDARDS.md) |
| `backend/app/services/**` | [backend/BACKEND-CODING-STANDARDS.md](backend/BACKEND-CODING-STANDARDS.md) |
| `backend/app/models/**` | [database/DATABASE-CODING-STANDARDS.md](database/DATABASE-CODING-STANDARDS.md) |
| `backend/app/database/queries/**` | [database/DATABASE-CODING-STANDARDS.md](database/DATABASE-CODING-STANDARDS.md) |
| `frontend/src/api/**` | [api-flow/API-FLOW.md](api-flow/API-FLOW.md), [frontend/FRONTEND-CODING-STANDARDS.md](frontend/FRONTEND-CODING-STANDARDS.md) |
| `frontend/src/components/**` | [frontend/FRONTEND-CODING-STANDARDS.md](frontend/FRONTEND-CODING-STANDARDS.md) |
| `frontend/src/types/**` | [api-flow/API-FLOW.md](api-flow/API-FLOW.md) §3, [frontend/FRONTEND-CODING-STANDARDS.md](frontend/FRONTEND-CODING-STANDARDS.md) |
| `database/migrations/**` | [database/DATABASE-MIGRATIONS.md](database/DATABASE-MIGRATIONS.md) |
| `database/rls-policies/**` | [database/DATABASE-RLS-POLICIES.md](database/DATABASE-RLS-POLICIES.md) |
| `mobile/**` (today) | [mobile/MOBILE-PARITY-TODO.md](mobile/MOBILE-PARITY-TODO.md) — most rules translate 1:1 from [frontend/](../frontend/) |
| `docs/**` | [../README.md](../README.md) + [../../README.md](../../README.md) (no rule doc — just style) |
| Anything else | Read [../00-ARCHITECTURE-INDEX.md](../00-ARCHITECTURE-INDEX.md) first |

## Active TODOs (cross-cutting)

- [x] Fold [api-flow/DATA-FLOW-RULES.md](api-flow/DATA-FLOW-RULES.md) into per-layer docs — completed 2026-06-28. File kept as legacy reference; full TODO list at the bottom of that file.
- [ ] Add [mobile/](mobile/) rule folder + `mobile.instructions.md` — tracked in [mobile/MOBILE-PARITY-TODO.md](mobile/MOBILE-PARITY-TODO.md).
- [ ] Audit any other rule docs that still reference the old umbrella names (`CODING-STANDARDS.md`, `FOLDER-CONVENTIONS.md`, `DATA-FLOW-RULES.md` at the top level) — should be zero after this restructuring.
- [x] **ESLint v9 flat-config** — `eslint.config.js` shipped 2026-06-28. `npm run lint` runs clean (13 warnings, 0 errors — all in pre-existing code, none blocking). `npm run verify` now does `type-check && lint`.
- [ ] **Husky / pre-commit wiring** — [`.husky/pre-commit`](../../../.husky/pre-commit) and [`.husky/pre-commit-backend`](../../../.husky/pre-commit-backend) are written and `husky` is in `frontend/node_modules`, but `git config core.hooksPath` is not set, so the hooks won't fire on commit. Diagnose & fix:
  - confirm `npm run postinstall` (which calls `husky install`) ran successfully,
  - confirm `git config core.hooksPath` is `.husky` (or that `husky install` succeeded),
  - if it's a permissions issue on Windows, document the workaround in [`.github/CONTRIBUTING.md`](../../../CONTRIBUTING.md).
  - Until fixed, run the pre-commit checks manually before every commit:
    ```bash
    cd frontend  && npm run verify && npm run build && cd ..
    cd backend   && uv run ruff check . && uv run black --check . && uv run pytest tests -q
    ```

---

## See also

- [`docs/TECHNICAL/00-ARCHITECTURE-INDEX.md`](../00-ARCHITECTURE-INDEX.md) — top-level architecture nav
- [`docs/README.md`](../../README.md) — documentation hub
