# Security Hardening Checklist

Implementation-level security controls for StrideAlytics.

## Secrets Management

- [ ] All secrets live in **GitHub Actions secrets** or **deployment env vars** — never in the repo.
- [ ] `SUPABASE_SERVICE_ROLE_KEY` is **server-only** — never shipped to the frontend.
- [ ] `SUPABASE_JWT_SECRET` rotates every 90 days.
- [ ] API keys are scoped to minimum required permissions.
- [ ] `.env` files are gitignored at all levels.

## Supply Chain

- [ ] `npm audit` runs on every PR touching `frontend/` or `mobile/`.
- [ ] `uv sync --frozen` enforced in backend CI.
- [ ] Dependencies updated monthly via Dependabot or Renovate.

## CI/CD

- [ ] `ruff`, `black`, `sqlfluff` run on every PR.
- [ ] Render deploy hook posts to a **protected environment** requiring manual approval for `main`.
- [ ] Vercel preview deployments are isolated per PR.

## Runtime

- [ ] All API routes require authentication.
- [ ] RLS policies verified on every database migration.
- [ ] CORS configured to allow only known origins.
- [ ] Rate limiting enabled on public endpoints.
