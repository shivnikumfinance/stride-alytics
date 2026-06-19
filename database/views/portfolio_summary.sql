-- Database view: portfolio summary with aggregated analytics
CREATE OR REPLACE VIEW portfolio_summary AS
SELECT
    p.id,
    p.user_id,
    p.name,
    COUNT(t.id)::BIGINT AS total_trades,
    COUNT(t.id) FILTER (WHERE t.exit_price IS NULL)::BIGINT AS open_trades,
    COALESCE(SUM(CASE
        WHEN t.exit_price IS NOT NULL THEN (t.exit_price - t.entry_price) * t.quantity
        ELSE 0
    END), 0)::NUMERIC(12,2) AS total_pnl,
    p.created_at,
    p.updated_at
FROM portfolios p
LEFT JOIN trades t ON p.id = t.portfolio_id
GROUP BY p.id, p.user_id, p.name, p.created_at, p.updated_at;