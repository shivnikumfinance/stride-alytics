-- symbols: static metadata
CREATE TABLE public.symbols (
  id SERIAL PRIMARY KEY,
  ticker TEXT UNIQUE NOT NULL,
  sector TEXT,
  market_cap NUMERIC,
  quality_score INTEGER
);

-- daily_metrics: per-ticker per-day metrics
CREATE TABLE public.daily_metrics (
  id SERIAL PRIMARY KEY,
  ticker TEXT NOT NULL,
  date DATE NOT NULL,
  price NUMERIC,
  avg_volume_shares NUMERIC,
  option_volume NUMERIC,
  max_oi_near_exp NUMERIC,
  bid_ask_spread_pct NUMERIC,
  iv_30d NUMERIC,
  iv_rank_1y NUMERIC,
  hv_30d NUMERIC,
  atr NUMERIC,
  trend TEXT,
  next_earnings_date DATE,
  short_interest_pct NUMERIC,
  revenue_growth_yoy NUMERIC,
  debt_equity NUMERIC,
  quality_score INTEGER,
  band TEXT,
  CONSTRAINT daily_metrics_ticker_date_unique UNIQUE (ticker, date)
);

-- option_scores: per-ticker per-day score
CREATE TABLE public.option_scores (
  id SERIAL PRIMARY KEY,
  ticker TEXT NOT NULL,
  date DATE NOT NULL,
  option_score INTEGER NOT NULL,
  band TEXT,
  CONSTRAINT option_scores_ticker_date_unique UNIQUE (ticker, date)
);

-- signals: buy/sell premium signals
CREATE TABLE public.signals (
  id SERIAL PRIMARY KEY,
  ticker TEXT NOT NULL,
  date DATE NOT NULL,
  signal_type TEXT,
  reason TEXT
);

-- trades: trade log + P&L
CREATE TABLE public.trades (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL,
  ticker TEXT NOT NULL,
  strategy TEXT,
  entry_strikes TEXT,
  expiry DATE,
  credit_debit TEXT,
  reason TEXT,
  exit_plan TEXT,
  exit_date DATE,
  exit_price NUMERIC,
  pnl NUMERIC
);

-- audit_log: changes / events
CREATE TABLE public.audit_log (
  id SERIAL PRIMARY KEY,
  event_time TIMESTAMP DEFAULT NOW(),
  entity TEXT,
  entity_id INTEGER,
  action TEXT,
  details TEXT
);

CREATE INDEX idx_daily_metrics_ticker_date ON public.daily_metrics (ticker, date);
CREATE INDEX idx_option_scores_ticker_date ON public.option_scores (ticker, date);
CREATE INDEX idx_trades_ticker_date ON public.trades (ticker, date);