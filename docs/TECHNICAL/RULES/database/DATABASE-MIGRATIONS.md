# Database — Migration Rules

**Layer:** `database/migrations/**`
**Sibling docs:** [DATABASE-CODING-STANDARDS.md](./DATABASE-CODING-STANDARDS.md),
[DATABASE-FOLDER-CONVENTIONS.md](./DATABASE-FOLDER-CONVENTIONS.md),
[DATABASE-RLS-POLICIES.md](./DATABASE-RLS-POLICIES.md).

---

## 1. Numbering

- Files are **append‑only**. Once applied, never edit a migration — write a new one.
- 3‑digit zero‑padded prefix: `001_`, `002_`, `003_`.
- Use the next available number; never re‑use or skip numbers.

## 2. Forward + rollback

Every destructive migration ships with a `_down.sql` file:

```
migrations/
├── 005_extended_features.sql
└── 005_extended_features_down.sql
```

The `_down.sql` must fully reverse the up migration **and** any data‑loss
must be acknowledged in the migration header.

## 3. Header comment (required)

```sql
-- 007_add_user_subscription_tier.sql
-- Adds public.users.subscription_plan (default 'free').
-- Backfill: existing rows default to 'free'.
-- Down: 007_add_user_subscription_tier_down.sql
-- Risk:  none — additive, nullable column with default.
```

## 4. Idempotency

Migrations must be safe to re‑run:

```sql
-- ✅ GOOD
create table if not exists public.options ( … );
create index if not exists idx_options_symbol on public.options (symbol);

-- ❌ BAD
create table public.options ( … );
```

## 5. Order within a migration

1. `CREATE TABLE`
2. `ALTER TABLE … ADD CONSTRAINT`
3. `CREATE INDEX`
4. `CREATE OR REPLACE FUNCTION / VIEW`
5. `INSERT … ON CONFLICT DO NOTHING` (data backfill)

## 6. Apply scripts

Use the shared scripts; do not run ad‑hoc `psql`:

```bash
./database/scripts/apply_migrations.sh        # POSIX
./database/scripts/apply_migrations.ps1       # Windows
```

## 7. CI

CI must run migrations against a fresh database before merge.
Migration files that fail the apply‑migrations script must block the PR.

## 8. Hard prohibitions

- ❌ Editing a migration that has already shipped to staging/prod.
- ❌ Skipping numbers or using non‑zero‑padded prefixes.
- ❌ Mixing `RENAME COLUMN` and `DROP COLUMN` in the same migration without a header warning.
- ❌ Running seeds in prod.

---

## See also

- [DATABASE-CODING-STANDARDS.md](./DATABASE-CODING-STANDARDS.md)
- [DATABASE-RLS-POLICIES.md](./DATABASE-RLS-POLICIES.md)
