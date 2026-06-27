-- Migration 004: Performance indexes + supporting view + helper function
-- Run AFTER 002 + 003.

BEGIN;

-- ===== Indexes =====
CREATE INDEX IF NOT EXISTS idx_portfolios_user_id     ON portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_trades_user_id        ON trades(user_id);
CREATE INDEX IF NOT EXISTS idx_trades_portfolio_id   ON trades(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol         ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_entry_date     ON trades(entry_date DESC);
CREATE INDEX IF NOT EXISTS idx_options_symbol        ON options(symbol);
CREATE INDEX IF NOT EXISTS idx_options_expiry        ON options(expiry);
CREATE INDEX IF NOT EXISTS idx_options_symbol_expiry ON options(symbol, expiry);
CREATE INDEX IF NOT EXISTS idx_options_iv            ON options(implied_vol) WHERE implied_vol IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_options_volume        ON options(volume)       WHERE volume       IS NOT NULL;

-- ===== View: portfolio summary =====
CREATE OR REPLACE VIEW portfolio_summary AS
SELECT
    p.id,
    p.user_id,
    p.name,
    COUNT(t.id)::BIGINT                                            AS total_trades,
    COUNT(t.id) FILTER (WHERE t.exit_price IS NULL)::BIGINT         AS open_trades,
    COALESCE(SUM(CASE
        WHEN t.exit_price IS NOT NULL
        THEN (t.exit_price - t.entry_price) * t.quantity
            * CASE WHEN t.direction = 'short' THEN -1 ELSE 1 END
        ELSE 0
    END), 0)::NUMERIC(12, 2)                                       AS total_pnl,
    p.created_at,
    p.updated_at
FROM portfolios p
LEFT JOIN trades t ON p.id = t.portfolio_id
GROUP BY p.id, p.user_id, p.name, p.created_at, p.updated_at;

-- ===== Function: portfolio stats (advanced) =====
CREATE OR REPLACE FUNCTION calculate_portfolio_stats(p_portfolio_id UUID)
RETURNS TABLE (
    total_trades BIGINT,
    open_trades  BIGINT,
    total_pnl    NUMERIC,
    win_rate     NUMERIC,
    avg_win      NUMERIC,
    avg_loss     NUMERIC
) LANGUAGE plpgsql STABLE AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT AS total_trades,
        COUNT(*) FILTER (WHERE exit_price IS NULL)::BIGINT AS open_trades,
        COALESCE(SUM(
            CASE WHEN exit_price IS NOT NULL
                 THEN (exit_price - entry_price) * quantity
                      * CASE WHEN direction = 'short' THEN -1 ELSE 1 END
                 ELSE 0 END
        ), 0) AS total_pnl,
        CASE
            WHEN COUNT(*) FILTER (WHERE exit_price IS NOT NULL) > 0 THEN
                ROUND(
                    100.0 * COUNT(*) FILTER (
                        WHERE exit_price IS NOT NULL
                          AND (CASE WHEN direction = 'short' THEN entry_price - exit_price
                                    ELSE exit_price - entry_price END) > 0
                    )::NUMERIC / COUNT(*) FILTER (WHERE exit_price IS NOT NULL)::NUMERIC,
                    2
                )
            ELSE 0
        END AS win_rate,
        COALESCE(AVG(
            CASE WHEN exit_price IS NOT NULL
                  AND (CASE WHEN direction = 'short' THEN entry_price - exit_price
                            ELSE exit_price - entry_price END) > 0
                 THEN (exit_price - entry_price) * quantity
                      * CASE WHEN direction = 'short' THEN -1 ELSE 1 END
            END
        ), 0) AS avg_win,
        COALESCE(AVG(
            CASE WHEN exit_price IS NOT NULL
                  AND (CASE WHEN direction = 'short' THEN entry_price - exit_price
                            ELSE exit_price - entry_price END) <= 0
                 THEN (exit_price - entry_price) * quantity
                      * CASE WHEN direction = 'short' THEN -1 ELSE 1 END
            END
        ), 0) AS avg_loss
    FROM trades
    WHERE portfolio_id = p_portfolio_id;
END;
$$;

COMMIT;
