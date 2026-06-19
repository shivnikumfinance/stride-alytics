# StrideAlytics — Financial Model

## 1. Revenue Model

### Pricing Tiers

- **Free Tier**
  - Access to basic screener
  - Unlimited Greeks calculator
  - Limited portfolio tracking
  - Market regime summary
  - Weekly email insights
- **PRO Tier**
  - $19/month
  - Unlimited screener results
  - Advanced filters and saved templates
  - Portfolio analytics and historical reporting
  - API access and webhooks
  - Real-time notifications and premium support

### Revenue Targets

- Early target: 150 PRO users → $2,850/mo
- Growth target: 500 PRO users → $9,500/mo
- Long-term target: 2,000 PRO users → $38,000/mo

## 2. Cost Assumptions

| Service | Free Tier Limits | Estimated Monthly Cost |
|---------|------------------|------------------------|
| Vercel | 100 GB bandwidth | $0-5 |
| Render | 750 compute hours | $10 |
| Supabase | 1 GB storage, 500K rows | $0 |
| GitHub Actions | 2,000 minutes | $0 |
| SendGrid | 100 emails/day | $0 |
| Monitoring | Free tier tools | $0-10 |
| Total | | ~$10-25 |

## 3. Break-even Analysis

- Break-even threshold: ~150 PRO users at $19/month.
- Net revenue after cost: $2,850 - $25 = $2,825.
- Key levers:
  - Improve conversion rate from free to PRO.
  - Increase ARPU via add-on products and API usage.
  - Control infrastructure cost growth through caching and tiered services.

## 4. Upgrade Economics

### Upgrade Triggers

- If frontend traffic exceeds 100 GB/month, upgrade Vercel plan.
- If API requests exceed 400/min or 750 compute hours/month, upgrade Render.
- If database size exceeds 1 GB or query volume grows, upgrade Supabase.
- If usage reaches 80% of free-tier limits for two consecutive weeks, evaluate upgrades.

### ROI Rules

- Only upgrade when incremental revenue exceeds incremental cost.
- Prioritize feature monetization before scaling expensive infrastructure.
- Maintain a buffer of 1.5x monthly revenue over projected monthly spend.

## 5. Financial KPIs

- **Free-to-PRO conversion rate**: 5-10%
- **LTV:CAC ratio**: target ≥ 3:1
- **Gross margin**: target ≥ 80%
- **CAC payback period**: < 6 months
- **Churn rate**: target < 5% monthly

## 6. Financial Controls

- Track revenue daily with a dashboard.
- Measure active usage and feature engagement per cohort.
- Reconcile billing and subscription data weekly.
- Conduct monthly cost reviews tied to growth metrics.
- Freeze new spending if revenue growth slows below 10% month over month.
