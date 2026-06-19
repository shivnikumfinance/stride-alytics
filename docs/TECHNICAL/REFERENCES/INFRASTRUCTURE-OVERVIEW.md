# StrideAlytics — Infrastructure Overview

**Deployment targets, services, and connectivity information**

---

## 1. Architecture Components

### Frontend (Web Application)
```
Platform:           Vercel
URL:                https://stridealytics.vercel.app
Custom Domain:      https://stridealytics.com
Build Command:      npm run build
Output Directory:   dist/
Build Time:         ~3-5 minutes
Cache Strategy:     Edge caching + SWR
SSL/TLS:            Automatic (Let's Encrypt)
Regions:            250+ edge locations globally
```

### Backend API
```
Platform:           Render
URL:                https://api.stridealytics.com
Service Type:       Web Service (Docker)
Plan:               Standard
Instances:          2 (min: 1, max: 10 auto-scaling)
Memory per dyno:    512 MB
CPU per dyno:       0.5 CPU
Build:              Docker-based
Deployment:         Git-connected
SSL/TLS:            Automatic
Health Check:       /health endpoint
Auto-scaling:       CPU > 70% or Memory > 80%
```

### Database
```
Platform:           Supabase
Type:               Managed PostgreSQL
Version:            15+
Plan:               Pro ($25/month)
Region:             us-east-1
Max Connections:    100
Connection Pool:    15 (PgBouncer)
Backup:             Daily (30-day retention)
High Availability:  Available (read replicas)
SSL/TLS:            Mandatory
```

### Mobile Apps
```
Platform:           Expo EAS
iOS:                TestFlight → App Store
Android:            Internal testing → Google Play
Build Service:      EAS Build (managed)
OTA Updates:        Expo Updates
Version Strategy:   Semantic versioning
```

### Automation & Scheduling
```
Platform:           GitHub Actions
Workflows:          Scheduled + Event-triggered
Minutes/month:      5,000 free tier
Storage:            500 MB artifacts
Runners:            Ubuntu latest
```

---

## 2. Networking & DNS

### Domain Configuration
```
Domain:             stridealytics.com
Registrar:          (Your registrar)
DNS Provider:       Vercel (recommended)

DNS Records:
- stridealytics.com          A → Vercel
- www.stridealytics.com      CNAME → stridealytics.vercel.app
- api.stridealytics.com      CNAME → api.stridealytics.render.com
- app.stridealytics.com      CNAME → (optional, can point to vercel)

SSL Certificates:
- Issued by:        Let's Encrypt (auto-renewed)
- Valid for:        90 days (auto-renews every 30 days)
- Covered domains:  *.stridealytics.com, stridealytics.com
```

### API Endpoints

```
Base URL:           https://api.stridealytics.com
API Version:        /v1
Health Check:       GET /health
Rate Limit:         100 req/min per IP

Endpoints:
- POST   /api/v1/auth/login
- POST   /api/v1/auth/signup
- GET    /api/v1/auth/profile
- GET    /api/v1/screener
- GET    /api/v1/screener/{id}
- POST   /api/v1/greeks/calculate
- GET    /api/v1/regime
- GET    /api/v1/picks
- GET    /api/v1/portfolio
- GET    /api/v1/trades
- POST   /api/v1/trades
- etc.
```

---

## 3. Environment-Specific Configuration

### Development
```
Frontend:
  URL:              http://localhost:5173
  API:              http://localhost:8000
  Database:         Local Supabase

Backend:
  URL:              http://localhost:8000
  Reload:           On file change
  Database:         Dev Supabase project

Database:
  URL:              https://xxx-dev.supabase.co
  Connection:       Direct
  Migrations:       Applied manually

Mobile:
  Build Type:       Debug
  API:              http://localhost:8000
  Environment:      Development
```

### Staging
```
Frontend:
  URL:              https://staging.stridealytics.com
  API:              https://staging-api.stridealytics.com
  Database:         Staging Supabase

Backend:
  URL:              https://staging-api.stridealytics.com
  Environment:      staging
  Database:         Staging Supabase project

Database:
  URL:              https://xxx-staging.supabase.co
  Connection:       Pooled
  Backups:          Daily

Mobile:
  Build Type:       Release (TestFlight/Internal)
  API:              https://staging-api.stridealytics.com
  Environment:      Staging
```

### Production
```
Frontend:
  URL:              https://stridealytics.com
  API:              https://api.stridealytics.com
  Database:         Production Supabase
  CDN:              Vercel global edge network

Backend:
  URL:              https://api.stridealytics.com
  Environment:      production
  Database:         Production Supabase project
  Auto-scaling:     Enabled
  Monitoring:       Enabled

Database:
  URL:              https://xxx.supabase.co
  Connection:       Pooled + replicas
  Backups:          Daily + point-in-time recovery
  High Availability: Enabled

Mobile:
  Build Type:       Release (App Store/Play Store)
  API:              https://api.stridealytics.com
  Environment:      Production
  Crash Reporting:  Enabled
```

---

## 4. Service Connectivity

### Frontend → Backend

```
HTTP Method:        REST (GET, POST, PUT, DELETE)
Protocol:           HTTPS
Authentication:     JWT Bearer Token
Headers:
  Authorization:    Bearer <jwt_token>
  Content-Type:     application/json

Example Request:
GET https://api.stridealytics.com/api/v1/screener
Headers:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  Content-Type: application/json

Response:
{
  "data": [...],
  "total": 50,
  "page": 1,
  "per_page": 20
}
```

### Backend → Database

```
Driver:             asyncpg (async)
Connection String:  postgresql://user:pass@host:5432/db
Connection Pool:    15 connections (PgBouncer)
SSL/TLS:            Required
Auth:               User/password or service role

Example:
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
client = create_client(supabase_url, supabase_key)
```

### Backend → External APIs

```
yfinance:
  URL:              https://query1.finance.yahoo.com
  Protocol:         HTTPS
  Auth:             None (public API)
  Rate Limit:       ~2000 requests per hour
  Timeout:          30 seconds

Other Data Sources:
  Protocol:         HTTPS
  Auth:             API Key (in env variables)
  Timeout:          30 seconds
```

### Mobile → Backend

```
Same as Frontend:
  Protocol:         HTTPS
  Auth:             JWT Bearer Token
  Base URL:         https://api.stridealytics.com
  Certificate Pinning: (Optional for security)
```

---

## 5. Load Balancing & Scaling

### Frontend (Vercel)
```
Automatic:          Yes
Strategy:           Geographic routing to nearest edge
Failover:           Automatic
Scale:              Automatic (no configuration needed)
```

### Backend (Render)
```
Load Balancer:      Built-in
Strategy:           Round-robin
Auto-scaling:       CPU/Memory based
Min Instances:      1
Max Instances:      10
Scale-up Trigger:   70% CPU or 80% Memory
Scale-down Delay:   5 minutes idle
```

### Database (Supabase)
```
Connection Pooling: PgBouncer
Pool Size:          15
Mode:               Transaction pooling
Read Replicas:      Available (with paid plan)
Auto-failover:      Automatic
```

---

## 6. Monitoring & Logging

### Application Monitoring

```
Vercel (Frontend):
  - Metrics dashboard
  - Real User Monitoring (RUM)
  - Analytics API
  - Performance insights
  
Render (Backend):
  - CPU, Memory graphs
  - Error logs
  - Event logs
  - Health checks
  
Supabase (Database):
  - Query performance
  - Connection stats
  - Backup status
  - Realtime stats
```

### External Monitoring (Optional)

```
Datadog:
  - APM (Application Performance Monitoring)
  - Infrastructure monitoring
  - Custom metrics
  - Alerting
  - Cost: $15+/month

Sentry:
  - Error tracking
  - Release tracking
  - Performance monitoring
  - Cost: Free tier available

LogRocket:
  - Session replay
  - Crash reporting
  - Network monitoring
  - Cost: $99+/month
```

### Logging

```
Vercel:
  - Automatic request/error logs
  - Accessible via dashboard
  - Retention: 48 hours (free), longer with upgrade

Render:
  - Service logs (stdout/stderr)
  - Build logs
  - Accessible via dashboard
  
Supabase:
  - Query logs
  - Auth logs
  - API logs
  - Retention: Depends on plan

Backend Application:
  - Structured logging (structlog)
  - Log level: DEBUG/INFO/WARNING/ERROR
  - Destination: stdout (Render captures)
```

---

## 7. Backup & Disaster Recovery

### Database Backups

```
Automatic Backups:
  Frequency:        Daily at 2 AM UTC
  Retention:        30 days
  Location:         Supabase managed storage
  Encryption:       AES-256
  
Manual Backups:
  Method:           Via Supabase console or pg_dump
  Frequency:        On-demand
  Storage:          AWS S3 (if exported)
  
Point-in-Time Recovery:
  Available:        Yes
  Retention:        30 days
  RTO:              ~1 hour
  RPO:              ~1 minute
```

### Code Backups

```
Primary:            GitHub repository
Mirror:             GitLab (optional)
Frequency:          On every push
Retention:          Unlimited
```

### Application State

```
Caching:            Redis (optional, not required)
Session State:      JWT tokens (stateless)
User Data:          PostgreSQL (backed up daily)
```

---

## 8. Performance SLA

```
Frontend:
  - Page Load:      < 3 seconds
  - Time to Interactive: < 5 seconds
  - Uptime:         99.9%

Backend:
  - API Response:   < 200ms (p95)
  - Error Rate:     < 0.1%
  - Uptime:         99.9%

Database:
  - Query Response: < 50ms (p95)
  - Connection Time: < 100ms
  - Uptime:         99.99%

Mobile:
  - App Load:       < 2 seconds
  - Response Time:  < 500ms
```

---

## 9. Cost Summary

| Service | Plan | Cost/Month | Purpose |
|---------|------|-----------|---------|
| Vercel | Hobby+Pro | $20 | Web hosting |
| Render | Standard | $14 | API hosting |
| Supabase | Pro | $25 | Database |
| GitHub | Free | $0 | CI/CD |
| Datadog | (optional) | $15+ | Monitoring |
| SendGrid | (optional) | $10 | Email |
| **Total** | | ~$84 | |

---

## 10. Maintenance Windows

```
Vercel:
  - Typically no downtime
  - Deployments: On-demand (blue-green)
  
Render:
  - Maintenance: Scheduled
  - Typical downtime: None (managed)
  
Supabase:
  - Maintenance: Sundays 2 AM UTC
  - Downtime: Usually none
  - Duration: ~15 minutes
  - Notification: Via dashboard
```

---

## 11. Compliance & Security

```
Data Encryption:
  - Transit: HTTPS/TLS 1.3
  - At Rest: AES-256 (Supabase)
  
Data Residency:
  - Frontend: Global (Vercel CDN)
  - Backend: us-east-1
  - Database: us-east-1
  
Compliance:
  - GDPR: Compliant
  - SOC 2: Available (Supabase Pro)
  - HIPAA: Not applicable (not regulated data)
  
Access Control:
  - API: JWT-based
  - Database: RLS policies
  - Admin: GitHub, Vercel, Render dashboards
```

---

## 12. Emergency Contacts

```
Service Issues:
- Vercel Status:     https://www.vercel-status.com
- Render Status:     https://render-status.com
- Supabase Status:   https://status.supabase.com

Support:
- Vercel:            support@vercel.com
- Render:            support@render.com
- Supabase:          support@supabase.com
- GitHub:            support@github.com
```

---

## Next Steps

- **See Deployment Details?** → [06-DEPLOYMENT-LAYER](../LAYERS/06-DEPLOYMENT-LAYER.md)
- **View Libraries?** → [LIBRARIES-BY-LAYER](./LIBRARIES-BY-LAYER.md)
- **Check System Diagrams?** → [02-SYSTEM-DIAGRAMS](../02-SYSTEM-DIAGRAMS.md)

---

**Version:** A | **Last Updated:** 2026-06-15
