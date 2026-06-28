# Database — Coding Standards

**Layer:** `database/**` (PostgreSQL / Supabase)
**Sibling docs:** [DATABASE-FOLDER-CONVENTIONS.md](./DATABASE-FOLDER-CONVENTIONS.md),
[DATABASE-MIGRATIONS.md](./DATABASE-MIGRATIONS.md),
[DATABASE-RLS-POLICIES.md](./DATABASE-RLS-POLICIES.md).

---

## 1. Style

- Lowercase SQL keywords: `select`, `create table`, `alter table`.
- Two‑space indentation; one statement per line.
- Always end statements with `;`.
- Wrap multi‑statement blocks in `BEGIN; … COMMIT;` (or `ROLLBACK;` on failure).

```sql
-- ✅ GOOD
create table if not exists public.trades (
  id uuid primary key default gen_random_uuid(),
  symbol text not null,
  quantity integer not null check (quantity > 0),
  created_at timestamptz not null default now()
);
```

## 2. Naming

| Construct | Rule | Example |
|-----------|------|---------|
| Table | lowercase, snake_case, plural | `portfolios`, `trades`, `options` |
| Column | snake_case | `entry_price`, `created_at`, `user_id` |
| Primary key | `id` of type `uuid` | `id uuid primary key default gen_random_uuid()` |
| Timestamp | `created_at`, `updated_at`, `_at` suffix | `created_at timestamptz` |
| Foreign key | `<singular_table>_id` | `user_id`, `portfolio_id` |
| Index | `idx_<table>_<columns>` | `idx_trades_user_id` |
| Constraint | `<table>_<col>_<rule>` | `trades_quantity_positive` |
| Policy | `<action>_<table>_<scope>` | `select_trades_owner` |

## 3. Required defaults

- Every table has `created_at` and `updated_at` (`timestamptz`, default `now()`).
- `updated_at` is bumped by a trigger `set_updated_at` (see [DATABASE-MIGRATIONS.md](./DATABASE-MIGRATIONS.md)).
- Primary keys are UUIDs unless the table is a pure join/lookup where a composite PK is justified.

## 4. Performance

- Add indexes for every FK column.
- Add indexes for columns that appear in `WHERE` clauses of slow queries.
- Avoid `select *` in production queries — enumerate columns explicitly.

## 5. Money / numeric data

- Use `numeric(p, s)` for prices, P&L, and strike prices.
- Use `integer` / `bigint` for counts.
- Never use `real` / `double precision` for financial values.

## 6. Documentation

Every migration file starts with a header comment:

```sql
-- 006_add_options_chain.sql
-- Adds the public.options table that stores option chain snapshots
-- populated by the scheduler (fetch_market_data.py).
-- Backfill: n/a (new table).
```

## 7. Hard prohibitions

- ❌ `select *` in views or stored procs.
- ❌ `text` for fixed‑format identifiers (use `varchar(n)` or `citext`).
- ❌ Removing a column without a deprecation phase.
- ❌ Using `now()` without `timestamptz`.
- ❌ Unindexed FK columns.

---

## See also

- [DATABASE-FOLDER-CONVENTIONS.md](./DATABASE-FOLDER-CONVENTIONS.md)
- [DATABASE-MIGRATIONS.md](./DATABASE-MIGRATIONS.md)
- [DATABASE-RLS-POLICIES.md](./DATABASE-RLS-POLICIES.md)
