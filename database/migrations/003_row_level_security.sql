-- Migration 003: Row-Level Security policies
-- Mirrors database/rls-policies/*.sql but bundled as a single migration
-- for ease of atomic apply on hosted Supabase.

BEGIN;

-- ===== users =====
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS users_select ON users;
CREATE POLICY users_select ON users
    FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS users_update ON users;
CREATE POLICY users_update ON users
    FOR UPDATE USING (auth.uid() = id) WITH CHECK (auth.uid() = id);

-- No INSERT/DELETE on users from clients; service_role only.

-- ===== portfolios =====
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS portfolios_select ON portfolios;
CREATE POLICY portfolios_select ON portfolios
    FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS portfolios_insert ON portfolios;
CREATE POLICY portfolios_insert ON portfolios
    FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS portfolios_update ON portfolios;
CREATE POLICY portfolios_update ON portfolios
    FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS portfolios_delete ON portfolios;
CREATE POLICY portfolios_delete ON portfolios
    FOR DELETE USING (auth.uid() = user_id);

-- ===== trades =====
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS trades_select ON trades;
CREATE POLICY trades_select ON trades
    FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS trades_insert ON trades;
CREATE POLICY trades_insert ON trades
    FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS trades_update ON trades;
CREATE POLICY trades_update ON trades
    FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS trades_delete ON trades;
CREATE POLICY trades_delete ON trades
    FOR DELETE USING (auth.uid() = user_id);

-- ===== options (public read, service_role write) =====
ALTER TABLE options ENABLE ROW LEVEL SECURITY;

-- Anyone (incl. anonymous) can read the public screener cache.
DROP POLICY IF EXISTS options_select_anon ON options;
CREATE POLICY options_select_anon ON options
    FOR SELECT TO anon, authenticated USING (true);

-- No client INSERT/UPDATE/DELETE on options; populated by the scheduler
-- using the service_role key.

COMMIT;
