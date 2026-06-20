# StrideAlytics — Complete Folder Structure Blueprint  
## Unified Architecture for All Layers

This document contains the **entire folder structure** for:

- Web App (React)
- Mobile App (React Native)
- Backend API (FastAPI)
- Database (Supabase)
- Auth Layer
- Scheduler Layer
- Shared Logic Layer
- Infrastructure Layer
- CI/CD Layer
- Root Files

All sections are deeply detailed and production‑ready.

---

# 1. FRONTEND (WEB APP — React + Vite + Tremor)

frontend/
│
├── src/
│   ├── components/
│   │   ├── ui/                    # shadcn components
│   │   ├── charts/                # Tremor chart wrappers
│   │   ├── layout/                # Sidebar, Navbar, Shell
│   │   └── tables/                # Data tables
│   │
│   ├── pages/
│   │   ├── dashboard/
│   │   ├── screener/
│   │   ├── greeks/
│   │   ├── regime/
│   │   ├── weekly-picks/
│   │   └── trade-log/
│   │
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useScreener.ts
│   │   ├── useGreeks.ts
│   │   └── useRegime.ts
│   │
│   ├── store/
│   │   ├── auth.store.ts
│   │   ├── screener.store.ts
│   │   ├── greeks.store.ts
│   │   └── ui.store.ts
│   │
│   ├── api/
│   │   ├── client.ts
│   │   ├── endpoints.ts
│   │   └── queries/
│   │       ├── screener.ts
│   │       ├── greeks.ts
│   │       ├── regime.ts
│   │       └── weeklyPicks.ts
│   │
│   ├── utils/
│   │   ├── formatters.ts
│   │   ├── math.ts
│   │   └── helpers.ts
│   │
│   ├── theme/
│   │   ├── index.css
│   │   └── tokens.ts
│   │
│   └── main.jsx
│
├── public/
├── index.html
├── package.json
└── vite.config.js

---

# 2. MOBILE APP (React Native + Expo)

mobile/
│
├── app/
│   ├── _layout.tsx
│   ├── index.tsx
│   ├── login.tsx
│   ├── signup.tsx
│   ├── screener/
│   ├── greeks/
│   ├── regime/
│   ├── weekly-picks/
│   └── trade-log/
│
├── components/
│   ├── ui/
│   ├── charts/
│   └── layout/
│
├── screens/
│
├── hooks/
│   ├── useAuth.ts
│   ├── useScreener.ts
│   ├── useGreeks.ts
│   └── useRegime.ts
│
├── store/
│   ├── auth.store.ts
│   ├── screener.store.ts
│   ├── greeks.store.ts
│   └── ui.store.ts
│
├── api/
│   ├── client.ts
│   ├── endpoints.ts
│   └── queries/
│       ├── screener.ts
│       ├── greeks.ts
│       ├── regime.ts
│       └── weeklyPicks.ts
│
├── assets/
│   ├── fonts/
│   ├── icons/
│   └── images/
│
├── utils/
│   ├── formatters.ts
│   ├── math.ts
│   └── helpers.ts
│
├── theme/
│   ├── colors.ts
│   ├── spacing.ts
│   └── typography.ts
│
├── app.json
├── package.json
└── tsconfig.json

---

# 3. BACKEND (FastAPI)

backend/
│
├── app/
│   ├── main.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── screener.py
│   │   ├── greeks.py
│   │   ├── regime.py
│   │   ├── weekly_picks.py
│   │   └── trades.py
│   │
│   ├── services/
│   │   ├── data_fetcher.py
│   │   ├── greeks_engine.py
│   │   ├── scoring_engine.py
│   │   └── regime_engine.py
│   │
│   ├── utils/
│   │   ├── jwt.py
│   │   ├── cache.py
│   │   ├── math.py
│   │   └── logging.py
│   │
│   ├── models/
│   │   ├── screener.py
│   │   ├── greeks.py
│   │   ├── regime.py
│   │   └── weekly_picks.py
│   │
│   └── config.py
│
├── requirements.txt
├── render.yaml
└── Dockerfile

---

# 4. DATABASE (Supabase)

database/
│
├── migrations/
│   ├── 001_init.sql
│   ├── 002_weekly_picks.sql
│   ├── 003_greeks_cache.sql
│   ├── 004_regime_scores.sql
│   └── 005_trade_log.sql
│
├── seed/
│   ├── tickers.sql
│   └── metadata.sql
│
└── README.md

---

# 5. AUTH LAYER (Supabase Auth + JWT)

auth/
│
├── policies/
│   ├── rls_trade_log.sql
│   ├── rls_weekly_picks.sql
│   ├── rls_greeks_cache.sql
│   └── rls_regime_scores.sql
│
├── jwt/
│   ├── verify.py
│   └── decode.py
│
└── tokens/
    └── refresh_strategy.md

---

# 6. SCHEDULER LAYER (GitHub Actions)

scheduler/
│
├── workflows/
│   ├── screener.yml
│   ├── greeks.yml
│   ├── regime.yml
│   ├── weekly_picks.yml
│   └── snapshots.yml
│
└── scripts/
    ├── run_screener.sh
    ├── run_greeks.sh
    ├── run_regime.sh
    ├── run_weekly_picks.sh
    └── run_snapshots.sh

---

# 7. SHARED LOGIC LAYER

shared/
│
├── api/
│   ├── client.ts
│   ├── endpoints.ts
│   └── types.ts
│
├── constants/
│   ├── bands.ts
│   ├── api.ts
│   └── config.ts
│
├── schemas/
│   ├── screener.schema.ts
│   ├── greeks.schema.ts
│   ├── regime.schema.ts
│   └── weekly_picks.schema.ts
│
├── utils/
│   ├── formatters.ts
│   ├── validators.ts
│   └── math.ts
│
└── types/
    ├── screener.ts
    ├── greeks.ts
    ├── regime.ts
    └── weekly_picks.ts

---

# 8. INFRASTRUCTURE LAYER

infra/
│
├── vercel.json
├── render.yaml
├── supabase.env.example
├── render.env.example
├── mobile.env.example
└── domains.md

---

# 9. CI/CD LAYER

.github/
│
└── workflows/
    ├── ci.yml
    └── deploy.yml

---

# 10. ROOT FILES

.gitignore  
README.md  
package.json  

---

# END OF MASTER FOLDER STRUCTURE



# StrideAlytics — Mega Architecture Diagrams  
Combined ASCII + Mermaid (safe text) views.

---

# 1. Visual ASCII Mega‑Diagram (System + Repo + Deployment)

                         ┌──────────────────────────────┐
                         │      Frontend (Vercel)       │
                         │   React + Tremor + Tailwind  │
                         └───────────────┬──────────────┘
                                         │
                                         ▼
                         ┌──────────────────────────────┐
                         │   Backend API (Render)       │
                         │        FastAPI + Python      │
                         └───────────────┬──────────────┘
                                         │
                                         ▼
                         ┌──────────────────────────────┐
                         │  Database (Supabase)         │
                         │  PostgreSQL + Auth + RLS     │
                         └───────────────┬──────────────┘
                                         │
                                         ▼
                         ┌──────────────────────────────┐
                         │ Schedulers (GitHub Actions)  │
                         │   CRON jobs → Backend API    │
                         └──────────────────────────────┘

---

# 1.1 Monorepo Context (OptionStride / StrideAlytics Repo)

optionstride/
 ├── frontend/      # Web app (Vercel)
 ├── mobile/        # Mobile app (Expo)
 ├── backend/       # FastAPI (Render)
 ├── database/      # Supabase migrations
 ├── scheduler/     # GitHub Actions workflows
 ├── shared/        # Shared TS types + API client
 └── infra/         # Deployment configs (Vercel, Render, Supabase)

---

# 1.2 Deployment Flow (CI/CD)

GitHub Push
   ↓
GitHub Actions (CI)
   ↓
 ├─ Vercel Deploy (frontend)
 ├─ Render Deploy (backend)
 ├─ Supabase Migrations (database)
 └─ GitHub Actions CRON (schedulers → backend)

---

# 2. Mermaid Version (Safe Text Representation)

Below is the **Mermaid diagram content**, written as plain text so it doesn’t conflict with Markdown code fences.
You can copy this into a Mermaid‑enabled tool (like VS Code, Obsidian, or a docs site) and wrap it in ```mermaid fences there.

System Architecture (Mermaid):

flowchart TD
    FE[Frontend - Vercel] --> BE[Backend API - Render]
    BE --> DB[Database - Supabase]
    SCH[GitHub Actions - Schedulers] --> BE

Monorepo Structure (Mermaid):

flowchart TD
    ROOT[optionstride/] --> F[frontend/]
    ROOT --> M[mobile/]
    ROOT --> B[backend/]
    ROOT --> D[database/]
    ROOT --> S[scheduler/]
    ROOT --> SH[shared/]
    ROOT --> I[infra/]

Deployment Flow (Mermaid):

flowchart TD
    PUSH[GitHub Push] --> CI[GitHub Actions - CI]
    CI --> V[Vercel Deploy - frontend]
    CI --> R[Render Deploy - backend]
    CI --> SM[Supabase Migrations - database]
    CI --> CRON[GitHub Actions CRON - schedulers]

---

# END OF MEGA DIAGRAMS

