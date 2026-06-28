# Backend â€” Data Flow Patterns

**Layer:** `backend/**` (FastAPI / Python)
**Sibling docs:** [BACKEND-CODING-STANDARDS.md](./BACKEND-CODING-STANDARDS.md),
[../api-flow/API-FLOW.md](../api-flow/API-FLOW.md).

---

## 1. Request lifecycle

```
HTTP request
   â”‚
   â–¼
FastAPI router (app/api/v1/router.py)
   â”‚  prefix="/api/v1"
   â–¼
Endpoint (app/api/v1/endpoints/<name>.py)
   â”‚  validates via Pydantic request model
   â”‚  applies Depends(get_current_user) where needed
   â–¼
Service (app/services/<name>.py)
   â”‚  pure business logic
   â”‚  talks to app/models/ via SQLAlchemy
   â”‚  talks to external APIs via httpx
   â–¼
Response Pydantic model (app/api/v1/schemas/<name>.py)
   â”‚
   â–¼
HTTP response
```

## 2. Standard response shape

Always wrap successful payloads in a Pydantic envelope so the frontend
gets a predictable `success / data` shape:

```python
class TickerEnvelope(BaseModel):
    success: bool = True
    data: Dict[str, TickerData]
```

Errors come from the global `error_handler` middleware, never from the
endpoint itself.

## 3. Auth

- All authenticated endpoints take `current_user: CurrentUser = Depends(get_current_user)`.
- `CurrentUser` is defined in `app/api/middleware/auth.py`.
- Plan limits (`FREE_TIER_*`, `PRO_TIER_*`) live in `app/utils/constants.py`.

## 4. Persistence

- All DB access goes through SQLAlchemy models in `app/models/`.
- No raw SQL in endpoints or services.
- Supabase access (auth, RLS) goes through `app/database/client.py`.

## 5. External HTTP

- All thirdâ€‘party URLs are moduleâ€‘level constants in `app/services/<name>.py`.
- Use `httpx.AsyncClient` with explicit timeouts.
- Always handle `httpx.TimeoutException` and `httpx.HTTPError`.
- Provide a graceful fallback so the UI never sees an empty payload.

---

## See also

- [BACKEND-CODING-STANDARDS.md](./BACKEND-CODING-STANDARDS.md)
- [../api-flow/API-FLOW.md](../api-flow/API-FLOW.md)


---

## 6. Transactions & consistency

Multi-step writes **must** be wrapped in a transaction so a partial failure cannot leave the DB in an inconsistent state.

```python
async with db.transaction():
    await update_portfolio(portfolio_id, stats)
    await update_trades(portfolio_id, trades)
    await update_user_cache(user_id)
```

Rules:

- One transaction per logical unit of work (e.g. closing a trade updates the trade row, the portfolio summary, and the user cache â€” all in one).
- Never hold a transaction across an `httpx` call or any other I/O that may take seconds.
- For optimistic locking, include a `version` field on the row and reject updates when the supplied version is stale:

  ```json
  PUT /api/v1/portfolio/123
  { "data": { ... }, "version": 5 }
  ```

  ```json
  409 Conflict
  { "error": "Resource was modified" }
  ```

---

## 7. PII & privacy

**Never** expose in any response (including errors):

- User passwords (or password hashes)
- API keys, JWT secrets, OAuth tokens
- Social security / national ID numbers
- Credit card numbers / CVV
- Health information

When returning a user record, always project to a safe shape â€” never `user.dict()`:

```python
# âœ… GOOD
def get_user_response(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,        # the user's own email only
        "full_name": user.full_name,
        "subscription_plan": user.subscription_plan,
    }

# âŒ BAD â€” leaks password_hash, refresh tokens, etc.
def get_user_response(user: User) -> dict:
    return user.dict()
```

For PII in logs, log the **id** (UUID), not the email / name / SSN.

---

## See also

- [BACKEND-CODING-STANDARDS.md](./BACKEND-CODING-STANDARDS.md)
- [../api-flow/API-FLOW.md](../api-flow/API-FLOW.md)

