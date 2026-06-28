---
description: "StrideAlytics database rules (PostgreSQL / Supabase) — applies to database/**. Reads docs/TECHNICAL/RULES/database/*."
applyTo: "database/**"
---

# StrideAlytics — Database Rules

**Authoritative sources (read before editing):**
- [`docs/TECHNICAL/RULES/database/DATABASE-CODING-STANDARDS.md`](../../docs/TECHNICAL/RULES/database/DATABASE-CODING-STANDARDS.md)
- [`docs/TECHNICAL/RULES/database/DATABASE-FOLDER-CONVENTIONS.md`](../../docs/TECHNICAL/RULES/database/DATABASE-FOLDER-CONVENTIONS.md)
- [`docs/TECHNICAL/RULES/database/DATABASE-MIGRATIONS.md`](../../docs/TECHNICAL/RULES/database/DATABASE-MIGRATIONS.md)
- [`docs/TECHNICAL/RULES/database/DATABASE-RLS-POLICIES.md`](../../docs/TECHNICAL/RULES/database/DATABASE-RLS-POLICIES.md)

If a planned change conflicts with any of the above, **stop and surface the conflict before writing code**.

## Hard prohibitions (the agent MUST refuse)

- ❌ Editing an already-applied migration file — write a new one instead.
- ❌ Mixing `RENAME COLUMN` and `DROP COLUMN` in the same migration without a header warning.
- ❌ Disabling RLS on a user-data table.
- ❌ `using (true)` or `with check (true)` for user tables.
- ❌ `select *` in views or stored procs.
- ❌ `text` for fixed-format identifiers (use `varchar(n)` or `citext`).
- ❌ Unindexed FK columns.
- ❌ Hard-coded secrets in SQL files.
- ❌ Running `seeds/` against production.

## Adding a new database resource — file checklist

1. `database/migrations/NNN_<name>.sql` with `if not exists` guards.
2. Paired `database/migrations/NNN_<name>_down.sql` for destructive changes.
3. `database/rls-policies/<table>.sql` with `enable` + `force row level security` + one policy per action.
4. (Optional) `database/functions/<verb>.sql` for stored procs.
5. (Optional) `database/views/<noun>.sql` for shared queries.

## Reference docs

- [`docs/TECHNICAL/LAYERS/04-DATABASE-LAYER.md`](../../docs/TECHNICAL/LAYERS/04-DATABASE-LAYER.md)
- [`docs/TECHNICAL/RULES/README.md`](../../docs/TECHNICAL/RULES/README.md)
