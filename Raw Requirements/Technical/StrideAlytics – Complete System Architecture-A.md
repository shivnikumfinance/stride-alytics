# StrideAlytics – Complete System Architecture  
## Version A — Consolidated Blueprint

A comprehensive, multi‑platform, production‑ready architecture blueprint for **StrideAlytics**, covering:

- Web App (React + Tremor)
- Mobile App (React Native + Expo)
- Backend (FastAPI)
- Database (Supabase)
- Authentication (Supabase Auth)
- Schedulers (GitHub Actions)
- Shared Logic (API, Types, Utils)
- Infrastructure (Vercel, Render, Supabase)
- CI/CD
- Full folder structure
- Library breakdown (by layer + by category)
- ASCII diagrams (Mermaid converted to ASCII)

---

## 1. System Overview

StrideAlytics is a **multi‑platform analytics system** consisting of:

- **Web App:** React + Vite + Tremor + Tailwind + shadcn/ui  
- **Mobile App:** React Native + Expo + NativeWind/Tamagui  
- **Backend API:** FastAPI + Pydantic + Uvicorn  
- **Database:** Supabase PostgreSQL + migrations  
- **Auth:** Supabase Auth (JWT)  
- **Schedulers:** GitHub Actions CRON jobs  
- **Shared Logic:** TypeScript types, shared API client, constants, utils  
- **Infra:** Vercel (web), Render (backend), Supabase (DB/auth), GitHub Actions (CI/CD)

---

## 2. Unified System Diagrams

### 2.1 ASCII Diagram (Primary)

                ┌──────────────────────────────┐
                │        Web App (React)       │
                │  https://stridealytics.vercel│
                └───────────────┬──────────────┘
                                │
                                ▼
                ┌──────────────────────────────┐
                │     Mobile App (Expo RN)     │
                │   iOS / Android / EAS Build  │
                └───────────────┬──────────────┘
                                │
                                ▼
                ┌──────────────────────────────┐
                │     Backend API (FastAPI)    │
                │ https://stridealytics-api... │
                └───────────────┬──────────────┘
                                │
                                ▼
                ┌──────────────────────────────┐
                │   Supabase (Auth + DB + RLS) │
                └───────────────┬──────────────┘
                                │
                                ▼
                ┌──────────────────────────────┐
                │ GitHub Actions (Schedulers)  │
                └──────────────────────────────┘

### 2.2 Mermaid Diagram (Converted to ASCII)

Mermaid removed per your request.  
Here is the **ASCII equivalent**:

                [Web App - React + Tremor]
                           |
                           v
                [Backend API - FastAPI]
                           ^
                           |
                [Mobile App - React Native + Expo]

                Backend API --> Supabase (Auth + PostgreSQL)
                GitHub Actions --> Backend API (CRON triggers)

---

## 3. Full Monorepo Folder Structure

stridealytics/
│
├── frontend/                          # Web App (React + Vite + Tremor)
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── charts/
│   │   │   ├── layout/
│   │   │   └── tables/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── store/
│   │   ├── api/
│   │   ├── utils/
│   │   ├── theme/
│   │   └── main.jsx
│   ├── public/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── mobile/                            # Mobile App (React Native + Expo)
│   ├── app/
│   ├── components/
│   ├── screens/
│   ├── hooks/
│   ├── store/
│   ├── api/
│   ├── assets/
│   ├── utils/
│   ├── theme/
│   ├── app.json
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                           # FastAPI Backend
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── models/
│   │   └── config.py
│   ├── requirements.txt
│   ├── render.yaml
│   └── Dockerfile
│
├── database/                          # Supabase Migrations
│   ├── migrations/
│   ├── seed/
│   └── README.md
│
├── scheduler/                         # GitHub Actions CRON Jobs
│   ├── workflows/
│   └── README.md
│
├── shared/                            # Shared Logic
│   ├── api/
│   ├── constants/
│   ├── schemas/
│   ├── utils/
│   └── types/
│
├── infra/
│   ├── vercel.json
│   ├── render.yaml
│   ├── supabase.env.example
│   ├── render.env.example
│   ├── mobile.env.example
│   └── domains.md
│
├── .github/
│   ├── workflows/
│
├── .gitignore
├── README.md
└── package.json

---

## 4. Web Architecture (Frontend)

- React 18 + Vite  
- Tremor  
- TailwindCSS  
- shadcn/ui  
- Lucide Icons  
- React Router  
- Zustand  
- React Query  
- Axios  
- React Hook Form  
- Vitest  
- Vercel deployment

---

## 5. Mobile Architecture

- React Native + Expo  
- Expo Router  
- React Navigation  
- NativeWind or Tamagui  
- Zustand  
- React Query  
- Axios  
- Victory Native  
- Supabase Auth + SecureStore  
- Expo EAS deployment

---

## 6. Backend Architecture (FastAPI)

- FastAPI  
- Uvicorn  
- Pydantic v2  
- HTTPX  
- Supabase Python Client  
- Pandas, NumPy, SciPy, TA‑Lib  
- yfinance  
- JWT verification  
- Redis (optional)  
- pytest  
- Render deployment

---

## 7. Database Architecture (Supabase)

- PostgreSQL  
- SQL migrations  
- Supabase Auth  
- RLS  
- Tables:  
  - trade_log  
  - weekly_picks  
  - greeks_cache  
  - regime_scores  
  - screener_results  
  - snapshots  
  - tickers_metadata  

---

## 8. Auth Architecture

- Supabase Auth  
- JWT  
- Secure token storage  
- Backend verification  
- RLS enforcement

---

## 9. Scheduler Architecture

- GitHub Actions  
- CRON jobs  
- curl triggers  
- Screener, Greeks, Regime, Weekly Picks, Snapshots

---

## 10. Shared API Client

- Shared Axios instance  
- Shared endpoints  
- Shared types  
- Token injection  
- Error handling

---

## 11. Mobile UI/UX Plan

- Analytics‑first  
- Dark mode  
- Bottom tabs  
- Screens:  
  - Login  
  - Signup  
  - Dashboard  
  - Screener  
  - Greeks  
  - Regime  
  - Weekly Picks  
  - Trade Log  
- Reusable components  
- Chart wrappers  

---

## 12. Library Breakdown by Layer

### Web  
React, Vite, Tremor, Tailwind, shadcn/ui, Zustand, React Query, Axios, Vitest

### Mobile  
React Native, Expo, NativeWind/Tamagui, Zustand, React Query, Axios, Victory Native

### Backend  
FastAPI, Uvicorn, Pydantic, HTTPX, Supabase Python, Pandas, NumPy, SciPy, TA‑Lib

### Database  
Supabase PostgreSQL, Supabase CLI, SQL migrations

### Auth  
Supabase Auth, JWT, python‑jose

### Scheduler  
GitHub Actions, curl, bash

### Shared  
TypeScript, Zod, Axios, utils

### Infra  
Vercel, Render, Supabase, GitHub Actions, Docker

---

## 13. Library Breakdown by Category

### UI  
Tremor, Tailwind, shadcn/ui, NativeWind, Tamagui

### State  
Zustand, React Query

### Networking  
Axios, HTTPX

### Analytics  
Pandas, NumPy, SciPy, TA‑Lib

### Auth  
Supabase Auth, JWT

### DevOps  
Vercel, Render, GitHub Actions, Docker

---

## 14. Final Notes

### Scalability  
- Horizontal backend scaling  
- Supabase DB scaling  
- Thin clients  
- Stateless frontend + mobile  
- Shared logic reduces duplication  
- CI/CD ensures consistent deployments  

### Future Enhancements  
- Additional data sources  
- Premium subscription tiers  
- Role‑based access control  
- Advanced analytics  
- Push notifications  
- Webhooks  
- AI‑powered insights  

---

# END OF VERSION A
