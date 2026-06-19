# StrideAlytics — Scheduler Layer

**GitHub Actions automated tasks and workflows**

---

## Overview

The **Scheduler Layer** automates recurring tasks like data collection, analysis, report generation, and system maintenance using GitHub Actions CRON jobs and event-driven workflows.

**Key Characteristics:**
- ✅ Scheduled CRON jobs
- ✅ Event-driven workflows
- ✅ Parallel execution
- ✅ Error notifications
- ✅ Audit logging
- ✅ Retry mechanisms
- ✅ Zero-cost automation
- ✅ Version controlled

---

## 1. Workflow Structure

### Directory Layout

```
.github/workflows/
├── fetch-market-data.yml       # Daily market data collection
├── calculate-greeks.yml        # Daily Greeks calculation
├── generate-regime.yml         # Weekly regime analysis
├── generate-picks.yml          # Weekly picks generation
├── health-check.yml            # Hourly health monitoring
├── deploy-frontend.yml         # Frontend deployment
├── deploy-backend.yml          # Backend deployment
├── deploy-mobile.yml           # Mobile app build
├── run-tests.yml               # Test suite
└── database-backup.yml         # Database backups
```

---

## 2. Core Workflows

### Fetch Market Data

```yaml
# .github/workflows/fetch-market-data.yml
name: Fetch Market Data

on:
  schedule:
    # Every day at 9:30 AM ET (market open)
    - cron: '30 13 * * MON-FRI'
  workflow_dispatch: # Manual trigger

jobs:
  fetch-data:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r scheduler/requirements.txt
      
      - name: Fetch market data
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: |
          python scheduler/scripts/fetch_market_data.py
      
      - name: Send notification
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: 1,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '❌ Market data fetch failed'
            })
```

### Calculate Greeks

```yaml
# .github/workflows/calculate-greeks.yml
name: Calculate Greeks

on:
  schedule:
    # Every day at 4:00 PM ET (market close)
    - cron: '00 20 * * MON-FRI'
  workflow_dispatch:

jobs:
  calculate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r scheduler/requirements.txt
      
      - name: Calculate Greeks
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: python scheduler/scripts/calculate_greeks.py
```

### Generate Weekly Picks

```yaml
# .github/workflows/generate-weekly-picks.yml
name: Generate Weekly Picks

on:
  schedule:
    # Every Friday at 5:00 PM ET
    - cron: '00 21 * * FRI'
  workflow_dispatch:

jobs:
  generate-picks:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Generate picks
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
          SEND_NOTIFICATIONS: 'true'
        run: python scheduler/scripts/generate_picks.py
      
      - name: Send picks to users
        env:
          SENDGRID_API_KEY: ${{ secrets.SENDGRID_API_KEY }}
        run: python scheduler/scripts/send_picks_email.py
```

### Health Check

```yaml
# .github/workflows/health-check.yml
name: Health Check

on:
  schedule:
    # Every 30 minutes
    - cron: '*/30 * * * *'
  workflow_dispatch:

jobs:
  health-check:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Run health checks
        env:
          API_URL: ${{ secrets.API_URL }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
        run: python scheduler/scripts/health_check.py
      
      - name: Report status
        if: always()
        run: |
          # Send metrics to monitoring service
          python scheduler/scripts/report_metrics.py
```

---

## 3. Python Scripts

### Fetch Market Data Script

```python
# scheduler/scripts/fetch_market_data.py
import asyncio
from datetime import datetime
import yfinance as yf
from app.database.client import supabase
import structlog

logger = structlog.get_logger()

async def fetch_market_data():
    """Fetch latest market data from yfinance and store in database"""
    
    logger.info("Starting market data fetch")
    
    # Get list of symbols to track
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'SPY']
    
    for symbol in symbols:
        try:
            # Fetch data
            stock = yf.Ticker(symbol)
            data = stock.history(period='1d')
            
            # Extract latest price
            latest = data.iloc[-1]
            
            # Store in database
            supabase.table('market_data').insert({
                'symbol': symbol,
                'price': float(latest['Close']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'volume': int(latest['Volume']),
                'timestamp': datetime.now().isoformat(),
            }).execute()
            
            logger.info(f"Fetched {symbol}", price=latest['Close'])
            
        except Exception as e:
            logger.error(f"Failed to fetch {symbol}", error=str(e))
    
    logger.info("Market data fetch complete")

if __name__ == '__main__':
    asyncio.run(fetch_market_data())
```

### Calculate Greeks Script

```python
# scheduler/scripts/calculate_greeks.py
from scipy.stats import norm
import math
from app.database.client import supabase
from app.services.greeks import calculate_greeks

async def calculate_all_greeks():
    """Calculate Greeks for all options in database"""
    
    # Fetch all active options
    result = supabase.table('options').select('*').is_('expiry', 'null', negate=True).execute()
    options = result.data
    
    for option in options:
        try:
            greeks = calculate_greeks(
                spot_price=option['spot_price'],
                strike=option['strike'],
                time_to_expiry=option['time_to_expiry'],
                risk_free_rate=0.05,
                volatility=option['implied_vol'],
                option_type=option['type'],
            )
            
            # Update database
            supabase.table('options').update({
                'delta': greeks['delta'],
                'gamma': greeks['gamma'],
                'theta': greeks['theta'],
                'vega': greeks['vega'],
                'rho': greeks['rho'],
                'updated_at': datetime.now().isoformat(),
            }).eq('id', option['id']).execute()
            
        except Exception as e:
            logger.error(f"Failed to calculate Greeks for {option['id']}", error=str(e))
```

### Health Check Script

```python
# scheduler/scripts/health_check.py
import requests
import structlog
from app.database.client import supabase

logger = structlog.get_logger()

async def health_check():
    """Check system health and report status"""
    
    checks = {
        'api': check_api(),
        'database': check_database(),
        'external_apis': check_external_apis(),
    }
    
    for service, result in checks.items():
        if result['status'] == 'healthy':
            logger.info(f"{service} is healthy")
        else:
            logger.error(f"{service} health check failed", details=result['details'])
    
    return all(check['status'] == 'healthy' for check in checks.values())

def check_api():
    """Check backend API health"""
    try:
        response = requests.get(
            f"{os.getenv('API_URL')}/health",
            timeout=5
        )
        return {'status': 'healthy' if response.status_code == 200 else 'unhealthy'}
    except Exception as e:
        return {'status': 'unhealthy', 'details': str(e)}

def check_database():
    """Check database connection"""
    try:
        result = supabase.table('users').select('count', count='exact').execute()
        return {'status': 'healthy'}
    except Exception as e:
        return {'status': 'unhealthy', 'details': str(e)}

def check_external_apis():
    """Check external API availability"""
    try:
        response = requests.get('https://query1.finance.yahoo.com/v10/finance/quoteSummary/AAPL', timeout=5)
        return {'status': 'healthy' if response.status_code == 200 else 'unhealthy'}
    except Exception as e:
        return {'status': 'unhealthy', 'details': str(e)}
```

---

## 4. CRON Schedule Reference

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday - Saturday)
│ │ │ │ │
│ │ │ │ │
* * * * *

Examples:
'30 9 * * *'        → 9:30 AM every day
'0 */6 * * *'       → Every 6 hours
'*/30 * * * *'      → Every 30 minutes
'0 0 * * 1'         → Every Monday at midnight
'0 9 1 * *'         → 9 AM on the 1st of every month
'0 13 * * MON-FRI'  → 1:00 PM weekdays (market open)
'0 20 * * MON-FRI'  → 8:00 PM weekdays (market close)
```

---

## 5. Secrets Management

### Setting Up Secrets

```bash
# In GitHub repository Settings > Secrets
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_anon_key
JWT_SECRET=your_secret
SENDGRID_API_KEY=your_api_key
API_URL=https://api.stridealytics.com
```

### Using Secrets in Workflows

```yaml
env:
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
```

---

## 6. Error Handling & Notifications

### Slack Notifications

```yaml
- name: Notify Slack on failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "❌ Scheduler workflow failed",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Workflow Failed*\nWorkflow: ${{ github.workflow }}\nBranch: ${{ github.ref }}"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 7. Monitoring & Logging

### Task Logging

```python
# All scripts log using structlog
logger.info("task_start", task="fetch_market_data")
logger.info("task_complete", task="fetch_market_data", duration=elapsed_time)
logger.error("task_failed", task="fetch_market_data", error=error_message)
```

### Metrics Reporting

```python
# scheduler/scripts/report_metrics.py
import os
from datadog import initialize, api

options = {
    'api_key': os.getenv('DATADOG_API_KEY'),
    'app_key': os.getenv('DATADOG_APP_KEY')
}

initialize(**options)

def report_metrics():
    """Report execution metrics to Datadog"""
    api.Metric.send(
        metric='stridealytics.market_data.fetch_duration',
        points=45,  # milliseconds
        tags=['env:production', 'service:scheduler']
    )
```

---

## 8. Best Practices

✅ **DO:**
- Use descriptive workflow names
- Add manual triggers for testing
- Implement proper error handling
- Log all important events
- Use secrets for sensitive data
- Set reasonable timeouts
- Monitor execution times
- Document schedule in comments

❌ **DON'T:**
- Hardcode sensitive data
- Use overly complex CRON expressions
- Skip error notifications
- Schedule too many jobs at same time
- Ignore workflow failures
- Use loose timeout values
- Forget to test schedules

---

## 9. Testing Schedules

```bash
# Test a workflow manually
gh workflow run fetch-market-data.yml --ref main

# View workflow runs
gh run list -w fetch-market-data.yml

# View detailed run info
gh run view <run_id>
```

---

## Next Steps

- **Deployment?** → [06-DEPLOYMENT-LAYER](./06-DEPLOYMENT-LAYER.md)
- **CI/CD Pipeline?** → [07-CI-CD-LAYER](./07-CI-CD-LAYER.md)
- **View Diagrams?** → [02-SYSTEM-DIAGRAMS](../02-SYSTEM-DIAGRAMS.md)

---

**Version:** A | **Last Updated:** 2026-06-15
