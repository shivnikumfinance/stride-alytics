# Mobile Layer — Parity TODO

> **Scope:** `mobile/**` (React Native + Expo + NativeWind).
> **Authoritative source (today):** [../README.md](../README.md) (mobile has no dedicated rule folder yet).
> **Sibling (most rules apply):** [../frontend/](../frontend/) (React + Vite rules translate 1:1 — both are TS + axios + Zustand).

The mobile layer mirrors the web frontend for ~80% of concerns (api wrapper, zustand store, types).
This file tracks the remaining 20% — the mobile‑specific rules and docs that still need to be authored
before mobile parity is complete.

---

## What already works (no action needed)

- `mobile/src/api/` mirrors `frontend/src/api/` — same axios client + same `xApi` wrapper pattern.
- `mobile/src/store/` mirrors `frontend/src/store/` — same Zustand stores (auth, screener, greeks).
- `mobile/src/types/` (when added) should mirror `frontend/src/types/` 1:1.
- All [api-flow/API-FLOW.md](../api-flow/API-FLOW.md) prohibitions apply unchanged.

---

## Pending

- [ ] **Create `mobile.instructions.md`** in `.github/instructions/` with `applyTo: "mobile/**"`.
      Load [../frontend/FRONTEND-CODING-STANDARDS.md](../frontend/FRONTEND-CODING-STANDARDS.md)
      and [../frontend/FRONTEND-DATA-FLOW.md](../frontend/FRONTEND-DATA-FLOW.md) plus the
      mobile‑specific deltas below. Wire it into the same Copilot loader.
- [ ] **Create `docs/TECHNICAL/RULES/mobile/` folder** with three focused files:
      - `MOBILE-CODING-STANDARDS.md` — RN + Expo + NativeWind conventions (component → screen split, expo-router, platform‑specific styling).
      - `MOBILE-FOLDER-CONVENTIONS.md` — `app/` (router) vs `src/screens/` (non‑router) layout, asset folder rules, eas.json semantics.
      - `MOBILE-DATA-FLOW.md` — `expo-secure-store` instead of `localStorage`, `expo-constants` instead of `import.meta.env`, offline‑first cache rules.
- [ ] **Add `mobile` row to [RULES/README.md `Folder map`](../README.md)** with placeholder links.
- [ ] **Update [00-ARCHITECTURE-INDEX.md](../../00-ARCHITECTURE-INDEX.md)** rules section to mention the new mobile folder once it exists.
- [ ] **Mirror all [frontend/src/types/](../../../../mobile/src/types) (when added) from `frontend/src/types/`** to keep wire‑shape parity. Today `mobile/src/types/` does not exist — flag in any future PR that adds a new backend type.
- [ ] **Confirm `mobile/src/api/client.ts` reads the URL via `expo-constants`** (not `import.meta.env` — Vite‑only) and uses `expo-secure-store` for the token (not `localStorage`). Audit before the rule doc ships.
- [ ] **Confirm `mobile/App.tsx` does not duplicate API I/O** — it should only wire up `expo-router` and providers; all HTTP goes through `mobile/src/api/`.
- [ ] **Add a one‑screen smoke test** (vitest + React Native Testing Library) so the rule docs can cite a passing example.

## Mobile‑specific deltas (capture these in the future docs)

| Concern | Web frontend | Mobile (planned) |
|---------|--------------|------------------|
| Env vars | `import.meta.env.VITE_*` | `expo-constants.expoConfig.extra.*` |
| Token store | `localStorage` (`stride_token`) | `expo-secure-store` |
| Routing | `react-router-dom` (`BrowserRouter`) | `expo-router` (file‑based in `app/`) |
| Styling | Tailwind utility classes | NativeWind (Tailwind for RN) |
| Charts | Tremor | `victory-native` (per [02-MOBILE-LAYER.md](../../LAYERS/02-MOBILE-LAYER.md)) |
| Layout components | `src/components/layout/` | `src/components/layout/` (same name) + SafeAreaView wrappers |
| HTTP base URL | `new URL("/api/v1/", API_BASE)` | Same; URL builder may move to `mobile/src/api/client.ts` |

## Hard prohibitions (apply today, will live in `MOBILE-CODING-STANDARDS.md` later)

- ❌ `localStorage` for auth tokens — use `expo-secure-store`.
- ❌ `import.meta.env` anywhere — it's Vite‑only and will crash at runtime in RN.
- ❌ `react-router-dom` — use `expo-router`.
- ❌ `fetch(...)` outside `mobile/src/api/` — use the existing `xApi` wrappers.
- ❌ Inline wire‑shape interfaces in `mobile/src/api/` — mirror the web pattern: one file per resource under `mobile/src/types/`.

---

## See also

- [../README.md](../README.md) — rules index (mobile row will be added here)
- [../frontend/](../frontend/) — most rules translate 1:1
- [../api-flow/API-FLOW.md](../api-flow/API-FLOW.md) — cross‑cutting api rules apply unchanged
- [../../LAYERS/02-MOBILE-LAYER.md](../../LAYERS/02-MOBILE-LAYER.md) — mobile architecture overview
