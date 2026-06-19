# StrideAlytics — Folder Conventions

**Directory naming, organization, and structural guidelines**

---

## 1. Top-Level Organization

### Root Folders

```
stridealytics/
├── frontend/              # ← Start here for web development
├── mobile/                # ← Start here for app development
├── backend/               # ← Start here for API development
├── database/              # ← Database schema & migrations
├── scheduler/             # ← Automated tasks
├── shared/                # ← Shared types & utilities
├── infra/                 # ← Deployment & infrastructure
├── docs/                  # ← Documentation (you are here)
├── .github/               # ← GitHub Actions workflows
├── package.json           # ← Monorepo root (if using npm workspaces)
└── README.md              # ← Project overview
```

### Naming Rules for Top-Level Folders

✅ **DO:**
- Use lowercase with hyphens for multi-word folders: `database-migrations`
- Use descriptive names: `api-server` instead of `back`
- Keep names short but clear: `mobile` not `mobile-application`
- Use plural for collections: `services`, `models`, `utils`

❌ **DON'T:**
- Mix case: `Frontend`, `MOBILE`, `BackEnd`
- Use abbreviations: `fe`, `be`, `db`
- Use generic names: `src`, `lib`, `code`
- Use numbers as primary identifier: `app1`, `api2`

---

## 2. Frontend Folder Structure

### Standard Layout

```
frontend/
├── src/
│   ├── components/          # ← Group components by feature
│   │   ├── screener/
│   │   │   ├── ScreenerPage.jsx
│   │   │   ├── ScreenerFilters.jsx
│   │   │   ├── ScreenerTable.jsx
│   │   │   ├── __tests__/
│   │   │   │   └── ScreenerPage.test.jsx
│   │   │   └── screener.module.css
│   │   │
│   │   ├── greeks/
│   │   │   ├── GreeksPage.jsx
│   │   │   ├── GreeksCalculator.jsx
│   │   │   └── __tests__/
│   │   │
│   │   ├── ui/              # ← Reusable components
│   │   │   ├── Button.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Modal.jsx
│   │   │   ├── __tests__/
│   │   │   └── ui.module.css
│   │   │
│   │   └── layout/
│   │       ├── Sidebar.jsx
│   │       ├── Navbar.jsx
│   │       └── Shell.jsx
│   │
│   ├── pages/               # ← Page-level components (or use routing)
│   │   ├── Dashboard.jsx
│   │   ├── NotFound.jsx
│   │   └── ...
│   │
│   ├── hooks/               # ← Custom React hooks
│   │   ├── useAuth.js
│   │   ├── useScreener.js
│   │   ├── useQuery.js
│   │   └── index.js         # ← Export all hooks
│   │
│   ├── store/               # ← Zustand stores
│   │   ├── auth.store.js
│   │   ├── screener.store.js
│   │   ├── ui.store.js
│   │   └── index.js         # ← Export all stores
│   │
│   ├── api/                 # ← API-related code
│   │   ├── client.js        # ← Axios instance
│   │   ├── endpoints.js     # ← Endpoint constants
│   │   ├── interceptors.js
│   │   └── queries/
│   │       ├── screener.queries.js
│   │       ├── greeks.queries.js
│   │       └── index.js
│   │
│   ├── utils/               # ← Utility functions
│   │   ├── formatters.js    # ← Number, date formatting
│   │   ├── helpers.js       # ← General helpers
│   │   ├── validators.js    # ← Input validation
│   │   ├── constants.js     # ← App constants
│   │   └── index.js
│   │
│   ├── theme/               # ← Styling & design
│   │   ├── index.css        # ← Global styles
│   │   ├── tailwind.config.js
│   │   ├── tokens.js        # ← Design tokens
│   │   └── colors.js
│   │
│   ├── types/               # ← TypeScript types (if using TS)
│   │   ├── index.ts
│   │   ├── api.types.ts
│   │   └── models.types.ts
│   │
│   ├── App.jsx              # ← Root component
│   ├── main.jsx             # ← Entry point
│   └── index.html           # ← HTML template
│
├── public/                  # ← Static assets
│   ├── favicon.ico
│   ├── logo.png
│   └── ...
│
├── __tests__/               # ← Integration & e2e tests
│   ├── integration/
│   └── e2e/
│
├── package.json
├── vite.config.js
├── tsconfig.json
├── tailwind.config.js
├── .env.example
└── README.md
```

### Component Folder Organization

✅ **GOOD:**
```
src/components/screener/
├── ScreenerFilters.jsx      # Component file
├── ScreenerResults.jsx
├── __tests__/
│   ├── ScreenerFilters.test.jsx
│   └── ScreenerResults.test.jsx
├── screener.module.css      # Component-specific styles
└── index.js                 # Re-exports for easy importing
```

❌ **BAD:**
```
src/components/
├── ScreenerFilters.jsx
├── ScreenerFilters.test.jsx
├── ScreenerFilters.css
├── ScreenerResults.jsx
├── ScreenerResults.test.jsx
├── ScreenerResults.css
├── ... (mixed flat structure)
```

---

## 3. Mobile Folder Structure

### Standard Layout

```
mobile/
├── app/                     # ← Expo Router screens (file-based routing)
│   ├── _layout.tsx         # ← Root layout
│   ├── index.tsx           # ← Home/splash
│   ├── login.tsx
│   ├── signup.tsx
│   │
│   ├── (tabs)/             # ← Grouped routes (tab navigation)
│   │   ├── _layout.tsx     # ← Tabs layout
│   │   ├── dashboard.tsx
│   │   ├── screener.tsx
│   │   ├── greeks.tsx
│   │   ├── regime.tsx
│   │   └── profile.tsx
│   │
│   ├── screener/           # ← Stack-based routes
│   │   ├── _layout.tsx
│   │   ├── index.tsx       # ← List view
│   │   └── [id].tsx        # ← Detail view (dynamic route)
│   │
│   └── _error.tsx          # ← Error boundary
│
├── components/             # ← Reusable components
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── ...
│   │
│   ├── charts/
│   │   ├── LineChart.tsx
│   │   └── ...
│   │
│   └── layout/
│       ├── TabBar.tsx
│       └── ...
│
├── screens/                # ← Full screen components (if not using routing)
│   └── DashboardScreen.tsx
│
├── hooks/
│   ├── useAuth.ts
│   ├── useScreener.ts
│   └── index.ts
│
├── store/
│   ├── auth.store.ts
│   ├── screener.store.ts
│   └── index.ts
│
├── api/
│   ├── client.ts
│   ├── endpoints.ts
│   └── queries/
│       └── screener.ts
│
├── utils/
│   ├── formatters.ts
│   ├── helpers.ts
│   └── index.ts
│
├── types/
│   └── index.ts
│
├── assets/                 # ← Images, fonts, icons
│   ├── images/
│   ├── fonts/
│   └── icons/
│
├── app.json               # ← Expo config
├── eas.json               # ← EAS config
├── package.json
├── tsconfig.json
└── README.md
```

---

## 4. Backend Folder Structure

### Standard Layout

```
backend/
├── app/
│   ├── main.py              # ← FastAPI app
│   ├── config.py            # ← Configuration
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py        # ← Main router
│   │   │
│   │   └── v1/              # ← API version
│   │       ├── __init__.py
│   │       ├── router.py    # ← V1 router
│   │       │
│   │       ├── endpoints/   # ← Route handlers
│   │       │   ├── __init__.py
│   │       │   ├── auth.py
│   │       │   ├── screener.py
│   │       │   ├── greeks.py
│   │       │   └── ...
│   │       │
│   │       └── schemas/     # ← Request/response models
│   │           ├── __init__.py
│   │           ├── auth.py
│   │           ├── screener.py
│   │           └── ...
│   │
│   ├── api/middleware/      # ← Middleware
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── logging.py
│   │   └── error_handler.py
│   │
│   ├── services/            # ← Business logic (organized by feature)
│   │   ├── __init__.py
│   │   ├── screener.py
│   │   ├── greeks.py
│   │   ├── regime.py
│   │   ├── auth.py
│   │   └── ...
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── client.py        # ← DB client initialization
│   │   ├── dependencies.py  # ← Dependency injection
│   │   │
│   │   ├── queries/         # ← Query functions (organized by entity)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── portfolio.py
│   │   │   └── ...
│   │   │
│   │   └── migrations/      # ← SQL migration files
│   │       ├── 001_initial.sql
│   │       ├── 002_add_trades.sql
│   │       └── ...
│   │
│   ├── models/              # ← Data models/entities
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── portfolio.py
│   │   ├── option.py
│   │   └── ...
│   │
│   ├── utils/               # ← Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py        # ← Logging setup
│   │   ├── validators.py    # ← Validation
│   │   ├── helpers.py
│   │   └── constants.py
│   │
│   └── external/            # ← External integrations
│       ├── __init__.py
│       ├── yfinance.py      # ← yfinance wrapper
│       └── ...
│
├── tests/                   # ← Test files
│   ├── __init__.py
│   ├── conftest.py          # ← Pytest fixtures
│   │
│   ├── unit/                # ← Unit tests
│   │   ├── test_screener.py
│   │   └── ...
│   │
│   ├── integration/         # ← Integration tests
│   │   ├── test_screener_api.py
│   │   └── ...
│   │
│   └── fixtures/
│       ├── mock_data.py
│       └── ...
│
├── scripts/                 # ← Utility scripts
│   ├── seed_database.py
│   ├── run_migrations.py
│   └── ...
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── pytest.ini
├── pyproject.toml
└── README.md
```

---

## 5. Database Folder Structure

### Standard Layout

```
database/
├── migrations/              # ← SQL migration files (chronological)
│   ├── 001_initial_schema.sql
│   ├── 002_add_auth_policies.sql
│   ├── 003_add_indexes.sql
│   └── ...
│
├── rls-policies/            # ← Row-Level Security policies
│   ├── users.sql
│   ├── portfolios.sql
│   └── ...
│
├── functions/               # ← Stored procedures
│   ├── calculate_portfolio_stats.sql
│   └── ...
│
├── triggers/                # ← Database triggers
│   ├── update_updated_at.sql
│   └── ...
│
├── views/                   # ← Database views
│   ├── portfolio_summary.sql
│   └── ...
│
├── seeds/                   # ← Test/development data
│   ├── dev_users.sql
│   ├── test_data.sql
│   └── ...
│
├── schema.sql               # ← Complete schema (combined)
└── README.md
```

---

## 6. Scheduler Folder Structure

### Standard Layout

```
scheduler/
├── .github/
│   └── workflows/
│       ├── fetch-market-data.yml
│       ├── calculate-greeks.yml
│       ├── generate-weekly-picks.yml
│       └── ...
│
├── scripts/                 # ← Python scripts for tasks
│   ├── fetch_market_data.py
│   ├── calculate_greeks.py
│   ├── generate_picks.py
│   ├── send_notifications.py
│   └── ...
│
├── requirements.txt         # ← Python dependencies
├── .env.example
└── README.md
```

---

## 7. Documentation Folder Structure

### Your Location

```
docs/                           # ← You are here
│
├── 00-ARCHITECTURE-INDEX.md    # ← START HERE
├── 01-SYSTEM-OVERVIEW.md
├── 02-SYSTEM-DIAGRAMS.md
├── 03-FOLDER-STRUCTURE.md
│
├── LAYERS/                      # ← Architecture layers
│   ├── 01-FRONTEND-LAYER.md
│   ├── 02-MOBILE-LAYER.md
│   ├── 03-BACKEND-LAYER.md
│   ├── 04-DATABASE-LAYER.md
│   ├── 05-SCHEDULER-LAYER.md
│   ├── 06-DEPLOYMENT-LAYER.md
│   └── 07-CI-CD-LAYER.md
│
├── REFERENCES/                  # ← Supporting docs
│   ├── LIBRARIES-BY-LAYER.md
│   └── INFRASTRUCTURE-OVERVIEW.md
│
└── RULES/                       # ← Standards & conventions
    ├── CODING-STANDARDS.md
    ├── FOLDER-CONVENTIONS.md    # ← YOU ARE HERE
    └── DATA-FLOW-RULES.md
```

---

## 8. Naming Rules Summary

| Item | Convention | Example |
|------|-----------|---------|
| **Folders (top-level)** | lowercase-kebab-case | `frontend`, `backend`, `database` |
| **Components** | PascalCase | `ScreenerTable.jsx`, `UserProfile.tsx` |
| **Utilities** | camelCase | `formatters.js`, `authService.py` |
| **Constants** | UPPER_SNAKE_CASE | `API_BASE_URL`, `MAX_RETRIES` |
| **Test files** | \*.test/spec | `Button.test.jsx`, `screener.spec.js` |
| **Config files** | lowercase | `vite.config.js`, `tailwind.config.js` |
| **CSS classes** | kebab-case | `.screener-container`, `.filter-panel` |

---

## 9. Best Practices

✅ **DO:**
- Keep component folders small and focused
- Co-locate tests with components
- Use index.js for re-exports
- Organize by feature, not by type
- Use consistent naming across languages
- Create README files for complex folders
- Keep migrations chronological

❌ **DON'T:**
- Create deeply nested folder structures (max 4 levels)
- Mix different organizational patterns
- Store test files separately from components
- Use inconsistent naming conventions
- Create "utils" with 50+ files
- Keep legacy code in same structure as new code
- Mix languages in same folder

---

## Next Steps

- **See Coding Standards?** → [CODING-STANDARDS](./CODING-STANDARDS.md)
- **Check Data Flow Rules?** → [DATA-FLOW-RULES](./DATA-FLOW-RULES.md)
- **View Architecture?** → [00-ARCHITECTURE-INDEX](../00-ARCHITECTURE-INDEX.md)

---

**Version:** A | **Last Updated:** 2026-06-15
