# StrideAlytics — Supabase Setup Guide

This guide walks through creating and configuring a Supabase project for the StrideAlytics platform.

---

## 1. Create a Supabase Project

1. Go to [https://supabase.com/dashboard/projects](https://supabase.com/dashboard/projects)
2. Click **New project**
3. Fill in:
   - **Name:** `stridealytics` (or `stridealytics-staging` / `stridealytics-prod`)
   - **Database Password:** Generate a strong password (save this!)
   - **Region:** Choose the closest to your users (e.g., `us-east-1`)
   - **Pricing Plan:** Free tier is fine to start
4. Click **Create new project** (takes 1-2 minutes)

---

## 2. Collect Project Credentials

Once the project is created, go to **Project Settings → API**:

| Setting | Where to find it | Used by |
|---------|-----------------|---------|
| `SUPABASE_URL` | Project Settings → API → Project URL | Backend, Scheduler, Frontend |
| `SUPABASE_ANON_KEY` | Project Settings → API → anon/public | Backend, Frontend |
| `SUPABASE_SERVICE_ROLE_KEY` | Project Settings → API → service_role (secret!) | Backend (server-only) |
| `SUPABASE_JWT_SECRET` | Project Settings → API → JWT Secret | Backend (auth middleware) |
| `DATABASE_URL` | Project Settings → Database → Connection string → Direct | Backend |

Then go to **Project Settings → General**:

| Setting | Value |
|---------|-------|
| `SUPABASE_PROJECT_REF` | The reference ID in the URL (e.g., `abcxyz` in `https://supabase.com/dashboard/project/abcxyz/settings/general`) |

---

## 3. Configure Local Environment

Copy the credentials into the local secrets template:

```bash
# From repo root
cp secrets/local.env.example secrets/local.env
```

Edit `secrets/local.env` and fill in:

```env
DATABASE_URL=postgresql://postgres:YOUR_DB_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_ANON_KEY=eyJ... (your anon key)
SUPABASE_SERVICE_ROLE_KEY=eyJ... (your service role key)
SUPABASE_JWT_SECRET=your-jwt-secret
```

Then propagate to the sub-project `.env` files:

```bash
# Windows PowerShell
.\scripts\load-secrets.ps1 -Env local

# OR cross-platform
node scripts/load-secrets.mjs local
```

---

## 4. Run Database Migrations

### Option A: Through Supabase Dashboard (SQL Editor)

1. Go to **SQL Editor** in the Supabase Dashboard
2. Open each file from `database/migrations/` in order:
   - `001_create_health_check_table.sql`
   - `002_initial_schema.sql`
   - `003_row_level_security.sql`
   - `004_indexes_views_functions.sql`
   - `005_extended_features.sql`
3. Run each one in sequence

### Option B: Via psql CLI

```bash
psql "$DATABASE_URL" -f database/migrations/001_create_health_check_table.sql
psql "$DATABASE_URL" -f database/migrations/002_initial_schema.sql
psql "$DATABASE_URL" -f database/migrations/003_row_level_security.sql
psql "$DATABASE_URL" -f database/migrations/004_indexes_views_functions.sql
psql "$DATABASE_URL" -f database/migrations/005_extended_features.sql
```

### Option C: Via migration scripts

```bash
# Windows PowerShell
.\database\scripts\apply_migrations.ps1

# Bash
./database/scripts/apply_migrations.sh
```

---

## 5. Configure Supabase Auth

1. Go to **Authentication → Settings**
2. Under **General**:
   - Set **Site URL** to `http://localhost:5173` (for local dev)
   - Add redirect URLs: `http://localhost:5173/**`
3. Under **Email Auth**:
   - Enable email/password signups
   - Optionally disable **Confirm email** for development
4. Under **Security** → **JWT expiry**: Default 1 hour (3600 seconds) is fine

---

## 6. Enable RLS Policies

The migrations already include RLS policies (migration 003). Verify they're active:

```sql
-- Check RLS is enabled on your tables
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';
```

---

## 7. Create Seed Data (Optional Development)

```bash
psql "$DATABASE_URL" -f database/seeds/dev_users.sql
```

This creates:
- `dev@stridealytics.com` (Pro user) / password: set via Supabase dashboard
- `test@stridealytics.com` (Free user)

To set passwords, go to **Authentication → Users** in the Supabase dashboard and create users manually with these emails.

---

## 8. Set Up GitHub Secrets

After deploying to Render/Vercel, add these secrets to your GitHub repository:

**Settings → Secrets and variables → Actions → New repository secret:**

```bash
SUPABASE_URL                   # From step 2
SUPABASE_ANON_KEY              # From step 2
SUPABASE_SERVICE_ROLE_KEY      # From step 2
SUPABASE_JWT_SECRET            # From step 2
SUPABASE_ACCESS_TOKEN          # Supabase → Account → Access Tokens → Generate token
SUPABASE_PROJECT_REF_STAGING   # Project reference ID
SUPABASE_PROJECT_REF_PROD      # Production project reference ID
SLACK_WEBHOOK                  # For failure alerts (optional)
SENDGRID_API_KEY               # For weekly picks email (optional)
```

For Vercel deploy:
```bash
VERCEL_TOKEN                   # vercel.com → Account → Tokens
VERCEL_ORG_ID                  # vercel.com → Team → Settings
VERCEL_PROJECT_ID              # vercel.com → Project → Settings
```

For Render deploy:
```bash
RENDER_STAGING_DEPLOY_HOOK     # Render → staging service → Deploy Hook
RENDER_PROD_DEPLOY_HOOK        # Render → production service → Deploy Hook
```

---

## 9. Verify Setup

Start the backend and verify it connects:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

Check the health endpoint:
```bash
curl http://localhost:8000/api/v1/health
# Expected: {"success":true,"data":{"status":"ok"}}
```

---

## Quick Reference

```bash
# All credentials in one place after setup:
#   secrets/local.env     → local dev credentials
#   secrets/staging.env   → staging credentials  
#   secrets/production.env → production credentials

# Propagate secrets to .env files:
.\scripts\load-secrets.ps1 -Env local      # Windows
node scripts/load-secrets.mjs local        # Cross-platform

# Run backend:
cd backend && uv run uvicorn app.main:app --reload

# Run frontend:
cd frontend && npm run dev

# Run scheduler script manually:
cd scheduler && python scripts/generate_picks.py

# Run tests:
cd backend && uv run pytest -v