# StrideAlytics — System Overview

**Comprehensive description of the multi-platform analytics system architecture**

---

## 1. Executive Summary

StrideAlytics is a **production-ready, multi-platform analytics system** designed for trading insights, options analysis, and investment decision-making.

**Key Characteristics:**
- ✅ **Multi-Platform:** Web, mobile, backend services
- ✅ **Real-time Data:** Live market feeds, options greeks, regime analysis
- ✅ **Scalable:** Monorepo with separate layers for independent scaling
- ✅ **Secure:** JWT-based auth, Row-Level Security (RLS) on database
- ✅ **Automated:** CRON jobs for data collection and analysis
- ✅ **Cloud-Native:** Serverless-friendly deployment on Vercel, Render, Supabase

---

## 2. Platform Components

### 2.1 Web Application
**Tech Stack:** React 18 + Vite + Tremor + TailwindCSS + shadcn/ui  
**Deployment:** Vercel  
**Purpose:** Main dashboard for traders and analysts

**Key Features:**
- Dashboard with KPIs and real-time metrics
- Options screener with filtering and sorting
- Greeks calculator and visualization
- Market regime analysis
- Weekly picks and recommendations
- Trade log tracking

### 2.2 Mobile Application
**Tech Stack:** React Native + Expo + NativeWind  
**Deployment:** Expo EAS Build (iOS/Android)  
**Purpose:** On-the-go access to analytics

**Key Features:**
- All dashboard features in mobile-first UI
- Push notifications for alerts
- Offline-capable screens
- Biometric authentication

### 2.3 Backend API
**Tech Stack:** FastAPI + Uvicorn + Python 3.10+  
**Deployment:** Render  
**Purpose:** Core business logic, data processing, external integrations

**Key Features:**
- REST endpoints for all data queries
- Real-time WebSocket connections (optional)
- Data aggregation from external APIs (yfinance, etc.)
- Options analysis calculations
- Market regime detection

### 2.4 Database
**Tech Stack:** Supabase (PostgreSQL 15+) + Auth  
**Deployment:** Supabase Cloud  
**Purpose:** Persistent storage, authentication, authorization

**Key Features:**
- PostgreSQL relational data
- Supabase Auth (JWT-based)
- Row-Level Security (RLS) policies
- Migrations and versioning
- Real-time subscriptions (optional)

### 2.5 Schedulers
**Tech Stack:** GitHub Actions + Python  
**Purpose:** Automated tasks (data collection, analysis, cleanup)

**Key Features:**
- CRON jobs for market data collection
- Daily/weekly report generation
- Data cleanup and archival
- Health checks and monitoring

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  StrideAlytics Platform                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  PRESENTATION LAYER                                    │
│  ┌──────────────────┐        ┌──────────────────┐     │
│  │  Web App         │        │  Mobile App      │     │
│  │  (Vercel)        │        │  (EAS Build)     │     │
│  └────────┬─────────┘        └────────┬─────────┘     │
│           │                           │                │
│           └───────────────┬───────────┘                │
│                           ▼                            │
│  ────────────────────────────────────────────────     │
│                                                        │
│  API LAYER                                           │
│  ┌──────────────────────────────────────┐            │
│  │      Backend API (FastAPI/Render)    │            │
│  │  ├─ Endpoints (REST/GraphQL)         │            │
│  │  ├─ Business Logic                   │            │
│  │  ├─ External Integrations            │            │
│  │  └─ Caching & Performance            │            │
│  └────────┬─────────────────────────────┘            │
│           │                                          │
│           ▼                                          │
│  ────────────────────────────────────────────────   │
│                                                      │
│  DATA LAYER                                         │
│  ┌──────────────────────────────────────┐          │
│  │    Database (Supabase PostgreSQL)    │          │
│  │  ├─ Core Tables                      │          │
│  │  ├─ Authentication (JWT)             │          │
│  │  ├─ RLS Policies                     │          │
│  │  └─ Migrations                       │          │
│  └──────────────────────────────────────┘          │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  AUTOMATION LAYER                                  │
│  ┌──────────────────────────────────────┐         │
│  │   GitHub Actions (Schedulers)        │         │
│  │  ├─ Data Collection CRON             │         │
│  │  ├─ Report Generation                │         │
│  │  └─ Health Checks                    │         │
│  └──────────────────────────────────────┘         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 4. Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18, Vite, Tremor, TailwindCSS, shadcn/ui | Web UI dashboard |
| **Mobile** | React Native, Expo, NativeWind | Mobile UI application |
| **Backend** | FastAPI, Uvicorn, Pydantic | REST API, business logic |
| **Database** | PostgreSQL (Supabase), Migrations | Data persistence |
| **Auth** | Supabase Auth, JWT | User authentication & authorization |
| **Caching** | Redis (optional) | Performance optimization |
| **Schedulers** | GitHub Actions, Python scripts | Automation & CRON jobs |
| **Deployment** | Vercel, Render, Supabase | Cloud hosting |
| **CI/CD** | GitHub Actions, Docker | Build & deployment automation |

---

## 5. Data Flow

### 5.1 User Request Flow
```
User (Web/Mobile)
    ↓
Frontend/Mobile App
    ↓ (HTTP/REST API)
Backend API (FastAPI)
    ↓
Database (Supabase)
    ↓
Response (JSON)
    ↑
Frontend/Mobile App
    ↓
Rendered UI
```

### 5.2 Scheduled Data Update Flow
```
GitHub Actions (CRON)
    ↓
Run Python Script
    ↓
Fetch External Data (yfinance, etc.)
    ↓
Process & Calculate Metrics
    ↓
Write to Database
    ↓
Trigger Notifications (optional)
```

---

## 6. Key Features

| Feature | Layer(s) | Status |
|---------|----------|--------|
| User Authentication | Auth + Backend + Database | ✅ Core |
| Options Screener | Frontend/Mobile + Backend | ✅ Core |
| Greeks Calculator | Backend + Frontend | ✅ Core |
| Market Regime Analysis | Backend + Frontend | ✅ Core |
| Weekly Picks | Backend + Frontend | ✅ Core |
| Trade Log | Frontend/Mobile + Backend | ✅ Core |
| Real-time Updates | WebSocket (optional) | 🔄 Optional |
| Push Notifications | Mobile + Backend | 🔄 Optional |
| Advanced Charting | Tremor + Frontend | ✅ Core |
| Data Export | Backend + Frontend | 🔄 Optional |

---

## 7. Security Considerations

- **Authentication:** Supabase Auth with JWT tokens
- **Authorization:** Row-Level Security (RLS) policies on database
- **API:** Rate limiting, input validation (Pydantic)
- **Data:** Encrypted at transit (HTTPS) and at rest
- **Secrets:** Environment variables (no hardcoding)
- **CI/CD:** Secure GitHub Actions workflows

---

## 8. Scalability & Performance

| Aspect | Strategy |
|--------|----------|
| **Frontend Load** | Vercel CDN + edge caching |
| **API Calls** | React Query caching + pagination |
| **Database Queries** | Indexes, query optimization, RLS |
| **Compute** | Render auto-scaling |
| **Background Jobs** | Async tasks, scheduled cleanup |
| **Real-time Updates** | WebSocket connections (optional) |

---

## 9. Deployment Environments

| Environment | Web | Mobile | API | Database |
|-------------|-----|--------|-----|----------|
| **Development** | localhost:5173 | Expo Dev Client | localhost:8000 | Local/Dev Supabase |
| **Staging** | preview.stridealytics... | TestFlight | staging-api... | Staging Supabase |
| **Production** | stridealytics.vercel.app | App Store/Play | api.stridealytics... | Production Supabase |

---

## 10. Integration Points

### External APIs
- **yfinance** - Market data, historical prices, options data
- **Other Data Providers** - Additional market feeds (optional)

### Internal Services
- **Backend ↔ Database** - Direct SQL queries via Supabase client
- **Frontend ↔ Backend** - REST API over HTTPS
- **Mobile ↔ Backend** - REST API over HTTPS
- **Schedulers ↔ Backend** - Direct database access via Python client

---

## 11. Project Structure (High-Level)

```
stridealytics/
├── frontend/              # React web application
├── mobile/                # React Native mobile app
├── backend/               # FastAPI backend services
├── database/              # Supabase migrations & schema
├── scheduler/             # GitHub Actions workflows
├── shared/                # Shared types, constants, utils
└── infra/                 # Deployment & infrastructure configs
```

See [03-FOLDER-STRUCTURE](./03-FOLDER-STRUCTURE.md) for complete details.

---

## 12. Next Steps

- **Understanding Layers?** → Read specific [LAYERS/](./LAYERS/) documents
- **Viewing Diagrams?** → See [02-SYSTEM-DIAGRAMS](./02-SYSTEM-DIAGRAMS.md)
- **Folder Details?** → Check [03-FOLDER-STRUCTURE](./03-FOLDER-STRUCTURE.md)
- **Tech Stack?** → Review [LIBRARIES-BY-LAYER](./REFERENCES/LIBRARIES-BY-LAYER.md)
- **Deployment?** → Go to [06-DEPLOYMENT-LAYER](./LAYERS/06-DEPLOYMENT-LAYER.md) + [07-CI-CD-LAYER](./LAYERS/07-CI-CD-LAYER.md)

---

**Version:** A | **Last Updated:** 2026-06-15
