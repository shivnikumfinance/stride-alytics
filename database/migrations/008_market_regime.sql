-- 008_market_regime.sql
-- Daily market regime score (0-100) shared by all users; written by the backend/scheduler with the
-- default weights, read by everyone. Used for the regime history and boundary-change detection.
-- Down: 008_market_regime_down.sql
-- Risk:  additive; the down migration drops the table and its history.

BEGIN;

CREATE TABLE IF NOT EXISTS market_regime (
    as_of       DATE PRIMARY KEY,
    score       NUMERIC(5, 1) CHECK (score IS NULL OR score BETWEEN 0 AND 100),
    state       TEXT NOT NULL CHECK (state IN ('DEFENSIVE', 'NORMAL', 'GROWTH', 'UNKNOWN')),
    components  JSONB NOT NULL DEFAULT '{}'::jsonb,
    weights     JSONB NOT NULL DEFAULT '{}'::jsonb,
    vix         NUMERIC(6, 2),
    iv_rank     NUMERIC(5, 1),
    market_down BOOLEAN,
    source      TEXT NOT NULL DEFAULT 'live',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_market_regime_asof ON market_regime(as_of DESC);

-- Everyone can read the regime history; there are no client write policies, so only the backend
-- (database role) and the scheduler (service role) can insert or update.
ALTER TABLE market_regime ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS market_regime_read ON market_regime;
CREATE POLICY market_regime_read ON market_regime
    FOR SELECT TO anon, authenticated USING (true);

COMMIT;
