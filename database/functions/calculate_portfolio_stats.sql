-- Stored procedure: calculate portfolio statistics
CREATE OR REPLACE FUNCTION calculate_portfolio_stats(p_portfolio_id UUID)
RETURNS TABLE (
    total_trades BIGINT,
    open_trades BIGINT,
    total_pnl NUMERIC,
    win_rate NUMERIC,
    avg_win NUMERIC,
    avg_loss NUMERIC
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT AS total_trades,
        COUNT(*) FILTER (WHERE exit_price IS NULL)::BIGINT AS open_trades,
        COALESCE(SUM(CASE WHEN exit_price IS NOT NULL THEN (exit_price - entry_price) * quantity ELSE 0 END), 0) AS total_pnl,
        CASE
            WHEN COUNT(*) FILTER (WHERE exit_price IS NOT NULL) > 0 THEN
                ROUND(
                    (COUNT(*) FILTER (WHERE exit_price > entry_price)::NUMERIC /
                     COUNT(*) FILTER (WHERE exit_price IS NOT NULL)::NUMERIC) * 100, 2
                )
            ELSE 0
        END AS win_rate,
        COALESCE(
            AVG(CASE WHEN exit_price > entry_price THEN (exit_price - entry_price) * quantity END), 0
        ) AS avg_win,
        COALESCE(
            AVG(CASE WHEN exit_price <= entry_price THEN (exit_price - entry_price) * quantity END), 0
        ) AS avg_loss
    FROM trades
    WHERE portfolio_id = p_portfolio_id;
END;
$$;