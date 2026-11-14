-- Rollback for migration 007 (drops the new tables/columns and the data in them)
BEGIN;

DROP TRIGGER IF EXISTS trg_audit_events_no_truncate  ON audit_events;
DROP TRIGGER IF EXISTS trg_audit_events_immutable    ON audit_events;
DROP TRIGGER IF EXISTS trg_signal_log_no_truncate ON signal_log;
DROP TRIGGER IF EXISTS trg_signal_log_immutable   ON signal_log;
DROP FUNCTION IF EXISTS prevent_log_mutation();

DROP TABLE IF EXISTS audit_events       CASCADE;
DROP TABLE IF EXISTS signal_log      CASCADE;
DROP TABLE IF EXISTS symbol_flags    CASCADE;
DROP TABLE IF EXISTS watchlist_items CASCADE;
DROP TABLE IF EXISTS watchlists      CASCADE;

ALTER TABLE user_settings
    DROP COLUMN IF EXISTS enforce_gate,
    DROP COLUMN IF EXISTS disclaimer_accepted_at,
    DROP COLUMN IF EXISTS widget_toggles,
    DROP COLUMN IF EXISTS regime_weights,
    DROP COLUMN IF EXISTS band_caps,
    DROP COLUMN IF EXISTS min_equity,
    DROP COLUMN IF EXISTS growth_risk_pct,
    DROP COLUMN IF EXISTS base_risk_pct,
    DROP COLUMN IF EXISTS account_size;

ALTER TABLE trades DROP CONSTRAINT IF EXISTS trades_band_check;
ALTER TABLE trades DROP CONSTRAINT IF EXISTS trades_layer_check;
ALTER TABLE trades DROP CONSTRAINT IF EXISTS trades_strike_check;
ALTER TABLE trades
    DROP COLUMN IF EXISTS credit,
    DROP COLUMN IF EXISTS risk_amount,
    DROP COLUMN IF EXISTS band,
    DROP COLUMN IF EXISTS layer,
    DROP COLUMN IF EXISTS strategy,
    DROP COLUMN IF EXISTS expiry,
    DROP COLUMN IF EXISTS strike;

COMMIT;
