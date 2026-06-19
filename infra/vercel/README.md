# Vercel Deployment

Frontend is deployed to Vercel via:

- **Manual:** `cd frontend && npx vercel deploy --prod`
- **CI/CD:** Auto-deployed via `.github/workflows/frontend-ci-cd.yml`

## Config Files

- `frontend/vercel.json` — SPA routes, build command, security headers
- Environment variables managed via Vercel Dashboard or CLI

## Required Secrets (GitHub Actions)

| Secret | Purpose |
|--------|---------|
| `VERCEL_TOKEN` | Vercel API token |
| `VERCEL_ORG_ID` | Vercel org ID |
| `VERCEL_PROJECT_ID` | Vercel project ID |