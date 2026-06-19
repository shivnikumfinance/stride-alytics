-- StrideAlytics Complete Schema
-- Generated from blueprint: tables, indexes, RLS, views, functions

BEGIN;

-- ===== TABLES =====

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT auth.uid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    subscription_plan TEXT DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT subscription_plan_check
        CHECK (subscription_plan IN ('free', 'pro'))
);

CREATE TABLE IF NOT EXISTS portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, name)
);

CREATE TABLE IF NOT EXISTS trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    trade_type TEXT NOT NULL,
    direction TEXT NOT NULL,
    entry_price DECIMAL(10,2) NOT NULL,
    exit_price DECIMAL(10,2),
    quantity INTEGER NOT NULL,
    entry_date TIMESTAMPTZ NOT NULL,
    exit_date TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT trade_type_check CHECK (trade_type IN ('call', 'put', 'stock')),
    CONSTRAINT direction_check CHECK (direction IN ('long', 'short'))
);

CREATE TABLE IF NOT EXISTS options (
    symbol TEXT NOT NULL,
    strike DECIMAL(10,2) NOT NULL,
    expiry DATE NOT NULL,
    option_type TEXT NOT NULL,
    bid DECIMAL(10,4),
    ask DECIMAL(10,4),
    last_price DECIMAL(10,4),
    implied_vol DECIMAL(5,4),
    delta DECIMAL(5,4),
    gamma DECIMAL(7,6),
    theta DECIMAL(5,4),
    vega DECIMAL(5,4),
    rho DECIMAL(5,4),
    open_interest INTEGER,
    volume INTEGER,
    updated_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (symbol, strike, expiry, option_type)
);

CREATE TABLE IF NOT EXISTS health_check (
    id SERIAL PRIMARY KEY,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    service VARCHAR(64) NOT NULL DEFAULT 'backend',
    status VARCHAR(16) NOT NULL DEFAULT 'ok'
);

-- ===== INDEXES =====
CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id);
CREATE INDEX IF NOT EXISTS idx_trades_portfolio_id ON trades(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_options_symbol ON options(symbol);
CREATE INDEX IF NOT EXISTS idx_options_expiry ON options(expiry);

COMMIT;