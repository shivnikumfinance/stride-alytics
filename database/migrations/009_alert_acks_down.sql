-- Rollback for migration 009 (drops the acknowledgement history)
BEGIN;
DROP TABLE IF EXISTS alert_acks CASCADE;
COMMIT;
