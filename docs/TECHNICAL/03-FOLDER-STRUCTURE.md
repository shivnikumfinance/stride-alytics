# StrideAlytics — Complete Folder Structure

**Comprehensive monorepo directory tree with all files, folders, and descriptions**

---

## Overview

```
stridealytics/
├── frontend/                          # Web App (React + Vite + Tremor)
├── mobile/                            # Mobile App (React Native + Expo)
├── backend/                           # Backend API (FastAPI)
├── database/                          # Database (Supabase migrations)
├── scheduler/                         # Schedulers (GitHub Actions)
├── shared/                            # Shared logic (Types, utils, constants)
├── infra/                             # Infrastructure configs (Docker, Vercel, Render)
└── docs/                              # Documentation (this folder)
```

---

## 1. Frontend (React + Vite + Tremor)

```
frontend/
│
├── src/
│   ├── components/
│   │   ├── ui/                        # shadcn/ui components
│   │   │   ├── button.jsx
│   │   │   ├── card.jsx
│   │   │   ├── modal.jsx
│   │   │   ├── badge.jsx
│   │   │   ├── table.jsx
│   │   │   └── ...more components
│   │   │
│   │   ├── charts/                    # Tremor chart wrappers
│   │   │   ├── LineChartWrapper.jsx
│   │   │   ├── BarChartWrapper.jsx
│   │   │   ├── AreaChartWrapper.jsx
│   │   │   ├── ScatterChartWrapper.jsx
│   │   │   └── ...more chart types
│   │   │
│   │   ├── layout/                    # Layout components
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Navbar.jsx
│   │   │   ├── Shell.jsx
│   │   │   ├── Footer.jsx
│   │   │   └── LayoutWrapper.jsx
│   │   │
│   │   └── tables/                    # Data tables
│   │       ├── ScreenerTable.jsx
│   │       ├── GreeksTable.jsx
│   │       ├── TradeLogTable.jsx
│   │       └── BaseTable.jsx
│   │
│   ├── pages/                          # Page components
│   │   ├── dashboard/
│   │   │   ├── Dashboard.jsx           # Main dashboard
│   │   │   ├── KPICards.jsx            # KPI metrics
│   │   │   └── widgets/                # Dashboard widgets
│   │   │       ├── MarketSummary.jsx
│   │   │       ├── PortfolioWidget.jsx
│   │   │       └── RecentTrades.jsx
│   │   │
│   │   ├── screener/
│   │   │   ├── Screener.jsx            # Main screener page
│   │   │   ├── ScreenerFilters.jsx     # Filter panel
│   │   │   ├── ScreenerResults.jsx     # Results grid
│   │   │   └── ScreenerDetail.jsx      # Stock detail modal
│   │   │
│   │   ├── greeks/
│   │   │   ├── Greeks.jsx              # Greeks calculator page
│   │   │   ├── GreeksInput.jsx         # Input form
│   │   │   ├── GreeksResults.jsx       # Display results
│   │   │   └── GreeksChart.jsx         # Visualization
│   │   │
│   │   ├── regime/
│   │   │   ├── Regime.jsx              # Regime analysis page
│   │   │   ├── RegimeChart.jsx         # Regime visualization
│   │   │   └── RegimeIndicators.jsx    # Indicator breakdown
│   │   │
│   │   ├── weekly-picks/
│   │   │   ├── WeeklyPicks.jsx         # Weekly recommendations
│   │   │   ├── PickCard.jsx            # Pick card component
│   │   │   └── PickDetail.jsx          # Detailed analysis
│   │   │
│   │   ├── trade-log/
│   │   │   ├── TradeLog.jsx            # Trade history
│   │   │   ├── TradeForm.jsx           # Add/edit trade
│   │   │   ├── TradeStats.jsx          # P&L stats
│   │   │   └── TradeExport.jsx         # Export trades
│   │   │
│   │   ├── auth/
│   │   │   ├── Login.jsx
│   │   │   ├── SignUp.jsx
│   │   │   ├── ForgotPassword.jsx
│   │   │   └── ProfilePage.jsx
│   │   │
│   │   ├── settings/
│   │   │   ├── Settings.jsx
│   │   │   ├── UserSettings.jsx
│   │   │   ├── NotificationSettings.jsx
│   │   │   └── ApiKeySettings.jsx
│   │   │
│   │   └── error/
│   │       ├── NotFound.jsx
│   │       ├── ErrorBoundary.jsx
│   │       └── UnauthorizedPage.jsx
│   │
│   ├── hooks/                          # Custom React hooks
│   │   ├── useAuth.js                  # Authentication context
│   │   ├── useScreener.js              # Screener data fetching
│   │   ├── useGreeks.js                # Greeks calculator logic
│   │   ├── useRegime.js                # Regime analysis logic
│   │   ├── useNotification.js           # Toast/notification system
│   │   ├── useLocalStorage.js           # Local storage wrapper
│   │   └── useDebounce.js              # Debouncing utility
│   │
│   ├── store/                          # Zustand state stores
│   │   ├── auth.store.js               # User, auth state
│   │   ├── screener.store.js           # Screener filters, results
│   │   ├── greeks.store.js             # Greeks form state
│   │   ├── regime.store.js             # Regime analysis state
│   │   ├── ui.store.js                 # UI state (modals, notifications)
│   │   └── cache.store.js              # Caching layer
│   │
│   ├── api/                            # API client & endpoints
│   │   ├── client.js                   # Axios instance
│   │   ├── endpoints.js                # Endpoint constants
│   │   ├── interceptors.js             # Request/response interceptors
│   │   │
│   │   └── queries/
│   │       ├── auth.queries.js         # Auth queries
│   │       ├── screener.queries.js     # Screener queries
│   │       ├── greeks.queries.js       # Greeks queries
│   │       ├── regime.queries.js       # Regime queries
│   │       └── portfolio.queries.js    # Portfolio queries
│   │
│   ├── utils/                          # Utility functions
│   │   ├── formatters.js               # Number/date formatting
│   │   ├── math.js                     # Mathematical operations
│   │   ├── helpers.js                  # General helpers
│   │   ├── validation.js               # Input validation
│   │   ├── constants.js                # App constants
│   │   └── colors.js                   # Color palette
│   │
│   ├── theme/                          # Styling & theme
│   │   ├── index.css                   # Global styles
│   │   ├── tailwind.config.js           # TailwindCSS config
│   │   ├── tokens.js                   # Design tokens
│   │   └── dark-mode.js                # Dark mode utilities
│   │
│   ├── types/                          # TypeScript types (if using TS)
│   │   ├── index.ts
│   │   ├── api.types.ts
│   │   ├── models.types.ts
│   │   └── ui.types.ts
│   │
│   ├── App.jsx                         # Root component
│   ├── main.jsx                        # Entry point
│   └── index.html                      # HTML template
│
├── public/                             # Static assets
│   ├── logo.png
│   ├── favicon.ico
│   └── ...assets
│
├── package.json                        # Dependencies
├── vite.config.js                      # Vite configuration
├── tailwind.config.js                  # Tailwind configuration
├── postcss.config.js                   # PostCSS configuration
├── .env.example                        # Environment variables template
├── .eslintrc.json                      # ESLint config
├── .prettierrc                         # Prettier config
└── README.md                           # Frontend documentation
```

---

## 2. Mobile (React Native + Expo)

```
mobile/
│
├── app/                                # Expo Router screens
│   ├── _layout.tsx                     # Root layout
│   ├── index.tsx                       # Home screen
│   ├── login.tsx                       # Login screen
│   ├── signup.tsx                      # Sign up screen
│   │
│   ├── (tabs)/                         # Tabbed layout
│   │   ├── _layout.tsx
│   │   ├── dashboard.tsx
│   │   ├── screener.tsx
│   │   ├── greeks.tsx
│   │   ├── regime.tsx
│   │   └── profile.tsx
│   │
│   ├── screener/
│   │   ├── _layout.tsx
│   │   ├── index.tsx                   # Screener list
│   │   └── [id].tsx                    # Screener detail
│   │
│   ├── greeks/
│   │   ├── _layout.tsx
│   │   ├── index.tsx                   # Greeks input
│   │   └── results.tsx                 # Results display
│   │
│   └── settings/
│       ├── _layout.tsx
│       ├── profile.tsx
│       ├── notifications.tsx
│       └── about.tsx
│
├── components/
│   ├── ui/                             # Custom UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Text.tsx
│   │   ├── Modal.tsx
│   │   └── ...more
│   │
│   ├── charts/                         # Chart components
│   │   ├── LineChart.tsx
│   │   ├── BarChart.tsx
│   │   ├── AreaChart.tsx
│   │   └── VictoryNativeCharts.tsx
│   │
│   ├── layout/
│   │   ├── TabBar.tsx
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── SafeAreaWrapper.tsx
│   │
│   └── tables/
│       ├── ScreenerTable.tsx
│       ├── DataTable.tsx
│       └── ScrollableTable.tsx
│
├── screens/                            # Full screen components
│   ├── DashboardScreen.tsx
│   ├── ScreenerScreen.tsx
│   ├── GreeksScreen.tsx
│   └── SettingsScreen.tsx
│
├── hooks/
│   ├── useAuth.ts
│   ├── useScreener.ts
│   ├── useGreeks.ts
│   ├── useNotification.ts
│   └── useAsyncStorage.ts
│
├── store/
│   ├── auth.store.ts
│   ├── screener.store.ts
│   ├── app.store.ts
│   └── notifications.store.ts
│
├── api/
│   ├── client.ts
│   ├── endpoints.ts
│   └── queries/
│       ├── screener.ts
│       ├── greeks.ts
│       └── auth.ts
│
├── utils/
│   ├── formatters.ts
│   ├── helpers.ts
│   ├── constants.ts
│   └── theme.ts
│
├── types/
│   ├── index.ts
│   ├── api.types.ts
│   └── models.types.ts
│
├── assets/
│   ├── images/
│   ├── fonts/
│   └── icons/
│
├── app.json                            # Expo configuration
├── app.config.js                       # Expo app config
├── package.json                        # Dependencies
├── eas.json                            # Expo EAS configuration
├── .env.example                        # Environment variables
├── .eslintrc.json                      # ESLint config
├── .prettierrc                         # Prettier config
├── tsconfig.json                       # TypeScript config
└── README.md                           # Mobile documentation
```

---

## 3. Backend (FastAPI)

```
backend/
│
├── app/
│   ├── main.py                         # FastAPI app initialization
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py                   # Main router
│   │   │
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py               # V1 router
│   │   │   │
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py             # Auth endpoints
│   │   │   │   ├── screener.py         # Screener endpoints
│   │   │   │   ├── greeks.py           # Greeks endpoints
│   │   │   │   ├── regime.py           # Regime analysis endpoints
│   │   │   │   ├── portfolio.py        # Portfolio endpoints
│   │   │   │   └── health.py           # Health check endpoints
│   │   │   │
│   │   │   └── schemas/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py             # Auth request/response schemas
│   │   │       ├── screener.py
│   │   │       ├── greeks.py
│   │   │       ├── portfolio.py
│   │   │       └── common.py
│   │
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── auth.py                 # JWT authentication
│   │       ├── logging.py              # Request logging
│   │       └── error_handler.py        # Global error handling
│   │
│   ├── services/                       # Business logic
│   │   ├── __init__.py
│   │   ├── screener.py                 # Screener logic
│   │   ├── greeks.py                   # Greeks calculations
│   │   ├── regime.py                   # Regime analysis
│   │   ├── portfolio.py                # Portfolio management
│   │   ├── data_fetch.py               # External data fetching
│   │   ├── auth.py                     # Authentication logic
│   │   └── notification.py             # Notification service
│   │
│   ├── models/                         # Data models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── portfolio.py
│   │   ├── options.py
│   │   ├── trade.py
│   │   └── regime.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── client.py                   # Supabase client
│   │   ├── dependencies.py             # Dependency injection
│   │   ├── queries/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── portfolio.py
│   │   │   ├── options.py
│   │   │   └── trade.py
│   │   │
│   │   └── migrations/
│   │       ├── 001_initial_schema.sql
│   │       ├── 002_add_trades.sql
│   │       └── ...migrations
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py                   # Logging setup
│   │   ├── validators.py               # Input validation
│   │   ├── math.py                     # Math utilities
│   │   ├── cache.py                    # Caching logic
│   │   ├── helpers.py                  # General helpers
│   │   └── constants.py                # Constants
│   │
│   ├── external/
│   │   ├── __init__.py
│   │   ├── yfinance.py                 # yfinance client
│   │   ├── options_api.py              # Options data API
│   │   └── ...other APIs
│   │
│   └── config.py                       # Configuration
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                     # Pytest fixtures
│   │
│   ├── unit/
│   │   ├── test_screener_service.py
│   │   ├── test_greeks_service.py
│   │   └── ...unit tests
│   │
│   ├── integration/
│   │   ├── test_screener_api.py
│   │   ├── test_auth_api.py
│   │   └── ...integration tests
│   │
│   └── fixtures/
│       ├── mock_data.py
│       └── sample_responses.py
│
├── scripts/
│   ├── __init__.py
│   ├── seed_database.py                # Seed test data
│   ├── run_migrations.py               # Migration runner
│   └── health_check.py                 # Health check script
│
├── Dockerfile                          # Docker configuration
├── docker-compose.yml                  # Docker compose (for dev)
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment variables template
├── .env.local                          # Local environment (git ignored)
├── .gitignore                          # Git ignore file
├── .dockerignore                       # Docker ignore file
├── pytest.ini                          # Pytest configuration
├── pyproject.toml                      # Project configuration
└── README.md                           # Backend documentation
```

---

## 4. Database (Supabase)

```
database/
│
├── migrations/
│   ├── 001_initial_schema.sql          # Initial tables & schema
│   ├── 002_add_auth_policies.sql       # RLS policies
│   ├── 003_add_user_tables.sql         # User-related tables
│   ├── 004_add_portfolio.sql           # Portfolio tables
│   ├── 005_add_trades.sql              # Trade log tables
│   ├── 006_add_options.sql             # Options data tables
│   ├── 007_add_regime.sql              # Regime analysis tables
│   ├── 008_add_indexes.sql             # Performance indexes
│   └── ...more migrations
│
├── schema.sql                          # Complete schema (combined)
│
├── rls-policies/
│   ├── users.sql                       # User row policies
│   ├── portfolios.sql                  # Portfolio row policies
│   ├── trades.sql                      # Trade row policies
│   └── options.sql                     # Options row policies
│
├── functions/                          # Supabase functions
│   ├── calculate_greeks.sql
│   ├── update_regime.sql
│   └── generate_report.sql
│
├── triggers/                           # Database triggers
│   ├── update_portfolio_stats.sql
│   ├── audit_trades.sql
│   └── validate_trade_entry.sql
│
├── views/                              # Database views
│   ├── portfolio_summary.sql
│   ├── options_summary.sql
│   └── trade_statistics.sql
│
├── seeds/
│   ├── dev_users.sql                   # Development users
│   ├── test_data.sql                   # Test data
│   └── sample_options.sql              # Sample options data
│
├── backups/
│   ├── 2026-06-01_backup.sql
│   └── ...backup files
│
├── scripts/
│   ├── apply_migrations.sh             # Apply all migrations
│   ├── rollback.sh                     # Rollback migrations
│   ├── seed_dev.sh                     # Seed dev database
│   └── export_schema.sh                # Export schema
│
├── .env.example                        # Environment variables
├── README.md                           # Database documentation
└── SCHEMA.md                           # Schema documentation
```

---

## 5. Scheduler (GitHub Actions)

```
scheduler/
│
├── .github/
│   └── workflows/
│       ├── fetch-market-data.yml       # Daily market data collection
│       ├── calculate-greeks.yml        # Daily Greeks calculation
│       ├── generate-regime.yml         # Weekly regime analysis
│       ├── generate-weekly-picks.yml   # Weekly picks generation
│       ├── health-check.yml            # Hourly health checks
│       ├── deploy-frontend.yml         # Frontend deployment (on push)
│       ├── deploy-backend.yml          # Backend deployment (on push)
│       ├── deploy-mobile.yml           # Mobile build (on tag)
│       ├── run-tests.yml               # Run all tests (on PR)
│       └── database-backup.yml         # Daily database backup
│
├── scripts/
│   ├── fetch_market_data.py            # Fetch market data
│   ├── calculate_greeks.py             # Calculate Greeks
│   ├── analyze_regime.py               # Analyze market regime
│   ├── generate_picks.py               # Generate picks
│   ├── send_notifications.py           # Send notifications
│   ├── health_check.py                 # Health checks
│   ├── backup_database.py              # Backup database
│   └── cleanup.py                      # Cleanup old data
│
├── requirements.txt                    # Python dependencies for schedulers
├── .env.example                        # Environment variables
└── README.md                           # Scheduler documentation
```

---

## 6. Shared (Shared Logic)

```
shared/
│
├── types/                              # Shared TypeScript types
│   ├── index.ts
│   ├── api.types.ts
│   ├── models.types.ts
│   ├── auth.types.ts
│   ├── portfolio.types.ts
│   └── options.types.ts
│
├── constants/
│   ├── index.ts
│   ├── api.constants.ts
│   ├── endpoints.constants.ts
│   ├── app.constants.ts
│   └── validation.constants.ts
│
├── utils/
│   ├── index.ts
│   ├── formatters.ts
│   ├── validators.ts
│   ├── math.ts
│   ├── helpers.ts
│   ├── date.ts
│   └── storage.ts
│
├── api-client/
│   ├── index.ts
│   ├── client.ts
│   ├── interceptors.ts
│   └── error-handler.ts
│
├── hooks/
│   ├── index.ts
│   ├── useApi.ts
│   ├── useAuth.ts
│   ├── useStorage.ts
│   └── ...shared hooks
│
├── package.json
├── tsconfig.json
└── README.md
```

---

## 7. Infrastructure (Deployment Configs)

```
infra/
│
├── docker/
│   ├── Dockerfile.frontend             # Frontend Docker image
│   ├── Dockerfile.backend              # Backend Docker image
│   ├── Dockerfile.scheduler            # Scheduler Docker image
│   └── docker-compose.yml              # Local development
│
├── vercel/
│   ├── vercel.json                     # Vercel deployment config
│   └── scripts/
│       ├── build.sh
│       └── start.sh
│
├── render/
│   ├── render.yaml                     # Render deployment config
│   └── scripts/
│       ├── build.sh
│       └── start.sh
│
├── kubernetes/
│   ├── deployment.yaml                 # K8s deployment (future)
│   ├── service.yaml
│   ├── ingress.yaml
│   └── namespace.yaml
│
├── terraform/
│   ├── main.tf                         # Main Terraform config
│   ├── variables.tf                    # Variables
│   ├── outputs.tf                      # Outputs
│   ├── backend.tf                      # State backend
│   └── modules/
│       ├── vercel/
│       ├── render/
│       └── supabase/
│
├── bicep/
│   ├── main.bicep                      # Main bicep template
│   ├── parameters.json                 # Parameters
│   └── modules/
│
├── secrets/
│   ├── .env.production                 # Production environment
│   ├── .env.staging                    # Staging environment
│   └── .gitignore                      # Keep secrets out of git
│
├── monitoring/
│   ├── datadog.yaml                    # Datadog config (optional)
│   ├── sentry.yaml                     # Sentry config (optional)
│   └── cloudwatch.yaml                 # CloudWatch config (optional)
│
├── scripts/
│   ├── deploy.sh                       # Deployment script
│   ├── scale-api.sh                    # Scale API
│   ├── backup-db.sh                    # Backup database
│   └── health-check.sh                 # Health checks
│
└── README.md                           # Infrastructure documentation
```

---

## 8. Documentation (This Folder)

```
docs/
│
├── 00-ARCHITECTURE-INDEX.md            # ← Navigation hub (START HERE)
├── 01-SYSTEM-OVERVIEW.md               # System description & tech stack
├── 02-SYSTEM-DIAGRAMS.md               # Visual diagrams
├── 03-FOLDER-STRUCTURE.md              # ← YOU ARE HERE
│
├── LAYERS/
│   ├── 01-FRONTEND-LAYER.md            # React layer details
│   ├── 02-MOBILE-LAYER.md              # React Native layer
│   ├── 03-BACKEND-LAYER.md             # FastAPI layer
│   ├── 04-DATABASE-LAYER.md            # Supabase layer
│   ├── 05-SCHEDULER-LAYER.md           # GitHub Actions layer
│   ├── 06-DEPLOYMENT-LAYER.md          # Deployment infrastructure
│   └── 07-CI-CD-LAYER.md               # CI/CD pipeline
│
├── REFERENCES/
│   ├── LIBRARIES-BY-LAYER.md           # Tech stack breakdown
│   └── INFRASTRUCTURE-OVERVIEW.md       # Services & deployment
│
└── RULES/
    ├── CODING-STANDARDS.md             # Code conventions
    ├── FOLDER-CONVENTIONS.md           # Naming rules
    └── DATA-FLOW-RULES.md              # Data contracts
```

---

## Root Level Files

```
stridealytics/
│
├── .github/
│   └── workflows/                      # GitHub Actions workflows
│
├── .gitignore                          # Git ignore rules
├── .env.example                        # Environment template
├── README.md                           # Main project README
├── package.json                        # Root monorepo package (if using)
├── pnpm-workspace.yaml                 # pnpm workspace config
├── lerna.json                          # Lerna config (if using)
├── docker-compose.yml                  # Local development
│
└── CONTRIBUTING.md                     # Contribution guidelines
```

---

## File Naming Conventions

- **Components:** PascalCase (e.g., `ScreenerTable.jsx`)
- **Utilities:** camelCase (e.g., `formatters.js`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `API_ENDPOINTS`)
- **Types:** PascalCase (e.g., `User.types.ts`)
- **Schemas:** camelCase (e.g., `user.schema.ts`)
- **Test files:** `*.test.js` or `*.spec.js`

---

## Next Steps

- **Understand each layer?** → Go to [LAYERS/](./LAYERS/)
- **See libraries?** → Check [LIBRARIES-BY-LAYER](./REFERENCES/LIBRARIES-BY-LAYER.md)
- **View diagrams?** → See [02-SYSTEM-DIAGRAMS](./02-SYSTEM-DIAGRAMS.md)
- **Deployment details?** → [06-DEPLOYMENT-LAYER](./LAYERS/06-DEPLOYMENT-LAYER.md)

---

**Version:** A | **Last Updated:** 2026-06-15
