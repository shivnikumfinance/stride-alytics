# StrideAlytics — Infrastructure

Everything needed to deploy and operate the StrideAlytics stack on the
free-tier hosts (Vercel + Render + Supabase).

## Layout

```
infra/
├── docker/
│   ├── docker-compose.yml       # Local dev stack (Postgres + backend + adminer/redis)
│   └── Dockerfile.backend       # (alternative; production image lives in /backend/Dockerfile)
├── render/
│   ├── render.yaml              # Render Blueprint (web service)
│   └── README.md                # Render deploy notes
├── vercel/
│   ├── vercel.json              # Vercel build config (root + security headers)
│   └── README.md                # Vercel deploy notes
└── README.md                    # (you are here)
```

## Local development stack

```bash
# from repo root
cp backend/.env.example backend/.env   # then fill in values

# Postgres + backend + adminer (UI on :8080)
docker compose --profile tools -f infra/docker/docker-compose.yml up

# Just the core stack
docker compose -f infra/docker/docker-compose.yml up

# Tear down
docker compose -f infra/docker/docker-compose.yml down -v
```

The backend mounts `./backend/app` read-only for live-reload; rebuild the
image (`docker compose build backend`) to pick up dependency changes.

## Production deployment

| Layer    | Host                  | Source                                                      |
|----------|-----------------------|-------------------------------------------------------------|
| Frontend | Vercel                | [`frontend/vercel.json`](../../frontend/vercel.json)        |
| Backend  | Render                | [`backend/render.yaml`](../../backend/render.yaml)          |
| Database | Supabase              | [`database/migrations/`](../../database/migrations)        |
| Scheduler| GitHub Actions cron   | [`.github/workflows/`](../../.github/workflows)             |

### CI / CD pipeline

```
Push to develop  ──► CI gate ──► Deploy staging (Vercel preview, Render staging)
Push to main     ──► CI gate ──► Manual approve ──► Deploy production
Tagged v*.*.*    ──► Mobile build (EAS) ──► Store / Play Console upload
```

Required GitHub secrets:

| Secret                              | Purpose                          |
|-------------------------------------|----------------------------------|
| `VERCEL_TOKEN`                      | Vercel deploy                    |
| `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`| Vercel scoping                   |
| `RENDER_STAGING_DEPLOY_HOOK`        | Render staging trigger           |
| `RENDER_PROD_DEPLOY_HOOK`           | Render prod trigger              |
| `SUPABASE_URL` / `SUPABASE_KEY`     | DB + auth from schedulers        |
| `SUPABASE_ACCESS_TOKEN`             | Migration runner                 |
| `SUPABASE_PROJECT_REF_STAGING`      | Migration target                 |
| `SUPABASE_PROJECT_REF_PROD`         | Migration target                 |
| `SLACK_WEBHOOK`                     | Failure alerts                   |
| `SENDGRID_API_KEY`                  | Weekly picks email               |
| `EXPO_TOKEN`                        | Mobile EAS builds                |
| `DOCKER_USERNAME` / `DOCKER_PASSWORD` | Docker Hub publish (optional) |

## Architecture decisions

- **Free-tier first.** Every service runs in the $0–$10/month band; upgrade
  triggers documented in [`../docs/TECHNICAL/BLUEPRINT.md`](../docs/TECHNICAL/BLUEPRINT.md).
- **Health-checked containers.** Backend Docker image includes a
  `HEALTHCHECK` against `/api/v1/health`.
- **Secret hygiene.** `.env.example` files exist at backend/ and frontend/
  roots; `.env*` is ignored by `.gitignore` and `.dockerignore`.
- **Manual prod approval.** `backend-ci-cd.yml` uses a `production`
  GitHub environment that requires a reviewer click.
