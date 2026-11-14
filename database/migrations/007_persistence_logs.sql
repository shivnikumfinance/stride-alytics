-- 007_persistence_logs.sql
-- Phase 1 (persistence + logs):
--   * trades: strike, expiry, strategy, layer, band, risk_amount, credit
--   * user_settings: account size, risk %, guardrails, band caps, regime weights, toggles, disclaimer, gate switch
--   * watchlists, watchlist_items, symbol_flags (manual NewsFlag)
--   * signal_log, audit_events: append-only (RLS owner SELECT/INSERT only + trigger blocks UPDATE/DELETE/TRUNCATE)
-- Down: 007_persistence_logs_down.sql
-- Risk:  additive; the down migration drops the new tables/columns and the data in them.

BEGIN;

-- ===== trades: fields needed for DTE, Greeks, risk and band caps =====
ALTER TABLE trades
    ADD COLUMN IF NOT EXISTS strike      NUMERIC(10, 2),
    ADD COLUMN IF NOT EXISTS expiry      DATE,
    ADD COLUMN IF NOT EXISTS strategy    TEXT,
    ADD COLUMN IF NOT EXISTS layer       TEXT,
    ADD COLUMN IF NOT EXISTS band        TEXT,
    ADD COLUMN IF NOT EXISTS risk_amount NUMERIC(12, 2),
    ADD COLUMN IF NOT EXISTS credit      NUMERIC(10, 4);

ALTER TABLE trades DROP CONSTRAINT IF EXISTS trades_strike_check;
ALTER TABLE trades ADD CONSTRAINT trades_strike_check CHECK (strike IS NULL OR strike > 0);
ALTER TABLE trades DROP CONSTRAINT IF EXISTS trades_layer_check;
ALTER TABLE trades ADD CONSTRAINT trades_layer_check CHECK (layer IS NULL OR layer IN ('base', 'growth'));
ALTER TABLE trades DROP CONSTRAINT IF EXISTS trades_band_check;
ALTER TABLE trades ADD CONSTRAINT trades_band_check CHECK (band IS NULL OR band IN ('A', 'B', 'C', 'D', 'E'));

-- ===== user_settings: risk and rule configuration =====
ALTER TABLE user_settings
    ADD COLUMN IF NOT EXISTS account_size           NUMERIC(14, 2) NOT NULL DEFAULT 100000,
    ADD COLUMN IF NOT EXISTS base_risk_pct          NUMERIC(5, 2)  NOT NULL DEFAULT 1.25,
    ADD COLUMN IF NOT EXISTS growth_risk_pct        NUMERIC(5, 2)  NOT NULL DEFAULT 2.5,
    ADD COLUMN IF NOT EXISTS min_equity             NUMERIC(14, 2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS band_caps              JSONB NOT NULL DEFAULT '{"A": 30, "B": 25, "C": 20, "D": 15, "E": 10}'::jsonb,
    ADD COLUMN IF NOT EXISTS regime_weights         JSONB NOT NULL DEFAULT '{"trend": 40, "vix": 30, "iv_rank": 30}'::jsonb,
    ADD COLUMN IF NOT EXISTS widget_toggles         JSONB NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN IF NOT EXISTS disclaimer_accepted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS enforce_gate           BOOLEAN NOT NULL DEFAULT true;

-- ===== watchlists =====
CREATE TABLE IF NOT EXISTS watchlists (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, name)
);
CREATE INDEX IF NOT EXISTS idx_watchlists_user ON watchlists(user_id);

CREATE TABLE IF NOT EXISTS watchlist_items (
    watchlist_id UUID NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
    symbol       TEXT NOT NULL,
    added_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (watchlist_id, symbol)
);

ALTER TABLE watchlists ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS watchlists_all ON watchlists;
CREATE POLICY watchlists_all ON watchlists
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

ALTER TABLE watchlist_items ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS watchlist_items_all ON watchlist_items;
CREATE POLICY watchlist_items_all ON watchlist_items
    FOR ALL USING (EXISTS (SELECT 1 FROM watchlists w WHERE w.id = watchlist_id AND w.user_id = auth.uid()))
    WITH CHECK (EXISTS (SELECT 1 FROM watchlists w WHERE w.id = watchlist_id AND w.user_id = auth.uid()));

-- ===== symbol_flags (manual NewsFlag, DNT rule BR-021) =====
CREATE TABLE IF NOT EXISTS symbol_flags (
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol     TEXT NOT NULL,
    news_flag  BOOLEAN NOT NULL DEFAULT false,
    note       TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, symbol)
);

DROP TRIGGER IF EXISTS trg_symbol_flags_updated_at ON symbol_flags;
CREATE TRIGGER trg_symbol_flags_updated_at
    BEFORE UPDATE ON symbol_flags
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE symbol_flags ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS symbol_flags_all ON symbol_flags;
CREATE POLICY symbol_flags_all ON symbol_flags
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- ===== append-only logs =====
-- No foreign key on user_id on purpose: deleting a user must not delete (or be blocked by) history.
CREATE TABLE IF NOT EXISTS signal_log (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    kind        TEXT NOT NULL,
    symbol      TEXT,
    rule_id     TEXT,
    decision    TEXT NOT NULL,
    message     TEXT,
    details     JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_signal_log_user_time ON signal_log(user_id, occurred_at DESC);

CREATE TABLE IF NOT EXISTS audit_events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    action      TEXT NOT NULL,
    entity      TEXT NOT NULL,
    entity_id   TEXT,
    before      JSONB,
    after       JSONB
);
CREATE INDEX IF NOT EXISTS idx_audit_events_user_time ON audit_events(user_id, occurred_at DESC);

CREATE OR REPLACE FUNCTION prevent_log_mutation()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION '% is append-only', TG_TABLE_NAME
        USING ERRCODE = 'integrity_constraint_violation';
END;
$$;

DROP TRIGGER IF EXISTS trg_signal_log_immutable ON signal_log;
CREATE TRIGGER trg_signal_log_immutable
    BEFORE UPDATE OR DELETE ON signal_log
    FOR EACH ROW EXECUTE FUNCTION prevent_log_mutation();
DROP TRIGGER IF EXISTS trg_signal_log_no_truncate ON signal_log;
CREATE TRIGGER trg_signal_log_no_truncate
    BEFORE TRUNCATE ON signal_log
    FOR EACH STATEMENT EXECUTE FUNCTION prevent_log_mutation();

DROP TRIGGER IF EXISTS trg_audit_events_immutable ON audit_events;
CREATE TRIGGER trg_audit_events_immutable
    BEFORE UPDATE OR DELETE ON audit_events
    FOR EACH ROW EXECUTE FUNCTION prevent_log_mutation();
DROP TRIGGER IF EXISTS trg_audit_events_no_truncate ON audit_events;
CREATE TRIGGER trg_audit_events_no_truncate
    BEFORE TRUNCATE ON audit_events
    FOR EACH STATEMENT EXECUTE FUNCTION prevent_log_mutation();

-- Owner can read and append; there are deliberately NO update/delete policies.
ALTER TABLE signal_log ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS signal_log_select ON signal_log;
CREATE POLICY signal_log_select ON signal_log FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS signal_log_insert ON signal_log;
CREATE POLICY signal_log_insert ON signal_log FOR INSERT WITH CHECK (auth.uid() = user_id);

ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS audit_events_select ON audit_events;
CREATE POLICY audit_events_select ON audit_events FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS audit_events_insert ON audit_events;
CREATE POLICY audit_events_insert ON audit_events FOR INSERT WITH CHECK (auth.uid() = user_id);

COMMIT;
