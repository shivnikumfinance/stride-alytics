# StrideAlytics â€” API Flow & Layering Rules

**The single source of truth for how the backend and frontend must call each other.**

> This rule is **crossâ€‘cutting** â€” both backend and frontend must follow it.
> For layerâ€‘specific rules see:
>
> - Backend â†’ [../backend/BACKEND-CODING-STANDARDS.md](../backend/BACKEND-CODING-STANDARDS.md), [../backend/BACKEND-FOLDER-CONVENTIONS.md](../backend/BACKEND-FOLDER-CONVENTIONS.md)
> - Frontend â†’ [../frontend/FRONTEND-CODING-STANDARDS.md](../frontend/FRONTEND-CODING-STANDARDS.md), [../frontend/FRONTEND-FOLDER-CONVENTIONS.md](../frontend/FRONTEND-FOLDER-CONVENTIONS.md)
> - Database â†’ [../database/DATABASE-CODING-STANDARDS.md](../database/DATABASE-CODING-STANDARDS.md)
> - Oneâ€‘page checklist â†’ [ENDPOINT-CHECKLIST.md](./ENDPOINT-CHECKLIST.md)
> - All rules index â†’ [../README.md](../README.md)

If you change or add an API, follow the diagram and checklist below. If a change
violates them, the PR review should reject it.

---

## 1. The mandatory flow

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   HTTP (axios / fetch)   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚   Frontend (UI)    â”‚ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¶ â”‚  Backend API endpoint   â”‚
â”‚ components /       â”‚                          â”‚  app/api/v1/endpoints/  â”‚
â”‚ stores / hooks     â”‚                          â”‚  (router + validation)  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
           â”‚                                                 â”‚
           â”‚ types in                                        â”‚ delegates to
           â”‚ src/types/                                      â–¼
           â”‚                                          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
           â–¼                                          â”‚  Service layer      â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”                                â”‚  app/services/      â”‚
â”‚  Frontend types    â”‚                                â”‚  (business logic,   â”‚
â”‚  frontend/src/     â”‚                                â”‚   external calls,   â”‚
â”‚  types/<name>.ts   â”‚                                â”‚   side effects)     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                                                â”‚
                                                                â–¼
                                                       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                       â”‚  ORM model         â”‚
                                                       â”‚  app/models/       â”‚
                                                       â”‚  (SQLAlchemy â€” DB  â”‚
                                                       â”‚   shape only)      â”‚
                                                       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                                                â”‚
                                                                â–¼
                                                       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                       â”‚  Database          â”‚
                                                       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Layer responsibilities

| Layer | Path | Responsibility | Must NOT contain |
|-------|------|----------------|------------------|
| **Endpoint** | `backend/app/api/v1/endpoints/<name>.py` | HTTP wiring: parse query/body via Pydantic, call service, return `response_model=...`. Auth via `Depends(get_current_user)` where needed. | Business logic, external HTTP calls, hardâ€‘coded URLs, fallback data. |
| **Schema** | `backend/app/api/v1/schemas/<name>.py` | Pydantic `BaseModel`s. Request bodies, query params, response models. Wire format only. | DB access, `httpx`/`requests`, business rules. |
| **Service** | `backend/app/services/<name>.py` | All business logic: external API calls, computation, caching, fallbacks. Returns plain Python types or Pydantic models. | `from fastapi import ...`, HTTP request objects, response status codes. |
| **Model** | `backend/app/models/<name>.py` | SQLAlchemy ORM mapped to DB tables. | Business logic, Pydanticâ€‘only fields. |
| **Database** | `backend/app/database/` (queries/migrations) | Raw SQL helpers + Alembic/Supabase migrations. | FastAPI imports. |
| **Frontend endpoint wrapper** | `frontend/src/api/endpoints.ts` (and friends) | One `xApi` object per resource. Calls `client` and unwraps `.data`. Typed. | Hardâ€‘coded URLs, envâ€‘var reads, raw `fetch`. |
| **Frontend service** | `frontend/src/api/services/<name>.service.ts` | Polling, retries, caching, fallbacks. Calls the endpoint wrapper only. | Hardâ€‘coded URLs, raw `fetch`, `import.meta.env`. |
| **Frontend types** | `frontend/src/types/<name>.ts` (mirrored 1:1 with backend schemas) | Exact wire shape + any clientâ€‘side extensions (`timestamp`, etc.). | Logic, axios imports. |
| **Component / store / hook** | `frontend/src/components/`, `store/`, `hooks/` | UI + state. Calls the service / endpoint wrapper. | `fetch`, `axios`, env vars, URL construction. |

---

## 2. Adding a new backend resource â€” checklist

Copy this checklist into the PR description.

- [ ] `backend/app/models/<name>.py` â€” SQLAlchemy ORM mapped to the new table (or reused from existing table).
- [ ] `backend/app/api/v1/schemas/<name>.py` â€” Pydantic models for request, response, and any subâ€‘models.
- [ ] `backend/app/api/v1/schemas/__init__.py` â€” reâ€‘export the new models.
- [ ] `backend/app/services/<name>.py` â€” pure business logic; no `fastapi` imports.
- [ ] `backend/app/services/__init__.py` â€” reâ€‘export public symbols.
- [ ] `backend/app/api/v1/endpoints/<name>.py` â€” `APIRouter`, thin adapter only.
- [ ] `backend/app/api/v1/endpoints/__init__.py` â€” register the new router module.
- [ ] `backend/app/api/v1/router.py` â€” `include_router(...)` with correct `prefix=` and `tags=`.

---

## 3. Adding a new frontend endpoint â€” checklist

- [ ] `frontend/src/types/<name>.ts` â€” wire shape mirroring `backend/.../schemas/<name>.py` 1:1.
- [ ] `frontend/src/types/index.ts` â€” add `export * from "./<name>"` to the barrel.
- [ ] `frontend/src/api/endpoints.ts` â€” add a `xApi` block that calls `client.<verb>(...)` and unwraps `.data`.
- [ ] If polling / caching / fallback is needed: `frontend/src/api/services/<name>.service.ts`.
- [ ] Component / store / hook imports the **service** (not the endpoint wrapper) when there's sideâ€‘effect logic; otherwise it may import the endpoint wrapper directly.

---

## 4. URL construction rules (frontend)

- The axios `client` (`frontend/src/api/client.ts`) is the **only** file that reads `VITE_API_URL`.
- The `client`'s `baseURL` is built with `new URL("/api/v1/", API_BASE)` â€” never with template literals.
- Components, stores, and services **never** read env vars or build URLs.
- Any new endpoint path is a relative string like `"/auth/login"` or `"/portfolio/{id}/trades"` (use the existing wrapper in `endpoints.ts`).

---

## 5. URL construction rules (backend)

- The `app/api/v1/router.py` `APIRouter(prefix="/api/v1")` is the **only** place the version prefix is set.
- Endpoint modules never repeat `/api/v1/...` paths â€” they use relative paths only.
- External URLs (Yahoo Finance, Supabase, scheduler webhooks) live in `app/services/<name>.py` as moduleâ€‘level constants. Endpoints never construct external URLs.

---

## 6. Why these rules exist

- **Single source of truth.** Change the URL in one place, not five.
- **Testability.** Services are pure functions â€” easy to unitâ€‘test without spinning up FastAPI.
- **Frontend safety.** JWT, 401 logout, base URL, and error handling come from the single axios client â€” every endpoint gets them for free.
- **Schema parity.** Pydantic on the backend + matching TypeScript on the frontend prevents shape drift.
- **No silent drift.** When the wire shape changes, both sides update together because the docs spell it out.

---

## 7. Common violations â€” how to fix them

| Violation | Fix |
|-----------|-----|
| Endpoint module contains `httpx.get(...)` or `requests.get(...)` | Move the call into `app/services/<name>.py`. |
| Endpoint module declares a dataclass / `BaseModel` inline | Move it into `app/api/v1/schemas/<name>.py`. |
| Service module imports `fastapi.HTTPException` | Raise a domain exception in the service; translate it in the endpoint (or use the global `error_handler` middleware). |
| Frontend component reads `import.meta.env.VITE_API_URL` | Use the axios `client` via `xApi`. |
| Frontend component calls `fetch(...)` directly | Use `xApi` or the matching `services/<name>.service.ts`. |
| Frontend types live inside `api/endpoints.ts` | Move to `frontend/src/types/<name>.ts` and reâ€‘export via `types/index.ts`. |
| Frontend has its own polling/cache logic in a component | Move it to `frontend/src/api/services/<name>.service.ts`. |
| Endpoint path is duplicated in the router (`include_router(..., prefix="/api/v1/...")`) | Drop the `prefix` â€” the parent router already owns `/api/v1`. |

---

## 8. Related documents

- [README.md](../README.md) â€” index of all rules, organized per layer
- [ENDPOINT-CHECKLIST.md](./ENDPOINT-CHECKLIST.md) â€” short checklist for adding a resource
- [01-SYSTEM-OVERVIEW.md](../../01-SYSTEM-OVERVIEW.md)
- [03-FOLDER-STRUCTURE.md](../../03-FOLDER-STRUCTURE.md)
- [LAYERS/01-FRONTEND-LAYER.md](../../LAYERS/01-FRONTEND-LAYER.md)
- [LAYERS/03-BACKEND-LAYER.md](../../LAYERS/03-BACKEND-LAYER.md)
- [../backend/BACKEND-FOLDER-CONVENTIONS.md](../backend/BACKEND-FOLDER-CONVENTIONS.md)
- [../backend/BACKEND-CODING-STANDARDS.md](../backend/BACKEND-CODING-STANDARDS.md)
- [../frontend/FRONTEND-FOLDER-CONVENTIONS.md](../frontend/FRONTEND-FOLDER-CONVENTIONS.md)
- [../frontend/FRONTEND-CODING-STANDARDS.md](../frontend/FRONTEND-CODING-STANDARDS.md)
- [../database/DATABASE-FOLDER-CONVENTIONS.md](../database/DATABASE-FOLDER-CONVENTIONS.md)
- [DATA-FLOW-RULES.md](./DATA-FLOW-RULES.md) â€” historical crossâ€‘layer doc (kept for reference)


---

## 9. Standard response shape

Successful payloads are wrapped in a Pydantic envelope so the frontend
gets a predictable `{ success, data }` shape:

```python
class TickerEnvelope(BaseModel):
    success: bool = True
    data: Dict[str, TickerData]
```

Errors come from the global `error_handler` middleware (`app/api/middleware/error_handler.py`),
**never** from an endpoint. The error envelope is:

```json
{
  "success": false,
  "error": {
    "type": "VALIDATION_ERROR",
    "status": 422,
    "message": "Invalid parameters",
    "details": { "symbol": "Symbol is required" }
  }
}
```

### Status codes

| Code | Use when |
|------|----------|
| `200` | Successful read / mutation that returns a body |
| `201` | Resource created |
| `204` | Success with no response body |
| `400` | Malformed request (bad JSON, missing required field) |
| `401` | Missing / invalid JWT |
| `403` | Authenticated but not authorized |
| `404` | Resource not found |
| `409` | Conflict (duplicate key, version mismatch) |
| `422` | Validation error (Pydantic `RequestValidationError`) |
| `429` | Rate-limited (free-tier cap, IP throttle) |
| `500` | Unhandled server error |
| `503` | Upstream outage, maintenance |

---

## 10. Authentication flow

All authenticated endpoints take `current_user: CurrentUser = Depends(get_current_user)`
(see `app/api/middleware/auth.py`).

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{ "email": "user@example.com", "password": "..." }
```

Response (`200`):

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user_id": "uuid",
    "email": "user@example.com",
    "subscription_plan": "free"
  }
}
```

The frontend stores the access token in `localStorage` (`stride_token` key) and the axios client attaches it as `Authorization: Bearer â€¦`. On `401`, the client clears the token and triggers `useAuthStore.logout()`.

### Token refresh

`POST /api/v1/auth/refresh` with a refresh token returns a new access token.
Until that endpoint ships, expired tokens force a re-login.

### Server-side verification

1. Extract `Authorization: Bearer <jwt>` header.
2. Verify signature with `SUPABASE_JWT_SECRET` (HS256).
3. Check expiry.
4. Read `sub` claim â†’ `user_id`.
5. Apply RLS via `auth.uid()` on every query.

---

## 11. Pagination & filtering

### Pagination

Two equivalent patterns â€” pick one and stay consistent per resource.

```http
# Offset/limit
GET /api/v1/trades?limit=50&offset=0

# Page/per_page
GET /api/v1/trades?page=1&per_page=50
```

Successful paginated response:

```json
{
  "success": true,
  "data": [ /* items */ ],
  "pagination": {
    "total": 1000,
    "page": 1,
    "per_page": 50,
    "pages": 20
  }
}
```

### Filtering

```http
# Query string for simple cases
GET /api/v1/screener?symbol=AAPL&min_price=100&max_price=150

# JSON body for complex cases
POST /api/v1/screener/search
{
  "filters": { "symbol": "AAPL", "min_price": 100, "max_price": 150 },
  "limit": 50,
  "offset": 0
}
```

### Sorting

```
sort=price          # ascending
sort=-price         # descending
sort=-price,symbol  # primary + secondary
```

---

## 12. Versioning & schema evolution

- **Current**: `/api/v1/*`. **Legacy**: `/api/v0/*` (kept for backward compatibility).
- Each version is **backward compatible**.
- Deprecation notice **6+ months** before removal.

### Schema evolution rules

| Change | Allowed? |
|--------|----------|
| Add **optional** field | Yes â€” always |
| Add **required** field with default | Yes (clients that ignore it still work) |
| Add new endpoint | Yes |
| Remove required field | No â€” add `v2` instead |
| Rename field | No â€” keep old, add new, deprecate over time |
| Change field type (incompatible) | No â€” add `v2` |
| Tighten validation (e.g. min length 5 to 10) | No â€” add `v2` |

---

## 13. Data contracts (reference shapes)

These mirror the Pydantic schemas in `backend/app/api/v1/schemas/`.
Frontend mirrors live in `frontend/src/types/`.

### Option

```typescript
interface Option {
  symbol: string;
  strike: number;
  expiry: string;          // ISO date
  option_type: "call" | "put";
  bid: number;
  ask: number;
  last_price: number;
  implied_vol: number;     // decimal, e.g. 0.25 = 25%
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
  open_interest: number;
  volume: number;
  updated_at: string;
}
```

### Portfolio / Trade

See the TypeScript types in [`frontend/src/types/portfolio.ts`](../../../../frontend/src/types/portfolio.ts)
and [`frontend/src/types/trades.ts`](../../../../frontend/src/types/trades.ts) â€” they are the
authoritative wire shape.

---

