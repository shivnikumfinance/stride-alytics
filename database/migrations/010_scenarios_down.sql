-- Rollback for migration 010 (drops saved scenarios)
BEGIN;
DROP TABLE IF EXISTS scenarios CASCADE;
COMMIT;
