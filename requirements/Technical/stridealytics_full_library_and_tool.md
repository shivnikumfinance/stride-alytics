# StrideAlytics — Full Library & Tool Reference  
Complete breakdown of every library, dependency, and tool used across all layers.

This is the authoritative, unified reference for the entire platform.

---

# 1. FRONTEND (WEB APP — React + Vite + Tremor)

## Core Framework
- React 18
- Vite

## UI Libraries
- Tremor (dashboards, charts, KPIs)
- TailwindCSS
- shadcn/ui
- Lucide Icons

## State Management
- Zustand
- React Query

## Forms
- React Hook Form
- Zod (optional)

## Networking
- Axios
- React Query (caching, retries)

## Routing
- React Router

## Charts
- Tremor Charts (Recharts under the hood)

## Testing
- Vitest
- React Testing Library

## Build & Deployment
- Vercel
- ESLint
- Prettier

---

# 2. MOBILE APP (React Native + Expo)

## Core Framework
- React Native
- Expo SDK
- Expo Router

## UI Libraries
- NativeWind (Tailwind for RN)
- Tamagui (optional)
- React Native SVG
- Victory Native (charts)

## State Management
- Zustand
- React Query

## Networking
- Axios
- React Query

## Auth
- Supabase JS Client
- Expo SecureStore

## Navigation
- React Navigation
- Expo Router

## Assets
- Expo Asset
- Expo Font

## Build & Deployment
- Expo EAS Build
- Expo OTA Updates

---

# 3. BACKEND (FastAPI)

## Core Framework
- FastAPI
- Uvicorn

## Data & Math
- Pandas
- NumPy
- SciPy (optional)
- TA‑Lib (optional)

## External Data
- yfinance
- HTTPX

## Auth
- python‑jose
- PyJWT

## Database
- Supabase Python Client
- asyncpg (optional)

## Caching
- Redis (optional)

## Logging
- structlog or Python logging

## Testing
- pytest
- pytest‑asyncio

## Deployment
- Render
- Docker

---

# 4. DATABASE LAYER (Supabase PostgreSQL)

## Database Engine
- PostgreSQL 15+

## Supabase Platform
- Supabase Auth
- Supabase Storage (optional)
- Supabase Edge Functions (optional)
- Supabase SQL Editor

## Migrations
- Supabase CLI
- SQL migration files

## Security
- Row Level Security (RLS)
- Policies
- JWT‑based access

## Extensions
- pg_cron (optional)
- pgvector (optional)
- uuid‑ossp

---

# 5. AUTH LAYER (Supabase Auth + JWT)

## Auth Provider
- Supabase Auth
  - Email/password
  - OAuth (optional)
  - Magic links (optional)

## Token Handling
- JWT
- python‑jose
- Expo SecureStore (mobile)
- localStorage / memory (web)

## Security
- RLS policies
- Postgres policies
- JWT claims

---

# 6. SCHEDULER LAYER (GitHub Actions)

## Scheduler Engine
- GitHub Actions CRON

## Tools
- curl
- bash
- Python (optional job logic)

## Workflows
- Screener
- Greeks
- Regime
- Weekly Picks
- Snapshots

---

# 7. SHARED LOGIC LAYER

## Shared API Client
- Axios
- TypeScript
- React Query (web/mobile)

## Shared Types
- TypeScript types
- Zod schemas

## Shared Utilities
- formatters
- validators
- math helpers

---

# 8. INFRASTRUCTURE LAYER

## Hosting
- Vercel (frontend)
- Render (backend)
- Supabase (DB + Auth)

## Config
- vercel.json
- render.yaml
- supabase.env.example

## DevOps Tools
- Docker
- GitHub Actions
- Environment variables

---

# 9. CI/CD LAYER

## CI
- GitHub Actions
- Vercel CI
- Render Deploy Hooks

## Testing
- Vitest
- pytest

## Linting
- ESLint
- Prettier

---

# 10. DEVELOPER TOOLING

## Code Quality
- ESLint
- Prettier
- TypeScript

## Package Managers
- npm
- pnpm (optional)
- yarn (optional)

## Version Control
- Git
- GitHub

## Local Dev
- VS Code
- Thunder Client / Postman

---

# END OF FULL LIBRARY & TOOL REFERENCE
