-- 010_scenarios.sql
-- Saved portfolio scenarios / stress tests (FR-530): a name plus the shocks to apply.
-- Down: 010_scenarios_down.sql
-- Risk:  additive; the down migration drops the table and the saved scenarios.

BEGIN;

CREATE TABLE IF NOT EXISTS scenarios (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name       TEXT NOT NULL,
    params     JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, name)
);

CREATE INDEX IF NOT EXISTS idx_scenarios_user ON scenarios(user_id, created_at DESC);

ALTER TABLE scenarios ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS scenarios_all ON scenarios;
CREATE POLICY scenarios_all ON scenarios
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

COMMIT;
