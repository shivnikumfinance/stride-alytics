-- Rollback for migration 002
BEGIN;
DROP TRIGGER IF EXISTS trg_trades_updated_at      ON trades;
DROP TRIGGER IF EXISTS trg_portfolios_updated_at  ON portfolios;
DROP TRIGGER IF EXISTS trg_users_updated_at      ON users;
DROP TABLE IF EXISTS options   CASCADE;
DROP TABLE IF EXISTS trades    CASCADE;
DROP TABLE IF EXISTS portfolios CASCADE;
DROP TABLE IF EXISTS users     CASCADE;
DROP FUNCTION IF EXISTS set_updated_at();
COMMIT;
