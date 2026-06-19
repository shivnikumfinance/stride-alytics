# StrideAlytics — Free-Tier Upgrade Triggers

**When and why to upgrade each service as you scale**

---

## Overview

This guide helps you understand at what point each service hits free-tier limits and when you should upgrade.

```
Free Tier Monitoring
    ↓
Track Usage
    ↓
Hit Threshold? (80%)
    ↓
Evaluate Cost vs. Benefit
    ↓
Upgrade or Optimize
    ↓
Track New Limits
```

---

## 1. Vercel (Frontend Hosting)

### Free Tier Limits

```
Bandwidth:          100 GB/month
Build time:         15 minutes per deploy
Functions:          100 invocations/day
Concurrent builds:  1
Performance budget: Standard
```

### When to Upgrade

**Trigger 1: Bandwidth > 80 GB/month**

```
Calculation:
- 100 GB free tier
- ~50 concurrent users
- ~20 KB average page size
- 100 requests/user/month
- = 100 GB used

Decision Tree:
├─ Traffic growing? → UPGRADE
├─ Most users on old devices? → OPTIMIZE (images)
├─ Large library bundles? → OPTIMIZE (tree-shake)
└─ Expected to continue? → UPGRADE to Pro ($20/month)
```

**Trigger 2: Deploy frequency > 5x/day**

```
At 6+ deploys/day with long builds:
├─ Upgrade to Pro ($20/month) for unlimited concurrent builds
└─ Or: Batch deployments (deploy 1x/day at night)
```

### What to Do When Triggered

```
UPGRADE PLAN:
├─ Vercel Pro: $20/month
├─ Includes:
│  ├─ Unlimited bandwidth
│  ├─ Unlimited concurrent builds
│  ├─ Advanced analytics
│  └─ Team features (if needed)
└─ Cost increase: $20/month

OPTIMIZE FIRST (before upgrading):
├─ Code splitting by route (automatic in Vite)
├─ Image optimization (use next-image or similar)
├─ Lazy load components
├─ Tree-shake unused dependencies
├─ Monitor bundle size
└─ Result: Usually stays under 80 GB
```

---

## 2. Render (Backend Hosting)

### Free Tier Limits

```
Compute Hours:      750/month (≈ 1 instance full-time)
Concurrent requests: ~200 req/min with connection pool
Auto-scaling:       Limited (1 instance only)
Memory:             512 MB per instance
Sleep:              No auto-sleep (good!)
```

### When to Upgrade

**Trigger 1: API > 400 requests/minute**

```
Calculation:
├─ Free tier: ~200 req/min stable
├─ 400 req/min = 2x free tier limit
└─ At this point: Errors, slowdowns, timeouts

Decision Tree:
├─ Traffic spike (temporary)? → OPTIMIZE (caching)
├─ Steady traffic growth? → UPGRADE
├─ Users signing up for PRO? → Revenue supports upgrade
└─ Expected continuous growth? → UPGRADE to Standard
```

**Trigger 2: Response time > 500ms (p95)**

```
Indicates:
├─ Database connection pool saturated
├─ CPU at 80%+
└─ Need more instances

Action:
├─ Check slow queries (enable query logging)
├─ Optimize hot paths
├─ If optimization doesn't help → UPGRADE
```

### What to Do When Triggered

```
OPTIMIZE FIRST:
├─ Enable Redis caching (AWS ElastiCache free tier)
├─ Cache screener results (5 min TTL)
├─ Cache Greeks calculations (1 hour TTL)
├─ Batch API requests where possible
├─ Enable connection pooling (PgBouncer via Supabase)
└─ Expected improvement: 40-60% request reduction

IF OPTIMIZATION INSUFFICIENT:
├─ Render Standard: $7/instance/month
├─ Run 2-3 instances with auto-scaling
├─ Monthly cost: $14-21/month
├─ Includes:
│  ├─ Continuous availability
│  ├─ Auto-scaling (up to 10 instances)
│  └─ Better monitoring
```

---

## 3. Supabase (Database)

### Free Tier Limits

```
Storage:            1 GB
Rows:               500K
Real-time queries:  100 concurrent
Database size:      8GB (with usage limit)
Backup retention:   7 days
CPU/RAM:            Shared
```

### When to Upgrade

**Trigger 1: Database size > 800 MB**

```
Calculation:
├─ 1 GB = 1,000 MB free tier
├─ At 800 MB: Getting close to limit
├─ Need: Backup space + growth buffer

Decision:
├─ What's using space?
│  ├─ historical options data? → Archive old data
│  ├─ user trades? → Keep (small)
│  └─ market snapshots? → Archive monthly
```

**Trigger 2: Row count approaching 500K**

```
Track by entity:
├─ users: Should stay < 10K (in free tier)
├─ portfolios: < 1K per user (depends on users)
├─ trades: Few hundred per portfolio (varies)
├─ options table: This grows to 500K+ fast
│  └─ Solution: Archive old options monthly

At 400K rows:
├─ Performance degrades
├─ Backup times increase
└─ Upgrade to Pro
```

**Trigger 3: Users > 100 and growing**

```
Calculation:
├─ Free tier: ~100 concurrent users
├─ 150 concurrent users: ~30% over limit
└─ At this point: Connection limits hit

Action:
├─ Supabase Pro: $25/month
├─ Includes:
│  ├─ 8 GB storage (8x)
│  ├─ 50K real-time connections
│  ├─ Daily backups + PITR
│  └─ Higher resource limits
```

### What to Do When Triggered

```
OPTIMIZE FIRST:
├─ Archive old options (older than 3 months)
├─ Delete test data
├─ Remove unused indexes (they take space)
├─ Analyze and optimize slow queries
├─ Enable query result caching (in backend)
└─ Expected space freed: 20-30%

IF STILL NEEDED:
├─ Supabase Pro: $25/month
├─ 8x storage, 8x performance
├─ Can run 1000+ users
├─ Upgrade now if:
│  ├─ Growing to 200+ users
│  ├─ Revenue from PRO tier supports it
│  └─ Historical data needed long-term
```

---

## 4. GitHub Actions (CI/CD)

### Free Tier Limits

```
Minutes:            2,000/month
Storage:            500 MB artifacts
Concurrent jobs:    20
```

### When to Upgrade

**Trigger 1: Workflows > 1,500 minutes/month**

```
Calculation:
├─ Frontend build: 5 min
├─ Backend build: 5 min
├─ Mobile build: 10 min (EAS)
├─ Tests: 5 min
├─ Per push: 25 minutes
├─ 10 pushes/day: 250 min/day = 7,500 min/month
└─ OOPS! Already over limit

Solution:
├─ Don't buy more minutes (GitHub Actions Pro is not available)
├─ Instead: Optimize workflows
│  ├─ Skip full build if only docs changed
│  ├─ Cache dependencies (saves 50% build time)
│  ├─ Run tests in parallel
│  ├─ Deploy only when tests pass
│  └─ Result: Usually stays under 2,000 min
```

### What to Do When Triggered

```
OPTIMIZE (required, not optional):
├─ Cache npm/pip dependencies
├─ Parallelize jobs (run tests while building)
├─ Skip unnecessary steps
│  ├─ Skip deploy on PR
│  ├─ Skip full test on doc changes
│  └─ Skip build if no changes in code
├─ Use native GitHub Actions for setup
├─ Result: Usually 30-50% time saved

EXAMPLE OPTIMIZED WORKFLOW:

name: CI/CD
on: [push]

jobs:
  lint-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          cache: 'npm'  # ← Cache node_modules
      - run: npm ci  # ← Faster than npm install
      - run: npm run lint
      - run: npm run test

  build-deploy:
    needs: lint-test
    if: github.ref == 'refs/heads/main'  # ← Deploy only on main
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      - run: npm run deploy
```

---

## 5. SendGrid (Email)

### Free Tier Limits

```
Emails/day:         100
Reputation:         Basic
Support:            Community
```

### When to Upgrade

**Trigger 1: Marketing emails > 80/day**

```
Examples:
├─ Weekly picks: 1 email/user/week (scale with users)
├─ At 100 users: ~15 emails/week = ~2/day (fine)
├─ At 500 users: ~70/week = ~10/day (still fine)
├─ At 1000 users: ~140/week = ~20/day (still fine)
└─ At 5000 users: ~700/week = ~100/day (AT LIMIT)

At 5000 users with PRO:
├─ Revenue: 5000 × 0.2 conversion × $19 = $19,000/month
├─ SendGrid Pro: $100-200/month (still tiny % of revenue)
└─ Upgrade yes
```

### What to Do When Triggered

```
IF UNDER LIMIT:
├─ Use free tier as long as possible
├─ Track email engagement
└─ No action needed

WHEN APPROACHING LIMIT:
├─ SendGrid Pro: $100+/month (based on volume)
├─ At 1,000 emails/day: Usually included in higher plans
└─ Upgrade when:
   ├─ Need > 100 emails/day
   ├─ Want dedicated IP (reputation)
   └─ Need advanced analytics
```

---

## 6. Cost Monitoring & Alerts

### Track These Metrics Daily

```
Vercel:
├─ Bandwidth used (target: < 80 GB)
├─ Build minutes (target: < 100/day)
└─ Dashboard: vercel.com → Project → Analytics

Render:
├─ CPU usage (target: < 60% avg)
├─ Memory usage (target: < 400 MB)
├─ Request rate (target: < 300 req/min)
└─ Dashboard: render.com → Services → Metrics

Supabase:
├─ Database size (target: < 800 MB)
├─ Row count (target: < 400K)
├─ Concurrent connections (target: < 80)
└─ Dashboard: supabase.com → Project → Settings → Usage
```

### Create Monitoring Dashboard

```python
# scheduler/scripts/cost_monitor.py
import os
from supabase import create_client
import datetime

# Query database size
query = """
SELECT
    pg_size_pretty(pg_database.datsize) as size,
    datname
FROM pg_database
WHERE datname = current_database();
"""

# Query row counts
row_counts = {
    'users': 'SELECT COUNT(*) FROM users',
    'portfolios': 'SELECT COUNT(*) FROM portfolios',
    'trades': 'SELECT COUNT(*) FROM trades',
    'options': 'SELECT COUNT(*) FROM options',
}

# Log to file or Slack
print(f"Database size: {db_size}")
print(f"User count: {user_count}")
# Alert if any metric > 80% of limit
```

---

## 7. Upgrade Cost vs. Revenue

### Simple Math

```
Current Free Tier Cost:
├─ Vercel:       $0-5
├─ Render:       $10
├─ Supabase:     $0
├─ GitHub:       $0
└─ Total:        ~$10/month

With 150 PRO Users @ $19/month:
├─ Revenue:      $2,850/month
├─ Costs at Pro: $65/month (Vercel $20 + Render $20 + Supabase $25)
├─ Profit:       $2,785/month
└─ ROI:          4,277%

Decision: Upgrade when revenue covers cost (usually immediately)
```

---

## 8. Upgrade Timeline Recommendations

### Months 0-1 (Launch)
```
Subscribers: 1-10
├─ All free tier
├─ Monitor but don't upgrade
└─ Monthly cost: ~$10
```

### Months 1-2 (Early Growth)
```
Subscribers: 10-50
├─ Monitor Render performance
├─ Consider Redis caching (add $0-5)
└─ Monthly cost: ~$10-15
```

### Months 2-4 (Traction)
```
Subscribers: 50-150
├─ Upgrade to Render Standard ($7-14/month)
├─ Consider Supabase Pro if > 100 users
├─ Add monitoring service ($10/month)
└─ Monthly cost: ~$50-70
```

### Months 4+ (Scale)
```
Subscribers: 150+
├─ Vercel Pro ($20/month)
├─ Render Pro ($20+/month)
├─ Supabase Pro ($25/month)
├─ Monitoring/Analytics ($50/month)
└─ Total: ~$115/month
   ├─ With 150 PRO users: $2,850 revenue
   ├─ Cost: $115
   └─ Margin: 96%
```

---

## 9. Upgrade Checklist

When you decide to upgrade a service:

```
☐ Document current usage
☐ Calculate ROI (revenue vs cost)
☐ Determine new plan size
☐ Test in staging first (if possible)
☐ Set billing alert notifications
☐ Update documentation
☐ Notify team
☐ Update .env variables (if needed)
☐ Monitor for 1 week after upgrade
☐ Adjust alerts/scaling policies
```

---

## Next Steps

- **See Implementation Phases?** → [IMPLEMENTATION-PHASES](./IMPLEMENTATION-PHASES.md)
- **Check Roadmap?** → [ROADMAP](./ROADMAP.md)
- **Review Checklist?** → [QUICK-START-CHECKLIST](./QUICK-START-CHECKLIST.md)

---

**Version:** Triggers-A | **Last Updated:** 2026-06-15
