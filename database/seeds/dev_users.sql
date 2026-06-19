-- Seed data for development environment
-- Run: psql -d stridealytics -f seeds/dev_users.sql

INSERT INTO users (id, email, full_name, subscription_plan)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'dev@stridealytics.com', 'Dev User', 'pro'),
    ('00000000-0000-0000-0000-000000000002', 'test@stridealytics.com', 'Test User', 'free')
ON CONFLICT (id) DO NOTHING;

INSERT INTO portfolios (id, user_id, name, description)
VALUES
    ('10000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'Main Portfolio', 'My primary trading portfolio'),
    ('10000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'Swing Trades', 'Swing trading positions')
ON CONFLICT (id) DO NOTHING;