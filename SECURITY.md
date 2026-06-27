# Security Policy

## Supported versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a vulnerability

**Please do not file public GitHub issues for security bugs.**

Email: **security@stridealytics.com** (PGP key on request).

We aim to:

- Acknowledge within **2 business days**
- Triage and provide a fix timeline within **7 days**
- Credit reporters (if desired) in the release notes

## Scope

In scope:

- Authentication / authorization bypass
- RLS policy holes in `database/rls-policies/`
- Injection (SQL, template, JWT)
- Secrets leaked in commits or logs
- Cross-tenant data leakage

Out of scope:

- Rate-limit / DoS (handled at Render / Vercel / Supabase edge)
- Self-XSS in the browser console

## Hardening checklist

- All secrets live in **GitHub Actions secrets** or **deployment env vars** — never in the repo.
- `SUPABASE_SERVICE_ROLE_KEY` is **server-only** — never shipped to the frontend.
- `SUPABASE_JWT_SECRET` rotates every 90 days.
- `ruff`, `black`, `sqlfluff` run on every PR via `.github/workflows/ci.yml`.
- Render deploy hook posts to a **protected environment** requiring manual approval for `main`.
