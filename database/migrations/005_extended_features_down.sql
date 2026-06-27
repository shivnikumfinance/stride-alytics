-- Rollback for migration 005
BEGIN;
DROP TRIGGER IF EXISTS trg_users_create_settings ON users;
DROP FUNCTION IF EXISTS create_default_user_settings();
DROP TABLE IF EXISTS screener_history CASCADE;
DROP TABLE IF EXISTS weekly_picks     CASCADE;
DROP TABLE IF EXISTS user_settings    CASCADE;
COMMIT;
