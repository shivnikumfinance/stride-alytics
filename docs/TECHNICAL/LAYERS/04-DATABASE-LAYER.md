# StrideAlytics — Database Layer

**Supabase PostgreSQL + Auth database architecture**

---

## Overview

The **Database Layer** provides persistent data storage, user authentication, and authorization using Supabase (PostgreSQL-based platform as a service).

**Key Characteristics:**
- ✅ PostgreSQL 15+ relational database
- ✅ Supabase Auth for JWT-based authentication
- ✅ Row-Level Security (RLS) for authorization
- ✅ Real-time capabilities (optional)
- ✅ Automated backups
- ✅ Edge functions (optional)
- ✅ Full-text search
- ✅ Version-controlled migrations

---

## 1. Technology Stack

| Tool | Purpose |
|------|---------|
| **PostgreSQL** | Database engine (v15+) |
| **Supabase** | Managed PostgreSQL platform |
| **Supabase Auth** | Authentication layer |
| **RLS Policies** | Row-level security |
| **Migrations** | Schema versioning |
| **pg_cron** | Scheduled jobs (optional) |
| **pgvector** | Vector search (optional) |

---

## 2. Core Schema

### Users Table

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT auth.uid(),
  email TEXT UNIQUE NOT NULL,
  username TEXT,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  
  FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only view their own data
CREATE POLICY "Users can view own data"
  ON users FOR SELECT
  USING (auth.uid() = id);
```

### Portfolios Table

```sql
CREATE TABLE portfolios (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their portfolios
CREATE POLICY "Users can view own portfolios"
  ON portfolios FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own portfolios"
  ON portfolios FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own portfolios"
  ON portfolios FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own portfolios"
  ON portfolios FOR DELETE
  USING (auth.uid() = user_id);
```

### Options Table

```sql
CREATE TABLE options (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  symbol TEXT NOT NULL,
  strike DECIMAL(10, 2) NOT NULL,
  expiry DATE NOT NULL,
  option_type VARCHAR(4) CHECK (option_type IN ('call', 'put')),
  bid DECIMAL(10, 4),
  ask DECIMAL(10, 4),
  last_price DECIMAL(10, 4),
  implied_vol DECIMAL(5, 4),
  delta DECIMAL(5, 4),
  gamma DECIMAL(5, 4),
  theta DECIMAL(5, 4),
  vega DECIMAL(5, 4),
  rho DECIMAL(5, 4),
  open_interest INT,
  volume INT,
  updated_at TIMESTAMP DEFAULT now(),
  
  UNIQUE(symbol, strike, expiry, option_type)
);

-- Index for faster queries
CREATE INDEX idx_options_symbol_expiry ON options(symbol, expiry);
CREATE INDEX idx_options_greeks ON options(delta, gamma, theta);
```

### Trades Table

```sql
CREATE TABLE trades (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  portfolio_id UUID REFERENCES portfolios(id) ON DELETE SET NULL,
  symbol TEXT NOT NULL,
  trade_type VARCHAR(4) CHECK (trade_type IN ('call', 'put', 'stock')),
  direction VARCHAR(4) CHECK (direction IN ('long', 'short')),
  entry_price DECIMAL(10, 4) NOT NULL,
  exit_price DECIMAL(10, 4),
  entry_date DATE NOT NULL,
  exit_date DATE,
  quantity INT NOT NULL,
  pnl DECIMAL(12, 2) GENERATED ALWAYS AS (
    CASE 
      WHEN direction = 'long' THEN quantity * (exit_price - entry_price)
      WHEN direction = 'short' THEN quantity * (entry_price - exit_price)
    END
  ) STORED,
  notes TEXT,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

ALTER TABLE trades ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own trades"
  ON trades FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

### Regime Table

```sql
CREATE TABLE market_regime (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  date DATE NOT NULL UNIQUE,
  regime VARCHAR(20) NOT NULL,
  confidence DECIMAL(3, 2),
  volatility DECIMAL(5, 4),
  trend VARCHAR(10),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_regime_date ON market_regime(date DESC);
```

---

## 3. Views

### Portfolio Summary View

```sql
CREATE VIEW portfolio_summary AS
SELECT 
  p.id,
  p.user_id,
  p.name,
  COUNT(t.id) as total_trades,
  SUM(CASE WHEN t.exit_date IS NULL THEN 1 ELSE 0 END) as open_trades,
  SUM(t.pnl) as total_pnl,
  AVG(t.pnl) as avg_pnl
FROM portfolios p
LEFT JOIN trades t ON p.id = t.portfolio_id
GROUP BY p.id;
```

---

## 4. Migrations

### Migration Structure

```sql
-- database/migrations/001_initial_schema.sql
-- Creates initial tables

-- database/migrations/002_add_auth_policies.sql
-- Adds RLS policies

-- database/migrations/003_add_indexes.sql
-- Creates performance indexes

-- database/migrations/004_add_functions.sql
-- Creates stored functions
```

### Running Migrations

```bash
# Using Supabase CLI
supabase migration new create_users_table
supabase migration up

# Or manually in Supabase console
```

---

## 5. Functions & Triggers

### Calculate Portfolio Stats Function

```sql
CREATE OR REPLACE FUNCTION calculate_portfolio_stats(portfolio_id UUID)
RETURNS TABLE (total_pnl DECIMAL, win_rate DECIMAL, total_trades INT) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    SUM(pnl)::DECIMAL,
    (SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100,
    COUNT(*)::INT
  FROM trades
  WHERE trades.portfolio_id = $1;
END;
$$ LANGUAGE plpgsql;
```

### Update Updated_At Trigger

```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_portfolios_updated_at
BEFORE UPDATE ON portfolios
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_trades_updated_at
BEFORE UPDATE ON trades
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();
```

---

## 6. Authentication Setup

### User Registration Flow

```typescript
// Frontend/Backend
const { user, session } = await supabase.auth.signUpWithPassword({
  email: 'user@example.com',
  password: 'secure-password',
});

// Supabase automatically creates auth.users record
// Trigger creates corresponding users table record
```

### JWT Token Flow

```
1. User signs up/logs in
2. Supabase Auth generates JWT token
3. Token contains user ID in 'sub' claim
4. RLS policies use auth.uid() to verify access
5. Only user's own data is returned
```

---

## 7. Row-Level Security (RLS)

### How RLS Works

```sql
-- Table with RLS enabled
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;

-- Policy: Only portfolio owner can SELECT
CREATE POLICY "portfolio_select_policy"
  ON portfolios
  FOR SELECT
  USING (auth.uid() = user_id);

-- Policy: Only portfolio owner can INSERT
CREATE POLICY "portfolio_insert_policy"
  ON portfolios
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Policy: Only portfolio owner can UPDATE
CREATE POLICY "portfolio_update_policy"
  ON portfolios
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Policy: Only portfolio owner can DELETE
CREATE POLICY "portfolio_delete_policy"
  ON portfolios
  FOR DELETE
  USING (auth.uid() = user_id);
```

### Testing RLS

```typescript
// As authenticated user
const { data } = await supabase
  .from('portfolios')
  .select()
  .eq('user_id', 'other-user-id');
// Returns empty due to RLS policy
```

---

## 8. Queries & Optimization

### Efficient Query Examples

```typescript
// Good: Use SELECT with necessary columns only
const { data } = await supabase
  .from('trades')
  .select('id, symbol, entry_price, exit_price')
  .eq('user_id', userId);

// Good: Use filters and pagination
const { data } = await supabase
  .from('trades')
  .select()
  .eq('user_id', userId)
  .range(0, 50); // Pagination

// Good: Use appropriate indexes
const { data } = await supabase
  .from('options')
  .select()
  .match({ symbol: 'AAPL', expiry: '2026-12-31' });
```

---

## 9. Real-Time Subscriptions (Optional)

### Real-Time Setup

```typescript
// Listen to trades changes
const subscription = supabase
  .channel('trades-updates')
  .on(
    'postgres_changes',
    {
      event: '*',
      schema: 'public',
      table: 'trades',
      filter: `user_id=eq.${userId}`,
    },
    (payload) => {
      console.log('Trade updated:', payload);
      // Update UI in real-time
    }
  )
  .subscribe();
```

---

## 10. Backups & Recovery

### Automatic Backups
- Supabase performs automatic daily backups
- 30-day retention policy
- Point-in-time recovery available

### Manual Backup

```bash
# Export database
pg_dump -h db.instance.supabase.co \
  -U postgres \
  -d postgres > backup.sql

# Import backup
psql -h db.instance.supabase.co \
  -U postgres \
  -d postgres < backup.sql
```

---

## 11. Performance Optimization

### Indexes

```sql
-- Fast symbol lookups
CREATE INDEX idx_options_symbol ON options(symbol);

-- Fast date range queries
CREATE INDEX idx_trades_date ON trades(entry_date, exit_date);

-- Fast foreign key joins
CREATE INDEX idx_trades_user ON trades(user_id);
CREATE INDEX idx_portfolios_user ON portfolios(user_id);

-- Compound index for common queries
CREATE INDEX idx_options_query ON options(symbol, expiry, option_type);
```

### Query Analysis

```sql
-- Analyze query performance
EXPLAIN ANALYZE
SELECT * FROM options
WHERE symbol = 'AAPL'
AND expiry = '2026-12-31';
```

---

## 12. Data Types Reference

| Type | PostgreSQL | Use Case |
|------|-----------|----------|
| UUID | UUID | Unique identifiers |
| TEXT | TEXT | Unlimited strings |
| VARCHAR(n) | VARCHAR(n) | Fixed-length strings |
| DECIMAL(p,s) | DECIMAL(10,4) | Financial values |
| DATE | DATE | Dates |
| TIMESTAMP | TIMESTAMP | Timestamps with tz |
| INT | INT | Whole numbers |
| BOOLEAN | BOOLEAN | True/false |
| JSONB | JSONB | Complex objects |

---

## 13. Connection String

```
postgresql://postgres:[password]@db.[instance].supabase.co:5432/postgres
```

---

## 14. Best Practices

✅ **DO:**
- Enable RLS on all tables with user data
- Use appropriate indexes
- Migrate schema changes with migrations
- Backup regularly
- Monitor query performance
- Use prepared statements
- Validate data at application level

❌ **DON'T:**
- Disable RLS for convenience
- Over-index tables
- Store secrets in database
- Perform heavy calculations in SQL
- Skip migrations
- Hardcode connection strings

---

## Next Steps

- **View Diagrams?** → [02-SYSTEM-DIAGRAMS](../02-SYSTEM-DIAGRAMS.md)
- **Scheduler Layer?** → [05-SCHEDULER-LAYER](./05-SCHEDULER-LAYER.md)
- **Deployment?** → [06-DEPLOYMENT-LAYER](./06-DEPLOYMENT-LAYER.md)

---

**Version:** A | **Last Updated:** 2026-06-15
