# StrideAlytics — Implementation Blueprint

**Complete technical specification, architecture diagrams, and 4-week launch plan**

---

## Executive Summary

### Platform Overview

StrideAlytics is a **free-tier options trading analytics platform** with multi-platform support (web, mobile, API) designed for sophisticated options traders and analysts.

**Core Value Proposition:**
- Real-time options screener with advanced filters (strike, expiry, Greeks, IV)
- Black-Scholes Greeks calculator for risk analysis
- Portfolio tracking with trade analytics
- Market regime detection (bull/bear/ranging)
- Weekly options picks based on technical analysis
- Mobile-first experience with offline support

### Target Users
- Options traders (retail + institutional)
- Risk analysts
- Portfolio managers
- Trading educators

### Business Model — Free Tier with Paid Upgrades

```
┌─────────────────────────────────────────────────┐
│ FREE TIER (All users start here)                │
├─────────────────────────────────────────────────┤
│ • Screener (50 results/day)                     │
│ • Greeks calculator (unlimited)                 │
│ • Market regime (1 update/day)                  │
│ • Basic portfolio tracking                      │
│ • Mobile app (iOS/Android)                      │
│ • Web access (no login required)                │
│ Cost: $0/month                                  │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│ PRO TIER (Upgrade triggers at 100 results/day)  │
├─────────────────────────────────────────────────┤
│ • Unlimited screener results                    │
│ • Real-time Greeks updates                      │
│ • Regime updates (hourly)                       │
│ • Advanced portfolio analytics                  │
│ • Trade PnL tracking                            │
│ • API access for bots                           │
│ • No ads                                        │
│ Cost: $19/month                                 │
└─────────────────────────────────────────────────┘
```

### Cost Structure (Free Tier)

| Service | Free Tier | Cost/Month |
|---------|-----------|-----------|
| Vercel (Frontend CDN) | 100 GB bandwidth | ~$0-5 |
| Render (Backend) | 750 compute hours | ~$10 |
| Supabase (Database) | 1 GB storage, 500K rows | ~$0 |
| GitHub Actions | 2,000 minutes | ~$0 |
| SendGrid (Email) | 100/day | ~$0 |
| **Total** | | ~**$10/month** |

**Revenue Goal:** $3,000/month (158 PRO users @ $19)

---

## System Architecture

### High-Level Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                         USERS                                │
├──────────────────────────────────────────────────────────────┤
│  Web Browser          │    iOS App          │   Android App   │
│  React + Vite         │    React Native     │   React Native  │
│  Vercel Hosting       │    Expo SDK 50      │   Expo SDK 50   │
└─────────┬──────────────┴───────┬────────────┴────────┬────────┘
          │                       │                     │
          └───────────────────────┼─────────────────────┘
                                  │ HTTPS + JWT
                                  ↓
                    ┌─────────────────────────┐
                    │   FastAPI Backend       │
                    │   Render Hosting        │
                    │   Python 3.11           │
                    │   /api/v1/*             │
                    └────────┬────────────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ↓            ↓            ↓
        ┌──────────────┐ ┌──────────┐ ┌──────────────┐
        │ Supabase DB  │ │ Redis    │ │ yfinance API │
        │ PostgreSQL   │ │ Cache    │ │ External     │
        │ with RLS     │ │ (optional)│ │ market data  │
        └──────────────┘ └──────────┘ └──────────────┘
                │
                ↓
        ┌──────────────┐
        │ GitHub Actions
        │ Schedulers   │
        │ CRON jobs    │
        └──────────────┘
```

### Request/Response Flow

```
1. USER INITIATES REQUEST
   ↓
2. Frontend sends HTTP GET/POST with JWT token
   ↓
3. API Gateway validates JWT & applies rate limits
   ↓
4. Router directs to appropriate endpoint
   ↓
5. Middleware: JWT verification, CORS checks
   ↓
6. Service layer: Business logic execution
   ↓
7. Database layer: Query execution with RLS
   ↓
8. Response formatted with metadata
   ↓
9. Frontend receives, caches, and displays
```

### CI/CD Pipeline Architecture

```
Git Push (main branch)
    ↓
┌─────────────────────┐
│ GitHub Actions      │
│ Workflow Triggered  │
└────────┬────────────┘
         │
    ┌────┴────┐
    ↓         ↓
FRONTEND    BACKEND
    │         │
┌───┴──────┬──┴────┐
│          │       │
Lint    Test   Build
│          │       │
↓          ↓       ↓
Pass?   Pass?   Pass?
│          │       │
├──────────┴───────┤
        ↓
    DEPLOY STAGING
        │
   ├─ Run E2E tests
   ├─ Performance checks
   ├─ Security scan
        │
    ALL PASS?
        │
    ├─ Manual approval needed
        │
    DEPLOY PRODUCTION
        │
    ├─ Blue-green deployment
    ├─ Health checks
    ├─ Monitoring alerts
```

---

## Monorepo Folder Structure

### Complete Directory Tree

```
stridealytics/
│
├── frontend/                          # React + Vite web app
│   ├── src/
│   │   ├── components/
│   │   │   ├── screener/              # Screener UI components
│   │   │   ├── greeks/                # Greeks calculator UI
│   │   │   ├── ui/                    # Reusable components (Button, Card, etc.)
│   │   │   └── layout/                # Page layout components
│   │   ├── pages/                     # Page-level components
│   │   ├── hooks/                     # Custom React hooks
│   │   ├── store/                     # Zustand state management
│   │   ├── api/                       # API client & queries
│   │   ├── utils/                     # Utilities (formatters, validators)
│   │   ├── types/                     # TypeScript type definitions
│   │   └── theme/                     # Tailwind config & design tokens
│   ├── public/                        # Static assets
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── package.json
│   └── README.md
│
├── mobile/                            # React Native + Expo app
│   ├── app/                           # Expo Router screens (file-based routing)
│   │   ├── (tabs)/                    # Tab-based navigation
│   │   ├── screener/                  # Screener screens
│   │   ├── auth/                      # Auth screens
│   │   └── _layout.tsx                # Root layout
│   ├── components/
│   │   ├── ui/                        # Reusable components
│   │   ├── charts/                    # Chart components
│   │   └── layout/                    # Layout components
│   ├── hooks/
│   ├── store/
│   ├── api/
│   ├── types/
│   ├── assets/
│   ├── app.json                       # Expo config
│   ├── eas.json                       # EAS config (build & deployment)
│   ├── package.json
│   └── README.md
│
├── backend/                           # FastAPI Python backend
│   ├── app/
│   │   ├── main.py                    # FastAPI application entry
│   │   ├── config.py                  # Configuration & environment
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── router.py          # Main router
│   │   │   │   ├── endpoints/         # Route handlers
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── screener.py
│   │   │   │   │   ├── greeks.py
│   │   │   │   │   ├── regime.py
│   │   │   │   │   ├── portfolio.py
│   │   │   │   │   └── trades.py
│   │   │   │   └── schemas/           # Pydantic request/response models
│   │   │   │       ├── auth.py
│   │   │   │       ├── screener.py
│   │   │   │       └── ...
│   │   │   └── middleware/            # Custom middleware
│   │   │       ├── auth.py            # JWT verification
│   │   │       ├── error_handler.py
│   │   │       └── logging.py
│   │   ├── services/                  # Business logic layer
│   │   │   ├── screener.py            # Screener filtering
│   │   │   ├── greeks.py              # Black-Scholes calculation
│   │   │   ├── regime.py              # Market regime detection
│   │   │   ├── auth.py                # Authentication
│   │   │   └── portfolio.py           # Portfolio analytics
│   │   ├── database/
│   │   │   ├── client.py              # Database client init
│   │   │   ├── queries/               # Query functions by entity
│   │   │   │   ├── user.py
│   │   │   │   ├── portfolio.py
│   │   │   │   ├── trade.py
│   │   │   │   └── option.py
│   │   │   └── migrations/            # SQL migration files
│   │   │       ├── 001_initial.sql
│   │   │       ├── 002_auth.sql
│   │   │       └── 003_indexes.sql
│   │   ├── models/                    # Data models
│   │   ├── utils/
│   │   │   ├── logger.py              # Structured logging
│   │   │   ├── validators.py
│   │   │   └── constants.py
│   │   └── external/                  # External APIs
│   │       ├── yfinance.py            # Market data fetching
│   │       └── slack.py               # Notifications
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── scripts/
│   │   ├── seed_database.py
│   │   └── run_migrations.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   ├── .env.example
│   ├── pytest.ini
│   └── README.md
│
├── database/                          # Database schema & migrations
│   ├── migrations/
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_add_rls_policies.sql
│   │   ├── 003_add_indexes.sql
│   │   └── 004_add_functions.sql
│   ├── rls-policies/                  # Row-Level Security
│   │   ├── users.sql
│   │   ├── portfolios.sql
│   │   └── trades.sql
│   ├── functions/                     # Stored procedures
│   │   └── calculate_portfolio_stats.sql
│   ├── views/                         # Database views
│   │   └── portfolio_summary.sql
│   ├── seeds/
│   │   ├── dev_users.sql
│   │   └── test_data.sql
│   ├── schema.sql                     # Complete schema
│   └── README.md
│
├── scheduler/                         # GitHub Actions & CRON jobs
│   ├── .github/workflows/
│   │   ├── fetch-market-data.yml      # Daily data fetch
│   │   ├── calculate-greeks.yml       # Greeks calculation
│   │   ├── generate-weekly-picks.yml  # Weekly analysis
│   │   ├── health-check.yml           # Service health
│   │   └── templates/
│   │       └── reusable-workflow.yml  # Reusable workflow
│   ├── scripts/
│   │   ├── fetch_market_data.py
│   │   ├── calculate_greeks.py
│   │   ├── generate_picks.py
│   │   ├── send_notifications.py
│   │   └── health_check.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── shared/                            # Shared types & utilities
│   ├── types/
│   │   ├── index.ts                   # All TypeScript types
│   │   ├── api.types.ts
│   │   ├── models.types.ts
│   │   ├── database.types.ts
│   │   └── enums.ts
│   ├── schemas/
│   │   ├── index.ts                   # All Zod schemas
│   │   ├── user.schema.ts
│   │   ├── option.schema.ts
│   │   ├── portfolio.schema.ts
│   │   └── trade.schema.ts
│   ├── constants/
│   │   ├── api.constants.ts
│   │   └── ui.constants.ts
│   └── README.md
│
├── infra/                             # Infrastructure & deployment
│   ├── docker/
│   │   ├── Dockerfile.backend
│   │   └── docker-compose.yml
│   ├── vercel/
│   │   ├── vercel.json
│   │   └── README.md
│   ├── render/
│   │   ├── render.yaml
│   │   └── README.md
│   ├── terraform/                     # Optional IaC (future)
│   │   └── main.tf
│   ├── k8s/                           # Optional Kubernetes (future)
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── README.md
│
├── docs/                              # Documentation (you are here)
│   ├── 00-ARCHITECTURE-INDEX.md
│   ├── 01-SYSTEM-OVERVIEW.md
│   ├── 02-SYSTEM-DIAGRAMS.md
│   ├── 03-FOLDER-STRUCTURE.md
│   ├── LAYERS/
│   ├── REFERENCES/
│   ├── RULES/
│   ├── PHASES/                        # Implementation phases
│   ├── GUIDES/                        # Setup & operations
│   └── README.md
│
├── .github/
│   ├── workflows/                     # GitHub Actions CI/CD
│   │   ├── frontend-deploy.yml
│   │   ├── backend-deploy.yml
│   │   ├── mobile-build.yml
│   │   └── database-migrate.yml
│   └── ISSUE_TEMPLATE/
│
├── .env.example                       # Environment variables template
├── package.json                       # Monorepo root (npm workspaces)
├── pnpm-workspace.yaml                # Or PNPM workspaces
├── .gitignore
├── .eslintrc.json                     # Shared ESLint config
├── .prettierrc                        # Shared Prettier config
├── README.md                          # Project overview
└── CONTRIBUTING.md                    # Contribution guidelines
```

---

## Frontend (Web) — Complete Stack

### Technology Stack

```
Framework:        React 18.2.0 with TypeScript
Build Tool:       Vite 4.4.0
Styling:          TailwindCSS 3.3.0
Components:       shadcn/ui + Tremor
State:            Zustand 4.4.0
Data Fetching:    @tanstack/react-query 4.32.0
Forms:            react-hook-form 7.45.0 + Zod 3.22.0
Routing:          react-router-dom 6.14.0
HTTP:             Axios 1.4.0
Icons:            Lucide Icons
Hosting:          Vercel
```

### Page Routes & Components

```
/                           # Home/Dashboard (public)
  ├── DashboardPage
  │   ├── MarketSummary
  │   ├── TopMovers
  │   └── QuickStats

/screener                   # Options Screener
  ├── ScreenerPage
  │   ├── FilterPanel
  │   ├── ResultsTable
  │   ├── OptionDetail (modal)
  │   └── ResultsPagination

/greeks                     # Greeks Calculator
  ├── GreeksPage
  │   ├── InputForm
  │   ├── GreeksCalculator (engine)
  │   ├── ResultsDisplay
  │   └── ChartViz

/regime                     # Market Regime
  ├── RegimePage
  │   ├── RegimeChart
  │   ├── Indicators
  │   └── HistoricalView

/picks                      # Weekly Picks
  ├── PicksPage
  │   ├── PicksList
  │   └── PickDetail

/portfolio                  # Portfolio (protected)
  ├── PortfolioPage
  │   ├── PortfolioSummary
  │   ├── TradesList
  │   ├── TradeDetail
  │   └── PnLChart

/auth/login                 # Login
/auth/signup                # Signup
/settings                   # User Settings (protected)
```

### State Architecture (Zustand)

```typescript
// Store structure
store/
├── auth.store.ts          # User, token, permissions
├── screener.store.ts      # Filters, results, pagination
├── greeks.store.ts        # Calculation inputs, results
├── portfolio.store.ts     # User's portfolio data
├── ui.store.ts            # UI state (modals, sidebaropen, etc.)
└── index.ts               # Exports all stores

// Example auth store
export const useAuthStore = create((set) => ({
  user: null,
  token: null,
  login: (user, token) => set({ user, token }),
  logout: () => set({ user: null, token: null }),
}))
```

### API Client Setup

```typescript
// api/client.ts
import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://api.stridealytics.com',
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor: add JWT token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: handle 401, refresh token
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Attempt refresh, redirect to login if failed
      await refreshToken()
    }
    return Promise.reject(error)
  }
)

export default client
```

### Data Fetching Hooks

```typescript
// hooks/useScreener.ts
import { useQuery } from '@tanstack/react-query'
import client from '../api/client'

export const useScreenerData = (filters) => {
  return useQuery({
    queryKey: ['screener', filters],
    queryFn: async () => {
      const { data } = await client.get('/api/v1/screener', { params: filters })
      return data
    },
    staleTime: 5 * 60 * 1000,  // 5 min cache
    gcTime: 30 * 60 * 1000,    // 30 min retention
    retry: 2,
  })
}
```

---

## Mobile (Expo) — Complete Stack

### Technology Stack

```
Framework:        React Native 0.73.0 with TypeScript
Platform:         Expo SDK 50.0.0
Routing:          Expo Router (file-based)
Styling:          NativeWind + Tailwind
Components:       Tamagui + custom components
State:            Zustand 4.4.0
Data Fetching:    @tanstack/react-query 4.32.0
Auth:             Expo SecureStore + Supabase
Biometric Auth:   expo-local-authentication
Storage:          Expo SecureStore (encrypted)
Notifications:    expo-notifications
Build/Deploy:     Expo EAS Build & Submit
```

### App Structure (Expo Router)

```
app/
├── _layout.tsx              # Root layout, navigation setup
├── index.tsx                # Splash/home screen
├── login.tsx                # Login screen
├── signup.tsx               # Signup screen
│
├── (tabs)/                  # Tab-based navigation
│   ├── _layout.tsx          # Tab layout with bottom tab bar
│   ├── dashboard.tsx        # Dashboard tab
│   ├── screener.tsx         # Screener tab
│   ├── greeks.tsx           # Greeks tab
│   ├── regime.tsx           # Regime tab
│   └── profile.tsx          # Profile tab
│
├── screener/                # Stack-based route
│   ├── _layout.tsx          # Header with back button
│   ├── index.tsx            # List of recent screeners
│   └── [id].tsx             # Detail view (dynamic)
│
├── portfolio/               # Protected route
│   ├── _layout.tsx
│   ├── index.tsx            # Portfolio list
│   └── [id].tsx             # Portfolio detail
│
└── _error.tsx               # Error boundary
```

### Authentication Flow

```
┌─────────────────────┐
│  Mobile App Launch  │
└──────────┬──────────┘
           │
           ↓
    ┌─────────────────────────┐
    │ Check secure storage    │
    │ for refresh_token       │
    └────┬──────────┬─────────┘
         │          │
       YES          NO
         │          │
    ┌────▼──┐  ┌────▼──────┐
    │ Try   │  │ Show      │
    │ silent│  │ login     │
    │ refresh
│  │ screen    │
    └────┬──┘  └───┬──────┘
         │         │
         ├─────┬───┘
               │
          ┌────▼────────────────┐
          │ POST /auth/refresh  │
          │ or login            │
          └────┬─────────┬──────┘
               │         │
            SUCCESS    FAILURE
               │         │
          ┌────▼────┐ ┌──▼────────┐
          │ Store   │ │ Clear     │
          │ tokens  │ │ storage   │
          └────┬────┘ └──┬────────┘
               │         │
               └────┬────┘
                    │
              ┌─────▼─────────┐
              │ Proceed to    │
              │ app or logout │
              └───────────────┘
```

### Secure Token Handling

```typescript
// utils/secureStorage.ts
import * as SecureStore from 'expo-secure-store'

export const saveToken = async (token: string) => {
  try {
    await SecureStore.setItemAsync('auth_token', token)
  } catch (error) {
    console.error('Failed to save token', error)
  }
}

export const getToken = async (): Promise<string | null> => {
  try {
    return await SecureStore.getItemAsync('auth_token')
  } catch (error) {
    console.error('Failed to retrieve token', error)
    return null
  }
}

export const clearToken = async () => {
  try {
    await SecureStore.deleteItemAsync('auth_token')
  } catch (error) {
    console.error('Failed to clear token', error)
  }
}
```

### Biometric Authentication

```typescript
// hooks/useBiometricAuth.ts
import * as LocalAuthentication from 'expo-local-authentication'

export const useBiometricAuth = () => {
  const [isBiometricAvailable, setIsBiometricAvailable] = useState(false)

  useEffect(() => {
    LocalAuthentication.hasHardwareAsync().then(setIsBiometricAvailable)
  }, [])

  const authenticate = async () => {
    try {
      await LocalAuthentication.authenticateAsync({
        disableDeviceFallback: false,
        reason: 'Authenticate to access your portfolio',
      })
      return true
    } catch {
      return false
    }
  }

  return { isBiometricAvailable, authenticate }
}
```

---

## Backend (FastAPI) — Complete Stack

### Technology Stack

```
Framework:        FastAPI 0.100.0
Server:           Uvicorn 0.23.0
Validation:       Pydantic 2.1.0
Database:         Supabase (PostgreSQL 15+)
Auth:             python-jose (JWT) + Supabase
Data Processing:  Pandas 2.0.0, NumPy 1.24.0
Technical Analysis: TA-Lib 0.4.27
Market Data:      yfinance 0.2.28
HTTP Client:      HTTPX 0.24.0 (async)
Logging:          structlog 23.1.0
Testing:          pytest 7.4.0
Code Quality:     black, pylint, mypy
Hosting:          Render
```

### Router Structure

```python
# app/api/v1/router.py
from fastapi import APIRouter, Depends
from .endpoints import auth, screener, greeks, regime, portfolio, trades

router = APIRouter(prefix='/api/v1')

router.include_router(auth.router, prefix='/auth', tags=['auth'])
router.include_router(screener.router, prefix='/screener', tags=['screener'])
router.include_router(greeks.router, prefix='/greeks', tags=['greeks'])
router.include_router(regime.router, prefix='/regime', tags=['regime'])
router.include_router(portfolio.router, prefix='/portfolio', tags=['portfolio'])
router.include_router(trades.router, prefix='/trades', tags=['trades'])

# Health check
@router.get('/health')
async def health():
    return {'status': 'ok'}
```

### JWT Verification Middleware

```python
# app/api/middleware/auth.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt
import os

security = HTTPBearer()

async def verify_jwt(credentials: HTTPAuthCredentials = Depends(security)):
    """Verify JWT token from Authorization header"""
    token = credentials.credentials
    secret = os.getenv('SUPABASE_JWT_SECRET')
    
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        user_id: str = payload.get('sub')
        if user_id is None:
            raise HTTPException(status_code=401, detail='Invalid token')
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid token')
```

### Black-Scholes Greeks Engine

```python
# app/services/greeks.py
import math
from scipy import stats

def calculate_greeks(
    spot: float,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float = 0.05,
    volatility: float = 0.20,
    option_type: str = 'call'
) -> dict:
    """
    Calculate option Greeks using Black-Scholes model
    
    Args:
        spot: Current stock price
        strike: Strike price
        time_to_expiry: Time to expiry in years
        risk_free_rate: Risk-free interest rate
        volatility: Implied volatility
        option_type: 'call' or 'put'
    
    Returns:
        Dictionary with Greeks: delta, gamma, theta, vega, rho
    """
    
    # Pre-calculations
    sqrt_t = math.sqrt(time_to_expiry)
    d1 = (math.log(spot / strike) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) / (volatility * sqrt_t)
    d2 = d1 - volatility * sqrt_t
    
    # Cumulative normal distributions
    nd1 = stats.norm.cdf(d1)
    nd2 = stats.norm.cdf(d2)
    npd1 = stats.norm.pdf(d1)
    
    # Greeks calculation
    if option_type == 'call':
        delta = nd1
        theta = (-spot * npd1 * volatility / (2 * sqrt_t) - 
                 risk_free_rate * strike * math.exp(-risk_free_rate * time_to_expiry) * nd2) / 365
    else:  # put
        delta = nd1 - 1
        theta = (-spot * npd1 * volatility / (2 * sqrt_t) + 
                 risk_free_rate * strike * math.exp(-risk_free_rate * time_to_expiry) * (1 - nd2)) / 365
    
    gamma = npd1 / (spot * volatility * sqrt_t)
    vega = spot * npd1 * sqrt_t / 100  # Per 1% change in IV
    rho = (strike * time_to_expiry * math.exp(-risk_free_rate * time_to_expiry) * nd2) / 100  # Per 1% rate change
    
    return {
        'delta': round(delta, 4),
        'gamma': round(gamma, 6),
        'theta': round(theta, 4),
        'vega': round(vega, 4),
        'rho': round(rho, 4),
        'price_call': calculate_option_price(spot, strike, time_to_expiry, risk_free_rate, volatility, 'call'),
        'price_put': calculate_option_price(spot, strike, time_to_expiry, risk_free_rate, volatility, 'put'),
    }
```

### Endpoint Example

```python
# app/api/v1/endpoints/greeks.py
from fastapi import APIRouter, Depends
from app.api.middleware.auth import verify_jwt
from app.api.v1.schemas.greeks import GreeksRequest, GreeksResponse
from app.services.greeks import calculate_greeks

router = APIRouter()

@router.post('/calculate', response_model=GreeksResponse)
async def calculate(
    request: GreeksRequest,
    user_id: str = Depends(verify_jwt)  # JWT verified here
):
    """Calculate Greeks for given parameters"""
    greeks = calculate_greeks(
        spot=request.spot,
        strike=request.strike,
        time_to_expiry=request.time_to_expiry,
        volatility=request.iv,
        option_type=request.option_type
    )
    
    return {
        'success': True,
        'data': greeks,
        'metadata': {'user_id': user_id}
    }
```

---

## Database (Supabase PostgreSQL)

### Core Schema (7 Tables)

#### 1. Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT auth.uid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    subscription_plan TEXT DEFAULT 'free',  -- 'free', 'pro'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT subscription_plan_check 
        CHECK (subscription_plan IN ('free', 'pro'))
);
```

#### 2. Portfolios Table

```sql
CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(user_id, name)
);
```

#### 3. Trades Table

```sql
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    trade_type TEXT NOT NULL,  -- 'call', 'put', 'stock'
    direction TEXT NOT NULL,   -- 'long', 'short'
    entry_price DECIMAL(10,2) NOT NULL,
    exit_price DECIMAL(10,2),
    quantity INTEGER NOT NULL,
    entry_date TIMESTAMP WITH TIME ZONE NOT NULL,
    exit_date TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT trade_type_check CHECK (trade_type IN ('call', 'put', 'stock')),
    CONSTRAINT direction_check CHECK (direction IN ('long', 'short'))
);
```

#### 4. Options Table

```sql
CREATE TABLE options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    strike DECIMAL(10,2) NOT NULL,
    expiry DATE NOT NULL,
    option_type TEXT NOT NULL,  -- 'call', 'put'
    bid DECIMAL(10,4),
    ask DECIMAL(10,4),
    last_price DECIMAL(10,4),
    implied_vol DECIMAL(5,4),   -- 0.2 = 20%
    delta DECIMAL(5,4),
    gamma DECIMAL(7,6),
    theta DECIMAL(5,4),
    vega DECIMAL(5,4),
    rho DECIMAL(5,4),
    open_interest INTEGER,
    volume INTEGER,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    PRIMARY KEY (symbol, strike, expiry, option_type)
);
```

#### 5. Portfolio Summary View

```sql
CREATE VIEW portfolio_summary AS
SELECT
    p.id,
    p.user_id,
    p.name,
    COUNT(t.id) as total_trades,
    SUM(CASE WHEN t.exit_price IS NULL THEN 1 ELSE 0 END) as open_trades,
    ROUND(SUM(CASE 
        WHEN t.exit_price IS NOT NULL THEN (t.exit_price - t.entry_price) * t.quantity
        ELSE 0 
    END)::numeric, 2) as total_pnl,
    p.created_at,
    p.updated_at
FROM portfolios p
LEFT JOIN trades t ON p.id = t.portfolio_id
GROUP BY p.id, p.user_id, p.name, p.created_at, p.updated_at;
```

### Row-Level Security (RLS) Policies

```sql
-- Enable RLS on all tables
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;

-- Portfolios: Users can only see their own
CREATE POLICY portfolio_select ON portfolios
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY portfolio_insert ON portfolios
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Trades: Users can only modify their own trades
CREATE POLICY trades_select ON trades
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY trades_update ON trades
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);
```

### Migration Example

```sql
-- migrations/001_initial_schema.sql
-- Run with: supabase db push

BEGIN;

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT auth.uid(),
    email TEXT UNIQUE NOT NULL,
    ...
);

CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    ...
);

-- Create indexes
CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX idx_trades_portfolio_id ON trades(portfolio_id);

COMMIT;
```

---

## Authentication Architecture

### Complete JWT Flow

```
┌─────────────────────────────────────────────────┐
│ 1. SIGNUP / LOGIN                               │
└─────────────────┬───────────────────────────────┘
                  │
                  ↓
    ┌─────────────────────────────────────┐
    │ Frontend sends credentials:         │
    │ POST /auth/login                    │
    │ { email, password }                 │
    └─────────────┬───────────────────────┘
                  │
                  ↓
    ┌─────────────────────────────────────────────┐
    │ Backend: Supabase Auth               │
    │ 1. Hash password (bcrypt)           │
    │ 2. Verify against DB                │
    │ 3. Create JWT token                 │
    │    - iss: supabase issuer           │
    │    - sub: user_id (for RLS)         │
    │    - exp: expires in 3600s          │
    └─────────────┬───────────────────────────────┘
                  │
                  ↓
    ┌─────────────────────────────────────────────┐
    │ Response:                           │
    │ {                                   │
    │   "access_token": "jwt...",         │
    │   "token_type": "bearer",           │
    │   "expires_in": 3600                │
    │ }                                   │
    └─────────────┬───────────────────────────────┘
                  │
                  ↓
    ┌─────────────────────────────────────────────┐
    │ Frontend: Store token securely      │
    │ - Web: localStorage (with HTTPS)    │
    │ - Mobile: expo-secure-store         │
    └─────────────┬───────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────┐
│ 2. AUTHENTICATED REQUEST                        │
└─────────────────┬───────────────────────────────┘
                  │
                  ↓
    ┌─────────────────────────────────────────────┐
    │ Frontend sends all requests with:   │
    │ Authorization: Bearer <jwt_token>   │
    │                                     │
    │ GET /api/v1/portfolio               │
    │ Headers: { Authorization: Bearer... }
    └─────────────┬───────────────────────────────┘
                  │
                  ↓
    ┌─────────────────────────────────────────────┐
    │ Backend Middleware: JWT Verification│
    │ 1. Extract token from Authorization header
    │ 2. Verify signature using secret   │
    │ 3. Check expiration                 │
    │ 4. Extract user_id from 'sub'       │
    │ 5. Attach user_id to request context│
    └─────────────┬───────────────────────────────┘
                  │
                  ↓
    ┌─────────────────────────────────────────────┐
    │ Database Query with RLS             │
    │ SELECT * FROM portfolios            │
    │ WHERE user_id = '${auth.uid()}'     │
    │                                     │
    │ Only rows matching user_id returned!│
    └─────────────┬───────────────────────────────┘
                  │
                  ↓
    ┌─────────────────────────────────────────────┐
    │ Response to client                  │
    │ (filtered by RLS)                   │
    └─────────────────────────────────────────────┘
```

### RLS SQL Examples

```sql
-- Verify JWT is valid and extract user_id
SELECT auth.uid();  -- Returns current user_id from JWT

-- Automatic RLS filtering
SELECT * FROM portfolios;  
-- Returns only portfolios WHERE user_id = auth.uid()

-- Admin bypass (service role)
-- Use service role only for backend operations
SELECT * FROM portfolios;  -- No filtering
```

---

## Schedulers — CRON Workflows

### 5 Core Workflows

#### 1. Fetch Market Data (Daily @ 3:00 PM EST)

```yaml
# .github/workflows/fetch-market-data.yml
name: Fetch Market Data
on:
  schedule:
    - cron: '0 20 * * 1-5'  # 8 PM UTC = 3 PM EST, Mon-Fri

jobs:
  fetch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - run: pip install -r scheduler/requirements.txt
      
      - env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: python scheduler/scripts/fetch_market_data.py
      
      - name: Notify on failure
        if: failure()
        uses: slackapi/slack-github-action@v1.24.0
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
```

#### 2. Calculate Greeks (Daily @ 4:00 PM EST)

```yaml
# .github/workflows/calculate-greeks.yml
name: Calculate Greeks
on:
  schedule:
    - cron: '0 21 * * 1-5'  # 9 PM UTC = 4 PM EST

jobs:
  calculate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - run: pip install -r scheduler/requirements.txt
      
      - env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: python scheduler/scripts/calculate_greeks.py
```

#### 3. Generate Weekly Picks (Sundays @ 6:00 PM EST)

```yaml
# .github/workflows/generate-weekly-picks.yml
name: Generate Weekly Picks
on:
  schedule:
    - cron: '0 23 * * 0'  # 11 PM UTC Sunday

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r scheduler/requirements.txt
      
      - env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SENDGRID_API_KEY: ${{ secrets.SENDGRID_API_KEY }}
        run: python scheduler/scripts/generate_picks.py
```

#### 4. Health Checks (Every 5 minutes)

```yaml
# .github/workflows/health-check.yml
name: Health Checks
on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r scheduler/requirements.txt
      
      - run: python scheduler/scripts/health_check.py
      
      - name: Alert if down
        if: failure()
        uses: slackapi/slack-github-action@v1.24.0
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
```

### Reusable Workflow Template

```yaml
# templates/reusable-workflow.yml
name: Reusable Python Task
on:
  workflow_call:
    inputs:
      script_name:
        required: true
        type: string

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - run: pip install -r scheduler/requirements.txt
      
      - env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
          SENDGRID_API_KEY: ${{ secrets.SENDGRID_API_KEY }}
        run: python scheduler/scripts/${{ inputs.script_name }}.py
```

---

## Shared Logic

### TypeScript Types

```typescript
// shared/types/index.ts

// User
export interface User {
  id: string
  email: string
  full_name?: string
  subscription_plan: 'free' | 'pro'
}

// Portfolio
export interface Portfolio {
  id: string
  user_id: string
  name: string
  created_at: string
  updated_at: string
}

// Trade
export interface Trade {
  id: string
  portfolio_id: string
  symbol: string
  trade_type: 'call' | 'put' | 'stock'
  direction: 'long' | 'short'
  entry_price: number
  exit_price?: number
  quantity: number
  entry_date: string
  exit_date?: string
  pnl?: number
}

// Option
export interface Option {
  symbol: string
  strike: number
  expiry: string
  option_type: 'call' | 'put'
  bid: number
  ask: number
  implied_vol: number
  delta: number
  gamma: number
  theta: number
  vega: number
}

// Greeks Result
export interface Greeks {
  delta: number
  gamma: number
  theta: number
  vega: number
  rho: number
  price_call: number
  price_put: number
}
```

### Zod Schemas

```typescript
// shared/schemas/index.ts
import { z } from 'zod'

export const userSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  full_name: z.string().optional(),
  subscription_plan: z.enum(['free', 'pro']),
})

export const greeksRequestSchema = z.object({
  spot: z.number().positive(),
  strike: z.number().positive(),
  time_to_expiry: z.number().positive(),
  iv: z.number().min(0.001).max(5),
  option_type: z.enum(['call', 'put']),
})

export const portfolioSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(100),
  user_id: z.string().uuid(),
})
```

---

## Infrastructure & CI/CD

### Free-Tier Limits Table

| Service | Free Tier | Monthly Cost | Upgrade Trigger |
|---------|-----------|--------------|-----------------|
| **Vercel** | 100 GB bandwidth | $0-5 | >500 GB/month |
| **Render** | 750 compute hours | ~$10 | >400 req/min |
| **Supabase** | 500K rows, 1 GB | $0 | >1 GB or high RPS |
| **GitHub Actions** | 2,000 minutes | $0 | >40 hrs workflows/month |
| **SendGrid** | 100 emails/day | $0 | >100/day |
| **Total** | | **~$10** | |

### Environment Variables

```bash
# Frontend (.env)
VITE_API_URL=https://api.stridealytics.com
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=xxx

# Backend (.env)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
SUPABASE_JWT_SECRET=xxx
DATABASE_URL=postgresql://xxx
SENDGRID_API_KEY=xxx
SLACK_WEBHOOK=https://hooks.slack.com/xxx
ENVIRONMENT=production

# Mobile (.env)
EXPO_PUBLIC_API_URL=https://api.stridealytics.com
EXPO_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=xxx
```

### CI Pipeline YAML

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, staging]

jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - run: cd frontend && npm install
      - run: cd frontend && npm run lint
      - run: cd frontend && npm run test
      - run: cd frontend && npm run build
      
      - name: Deploy to Vercel
        if: github.ref == 'refs/heads/main'
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        run: npx vercel --prod --token $VERCEL_TOKEN

  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - run: cd backend && pip install -r requirements.txt
      - run: cd backend && pylint app/
      - run: cd backend && pytest
      
      - name: Build Docker image
        run: docker build -t stridealytics-backend .
      
      - name: Deploy to Render
        if: github.ref == 'refs/heads/main'
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: |
          curl -X POST https://api.render.com/deploy/xxx \
            -H "Authorization: Bearer $RENDER_API_KEY"
```

---

**Continue reading to see Implementation Phases, Upgrade Triggers, Roadmap, and Quick-Start Checklist →**

Version: Blueprint-A | Last Updated: 2026-06-15
