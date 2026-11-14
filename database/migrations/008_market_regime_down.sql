-- Rollback for migration 008 (drops the regime history)
BEGIN;
DROP TABLE IF EXISTS market_regime CASCADE;
COMMIT;
