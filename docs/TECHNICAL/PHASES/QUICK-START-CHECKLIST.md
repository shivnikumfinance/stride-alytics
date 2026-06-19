# StrideAlytics — Quick-Start Checklist

**Step-by-step launch checklist organized by layer**

---

## Pre-Launch Checklist

### Project Setup

```
☐ Create GitHub organization/repo
☐ Set up monorepo structure
  ☐ frontend/ folder created
  ☐ mobile/ folder created
  ☐ backend/ folder created
  ☐ database/ folder created
  ☐ scheduler/ folder created
  ☐ shared/ folder created
  ☐ infra/ folder created
  ☐ docs/ folder created
☐ Initialize git with .gitignore
☐ Set up branch protection rules
☐ Create GitHub Issues for Phase 1 tasks
☐ Set up GitHub Projects kanban board
```

### Accounts & Services

```
☐ Supabase account (Pro plan trial)
☐ Vercel account
☐ Render account
☐ GitHub account (if not already)
☐ Expo account (for mobile)
☐ SendGrid account (for emails)
☐ Slack workspace (for notifications)
☐ Custom domain (optional)
☐ SSL certificate (auto from Vercel/Render)
```

---

## Week 1: Foundation

### Database Setup

```
☐ Create Supabase project
  ☐ Choose region: us-east-1 (AWS)
  ☐ Choose plan: Pro (trial)
  ☐ Confirm database URL
☐ Create .env file with Supabase credentials
  ☐ SUPABASE_URL
  ☐ SUPABASE_KEY
  ☐ SUPABASE_JWT_SECRET
☐ Create database schema (SQL migrations)
  ☐ users table with fields
  ☐ portfolios table
  ☐ trades table
  ☐ options table
  ☐ Create indexes
  ☐ Run migration successfully
☐ Configure RLS (Row-Level Security)
  ☐ Enable RLS on portfolios table
  ☐ Enable RLS on trades table
  ☐ Create policy: users see own data
  ☐ Test RLS with SQL queries
☐ Create portfolio_summary view
☐ Seed test data
  ☐ Create 3 test users
  ☐ Create sample portfolios
  ☐ Create sample trades
☐ Verify data with queries
  ☐ SELECT * FROM portfolios returns data
  ☐ RLS policy blocks cross-user access
  ☐ View works and returns correct stats
```

### Authentication Setup

```
☐ Configure Supabase Auth
  ☐ Enable email/password auth
  ☐ Confirm email settings
  ☐ Set JWT expiration to 3600s (1 hour)
☐ Create auth service (Python)
  ☐ Login function
  ☐ Signup function
  ☐ JWT verification
  ☐ Token refresh logic
☐ Create auth endpoints (FastAPI)
  ☐ POST /api/v1/auth/login
  ☐ POST /api/v1/auth/signup
  ☐ POST /api/v1/auth/refresh
  ☐ POST /api/v1/auth/logout (optional)
☐ Test auth endpoints
  ☐ Login with test user → returns JWT
  ☐ Refresh token works
  ☐ Expired token rejected
  ☐ Invalid token rejected
☐ Create .env file with auth credentials
  ☐ SUPABASE_JWT_SECRET
  ☐ SUPABASE_URL
  ☐ SUPABASE_KEY (service role)
```

### Backend API Foundation

```
☐ Create FastAPI project
  ☐ poetry init or requirements.txt
  ☐ Install dependencies
  ☐ Create app/main.py
☐ Set up FastAPI application
  ☐ Configure CORS for localhost
  ☐ Add middleware (logging, error handling)
  ☐ Create health check endpoint
  ☐ Test locally: http://localhost:8000
☐ Create API router structure
  ☐ v1 router created
  ☐ Endpoint routers created (auth, screener, etc.)
  ☐ All routers imported and registered
☐ Deploy to Render
  ☐ Create Render account
  ☐ Create service from GitHub repo
  ☐ Configure environment variables
  ☐ Deploy backend
  ☐ Test: curl https://api-xxx.onrender.com/health
☐ Verify CORS works from frontend URL
```

### Frontend & Mobile Init

```
☐ Initialize React + Vite project
  ☐ npm create vite@latest frontend -- --template react
  ☐ npm install
  ☐ npm run dev → works at localhost:5173
  ☐ Install dependencies (axios, zustand, react-query)
☐ Initialize Expo project
  ☐ npx create-expo-app mobile
  ☐ cd mobile && npm install
  ☐ npx expo start
  ☐ App opens in Expo Go on phone
☐ Create shared types
  ☐ shared/types/index.ts
  ☐ Define core types (User, Portfolio, Trade, Option)
  ☐ Export from index
☐ Create .env.example files
  ☐ frontend/.env.example
  ☐ mobile/.env.example
  ☐ backend/.env.example
  ☐ All contain masked secrets
☐ Both apps can call health endpoint
  ☐ Frontend: GET /api/v1/health → 200 OK
  ☐ Mobile: GET /api/v1/health → 200 OK
```

### Week 1 Verification

```
✓ All environments connected:
  ☐ Supabase dashboard loads and shows tables
  ☐ Render dashboard shows deployed service
  ☐ Vercel connected (not deployed yet)
  ☐ GitHub Actions triggered on push
  
✓ Auth flow works:
  ☐ Can signup via API
  ☐ Can login and receive JWT
  ☐ JWT can be verified

✓ Repos ready:
  ☐ All code pushed to GitHub
  ☐ CI/CD workflow runs (even if tests fail)
  ☐ Team can clone and run locally
```

---

## Week 2: Core Features

### Screener Service

```
☐ Create screener service (Python)
  ☐ ScreenerService class
  ☐ filter_options method
  ☐ Support filters: symbol, strike range, expiry, Greeks
  ☐ Pagination support (limit, offset)
  ☐ Caching for free tier
☐ Create screener schemas (Pydantic)
  ☐ ScreenerFilterRequest
  ☐ ScreenerResponse
  ☐ OptionData model
☐ Create screener endpoint
  ☐ GET /api/v1/screener
  ☐ Accept query params (symbol, min_price, etc.)
  ☐ Return paginated results
  ☐ Require JWT for free tier limits
☐ Test screener
  ☐ Curl test: GET /api/v1/screener?symbol=AAPL
  ☐ Pagination: limit=50&offset=0 works
  ☐ Empty results handled gracefully
  ☐ Performance: <500ms response time
☐ Add to free tier limits
  ☐ Free users: 50 results/page max
  ☐ PRO users: unlimited
```

### Greeks Calculator

```
☐ Create greeks service (Python)
  ☐ Black-Scholes formulas
  ☐ calculate_greeks() function
  ☐ All Greeks: delta, gamma, theta, vega, rho
  ☐ Both call and put options
☐ Create unit tests for Greeks
  ☐ Test against known values
  ☐ Test edge cases (at expiry, deep ITM/OTM)
  ☐ Test all Greek components
  ☐ Target: 100% test coverage
☐ Create greeks schemas (Pydantic)
  ☐ GreeksRequest (spot, strike, time, IV)
  ☐ GreeksResponse (all Greeks + prices)
☐ Create greeks endpoint
  ☐ POST /api/v1/greeks/calculate
  ☐ Accept JSON body with Greeks params
  ☐ Return calculated Greeks
☐ Test greeks endpoint
  ☐ Curl test: POST with params
  ☐ Validate against external calculator
  ☐ Performance: <100ms
☐ Greeks unlimited for all users
```

### Portfolio & Trades

```
☐ Create portfolio service
  ☐ create_portfolio()
  ☐ get_user_portfolios()
  ☐ delete_portfolio()
  ☐ get_portfolio_stats()
☐ Create trade service
  ☐ add_trade()
  ☐ get_trades()
  ☐ close_trade()
  ☐ calculate_pnl()
☐ Create portfolio/trade schemas
  ☐ PortfolioCreate
  ☐ TradeCreate
  ☐ TradeUpdate
☐ Create endpoints
  ☐ POST /api/v1/portfolio (create)
  ☐ GET /api/v1/portfolio (list)
  ☐ DELETE /api/v1/portfolio/{id}
  ☐ POST /api/v1/trades (add)
  ☐ GET /api/v1/trades (list)
  ☐ PUT /api/v1/trades/{id} (update)
☐ Test portfolio endpoints
  ☐ Create portfolio → portfolio created with ID
  ☐ Add trade → trade assigned to portfolio
  ☐ RLS works → user only sees own data
  ☐ PnL calculated → numbers make sense
```

### Market Data

```
☐ Create market data service
  ☐ Fetch from yfinance
  ☐ Get options chain for symbol
  ☐ Parse options data
  ☐ Error handling for network issues
☐ Create database queries for options
  ☐ Save options to options table
  ☐ Update existing options (don't duplicate)
  ☐ Delete old options (older than 3 months)
☐ Create manual test script
  ☐ python scripts/fetch_market_data.py
  ☐ Manually run for AAPL, SPY, QQQ
  ☐ Verify data in database
  ☐ Check data quality (no NaN, prices reasonable)
☐ Document data source (yfinance)
  ☐ Explain rate limits
  ☐ Explain data latency (15+ min delayed)
☐ Plan for Week 3 automation
```

### Week 2 Verification

```
✓ Screener working:
  ☐ API returns options data
  ☐ Filters work correctly
  ☐ Pagination works
  ☐ Performance acceptable

✓ Greeks working:
  ☐ Calculates correctly
  ☐ Matches known calculators
  ☐ Handles edge cases

✓ Portfolio working:
  ☐ Users can create portfolios
  ☐ Users can add trades
  ☐ Users only see own data
  ☐ PnL calculations correct

✓ All tested:
  ☐ Unit tests passing (80%+ coverage)
  ☐ Integration tests passing
  ☐ Manual testing complete
```

---

## Week 3: Frontend & Mobile

### Frontend (React)

```
☐ Create page components
  ☐ DashboardPage (home)
  ☐ ScreenerPage (main feature)
  ☐ GreeksPage (calculator)
  ☐ PortfolioPage (protected)
  ☐ LoginPage (auth)
  ☐ SignupPage (auth)
☐ Create UI components
  ☐ FilterPanel (inputs for screener)
  ☐ ResultsTable (display options)
  ☐ TradeForm (add/edit trade)
  ☐ Button, Card, Modal (reusables)
☐ Set up state management
  ☐ auth.store (user, token)
  ☐ screener.store (filters, results)
  ☐ portfolio.store (portfolios, trades)
  ☐ ui.store (modal states)
☐ Set up API integration
  ☐ axios client with JWT interceptor
  ☐ React Query hooks for data fetching
  ☐ useScreener hook
  ☐ usePortfolios hook
  ☐ useGreeks hook
☐ Set up routing
  ☐ React Router configured
  ☐ Protected routes (require login)
  ☐ Public routes (no login needed)
☐ Styling
  ☐ TailwindCSS configured
  ☐ Global styles
  ☐ Responsive design (mobile + desktop)
☐ Deploy to Vercel
  ☐ Connect GitHub repo
  ☐ Deploy staging: vercel-staging.stridealytics.com
  ☐ Test staging deployment
  ☐ Fix any issues
☐ Test all features
  ☐ Can login
  ☐ Can use screener
  ☐ Can calculate Greeks
  ☐ Can view portfolio
```

### Mobile (React Native + Expo)

```
☐ Set up Expo Router
  ☐ File-based routing structure
  ☐ (tabs) grouped route for bottom tabs
  ☐ Auth routes (login, signup)
☐ Create screens
  ☐ DashboardScreen
  ☐ ScreenerScreen
  ☐ GreeksScreen
  ☐ PortfolioScreen
  ☐ ProfileScreen
☐ Set up navigation
  ☐ Tab navigator (bottom tabs)
  ☐ Stack navigator (stack screens)
  ☐ Auth flow (show login when not auth)
☐ Implement secure token storage
  ☐ expo-secure-store integration
  ☐ Save JWT on login
  ☐ Retrieve JWT on app start
  ☐ Clear JWT on logout
☐ Set up API client
  ☐ axios or fetch
  ☐ JWT interceptor
  ☐ Error handling
☐ Styling
  ☐ NativeWind + Tailwind configured
  ☐ Responsive to different screen sizes
  ☐ Dark mode support
☐ Test on simulators
  ☐ iOS simulator: app launches
  ☐ Android emulator: app launches
  ☐ Login works
  ☐ Can navigate between screens
☐ Build with EAS
  ☐ Create Expo.dev account
  ☐ eas build --platform ios (creates TestFlight build)
  ☐ eas build --platform android (creates internal testing)
  ☐ Download and install on physical devices
  ☐ Test end-to-end
```

### Week 3 Verification

```
✓ Web app working:
  ☐ Deployed to Vercel
  ☐ All pages load
  ☐ Authentication works
  ☐ API calls work
  ☐ Responsive on mobile

✓ Mobile app working:
  ☐ Launches on iOS simulator
  ☐ Launches on Android emulator
  ☐ Authentication works
  ☐ Can use all features
  ☐ Token storage works

✓ User flows tested:
  ☐ Web: Signup → Login → Use screener → Portfolio
  ☐ Mobile: Signup → Login → Use screener → Portfolio
```

---

## Week 4: Polish & Launch

### Testing

```
☐ Frontend tests
  ☐ Unit tests: 80%+ coverage
  ☐ Component tests
  ☐ Integration tests
  ☐ Run: npm test
☐ Backend tests
  ☐ Unit tests: 80%+ coverage
  ☐ Endpoint tests
  ☐ Integration tests
  ☐ Run: pytest
☐ Manual testing
  ☐ Test signup flow
  ☐ Test login flow
  ☐ Test screener with different filters
  ☐ Test Greeks calculator
  ☐ Test portfolio CRUD
  ☐ Test on mobile (iOS + Android)
  ☐ Test on different browsers (Chrome, Safari, Firefox)
  ☐ Test error handling (offline, 401, etc.)
```

### Schedulers & Automation

```
☐ Create GitHub Actions workflows
  ☐ .github/workflows/fetch-market-data.yml
  ☐ .github/workflows/calculate-greeks.yml
  ☐ .github/workflows/health-check.yml
  ☐ .github/workflows/ci-cd.yml (on push)
☐ Create scheduler scripts
  ☐ scheduler/scripts/fetch_market_data.py
  ☐ scheduler/scripts/calculate_greeks.py
  ☐ scheduler/scripts/health_check.py
☐ Configure schedules
  ☐ Fetch market data: Daily 3 PM EST
  ☐ Calculate Greeks: Daily 4 PM EST
  ☐ Health check: Every 5 minutes
☐ Test workflows
  ☐ Manually trigger fetch workflow
  ☐ Verify data updated in database
  ☐ Check logs for errors
  ☐ Set up Slack notifications for failures
☐ Document workflows
  ☐ Document schedule times (EST)
  ☐ Document what each does
  ☐ Document troubleshooting
```

### Production Deployment

```
☐ Pre-production checklist
  ☐ Security audit (no hardcoded secrets)
  ☐ Performance review (Lighthouse 90+)
  ☐ Test all endpoints (Postman collection)
  ☐ Check error handling
  ☐ Verify database backups
☐ Production environment
  ☐ Set production .env variables
  ☐ Enable HTTPS/SSL
  ☐ Configure CORS for production domain
  ☐ Set up monitoring/alerts
☐ Deploy frontend to Vercel
  ☐ Vercel settings → Production domain
  ☐ Deploy: vercel --prod
  ☐ Test: https://stridealytics.com works
  ☐ Test API calls work
☐ Deploy backend to Render
  ☐ Render settings → Production
  ☐ Set environment variables
  ☐ Deploy: Git push triggers deploy
  ☐ Test: https://api.stridealytics.com/health → 200
☐ Verify database
  ☐ Production data ready
  ☐ Backups configured
  ☐ RLS policies enabled
  ☐ Monitoring set up
☐ Post-deployment
  ☐ Monitor error logs
  ☐ Monitor API response times
  ☐ Monitor database query times
  ☐ Be on-call for first 48 hours
```

### Documentation & Runbooks

```
☐ Create documentation
  ☐ README.md (top-level project overview)
  ☐ SETUP.md (how to set up locally)
  ☐ DEPLOYMENT.md (deployment guide)
  ☐ API.md (API endpoints reference)
  ☐ TROUBLESHOOTING.md (common issues)
☐ Create runbooks
  ☐ Incident response playbook
  ☐ Deployment rollback procedure
  ☐ Database recovery procedure
  ☐ How to add new feature (process)
☐ Document infrastructure
  ☐ Architecture diagrams
  ☐ Data flow diagrams
  ☐ Database schema documentation
☐ Team documentation
  ☐ Add team members to GitHub
  ☐ Grant access to services (Vercel, Render, Supabase)
  ☐ Share Slack channel
  ☐ Onboarding doc for new developers
```

### Launch

```
☐ Final checks
  ☐ All tests passing
  ☐ No console errors
  ☐ All features working
  ☐ Mobile apps submitted to stores (or in internal testing)
  ☐ Monitoring set up
☐ Announce launch
  ☐ Email to interested users
  ☐ Social media post
  ☐ Product Hunt post (optional)
☐ Monitor first week
  ☐ Watch error logs
  ☐ Track user signups
  ☐ Gather feedback
  ☐ Fix critical bugs immediately
  ☐ Be available for support
☐ Celebrate! 🎉
```

---

## Post-Launch (Week 5+)

### Monitor & Iterate

```
☐ Daily
  ☐ Check error logs
  ☐ Monitor API response times
  ☐ Monitor database size
  ☐ Check uptime

☐ Weekly
  ☐ Review user feedback
  ☐ Review analytics
  ☐ Plan improvements
  ☐ Update roadmap

☐ Monthly
  ☐ Full system audit
  ☐ Performance review
  ☐ Cost review
  ☐ Team sync
```

### Start Phase 2 (Month 2+)

```
☐ After stabilization (1-2 weeks):
  ☐ Implement advanced screener filters
  ☐ Add real-time alerts
  ☐ Build API for power users
  ☐ Start community features
```

---

## Quick Reference

### Commands

```bash
# Frontend
npm run dev              # Dev server
npm run build            # Production build
npm run lint             # Lint code
npm test                 # Run tests

# Mobile
npm start                # Expo dev server
npx expo build:preview   # Build for Expo Go
eas build --platform ios # Build for TestFlight

# Backend
python -m uvicorn app.main:app --reload  # Dev server
pytest                                    # Run tests
black app/                               # Format code
pylint app/                              # Lint code

# Database
supabase db push         # Run migrations
supabase db pull         # Pull remote schema
```

### Useful Links

```
Vercel Dashboard:       vercel.com/dashboard
Render Dashboard:       dashboard.render.com
Supabase Dashboard:     app.supabase.com
GitHub Actions:         github.com/USERNAME/stridealytics/actions
Expo Dashboard:         expo.dev
```

### Emergency Contacts

```
Vercel Support:         support@vercel.com
Render Support:         support@render.com
Supabase Support:       support@supabase.com
GitHub Support:         github.com/support
```

---

## Success Checklist

By launch day, you should have:

```
✅ 100+ GitHub stars
✅ Live product at stridealytics.com
✅ Backend API running at api.stridealytics.com
✅ Mobile apps in TestFlight/internal testing
✅ Database with test data
✅ Monitoring & alerts set up
✅ Documentation complete
✅ Team trained and ready
✅ First users signing up
✅ Positive feedback from early users
✅ 0 critical bugs in production
```

---

**Version:** Checklist-A | **Last Updated:** 2026-06-15

---

## Print-Friendly Version

Save this page as PDF or print for physical checklist:

```
Week 1:   ☐ ☐ ☐ ☐ ☐
Week 2:   ☐ ☐ ☐ ☐ ☐
Week 3:   ☐ ☐ ☐ ☐ ☐
Week 4:   ☐ ☐ ☐ ☐ ☐
Launch:   ☐ READY
```

Celebrate when all boxes checked! 🚀
