# Frontend â€” Data Flow Patterns

**Layer:** `frontend/src/**` (React + Vite + TypeScript + Tailwind)
**Sibling docs:** [FRONTEND-CODING-STANDARDS.md](./FRONTEND-CODING-STANDARDS.md),
[../api-flow/API-FLOW.md](../api-flow/API-FLOW.md).

---

## 1. Request lifecycle

```
User action
   â”‚
   â–¼
Component / Page (React)
   â”‚  subscribes via hook OR calls service directly
   â–¼
src/api/services/<name>.service.ts        â† optional (polling/caching/fallback)
   â”‚  uses
   â–¼
src/api/endpoints.ts  (xApi.<verb>(...))
   â”‚  uses
   â–¼
src/api/client.ts (axios instance)
   â”‚  reads VITE_API_URL  â† ONLY file that does this
   â”‚  injects JWT, handles 401
   â–¼
HTTP  â†’  Backend API
```

## 2. Standard response shape

Backend returns a Pydantic envelope:

```typescript
interface TickerPayload {
  success: boolean;
  data: Record<string, RawTicker>;
}
```

`xApi.tickers()` returns the full envelope. Services / components unwrap
`.data` where appropriate.

## 3. Auth

- The single `client` reads `tokenStore.get()` and sets `Authorization: Bearer â€¦`.
- On `401`, the response interceptor clears the token and calls `useAuthStore.getState().logout()`.
- Components never read `localStorage` directly for auth.

## 4. State separation

| Kind | Where |
|------|-------|
| Local view state | `useState` inside the component |
| Crossâ€‘component UI state | Zustand store (`useXStore`) |
| Server state | endpoint wrapper in `src/api/endpoints.ts`, optionally wrapped in a service |
| Auth state | `useAuthStore` |

Never copy server data into a Zustand store.

## 5. Caching / polling / fallback

- A polling/caching layer lives in `src/api/services/<name>.service.ts`.
- The service exposes `startPolling(cb)`, `stopPolling()`, and a single source of truth for stale data.
- Components never own `setInterval` or `setTimeout` for data fetching.

---

## See also

- [FRONTEND-CODING-STANDARDS.md](./FRONTEND-CODING-STANDARDS.md)
- [../api-flow/API-FLOW.md](../api-flow/API-FLOW.md)


---

## 6. Caching

When using React Query (or any cache layer), always include **every variable** that affects the result in the `queryKey`. Same key + different filters = wrong data.

```typescript
// âœ… GOOD
queryKey: ["screener", { symbol: "AAPL", min_price: 100 }]

// âŒ BAD â€” collides across users / filters
queryKey: ["screener"]
```

Default `staleTime` and `gcTime` by data type:

| Data | `staleTime` | `gcTime` |
|------|-------------|----------|
| Tickers / market data | 15 s | 1 min |
| Screener results | 5 min | 30 min |
| Portfolio summary | 30 s | 5 min |
| User profile / settings | 5 min | 30 min |
| Static reference data (e.g. SPY constituents) | 1 h | 24 h |

---

## 7. Retries & rate-limit headers

### Retry with exponential backoff

The axios client already handles transient network errors. For app-level retries, wrap the call yourself or use React Query's built-in retry:

```typescript
useQuery({
  queryKey: ["screener", filters],
  queryFn: () => screenerApi.run(filters),
  retry: 3,
  retryDelay: (attemptIndex) => Math.pow(2, attemptIndex) * 1000, // 1s, 2s, 4s
});
```

### Retryable vs non-retryable

| Retryable | Non-retryable |
|-----------|---------------|
| `5xx` server errors | `400` bad request |
| `503` service unavailable | `401` unauthorized (clear token + logout) |
| Network timeouts | `403` forbidden |
| Connection refused | `404` not found |
| | `409` conflict (let UI surface the conflict) |
| | `422` validation (let UI surface field errors) |

### Rate-limit headers

Respect the upstream's signal â€” back off when `X-RateLimit-Remaining` hits zero:

```
X-RateLimit-Limit:     100
X-RateLimit-Remaining: 0
X-RateLimit-Reset:     1623801600
```

If the backend returns `429`, do **not** auto-retry inside the UI â€” show a "slow down" banner instead. Free-tier caps on the screener endpoint are enforced server-side.

---

## See also

- [FRONTEND-CODING-STANDARDS.md](./FRONTEND-CODING-STANDARDS.md)
- [../api-flow/API-FLOW.md](../api-flow/API-FLOW.md)

