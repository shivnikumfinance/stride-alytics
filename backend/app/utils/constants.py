"""Application-wide constants."""

# --- API ---
API_V1_PREFIX: str = "/api/v1"
FREE_TIER_SCREENER_LIMIT: int = 50
PRO_TIER_SCREENER_LIMIT: int = 10_000
FREE_TIER_REGIME_PER_DAY: int = 1

# --- Default Greeks inputs ---
DEFAULT_RISK_FREE_RATE: float = 0.05
DEFAULT_VOLATILITY: float = 0.20
TRADING_DAYS_PER_YEAR: int = 252

# --- Market regime thresholds (used by services/regime.py) ---
REGIME_BULL_THRESHOLD: float = 0.02  # +2% over lookback = bull
REGIME_BEAR_THRESHOLD: float = -0.02  # -2% over lookback = bear

# --- Cache / freshness ---
SCREENER_CACHE_TTL_SECONDS: int = 300  # 5 min
GREEKS_CACHE_TTL_SECONDS: int = 600  # 10 min
REGIME_CACHE_TTL_SECONDS: int = 3600  # 1 hour
