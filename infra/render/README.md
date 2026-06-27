# Render Deployment

Backend API is deployed to Render via:

- **Manual:** Push to `main` branch triggers auto-deploy via `backend/render.yaml`
- **CI/CD:** Auto-deployed via `.github/workflows/backend-ci-cd.yml` using Render Deploy Hooks

## Config Files

- `backend/render.yaml` — Web service definition, build & start commands, env vars
- `backend/Dockerfile` — Containerized build with uv

## Required Secrets (GitHub Actions)

| Secret | Purpose |
|--------|---------|
| `RENDER_STAGING_DEPLOY_HOOK` | Render deploy hook URL for staging |
| `RENDER_PROD_DEPLOY_HOOK` | Render deploy hook URL for production |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase anonymous key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key |
| `DATABASE_URL` | PostgreSQL connection string |