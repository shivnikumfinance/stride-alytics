# Database — Folder Conventions

**Layer:** `database/**` (Supabase / PostgreSQL / SQL migrations)
**Sibling docs:** [DATABASE-MIGRATIONS.md](./DATABASE-MIGRATIONS.md),
[DATABASE-RLS-POLICIES.md](./DATABASE-RLS-POLICIES.md),
[DATABASE-CODING-STANDARDS.md](./DATABASE-CODING-STANDARDS.md).

---

## 1. Canonical layout

```
database/
├── schema.sql                  # Combined view of the latest schema (auto-generated)
├── README.md
│
├── migrations/                 # Numbered, append-only SQL migrations
│   ├── 001_create_health_check_table.sql
│   ├── 002_initial_schema.sql
│   ├── 002_initial_schema_down.sql   # paired rollback when destructive
│   ├── 003_row_level_security.sql
│   ├── 004_indexes_views_functions.sql
│   └── 005_extended_features.sql
│
├── rls-policies/               # One file per table that has RLS
│   ├── users.sql
│   ├── portfolios.sql
│   └── trades.sql
│
├── functions/                  # Stored procedures / PL/pgSQL functions
│   └── calculate_portfolio_stats.sql
│
├── views/                      # SQL views
│   └── portfolio_summary.sql
│
├── seeds/                      # Dev/test fixtures — NEVER run in prod
│   └── dev_users.sql
│
└── scripts/                    # Apply / rollback helpers
    ├── apply_migrations.sh
    └── apply_migrations.ps1
```

## 2. Naming rules

| Thing | Rule | Example |
|-------|------|---------|
| Folder | lowercase, snake_case | `rls-policies/`, `seeds/` |
| Migration file | `NNN_<snake_case>.sql` (3‑digit zero‑padded) | `006_add_options_chain.sql` |
| Rollback file | Same number + `_down.sql` | `006_add_options_chain_down.sql` |
| RLS file | one per table | `trades.sql`, `users.sql` |
| Function file | snake_case verb | `calculate_portfolio_stats.sql` |
| View file | snake_case noun | `portfolio_summary.sql` |

## 3. Adding a new resource — file checklist

1. `migrations/NNN_<name>.sql` — `CREATE TABLE`, indexes, constraints.
2. `migrations/NNN_<name>_down.sql` — paired `DROP …` for destructive changes.
3. `rls-policies/<table>.sql` — `ALTER TABLE … ENABLE ROW LEVEL SECURITY` + policies.
4. `functions/<verb>.sql` (only if a stored proc makes sense).
5. `views/<noun>.sql` (only if it's used by ≥2 queries).
6. Update `schema.sql` if the project keeps a hand‑maintained copy.

## 4. Hard prohibitions

- ❌ Editing an already‑applied migration file — write a new one instead.
- ❌ Running `seeds/` against production.
- ❌ Putting business logic in `rls-policies/` (only access control).
- ❌ Mixing RLS DDL and table DDL in the same file (separation of concerns).
- ❌ Hard‑coding secrets in SQL files (use Supabase Vault / env vars).

---

## See also

- [DATABASE-CODING-STANDARDS.md](./DATABASE-CODING-STANDARDS.md)
- [DATABASE-MIGRATIONS.md](./DATABASE-MIGRATIONS.md)
- [DATABASE-RLS-POLICIES.md](./DATABASE-RLS-POLICIES.md)
- [../../LAYERS/04-DATABASE-LAYER.md](../../LAYERS/04-DATABASE-LAYER.md)
