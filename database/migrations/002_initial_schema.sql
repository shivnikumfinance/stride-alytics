-- Migration 002: Initial schema (users, portfolios, trades, options)
-- Reversible: see 002_initial_schema_down.sql
-- Run: psql -d stridealytics -f database/migrations/002_initial_schema.sql

BEGIN;

-- ---------- USERS ----------
CREATE TABLE IF NOT EXISTS users (
    id                  UUID PRIMARY KEY DEFAULT auth.uid(),
    email               TEXT UNIQUE NOT NULL,
    full_name           TEXT,
    avatar_url          TEXT,
    subscription_plan   TEXT NOT NULL DEFAULT 'free',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT subscription_plan_check
        CHECK (subscription_plan IN ('free', 'pro'))
);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------- PORTFOLIOS ----------
CREATE TABLE IF NOT EXISTS portfolios (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name         TEXT NOT NULL,
    description  TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, name)
);

DROP TRIGGER IF EXISTS trg_portfolios_updated_at ON portfolios;
CREATE TRIGGER trg_portfolios_updated_at
    BEFORE UPDATE ON portfolios
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------- TRADES ----------
CREATE TABLE IF NOT EXISTS trades (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES users(id)       ON DELETE CASCADE,
    portfolio_id  UUID NOT NULL REFERENCES portfolios(id)  ON DELETE CASCADE,
    symbol        TEXT NOT NULL,
    trade_type    TEXT NOT NULL,
    direction     TEXT NOT NULL,
    entry_price   NUMERIC(10, 2) NOT NULL CHECK (entry_price  > 0),
    exit_price    NUMERIC(10, 2)            CHECK (exit_price IS NULL OR exit_price > 0),
    quantity      INTEGER      NOT NULL CHECK (quantity     > 0),
    entry_date    TIMESTAMPTZ  NOT NULL,
    exit_date     TIMESTAMPTZ,
    notes         TEXT,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT trade_type_check CHECK (trade_type IN ('call', 'put', 'stock')),
    CONSTRAINT direction_check  CHECK (direction  IN ('long', 'short')),
    CONSTRAINT exit_after_entry CHECK (exit_date IS NULL OR exit_date >= entry_date)
);

DROP TRIGGER IF EXISTS trg_trades_updated_at ON trades;
CREATE TRIGGER trg_trades_updated_at
    BEFORE UPDATE ON trades
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------- OPTIONS (screener cache) ----------
CREATE TABLE IF NOT EXISTS options (
    symbol        TEXT           NOT NULL,
    strike        NUMERIC(10, 2) NOT NULL,
    expiry        DATE           NOT NULL,
    option_type   TEXT           NOT NULL,
    bid           NUMERIC(10, 4),
    ask           NUMERIC(10, 4),
    last_price    NUMERIC(10, 4),
    implied_vol   NUMERIC(5, 4),
    delta         NUMERIC(5, 4),
    gamma         NUMERIC(7, 6),
    theta         NUMERIC(5, 4),
    vega          NUMERIC(5, 4),
    rho           NUMERIC(5, 4),
    open_interest INTEGER,
    volume        INTEGER,
    updated_at    TIMESTAMPTZ    NOT NULL DEFAULT now(),
    PRIMARY KEY (symbol, strike, expiry, option_type),
    CONSTRAINT options_type_check CHECK (option_type IN ('call', 'put')),
    CONSTRAINT options_strike_check CHECK (strike > 0)
);

COMMIT;
