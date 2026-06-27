-- RLS policies for users table

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Users can read their own record
CREATE POLICY users_select ON users
    FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own record
CREATE POLICY users_update ON users
    FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);