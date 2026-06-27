# ============================================================================
# secrets/ — LOCAL-ONLY credentials (NEVER COMMITTED)
# ============================================================================
#
# This directory holds every secret the StrideAlytics project needs.
# All real values live here; the .env.example templates elsewhere in the
# repo only describe the *shape* of the variables.
#
# Layout:
#   secrets/
#   ├── README.md               ← you are here
#   ├── local.env.example       ← template for local dev (committed)
#   ├── staging.env.example     ← template for staging (committed)
#   ├── production.env.example  ← template for production (committed)
#   ├── github-secrets.txt      ← checklist of GitHub secret names (committed)
#   ├── local.env               ← YOUR real local values (git-ignored)
#   ├── staging.env             ← staging values (git-ignored)
#   └── production.env          ← production values (git-ignored)
#
# How to use:
#   1. cp secrets/local.env.example secrets/local.env
#   2. Fill in the real values in secrets/local.env
#   3. Run `npm run secrets:load -- local` (or .\scripts\load-secrets.ps1 local)
#      to populate backend/.env + frontend/.env + scheduler/.env from it.
#   4. CI uses GitHub Actions secrets — see secrets/github-secrets.txt.
#
# How secrets are protected:
#   - The whole `secrets/` directory is in .gitignore (see root .gitignore)
#   - The `*.example` files are FORCE-INCLUDED so templates stay tracked
#   - GitHub push-protection / pre-commit hooks SHOULD scan for high-entropy
#     strings (see infra/README.md → "Hardening checklist")
# ============================================================================

## Adding a new secret

1. Add the key to **all three** `.env.example` files (local, staging, production).
2. Add the key to [secrets/github-secrets.txt](github-secrets.txt) if CI needs it.
3. Document where to find the value (Supabase dashboard URL, etc.).
4. Run `scripts/load-secrets.ps1 local` to verify it propagates to the right place.

## Quick reference — where to find each value

| Secret                     | Where to get it                                                |
|----------------------------|----------------------------------------------------------------|
| `DATABASE_URL`             | Supabase → Project → Settings → Database → Connection string   |
| `SUPABASE_URL`             | Supabase → Project → Settings → API → Project URL              |
| `SUPABASE_ANON_KEY`        | Supabase → Project → Settings → API → anon / public key        |
| `SUPABASE_SERVICE_ROLE_KEY`| Supabase → Project → Settings → API → service_role secret      |
| `SUPABASE_JWT_SECRET`      | Supabase → Project → Settings → API → JWT Secret               |
| `SENDGRID_API_KEY`         | SendGrid → Settings → API Keys                                 |
| `SLACK_WEBHOOK`            | Slack → Apps → Incoming Webhooks                               |
| `VERCEL_TOKEN`             | Vercel → Account Settings → Tokens                             |
| `VERCEL_ORG_ID`            | Vercel → Team Settings → General                              |
| `VERCEL_PROJECT_ID`        | Vercel → Project → Settings → General                          |
| `RENDER_*_DEPLOY_HOOK`     | Render → Service → Settings → Deploy Hook                      |
| `DOCKER_USERNAME/PASSWORD` | hub.docker.com → Account Settings → Security                   |
| `EXPO_TOKEN`               | expo.dev → Account Settings → Access Tokens                    |
| `SUPABASE_ACCESS_TOKEN`    | Supabase → Account → Access Tokens                             |
| `SUPABASE_PROJECT_REF_*`   | Supabase → Project → Settings → General → Reference ID         |
