# StrideAlytics — Platform Mock

A comprehensive mock implementation of the StrideAlytics Options Selling Platform for frontend development, testing, and demonstration purposes.

## Directory Structure

```
mock/
├── README.md                    # This file
├── data/
│   └── mock_data.json           # Complete mock data (regime, portfolio, trades, watchlist, etc.)
├── backend/
│   └── main.py                  # FastAPI mock backend with 30+ API endpoints
├── frontend/
│   └── index.html               # Interactive dark-mode UI with 10 screens
```

## Quick Start

### Option 1: Standalone Frontend (No Backend)

Simply open `mock/frontend/index.html` in a browser. The frontend automatically loads data from `mock/data/mock_data.json`. All data is embedded and fully interactive.

### Option 2: Frontend + Backend API

1. **Install Python dependencies:**

```bash
cd mock/backend
pip install fastapi uvicorn
```

2. **Start the mock API server:**

```bash
uvicorn main:app --reload --port 8000
```

3. **Open the frontend** at `mock/frontend/index.html` — it will automatically detect and use the running API.

### Option 3: Docker (if available)

```bash
cd mock
docker build -f Dockerfile -t stridealytics-mock .
docker run -p 8000:8000 -p 8080:8080 stridealytics-mock
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/dashboard` | Aggregate dashboard data |
| GET | `/api/v1/regime` | Current regime score & mood |
| GET | `/api/v1/regime/history` | Regime score history |
| GET | `/api/v1/heat-dashboard` | Risk gauges, volatility, trend, breadth |
| GET | `/api/v1/master-gate` | CLEAR TO TRADE / BLOCKED status |
| GET | `/api/v1/portfolio` | Portfolio summary |
| GET | `/api/v1/portfolio/capital-bands` | Capital band allocation |
| GET | `/api/v1/portfolio/sector-exposure` | Sector exposure breakdown |
| GET | `/api/v1/trades/active` | Active trades list |
| GET | `/api/v1/trades/active/{id}` | Single active trade |
| GET | `/api/v1/trades/closed` | Closed trades history |
| GET | `/api/v1/trades/exit-alerts` | Exit alerts |
| GET | `/api/v1/watchlist` | Watchlist with metrics |
| GET | `/api/v1/watchlist/{symbol}` | Single symbol detail |
| GET | `/api/v1/option-chain/{symbol}` | Option chain with Greeks |
| GET | `/api/v1/weekly-picks` | Ranked weekly trade picks |
| GET | `/api/v1/sizing-calculator` | Sizing defaults |
| POST | `/api/v1/sizing-calculator/calculate` | Calculate position size |
| GET | `/api/v1/scenarios` | Scenario stress tests |
| GET | `/api/v1/signal-log` | Immutable rule-based signal log |
| GET | `/api/v1/settings` | All settings |
| GET | `/api/v1/settings/account` | Account settings |
| GET | `/api/v1/settings/risk` | Risk defaults |
| GET | `/api/v1/settings/dnt` | DNT settings |
| GET | `/api/v1/settings/preferences` | User preferences |
| GET | `/api/v1/auth/me` | Current user |
| POST | `/api/v1/auth/login` | Mock login |
| GET | `/api/v1/admin/users` | User management |
| GET | `/api/v1/admin/health` | System health |
| GET | `/api/v1/admin/audit-log` | Audit log |

## Frontend Screens

1. **Dashboard** — Market regime, master gate, portfolio summary, exit alerts, top picks
2. **Watchlist** — 10 symbols with price, IV, trend, DNT status, band allocation
3. **Option Chain** — SPY strike ladder with Calls/Puts, Greeks, IV
4. **Weekly Picks** — Ranked recommendations by EV score
5. **Active Trades** — 6 open positions with P&L, Greeks, exit signals
6. **Position Sizing** — Interactive calculator with regime multipliers
7. **Scenarios** — 4 stress test simulations with P&L impact
8. **Heat Dashboard** — Risk gauges, market breadth, volatility, trend, macro
9. **Signal Log** — Immutable rule-based decisions and regime shifts
10. **Admin Panel** — User management, system health, audit log

## Data Coverage

The mock data comprehensively covers all platform domains:
- **Regime Engine**: Score, state, history, components (VIX, IV Rank, SPY trend)
- **Master Gate**: CLEAR TO TRADE with 4 gate checks
- **Portfolio**: $87.5K value, sector exposure (8 sectors), capital bands (A-E)
- **Active Trades**: 6 positions (SPY, AAPL, MSFT, NVDA, AMZN, TSLA) with full Greeks
- **Closed Trades**: 3 historical trades with P&L
- **Watchlist**: 10 symbols with live-like metrics
- **Option Chain**: SPY 30 DTE with 11 strikes, calls & puts
- **Weekly Picks**: 6 ranked trades with EV scoring
- **Heat Dashboard**: VIX, breadth, trend, macro indicators
- **Scenario Simulations**: 4 scenarios from -5% decline to -15% crash
- **Signal Log**: 5 immutable events (regime shift, DNT, allocation, exit, band)
- **Settings**: Account, risk defaults, DNT, preferences
- **Admin**: 4 users, system health, 3 audit log entries
- **Exit Alerts**: 2 active recommendations

## Tech Stack

- **Frontend**: Vanilla HTML/CSS/JS — dark theme, responsive, zero dependencies
- **Backend**: FastAPI (Python) — 30+ REST endpoints with CORS
- **Data**: JSON — easily modifiable for different scenarios