-- Migration 006: drop users.subscription_plan
-- The PRO plan / subscription tier was removed (personal-use scope).
-- Down: 006_drop_subscription_plan_down.sql
-- Risk:  data loss — existing subscription_plan values are discarded. Nothing reads them
--        after this change (backend, frontend and seeds no longer use the column).
BEGIN;
ALTER TABLE users DROP CONSTRAINT IF EXISTS subscription_plan_check;
ALTER TABLE users DROP COLUMN IF EXISTS subscription_plan;
COMMIT;
