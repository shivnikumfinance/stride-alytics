# StrideAlytics Database

PostgreSQL schema, migrations, RLS policies, views, functions, and seed
data for the StrideAlytics platform. Targets **Supabase (Postgres 15+)**.

## Layout

```
database/
├── schema.sql                    # Full schema dump (for reference)
├── migrations/                   # Numbered, ordered, reversible migrations
│   ├── 001_create_health_check_table.sql
│   ├── 001_create_health_check_table_down.sql
│   ├── 002_initial_schema.sql          # users, portfolios, trades, options
│   ├── 002_initial_schema_down.sql
│   ├── 003_row_level_security.sql      # RLS policies for all tables
│   ├── 004_indexes_views_functions.sql # Performance indexes + view + fn
│   ├── 005_extended_features.sql       # user_settings, weekly_picks, screener_history
│   └── 005_extended_features_down.sql
├── rls-policies/                 # Individual RLS files (mirror migration 003)
│   ├── users.sql
│   ├── portfolios.sql
│   ├── trades.sql
├── views/                        # Materialized view definitions
│   └── portfolio_summary.sql
├── functions/                    # Stored procedure definitions
│   └── calculate_portfolio_stats.sql
├── seeds/                        # Dev-only seed data (NEVER for production)
│   └── dev_users.sql
└── scripts/                      # CLI helpers
    ├── apply_migrations.sh
    └── apply_migrations.ps1
```

## Apply migrations

### Supabase (hosted)

The CI workflow [`.github/workflows/database-migrate.yml`](../.github/workflows/database-migrate.yml)
runs `npx supabase db push` on push to `main`. You can also trigger it
manually via the Actions tab → "Database Migrate" → Run workflow.

### Local (docker-compose)

```bash
# Start Postgres
docker compose -f infra/docker/docker-compose.yml up db -d

# Apply every migration in order
./database/scripts/apply_migrations.sh
# or on Windows
.\database\scripts\apply_migrations.ps1
```

### Direct psql

```bash
psql "$DATABASE_URL" -f database/migrations/002_initial_schema.sql
psql "$DATABASE_URL" -f database/migrations/003_row_level_security.sql
psql "$DATABASE_URL" -f database/migrations/004_indexes_views_functions.sql
psql "$DATABASE_URL" -f database/migrations/005_extended_features.sql
```

## Tables

| Table              | Owner  | RLS                  | Purpose                          |
|--------------------|--------|----------------------|----------------------------------|
| `users`            | self   | SELECT/UPDATE self   | Auth-linked user profile         |
| `portfolios`       | self   | full CRUD self       | Group of trades per user         |
| `trades`           | self   | full CRUD self       | Individual trade records         |
| `options`          | public | SELECT public        | Screener cache (read-only)       |
| `user_settings`    | self   | all self             | Per-user preferences             |
| `weekly_picks`     | public | SELECT public        | Sunday picks (service writes)    |
| `screener_history` | self   | all self             | Saved screener presets           |
| `health_check`     | public | none                 | Migration smoke row              |

## Key queries

```sql
-- Win rate per portfolio
SELECT * FROM calculate_portfolio_stats('00000000-0000-0000-0000-000000000001');

-- Portfolio summary (denormalized)
SELECT * FROM portfolio_summary WHERE user_id = auth.uid();

-- Active screener results for a ticker
SELECT * FROM options
WHERE symbol = 'AAPL'
  AND expiry BETWEEN current_date AND current_date + interval '60 days'
ORDER BY strike;
```

## Seeding (dev only)

```bash
psql "$DATABASE_URL" -f database/seeds/dev_users.sql
```

> ⚠️ Never run `seeds/*.sql` against staging or production. The seed
> UUIDs (`00000000-...`) are reserved for development fixtures.

## Rollback

Every migration has a matching `*_down.sql`. To reverse:

```bash
psql "$DATABASE_URL" -f database/migrations/005_extended_features_down.sql
psql "$DATABASE_URL" -f database/migrations/004_indexes_views_functions_down.sql  # if exists
psql "$DATABASE_URL" -f database/migrations/003_row_level_security_down.sql        # if exists
psql "$DATABASE_URL" -f database/migrations/002_initial_schema_down.sql
```

## Testing

The SQL syntax tests in [backend/tests/test_db_sql.py](../backend/tests/test_db_sql.py)
validate every migration file parses cleanly and is reversible.
