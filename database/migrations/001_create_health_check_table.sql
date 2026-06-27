-- Phase 0: Migration 001 — Create a simple health_check table
-- to verify database connectivity and migration tooling.

CREATE TABLE IF NOT EXISTS health_check (
    id          SERIAL PRIMARY KEY,
    checked_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    service     VARCHAR(64) NOT NULL DEFAULT 'backend',
    status      VARCHAR(16) NOT NULL DEFAULT 'ok'
);

-- Seed a single row so we can confirm the table is working.
INSERT INTO health_check (service, status)
VALUES ('migration', 'ok')
ON CONFLICT DO NOTHING;