-- Minimal stand-in for the Supabase pieces the migrations rely on, so they can be applied to a
-- plain PostgreSQL (for example a throwaway Docker container) for testing. NOT for Supabase itself.
--
--   docker run -d --name stride-smoke -e POSTGRES_PASSWORD=smoke -e POSTGRES_DB=smoke -p 55432:5432 postgres:16-alpine
--   docker exec -i stride-smoke psql -U postgres -d smoke -v ON_ERROR_STOP=1 < database/scripts/local_supabase_shim.sql
--   for f in $(ls database/migrations/[0-9]*.sql | grep -v _down | sort); do
--     docker exec -i stride-smoke psql -U postgres -d smoke -v ON_ERROR_STOP=1 -q < $f; done
--   cd backend && TEST_PG_URL=postgresql://postgres:smoke@localhost:55432/smoke uv run pytest tests -q
--   SMOKE_DB_URL=postgresql://postgres:smoke@localhost:55432/smoke uv run python scripts/smoke_db.py --disposable

CREATE SCHEMA IF NOT EXISTS auth;

CREATE OR REPLACE FUNCTION auth.uid() RETURNS uuid
LANGUAGE sql STABLE AS $$
    SELECT nullif(current_setting('request.jwt.claim.sub', true), '')::uuid
$$;

DO $$ BEGIN CREATE ROLE anon NOLOGIN; EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE ROLE service_role NOLOGIN; EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE ROLE authenticated NOLOGIN; EXCEPTION WHEN duplicate_object THEN NULL; END $$;
