# Database — RLS Policy Rules

**Layer:** `database/rls-policies/**`
**Sibling docs:** [DATABASE-CODING-STANDARDS.md](./DATABASE-CODING-STANDARDS.md),
[DATABASE-MIGRATIONS.md](./DATABASE-MIGRATIONS.md),
[DATABASE-FOLDER-CONVENTIONS.md](./DATABASE-FOLDER-CONVENTIONS.md).

---

## 1. Enable RLS on every table

```sql
alter table public.portfolios enable row level security;
alter table public.portfolios force row level security;  -- applies to table owner too
```

`force` is required for the Supabase `service_role` to still bypass — leave
it off only if backend service code intentionally runs as `anon`.

## 2. One file per table

```
database/rls-policies/
├── users.sql
├── portfolios.sql
└── trades.sql
```

Each file:
1. `enable row level security` + `force row level security`.
2. Define one policy per action (`select`, `insert`, `update`, `delete`).
3. Use a stable naming convention: `<action>_<table>_<scope>`.

## 3. Policy template (owner‑scoped)

```sql
-- trades.sql
alter table public.trades enable row level security;
alter table public.trades force row level security;

create policy select_trades_owner
  on public.trades for select
  using (user_id = auth.uid());

create policy insert_trades_owner
  on public.trades for insert
  with check (user_id = auth.uid());

create policy update_trades_owner
  on public.trades for update
  using (user_id = auth.uid())
  with check (user_id = auth.uid());

create policy delete_trades_owner
  on public.trades for delete
  using (user_id = auth.uid());
```

## 4. Required predicates

| Action | Predicate |
|--------|-----------|
| `select` | `using (...)` |
| `insert` | `with check (...)` |
| `update` | both `using` and `with check` |
| `delete` | `using (...)` |

`with check` is what prevents a user from inserting/updating a row they
can't read — never omit it.

## 5. Performance

- Wrap predicates in `(select auth.uid())` so the planner can hoist it out of per‑row evaluation.
- Index every column that appears in a policy predicate.

## 6. Testing

- Every RLS change must be paired with a test under `database/seeds/` or a CI script.
- Tests must cover the **negative** case (different user → denied).

## 7. Hard prohibitions

- ❌ Disabling RLS on a table that holds user data.
- ❌ `using (true)` or `with check (true)` for user tables.
- ❌ Putting business logic in a policy (use a function in `functions/` instead).
- ❌ Missing `with check` on `insert`/`update`.

---

## See also

- [DATABASE-CODING-STANDARDS.md](./DATABASE-CODING-STANDARDS.md)
- [DATABASE-MIGRATIONS.md](./DATABASE-MIGRATIONS.md)
- [../../LAYERS/04-DATABASE-LAYER.md](../../LAYERS/04-DATABASE-LAYER.md)
