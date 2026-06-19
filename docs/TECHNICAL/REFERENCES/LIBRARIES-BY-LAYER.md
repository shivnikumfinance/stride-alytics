# StrideAlytics — Libraries & Tools by Layer

**Complete technology stack breakdown across all architecture layers**

---

## 1. Frontend (React + Vite + Tremor)

### Core Framework & Build
```
React                          18.2.0       - UI library & hooks
Vite                           4.4.0        - Fast build tool & dev server
TypeScript                     5.1.0        - Type safety
```

### UI & Styling
```
TailwindCSS                    3.3.0        - Utility-first CSS framework
shadcn/ui                      Latest       - Accessible component library
Tremor                         Latest       - Advanced charting & dashboards
Lucide Icons                   Latest       - Icon set
```

### State Management & Data
```
Zustand                        4.4.0        - Lightweight state management
@tanstack/react-query          4.32.0       - Data fetching & caching
Axios                          1.4.0        - HTTP client
```

### Forms & Validation
```
react-hook-form               7.45.0        - Form state management
Zod                           3.22.0        - TypeScript-first validation
```

### Routing & Navigation
```
react-router-dom              6.14.0        - Client-side routing
history                       5.3.0         - Browser history management
```

### Charts & Visualization
```
Recharts                       (Tremor uses)  - Charting library
react-big-calendar            Latest         - Calendar component
```

### Testing
```
Vitest                        0.33.0         - Unit test framework
@testing-library/react        14.0.0         - React component testing
@testing-library/user-event   14.4.0         - User interaction simulation
jsdom                         22.1.0         - DOM simulation
```

### Development Tools
```
ESLint                        8.45.0         - JavaScript linting
Prettier                      3.0.0          - Code formatter
Vite Plugin React             4.1.0          - React plugin for Vite
```

### Build & Deployment
```
Vercel CLI                    Latest         - Deployment tool
```

### Complete Dependencies List

```json
{
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/user-event": "^14.4.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.1.0",
    "autoprefixer": "^10.4.0",
    "eslint": "^8.45.0",
    "eslint-config-prettier": "^8.9.0",
    "postcss": "^8.4.0",
    "prettier": "^3.0.0",
    "tailwindcss": "^3.3.0",
    "typescript": "^5.1.0",
    "vite": "^4.4.0",
    "vitest": "^0.33.0"
  },
  "dependencies": {
    "@hookform/resolvers": "^3.3.0",
    "@tanstack/react-query": "^4.32.0",
    "axios": "^1.4.0",
    "lucide-react": "^latest",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-hook-form": "^7.45.0",
    "react-router-dom": "^6.14.0",
    "recharts": "^2.8.0",
    "shadcn-ui": "^latest",
    "tailwindcss": "^3.3.0",
    "tremor": "^latest",
    "zod": "^3.22.0",
    "zustand": "^4.4.0"
  }
}
```

---

## 2. Mobile (React Native + Expo)

### Core Framework
```
React Native                   0.73.0        - Mobile framework
Expo SDK                       50.0.0        - Managed development platform
Expo Router                    Latest        - File-based routing for RN
TypeScript                     5.1.0         - Type safety
```

### UI & Styling
```
NativeWind                     Latest        - Tailwind CSS for React Native
Tamagui                        Latest        - Cross-platform component lib
React Native SVG              13.12.0        - SVG support for React Native
Lucide React Native           Latest         - Icons for React Native
```

### State Management & Data
```
Zustand                        4.4.0         - Lightweight state management
@tanstack/react-query          4.32.0        - Data fetching & caching
Axios                          1.4.0         - HTTP client
```

### Navigation
```
@react-navigation/native      Latest         - Navigation library
@react-navigation/stack       Latest         - Stack navigator
@react-navigation/bottom-tabs Latest         - Tab navigator
Expo Router                    Latest         - File-based routing
```

### Charts & Visualization
```
Victory Native                Latest         - Mobile-ready charts
React Native SVG              13.12.0        - Vector graphics
```

### Authentication & Storage
```
Supabase JS Client            Latest         - Backend client
expo-secure-store             Latest         - Secure token storage
expo-local-authentication     Latest         - Biometric auth
```

### Native Features
```
expo-notifications            Latest         - Push notifications
expo-asset                    Latest         - Asset management
expo-font                     Latest         - Font loading
expo-splash-screen            Latest         - Splash screen
expo-status-bar               Latest         - Status bar
expo-battery                  Latest         - Battery info
expo-constants                Latest         - App constants
```

### Testing
```
Jest                          29.6.0         - Test framework
@testing-library/react-native Latest         - React Native testing
detox                         Latest         - E2E testing
```

### Build & Deployment
```
Expo EAS CLI                   Latest         - Build & submit service
Expo Prebuild                  Latest         - Native project generation
```

### Complete Dependencies List

```json
{
  "devDependencies": {
    "@testing-library/react-native": "^latest",
    "@types/react": "^18.2.0",
    "@types/react-native": "^0.73.0",
    "detox": "^latest",
    "detox-cli": "^latest",
    "jest": "^29.6.0",
    "typescript": "^5.1.0"
  },
  "dependencies": {
    "@hookform/resolvers": "^3.3.0",
    "@react-navigation/bottom-tabs": "^latest",
    "@react-navigation/native": "^latest",
    "@react-navigation/stack": "^latest",
    "@supabase/supabase-js": "^latest",
    "@tanstack/react-query": "^4.32.0",
    "axios": "^1.4.0",
    "expo": "^50.0.0",
    "expo-asset": "^latest",
    "expo-battery": "^latest",
    "expo-constants": "^latest",
    "expo-font": "^latest",
    "expo-local-authentication": "^latest",
    "expo-notifications": "^latest",
    "expo-router": "^latest",
    "expo-secure-store": "^latest",
    "expo-splash-screen": "^latest",
    "expo-status-bar": "^latest",
    "nativewind": "^latest",
    "react": "^18.2.0",
    "react-hook-form": "^7.45.0",
    "react-native": "^0.73.0",
    "react-native-svg": "^13.12.0",
    "react-native-web": "^latest",
    "tamagui": "^latest",
    "victory-native": "^latest",
    "zod": "^3.22.0",
    "zustand": "^4.4.0"
  }
}
```

---

## 3. Backend (FastAPI + Python)

### Core Framework
```
FastAPI                       0.100.0       - Web framework
Uvicorn                       0.23.0        - ASGI server
Pydantic                      2.1.0         - Data validation
Pydantic Settings             2.1.0         - Configuration management
Python                        3.11          - Programming language
```

### Database & ORM
```
Supabase Python               1.0.0         - Database client
asyncpg                       0.27.0        - PostgreSQL async driver
SQLAlchemy                    2.0.0         - SQL toolkit (optional)
```

### Data Processing
```
Pandas                        2.0.0         - Data manipulation
NumPy                         1.24.0        - Numerical computing
SciPy                         1.11.0        - Scientific computing
TA-Lib                        0.4.27        - Technical analysis
```

### External Data Sources
```
yfinance                      0.2.28        - Yahoo Finance data
HTTPX                         0.24.0        - Async HTTP client
requests                      2.31.0        - HTTP client
```

### Authentication & Security
```
python-jose                   3.3.0         - JWT token handling
PyJWT                         2.8.0         - JWT encoding/decoding
passlib                       1.7.4         - Password hashing
bcrypt                        4.0.0         - Password hashing
python-multipart              0.0.6         - Form data handling
```

### Logging & Monitoring
```
structlog                     23.1.0        - Structured logging
python-logging-loki           Latest        - Loki integration
```

### Caching & Performance
```
redis                         4.5.0         - Redis client (optional)
aioredis                      2.0.0         - Async Redis (optional)
```

### Email & Notifications
```
python-email-validator       2.0.0          - Email validation
aiosmtplib                   Latest         - Async SMTP
sendgrid                     6.10.0         - SendGrid integration
```

### Testing
```
pytest                        7.4.0         - Test framework
pytest-asyncio                0.21.0        - Async test support
pytest-cov                    4.1.0         - Coverage reporting
httpx-mock                    0.1.0         - HTTP mocking
```

### Code Quality
```
pylint                        2.17.0        - Code linting
black                         23.7.0        - Code formatter
flake8                        6.0.0         - Style guide enforcement
isort                         5.12.0        - Import sorting
mypy                          1.4.0         - Type checking
```

### Development
```
python-dotenv                 1.0.0         - .env file support
```

### Complete Requirements

```txt
# Core
fastapi==0.100.0
uvicorn[standard]==0.23.0
pydantic==2.1.0
pydantic-settings==2.1.0

# Database
supabase==1.0.0
asyncpg==0.27.0
sqlalchemy==2.0.0

# Data
pandas==2.0.0
numpy==1.24.0
scipy==1.11.0
ta-lib==0.4.27

# External Data
yfinance==0.2.28
httpx==0.24.0
requests==2.31.0

# Auth & Security
python-jose==3.3.0
pyjwt==2.8.0
passlib==1.7.4
bcrypt==4.0.0
python-multipart==0.0.6

# Logging
structlog==23.1.0

# Caching (optional)
redis==4.5.0
aioredis==2.0.0

# Notifications
sendgrid==6.10.0
aiosmtplib==3.0.0

# Testing
pytest==7.4.0
pytest-asyncio==0.21.0
pytest-cov==4.1.0

# Quality
pylint==2.17.0
black==23.7.0
flake8==6.0.0
isort==5.12.0
mypy==1.4.0

# Utilities
python-dotenv==1.0.0
```

---

## 4. Database (Supabase PostgreSQL)

### Database Engine
```
PostgreSQL                    15+           - Relational database
```

### Supabase Platform
```
Supabase Auth                 Latest        - JWT authentication
Supabase Storage              Latest        - File storage (optional)
Supabase Edge Functions       Latest        - Serverless functions (optional)
Supabase Realtime             Latest        - Real-time subscriptions (optional)
```

### Extensions
```
pg_cron                       Latest        - Scheduled jobs
pgvector                      Latest        - Vector similarity search
uuid-ossp                     Latest        - UUID generation
```

### Migrations & CLI
```
Supabase CLI                  1.92+         - CLI tool for migrations
```

---

## 5. Deployment & Infrastructure

### Web Hosting
```
Vercel                        Latest        - Frontend hosting & CDN
```

### Backend Hosting
```
Render                        Latest        - Backend server hosting
```

### Database Hosting
```
Supabase                      Latest        - Managed PostgreSQL
```

### Mobile
```
Expo EAS                      Latest        - Mobile build & CI/CD
```

### Containerization
```
Docker                        Latest        - Container runtime
Docker Compose                Latest        - Multi-container orchestration
```

### CI/CD
```
GitHub Actions                Latest        - Workflow automation
```

### Monitoring (Optional)
```
Datadog                       Latest        - APM & monitoring
Sentry                        Latest        - Error tracking
LogRocket                     Latest        - Session replay
UptimeRobot                   Latest        - Uptime monitoring
Cloudflare                    Latest        - DDoS protection
```

---

## 6. Shared Libraries

### TypeScript Types & Utilities
```
TypeScript                    5.1.0         - Type definitions
```

### API Client
```
Axios                         1.4.0         - HTTP client (shared)
```

---

## Quick Reference Table

| Category | Tool | Version | Purpose |
|----------|------|---------|---------|
| **Web Frontend** | React | 18.2 | UI Framework |
| | Vite | 4.4 | Build Tool |
| | Tremor | Latest | Charting |
| | TailwindCSS | 3.3 | Styling |
| **Mobile** | React Native | 0.73 | Mobile Framework |
| | Expo | 50.0 | Development Platform |
| | NativeWind | Latest | Mobile Styling |
| **Backend** | FastAPI | 0.100 | API Framework |
| | Uvicorn | 0.23 | ASGI Server |
| | Pydantic | 2.1 | Validation |
| **Database** | PostgreSQL | 15+ | Database |
| | Supabase | Latest | Platform |
| **Deployment** | Vercel | Latest | Web Hosting |
| | Render | Latest | API Hosting |
| | Expo EAS | Latest | Mobile Build |
| **CI/CD** | GitHub Actions | Latest | Automation |

---

## Version Update Schedule

- **Frontend:** Quarterly (React, Vite patches monthly)
- **Mobile:** Quarterly (Expo SDK yearly)
- **Backend:** Quarterly (FastAPI patches monthly)
- **Database:** Managed by Supabase (automatic)
- **Deployment:** Continuous (managed platforms)

---

## Security & Compliance

All major libraries are:
- ✅ Actively maintained
- ✅ Community verified
- ✅ Regularly updated
- ✅ Industry standard
- ✅ Open source (where applicable)

---

## Next Steps

- **View Infrastructure?** → [06-DEPLOYMENT-LAYER](../LAYERS/06-DEPLOYMENT-LAYER.md)
- **Check Diagrams?** → [02-SYSTEM-DIAGRAMS](../02-SYSTEM-DIAGRAMS.md)

---

**Version:** A | **Last Updated:** 2026-06-15
