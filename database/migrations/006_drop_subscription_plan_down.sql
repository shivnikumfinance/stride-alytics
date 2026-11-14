-- Rollback for migration 006 (restores the column; previous values are not recoverable)
BEGIN;
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_plan TEXT NOT NULL DEFAULT 'free';
ALTER TABLE users
    ADD CONSTRAINT subscription_plan_check
    CHECK (subscription_plan IN ('free', 'pro'));
COMMIT;
