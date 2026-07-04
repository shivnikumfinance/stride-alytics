-- Alpha Option Trading System — Supabase Schema
-- Create all tables required for ingestion, scoring, bands, trades, watchlist, and audit logs.

-- ─────────────────────────────────────────────
-- 1. daily_metrics — Raw daily ingestion data
-- ─────────────────────────────────────────────
create table if not exists daily_metrics (
    id bigint generated always as identity primary key,
    date text not null,
    ticker text not null,

    -- yfinance
    price numeric,
    hv_30d numeric,
    next_earnings_date text,
    sector text,

    -- polygon
    option_volume numeric,
    max_oi_near_exp numeric,
    bid_ask_spread_pct numeric,
    iv_30d numeric,
    iv_rank_1y numeric,
    atr numeric,

    -- fmp
    revenue_growth_yoy numeric,
    debt_equity numeric,
    quality_score numeric,

    -- massive (optional)
    float_shares numeric,
    beta numeric,

    inserted_at timestamp default now()
);

create index if not exists idx_daily_metrics_ticker on daily_metrics(ticker);
create index if not exists idx_daily_metrics_date on daily_metrics(date);


-- ─────────────────────────────────────────────
-- 2. option_scores — Daily scoring results
-- ─────────────────────────────────────────────
create table if not exists option_scores (
    id bigint generated always as identity primary key,
    date text not null,
    ticker text not null,
    option_score numeric,
    trend text,
    strategy text,
    inserted_at timestamp default now()
);

create index if not exists idx_option_scores_ticker on option_scores(ticker);
create index if not exists idx_option_scores_date on option_scores(date);


-- ─────────────────────────────────────────────
-- 3. bands — Daily band classification (A–E)
-- ─────────────────────────────────────────────
create table if not exists bands (
    id bigint generated always as identity primary key,
    date text not null,
    ticker text not null,
    band text,
    inserted_at timestamp default now()
);

create index if not exists idx_bands_ticker on bands(ticker);
create index if not exists idx_bands_date on bands(date);


-- ─────────────────────────────────────────────
-- 4. weekly_watchlist — Weekly top picks
-- ─────────────────────────────────────────────
create table if not exists weekly_watchlist (
    id bigint generated always as identity primary key,
    date text not null,
    ticker text not null,
    price numeric,
    option_score numeric,
    trend text,
    strategy text,
    iv_rank_1y numeric,
    next_earnings_date text,
    inserted_at timestamp default now()
);

create index if not exists idx_weekly_watchlist_ticker on weekly_watchlist(ticker);
create index if not exists idx_weekly_watchlist_date on weekly_watchlist(date);


-- ─────────────────────────────────────────────
-- 5. trades — Trade log
-- ─────────────────────────────────────────────
create table if not exists trades (
    id bigint generated always as identity primary key,
    date text not null,
    ticker text not null,
    strategy text,
    entry_strikes text,
    expiry text,
    credit_debit numeric,
    reason text,
    exit_plan text,
    inserted_at timestamp default now()
);

create index if not exists idx_trades_ticker on trades(ticker);
create index if not exists idx_trades_date on trades(date);


-- ─────────────────────────────────────────────
-- 6. audit_log — System events
-- ─────────────────────────────────────────────
create table if not exists audit_log (
    id bigint generated always as identity primary key,
    timestamp text not null,
    event text not null
);

create index if not exists idx_audit_log_timestamp on audit_log(timestamp);