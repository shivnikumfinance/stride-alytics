-- RLS policies for trades table

ALTER TABLE trades ENABLE ROW LEVEL SECURITY;

-- Users can only see their own trades
CREATE POLICY trades_select ON trades
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own trades
CREATE POLICY trades_insert ON trades
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own trades
CREATE POLICY trades_update ON trades
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can delete their own trades
CREATE POLICY trades_delete ON trades
    FOR DELETE
    USING (auth.uid() = user_id);