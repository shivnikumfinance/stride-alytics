# StrideAlytics — Roadmap

**Feature plan for a personal-use, free-tier tool**

> **SCOPE (2026-11-14):** Personal use only. There is no PRO plan, user-growth target or revenue goal. Free tiers are the default; paid APIs or services may be added later if needed. The **mobile app** is deferred until further confirmation. Dates are not committed; order is by priority.

---

## Vision

A rules-driven options-selling analytics tool for one trader: screen, score, gate and track trades under a regime-aware risk framework, on free tiers by default.

**Success measures**
- The daily pipeline runs reliably and data is fresh.
- Picks, regime and DNT gates are trustworthy and explainable.
- Stays within free-tier limits (see [UPGRADE-TRIGGERS](./UPGRADE-TRIGGERS.md)).

---

## Phase 1: Core (now)

```
Goal: a useful daily workflow
  ├─ Daily pipeline: load → score → bands → filters → weekly watchlist (alpha/)
  ├─ Streamlit dashboard on Supabase data
  ├─ Greeks calculator
  ├─ Portfolio and trade tracking
  ├─ Market regime score (VIX, SPY trend, IV Rank)
  ├─ DNT gates and position sizing
  ├─ Authentication (single user)
  └─ Health check and Slack/Discord failure alerts
```

## Phase 2: Analytics

- **Portfolio heat map** (risk by position)
- **Trade analytics** (win rate, average profit, risk/reward)
- **Historical performance** (portfolio over time)
- **Greeks exposure** (aggregate delta, gamma, theta)
- **Advanced screener filters** (spread, open interest, volume)
- **Custom watchlists**
- **Compare options** (side-by-side Greeks)
- **Alerts** (price, IV rank, regime changes) through Slack or Discord webhooks
- **Home hub** and Strategy Design Matrix in the React frontend

## Phase 3: Decision support

- **Scenario and stress testing** (Greeks sensitivity, what-if)
- **EV scoring** calibrated monthly against realized P&L
- **Correlation matrix**
- **Backtesting** on stored history
- **Implied move calculator** (earnings)
- **P&L breakdown** (delta, gamma, theta)

## Later (unscheduled)

- Broker import of real positions (read-only)
- Additional data sources to cover yfinance gaps (a paid data API is acceptable if free sources fall short)
- Backend caching
- Mobile app (deferred, requires confirmation)

---

## Technical improvements

```
Performance:
├─ Precompute heavy work in the scheduled pipeline; serve stored results
├─ Calculate Greeks client-side for the calculator
└─ Cache repeated backend calculations

Data quality:
├─ yfinance has gaps; keep the CSV fallback and add a second source if needed
└─ Retention job to keep the database under the free-tier size

Testing:
├─ alpha/ has no pytest suite yet
└─ Add end-to-end coverage for the scoring, band and DNT logic

Frontend:
├─ Code splitting by route
└─ Bundle analysis
```

---

## Review

Review this roadmap monthly together with the free-tier usage check.

## Next Steps

- **Implementation phases?** → [IMPLEMENTATION-PHASES](./IMPLEMENTATION-PHASES.md)
- **Free-tier limits?** → [UPGRADE-TRIGGERS](./UPGRADE-TRIGGERS.md)
- **Checklist?** → [QUICK-START-CHECKLIST](./QUICK-START-CHECKLIST.md)
