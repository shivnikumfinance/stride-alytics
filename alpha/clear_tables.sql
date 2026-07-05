-- CRITICAL: Run this SQL in Supabase SQL editor to clear ALL data and update schema

-- Clear all duplicate data
TRUNCATE TABLE daily_metrics;
TRUNCATE TABLE option_scores;
TRUNCATE TABLE bands;
TRUNCATE TABLE weekly_watchlist;

-- Add all required columns to daily_metrics (if missing)
ALTER TABLE daily_metrics ADD COLUMN IF NOT EXISTS avg_volume_shares numeric;
ALTER TABLE daily_metrics ADD COLUMN IF NOT EXISTS short_interest_pct numeric;
ALTER TABLE daily_metrics ADD COLUMN IF NOT EXISTS market_cap numeric;
ALTER TABLE daily_metrics ADD COLUMN IF NOT EXISTS option_score numeric;
ALTER TABLE daily_metrics ADD COLUMN IF NOT EXISTS band text;
ALTER TABLE daily_metrics ADD COLUMN IF NOT EXISTS trend text;
ALTER TABLE daily_metrics ADD COLUMN IF NOT EXISTS strategy text;

-- Verify tables are empty
SELECT COUNT(*) FROM daily_metrics;
SELECT COUNT(*) FROM option_scores;
SELECT COUNT(*) FROM bands;
SELECT COUNT(*) FROM weekly_watchlist;