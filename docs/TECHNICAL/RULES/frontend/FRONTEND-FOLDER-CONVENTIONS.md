# Frontend — Folder Conventions

**Layer:** `frontend/src/**` (React + Vite + TypeScript + Tailwind)
**Sibling docs:** [FRONTEND-CODING-STANDARDS.md](./FRONTEND-CODING-STANDARDS.md),
[../api-flow/API-FLOW.md](../api-flow/API-FLOW.md).

---

## 1. Canonical layout

```
frontend/
├── src/
│   ├── App.tsx                  # Root component + router
│   ├── main.tsx                 # Entry point
│   ├── index.css                # Global styles
│   │
│   ├── api/                     # All backend I/O lives here
│   │   ├── client.ts            # Single axios instance; reads VITE_API_URL
│   │   ├── endpoints.ts         # Typed wrappers per resource (xApi blocks)
│   │   └── services/            # Polling, retries, caching, fallbacks
│   │       └── ticker.service.ts
│   │
│   ├── components/              # UI components, grouped by feature
│   │   ├── ui/                  # Reusable atoms (Button, Card, Modal)
│   │   ├── layout/              # Header, Sidebar, AppLayout
│   │   ├── charts/              # Tremor wrappers
│   │   └── tables/              # Data tables
│   │
│   ├── pages/                   # Route-level components
│   │
│   ├── hooks/                   # Custom React hooks (useXxx)
│   │
│   ├── store/                   # Zustand stores
│   │
│   ├── types/                   # Wire-shape TS types, one file per resource
│   │   ├── auth.ts
│   │   ├── greeks.ts
│   │   ├── market.ts
│   │   └── index.ts             # barrel re-export
│   │
│   ├── utils/                   # formatters, helpers, validators, constants
│   │
│   └── theme/                   # design tokens, tailwind theme
│
├── public/                      # static assets
├── index.html
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── vite.config.ts
```

## 2. Adding a new resource — file checklist

1. `src/types/<name>.ts` — wire shape mirroring the backend Pydantic model 1:1.
2. `src/types/index.ts` — add `export * from "./<name>"`.
3. `src/api/endpoints.ts` — add a `xApi` block using `client`.
4. If polling / caching / fallback is needed → `src/api/services/<name>.service.ts`.
5. Components / stores / hooks import the service or wrapper — never raw `fetch`.

## 3. Naming rules

| Thing | Rule | Example |
|-------|------|---------|
| Component folder | lowercase, by feature | `src/components/screener/` |
| Component file | PascalCase `.tsx` | `ScreenerFilters.tsx` |
| Styles | co-located `.module.css` | `ScreenerFilters.module.css` |
| Test | co-located `__tests__/` or `*.test.tsx` | `ScreenerFilters.test.tsx` |
| API file | camelCase `.ts` | `ticker.service.ts`, `client.ts` |
| Type file | lowercase `.ts` | `market.ts`, `auth.ts` |

## 4. Hard prohibitions

- ❌ `fetch`, `axios`, `import.meta.env` in `components/`, `pages/`, `store/`, `hooks/`.
- ❌ `api/endpoints.ts` containing `interface Foo {}` for a wire shape.
- ❌ Multiple axios instances — only `src/api/client.ts` exports one.
- ❌ Inline Pydantic‑style schemas anywhere except `src/types/`.

---

## See also

- [FRONTEND-CODING-STANDARDS.md](./FRONTEND-CODING-STANDARDS.md)
- [../api-flow/API-FLOW.md](../api-flow/API-FLOW.md)
- [../../03-FOLDER-STRUCTURE.md](../../03-FOLDER-STRUCTURE.md)
