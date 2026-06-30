# Frontend — Coding Standards

**Layer:** `frontend/src/**` (React + Vite + TypeScript + Tailwind)
**Sibling docs:** [FRONTEND-FOLDER-CONVENTIONS.md](./FRONTEND-FOLDER-CONVENTIONS.md),
[../api-flow/API-FLOW.md](../api-flow/API-FLOW.md).

---

## 1. Naming

| Construct | Convention | Example |
|-----------|------------|---------|
| Component (file + symbol) | PascalCase | `ScreenerTable.tsx`, `Header.tsx` |
| Hook | `use<Thing>` camelCase | `useScreener.ts`, `useDebounce.ts` |
| Store (Zustand) | `use<X>Store` | `useAuthStore`, `useScreenerStore` |
| Service | camelCase + `.service.ts` | `ticker.service.ts` |
| Type / interface | PascalCase | `TickerData`, `LoginRequest` |
| Constant | UPPER_SNAKE_CASE | `API_BASE_URL`, `POLL_INTERVAL_MS` |
| Boolean | `is` / `has` / `can` prefix | `isLoading`, `hasError` |
| Event handler prop | `on` prefix | `onMenuClick`, `onFilterChange` |
| Private | leading `_` | `_internalHelper` |

## 2. Imports — required order

```typescript
// React / framework
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

// Third-party
import { Clock, Menu } from "lucide-react";
import axios from "axios";

// Local — components
import { Button } from "../ui/Button";
import { Header } from "./Header";

// Local — utilities / hooks / api
import { classNames } from "../../utils";
import { tickerService } from "../../api/services/ticker.service";
import type { TickerData } from "../../types/market";
```

`import type` for types only. No inline `interface Foo {}` in components.

## 3. Component structure

```typescript
interface ScreenerProps {
  filters: ScreenerFilters;
  onSelect: (id: string) => void;
  loading?: boolean;
}

export function Screener({ filters, onSelect, loading }: ScreenerProps) {
  // 1. hooks first
  const [results, setResults] = useState<ScreenerRow[]>([]);

  // 2. effects
  useEffect(() => { /* ... */ }, [filters]);

  // 3. handlers
  const handleSelect = (id: string) => onSelect(id);

  // 4. render
  return <div>…</div>;
}
```

- Default to **named exports** for components; only use `export default` for `App` / route elements.
- Never read env vars (`import.meta.env.*`) outside `src/api/client.ts`.

## 4. Styling

- Tailwind utility classes by default; CSS modules only when utilities aren't enough.
- No inline `style={{ ... }}` for repeated styling.
- Class composition via `classNames(...)` helper.

## 5. State

- **Local UI state** (`useState`) only for view state (open/closed, hover).
- **Cross‑component state** → Zustand store under `src/store/`.
- **Server state** → endpoint wrapper in `src/api/endpoints.ts` (optionally wrapped in a service).
- Never duplicate server data into Zustand.

## 6. API access (THE rule)

- The single axios `client` in `src/api/client.ts` is the **only** file that reads `VITE_API_URL`.
- Components / stores / hooks call `xApi` blocks in `src/api/endpoints.ts`.
- For polling / caching / fallback → `src/api/services/<name>.service.ts`.
- No raw `fetch`, no `import.meta.env`, no template‑literal URLs anywhere else.

## 7. Hard prohibitions

- ❌ `fetch(...)` inside components, stores, or hooks.
- ❌ `import.meta.env.VITE_API_URL` outside `src/api/client.ts`.
- ❌ Inline wire‑shape `interface Foo {}` inside `api/endpoints.ts`.
- ❌ Duplicate `TickerData`, `LoginRequest`, etc. in `api/` files.
- ❌ `any` (use `unknown` + narrowing or a proper type).

---

---



## 8. Before you finish

Stale Pylance / TS-server indexes, leftover dist artefacts, and stale Vite
caches are easy to introduce and hard to spot in review. Run these **before
every commit** — the husky pre-commit hook runs the same sequence:

```bash
# from frontend/
npm run clean         # wipe dist/, .vite/, node_modules/.cache, tsconfig.tsbuildinfo
npm run type-check    # tsc --noEmit
npm run build:prod    # clean + tsc + vite build (production)
```

You can also run them in one shot via `npm run prebuild:prod && npm run build:prod`.
Or use the VS Code task: **"Verify Types"** (Ctrl+Shift+P → "Tasks: Run Task").

### The new-file trap

When you **add a new file** under `src/` (e.g. `src/types/<name>.ts` or
`src/api/services/<name>.service.ts`), three things can go wrong:

1. Pylance has a stale index — it won't see the new file until the TS
   server reloads. **Reload it:** Ctrl+Shift+P → "TypeScript: Restart TS
   Server".
2. Your import path is off — `tsc --noEmit` will catch this **only if you
   run it**. Pylance won't always.
3. The relative import depth is wrong (`../../types/market` vs
   `../types/market`). The CLI compiler agrees with the editor on this
   one, but only after the index is current.

**Mandatory verification before declaring any task done that added or moved a file:**

- [ ] `npm run type-check` exits 0 from inside `frontend/`.
- [ ] `npm run build:prod` exits 0 from inside `frontend/` (full clean + production build).
- [ ] VS Code Problems panel shows no errors for the changed file(s).
- [ ] If Problems panel disagrees with `tsc --noEmit`, **trust `tsc`** —
      restart the TS server, then re-check.

### Why Pylance and tsc can disagree

Pylance runs its own TS server. It keeps an in-memory module graph that
can lag behind disk reality. When a file is created mid-session, the
graph may not know about it yet, producing red squiggles that `tsc
--noEmit` does not see. The two will agree again after:

- A full VS Code reload (`Developer: Reload Window`), or
- A targeted TS-server restart (`TypeScript: Restart TS Server`).

**Never** commit "fixes" for problems that only Pylance shows until
`tsc --noEmit` agrees with them. Otherwise you may delete a working
import in pursuit of a phantom error.

## See also

- [FRONTEND-FOLDER-CONVENTIONS.md](./FRONTEND-FOLDER-CONVENTIONS.md)
- [../api-flow/API-FLOW.md](../api-flow/API-FLOW.md) §3 — frontend checklist
- [../../LAYERS/01-FRONTEND-LAYER.md](../../LAYERS/01-FRONTEND-LAYER.md)

