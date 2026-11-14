-- 009_alert_acks.sql
-- Acknowledgements for exit/risk alerts (BR-096, BR-098): a Critical alert stays "unacknowledged"
-- until the user acknowledges it; an acknowledgement is resolved when the condition clears or the
-- position is closed, so a recurrence has to be acknowledged again.
-- Down: 009_alert_acks_down.sql
-- Risk:  additive; the down migration drops the table and the acknowledgement history.

BEGIN;

CREATE TABLE IF NOT EXISTS alert_acks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    trade_id        UUID NOT NULL REFERENCES trades(id) ON DELETE CASCADE,
    code            TEXT NOT NULL,
    severity        TEXT NOT NULL CHECK (severity IN ('watch', 'warning', 'critical')),
    note            TEXT,
    acknowledged_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_alert_acks_user ON alert_acks(user_id, acknowledged_at DESC);
-- At most one unresolved acknowledgement per user, trade and alert code.
CREATE UNIQUE INDEX IF NOT EXISTS uq_alert_acks_active
    ON alert_acks(user_id, trade_id, code) WHERE resolved_at IS NULL;

ALTER TABLE alert_acks ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS alert_acks_all ON alert_acks;
CREATE POLICY alert_acks_all ON alert_acks
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

COMMIT;
