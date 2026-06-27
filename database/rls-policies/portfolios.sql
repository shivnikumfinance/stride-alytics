-- RLS policies for portfolios table

ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;

-- Users can only see their own portfolios
CREATE POLICY portfolios_select ON portfolios
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only insert their own portfolios
CREATE POLICY portfolios_insert ON portfolios
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own portfolios
CREATE POLICY portfolios_update ON portfolios
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can delete their own portfolios
CREATE POLICY portfolios_delete ON portfolios
    FOR DELETE
    USING (auth.uid() = user_id);