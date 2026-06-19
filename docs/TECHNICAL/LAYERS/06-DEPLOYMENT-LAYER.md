# StrideAlytics — Deployment Layer

**Cloud infrastructure and hosting configuration**

---

## Overview

The **Deployment Layer** defines how StrideAlytics is hosted, scaled, and managed across multiple cloud services for production operations.

**Key Characteristics:**
- ✅ Multi-cloud deployment strategy
- ✅ Automated scaling
- ✅ Global CDN distribution
- ✅ Database high availability
- ✅ Security & SSL/TLS
- ✅ Monitoring & alerting
- ✅ Disaster recovery
- ✅ Cost optimization

---

## 1. Infrastructure Overview

```
┌────────────────────────────────────────────────────┐
│              StrideAlytics Infrastructure          │
├────────────────────────────────────────────────────┤
│                                                    │
│  🌐 Frontend (Vercel)                             │
│    - Global CDN                                   │
│    - Auto-scaling                                 │
│    - Edge functions                               │
│                                                    │
│  🖥️ Backend (Render)                              │
│    - FastAPI servers                              │
│    - Auto-scaling dynos                           │
│    - Managed database connections                 │
│                                                    │
│  🗄️ Database (Supabase)                           │
│    - PostgreSQL managed service                   │
│    - Automatic backups                            │
│    - Connection pooling                           │
│                                                    │
│  📱 Mobile (Expo EAS)                             │
│    - Native app builds                            │
│    - OTA updates                                  │
│                                                    │
│  ⚙️ Automation (GitHub Actions)                    │
│    - CI/CD pipelines                              │
│    - Scheduled jobs                               │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## 2. Web Frontend (Vercel)

### Deployment Configuration

```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "env": {
    "VITE_API_URL": "@vite_api_url",
    "VITE_SUPABASE_URL": "@vite_supabase_url"
  },
  "routes": [
    {
      "src": "^/api/(.*)",
      "dest": "https://api.stridealytics.com/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html",
      "status": 200
    }
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=3600"
        }
      ]
    }
  ]
}
```

### Environment Variables

```bash
# Production
VITE_API_URL=https://api.stridealytics.com
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_KEY=public-key

# Staging
VITE_API_URL=https://staging-api.stridealytics.com
VITE_SUPABASE_URL=https://xxx-staging.supabase.co
```

### Deployment Command

```bash
# Deploy to Vercel
vercel deploy --prod

# Deploy to staging
vercel deploy
```

### Performance Optimization

- **Image Optimization:** Vercel automatically optimizes images
- **Code Splitting:** Vite handles bundle splitting
- **CDN Caching:** Vercel serves from 250+ global locations
- **Instant Rollback:** One-click rollback to previous deployments

---

## 3. Backend API (Render)

### Deployment Configuration

```yaml
# render.yaml
services:
  - type: web
    name: stridealytics-api
    env: python
    plan: standard
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    numInstances: 2
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11
    disk:
      name: model_cache
      mountPath: /app/models
      sizeGB: 10
```

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Auto-scaling Configuration

```yaml
# Based on CPU & Memory
Auto-scaling enabled:
  - Min instances: 1
  - Max instances: 10
  - CPU target: 70%
  - Memory target: 80%
```

### Environment Variables

```bash
# Production
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=service-role-key
JWT_SECRET=your-secret
API_ENV=production
LOG_LEVEL=info

# Staging
API_ENV=staging
LOG_LEVEL=debug
```

---

## 4. Database (Supabase)

### Project Setup

**Plan:** Pro ($25/month)  
**Region:** us-east-1  
**PostgreSQL Version:** 15+

### Connections & Pooling

```
Connection string: postgres://...
Max connections: 100
Pooling mode: Transaction (PgBouncer)
Pool size: 15
Connection timeout: 30s
```

### Backups

- **Automatic:** Daily at 2 AM UTC
- **Retention:** 30 days
- **Point-in-time Recovery:** Available
- **Manual:** On-demand via console

### High Availability

- **Replication:** Read replicas available
- **Failover:** Automatic
- **Maintenance:** Scheduled updates (Sundays 2 AM UTC)

---

## 5. Mobile Apps (Expo EAS)

### EAS Build Configuration

```json
// eas.json
{
  "cli": {
    "version": ">= 3.0.0"
  },
  "build": {
    "preview": {
      "android": {
        "buildType": "apk",
        "gradleCommand": ":app:assembleRelease"
      },
      "ios": {
        "buildType": "simulator"
      }
    },
    "production": {
      "android": {
        "buildType": "aab",
        "release": true
      },
      "ios": {
        "buildType": "archive",
        "provisioning": "adhoc"
      }
    }
  },
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "./android-key.json",
        "track": "production"
      },
      "ios": {
        "appleId": "your-email@example.com",
        "ascAppId": "123456789"
      }
    }
  }
}
```

### Release Process

```bash
# Build for preview
eas build --platform ios --profile preview

# Build for production
eas build --platform ios --profile production

# Submit to app store
eas submit -p ios --latest

# Submit to play store
eas submit -p android --latest
```

---

## 6. Monitoring & Observability

### Services

| Service | Purpose | Cost |
|---------|---------|------|
| **Datadog** | Metrics & APM | $15+/month |
| **Sentry** | Error tracking | Free tier |
| **LogRocket** | Session replay | $99+/month |
| **UptimeRobot** | Uptime monitoring | Free tier |

### Setup Example (Sentry)

```python
# Backend integration
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=os.getenv('ENVIRONMENT'),
)
```

---

## 7. Security

### SSL/TLS Certificates

- **Provider:** Let's Encrypt (auto-renewed)
- **Domains:** 
  - stridealytics.com
  - api.stridealytics.com
  - app.stridealytics.com

### Network Security

- **Firewall:** Render managed firewall
- **DDoS Protection:** Cloudflare (optional)
- **Rate Limiting:** API-level rate limiting
- **IP Whitelisting:** Optional for API calls

### Data Encryption

- **Transit:** HTTPS/TLS 1.3
- **At Rest:** AES-256 (Supabase)
- **Backups:** Encrypted storage

---

## 8. Cost Estimation (Monthly)

| Service | Plan | Cost |
|---------|------|------|
| **Vercel** | Hobby + Pro | $20 |
| **Render** | Standard 2x | $7/dyno × 2 = $14 |
| **Supabase** | Pro | $25 |
| **GitHub Actions** | Included | Free* |
| **Monitoring** | Datadog Lite | $15 |
| **CDN** | Vercel included | Free |
| **Email** | SendGrid | $10 |
| **Total** | | ~$84/month |

*5,000 free minutes/month

---

## 9. Disaster Recovery

### Backup Strategy

```
Database Backups:
- Automatic daily backups (30-day retention)
- Weekly offsite backup (S3)
- Point-in-time recovery capability

Code Backups:
- GitHub is primary backup
- Mirror to GitLab (optional)

Infrastructure as Code:
- Vercel config checked in
- Docker configs versioned
- Terraform templates available
```

### Recovery Plan

```
RTO (Recovery Time Objective): 1 hour
RPO (Recovery Point Objective): 1 day

Steps:
1. Restore database from backup
2. Redeploy API from git
3. Redeploy frontend from git
4. Run health checks
5. Validate data integrity
6. Switch DNS if needed
```

---

## 10. Deployment Checklist

```yaml
Pre-Deployment:
  - [ ] All tests passing
  - [ ] Code reviewed & merged
  - [ ] Migration scripts prepared
  - [ ] Rollback plan documented
  - [ ] Monitoring alerts configured
  - [ ] Stakeholders notified

Deployment:
  - [ ] Deploy to staging first
  - [ ] Run integration tests
  - [ ] Manual testing
  - [ ] Performance check
  - [ ] Security scan
  - [ ] Database migrations
  - [ ] Deploy to production
  - [ ] Smoke tests
  - [ ] Monitor metrics

Post-Deployment:
  - [ ] Verify health checks
  - [ ] Check error rates
  - [ ] Monitor performance
  - [ ] Validate user flows
  - [ ] Document changes
  - [ ] Update status page
```

---

## 11. Scaling Strategy

### Horizontal Scaling

```
Frontend (Vercel):
- Automatic global distribution
- Scale by region

Backend (Render):
- Scale dynos: 1 → 5 → 10
- Load balanced

Database (Supabase):
- Connection pooling
- Read replicas (upgrade to Pro+)
```

### Performance Targets

- **API Response:** < 200ms
- **Frontend Load:** < 3s
- **Database Query:** < 50ms
- **Uptime:** 99.9%

---

## 12. Environment Parity

```
Development ≈ Staging ≈ Production

Same:
- Code (same branch/tag)
- Configuration structure
- Dependency versions
- Database schema

Different:
- Scale (dev: small, prod: large)
- Data volume
- Secrets/API keys
- Logging levels
```

---

## Next Steps

- **CI/CD Pipeline?** → [07-CI-CD-LAYER](./07-CI-CD-LAYER.md)
- **Scheduler?** → [05-SCHEDULER-LAYER](./05-SCHEDULER-LAYER.md)
- **View Diagrams?** → [02-SYSTEM-DIAGRAMS](../02-SYSTEM-DIAGRAMS.md)

---

**Version:** A | **Last Updated:** 2026-06-15
