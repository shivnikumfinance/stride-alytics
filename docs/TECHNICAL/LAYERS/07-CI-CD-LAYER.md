# StrideAlytics — CI/CD Layer

**Continuous Integration and Continuous Deployment pipeline**

---

## Overview

The **CI/CD Layer** automates testing, building, and deployment of all system components through GitHub Actions workflows, ensuring code quality and rapid iteration cycles.

**Key Characteristics:**
- ✅ Automated testing on every commit
- ✅ Linting and code quality checks
- ✅ Build artifact generation
- ✅ Automated deployments to staging & production
- ✅ Rollback capabilities
- ✅ Environment-specific configs
- ✅ Parallel job execution
- ✅ Approval workflows

---

## 1. CI/CD Pipeline Architecture

```
Developer Push to main/dev
    ↓
GitHub Actions Triggered
    ├─ LINT & FORMAT
    │  ├─ ESLint (Frontend/Mobile)
    │  ├─ Prettier
    │  └─ Pylint (Backend)
    │
    ├─ UNIT TESTS
    │  ├─ Frontend: Vitest
    │  ├─ Mobile: Jest
    │  └─ Backend: pytest
    │
    ├─ INTEGRATION TESTS
    │  └─ Full system tests
    │
    ├─ BUILD
    │  ├─ Frontend: npm run build
    │  ├─ Backend: Docker build
    │  └─ Mobile: EAS build
    │
    ├─ SECURITY SCAN
    │  └─ Dependency check, SAST
    │
    └─ DEPLOY (if all pass)
       ├─ Staging: Auto-deploy
       └─ Production: Manual approval
```

---

## 2. Frontend CI/CD Workflow

### Workflow File

```yaml
# .github/workflows/frontend-ci-cd.yml
name: Frontend CI/CD

on:
  push:
    branches: [main, dev]
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-ci-cd.yml'
  pull_request:
    branches: [main, dev]
    paths: ['frontend/**']

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: 'frontend/package-lock.json'
      
      - name: Install dependencies
        run: cd frontend && npm ci
      
      - name: Run ESLint
        run: cd frontend && npm run lint
      
      - name: Run Prettier check
        run: cd frontend && npm run format:check
      
      - name: Run tests
        run: cd frontend && npm run test:ci
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/coverage-final.json
          flags: frontend
  
  build:
    runs-on: ubuntu-latest
    needs: lint-and-test
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: cd frontend && npm ci
      
      - name: Build
        env:
          VITE_API_URL: ${{ secrets.VITE_API_URL }}
        run: cd frontend && npm run build
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: frontend-build
          path: frontend/dist/

  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/dev'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: frontend-build
          path: dist/
      
      - name: Deploy to Vercel staging
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
        run: |
          npx vercel deploy --prebuilt --token $VERCEL_TOKEN

  deploy-production:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Download build artifacts
        uses: actions/download-artifact@v3
      
      - name: Deploy to Vercel production
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
        run: |
          npx vercel deploy --prod --prebuilt --token $VERCEL_TOKEN
      
      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        if: always()
        with:
          status: ${{ job.status }}
          text: 'Frontend deployed to production'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 3. Backend CI/CD Workflow

```yaml
# .github/workflows/backend-ci-cd.yml
name: Backend CI/CD

on:
  push:
    branches: [main, dev]
    paths:
      - 'backend/**'
      - 'requirements.txt'
  pull_request:
    branches: [main, dev]
    paths: ['backend/**']

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pylint black
      
      - name: Run Pylint
        run: pylint backend/
      
      - name: Check code format
        run: black --check backend/
      
      - name: Run unit tests
        run: pytest backend/tests/unit -v --cov=backend --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: backend
  
  build:
    runs-on: ubuntu-latest
    needs: lint-and-test
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: |
          docker build -t stridealytics-api:${{ github.sha }} .
          docker tag stridealytics-api:${{ github.sha }} stridealytics-api:latest
      
      - name: Push to Docker Hub
        if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/dev'
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push stridealytics-api:${{ github.sha }}
          docker push stridealytics-api:latest

  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/dev'
    
    steps:
      - name: Deploy to Render staging
        env:
          RENDER_DEPLOY_HOOK: ${{ secrets.RENDER_STAGING_DEPLOY_HOOK }}
        run: curl $RENDER_DEPLOY_HOOK

  deploy-production:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - name: Deploy to Render production
        env:
          RENDER_DEPLOY_HOOK: ${{ secrets.RENDER_PROD_DEPLOY_HOOK }}
        run: curl $RENDER_DEPLOY_HOOK
      
      - name: Run integration tests
        env:
          API_URL: ${{ secrets.PROD_API_URL }}
        run: pytest backend/tests/integration -v
```

---

## 4. Mobile CI/CD Workflow

```yaml
# .github/workflows/mobile-ci-cd.yml
name: Mobile CI/CD

on:
  push:
    branches: [main, dev]
    paths: ['mobile/**']
  pull_request:
    branches: [main, dev]
    paths: ['mobile/**']

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: cd mobile && npm ci
      
      - name: Run tests
        run: cd mobile && npm run test
      
      - name: Type check
        run: cd mobile && npm run type-check

  build-ios:
    runs-on: macos-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: cd mobile && npm ci
      
      - name: Build iOS with EAS
        env:
          EAS_TOKEN: ${{ secrets.EAS_TOKEN }}
        run: |
          npm install -g eas-cli
          cd mobile
          eas build --platform ios --profile production

  build-android:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: cd mobile && npm ci
      
      - name: Build Android with EAS
        env:
          EAS_TOKEN: ${{ secrets.EAS_TOKEN }}
        run: |
          npm install -g eas-cli
          cd mobile
          eas build --platform android --profile production
```

---

## 5. Integration & Smoke Tests

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on:
  workflow_run:
    workflows:
      - Backend CI/CD
      - Frontend CI/CD
    types: [completed]
    branches: [main]

jobs:
  smoke-tests:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install pytest requests
      
      - name: Wait for deployment
        run: sleep 30
      
      - name: Run smoke tests
        env:
          API_URL: https://staging-api.stridealytics.com
          FRONTEND_URL: https://staging.stridealytics.com
        run: pytest tests/smoke/ -v
      
      - name: Notify on failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Smoke tests failed on production'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 6. Database Migrations

```yaml
# .github/workflows/db-migrations.yml
name: Database Migrations

on:
  push:
    branches: [main]
    paths: ['database/migrations/**']

jobs:
  migrate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Supabase CLI
        run: npm install -g supabase
      
      - name: List migrations
        run: supabase migration list --db-url ${{ secrets.SUPABASE_DB_URL }}
      
      - name: Apply migrations
        run: supabase migration up --db-url ${{ secrets.SUPABASE_DB_URL }}
      
      - name: Verify schema
        run: supabase db pull --db-url ${{ secrets.SUPABASE_DB_URL }}
```

---

## 7. Code Quality & Security

```yaml
# .github/workflows/security.yml
name: Security Checks

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main, dev]

jobs:
  dependency-check:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Dependency check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          path: '.'
          format: 'HTML'
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: dependency-check-report
          path: reports/

  sast-scan:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: SonarCloud scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

---

## 8. Release & Version Management

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags: ['v*']

jobs:
  create-release:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Create release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
      
      - name: Publish to npm
        run: npm publish
```

---

## 9. Rollback Procedure

### Automatic Rollback

```yaml
jobs:
  deploy-with-rollback:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: vercel deploy --prod
      
      - name: Health check
        run: |
          for i in {1..5}; do
            if curl https://stridealytics.com/health; then
              exit 0
            fi
            sleep 10
          done
          exit 1
      
      - name: Rollback on failure
        if: failure()
        run: vercel rollback
```

---

## 10. Performance Testing

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on:
  schedule:
    - cron: '0 2 * * *'

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v9
        with:
          configPath: './lighthouserc.json'
          uploadArtifacts: true
```

---

## 11. Secrets Management

```bash
# GitHub Secrets (Settings > Secrets)
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
DOCKER_USERNAME
DOCKER_PASSWORD
EAS_TOKEN
SUPABASE_DB_URL
SONAR_TOKEN
SLACK_WEBHOOK
SENTRY_DSN
```

---

## 12. Status Dashboard

```
Pipeline Status:
┌─────────────────────────────────────────┐
│ Frontend  │ ✅ Build │ ✅ Deploy      │
│ Backend   │ ✅ Build │ ✅ Deploy      │
│ Mobile    │ ✅ Build │ ⏳ Deploy       │
│ Database  │ ✅ Migrate              │
│ Overall   │ ✅ Passing              │
└─────────────────────────────────────────┘
```

---

## 13. Best Practices

✅ **DO:**
- Run linting & tests before building
- Use environment-specific configs
- Implement approval gates for production
- Notify team of deployments
- Keep workflows DRY (reusable)
- Cache dependencies
- Parallel jobs when possible
- Monitor pipeline execution

❌ **DON'T:**
- Deploy without tests
- Hardcode secrets
- Run everything sequentially
- Skip security checks
- Forget rollback procedures
- Ignore pipeline failures
- Use old GitHub Actions
- Skip notifications

---

## 14. Monitoring CI/CD

```bash
# View workflow runs
gh run list

# View specific workflow
gh run view <run_id>

# Tail logs
gh run view <run_id> --log
```

---

## Next Steps

- **View Deployment Details?** → [06-DEPLOYMENT-LAYER](./06-DEPLOYMENT-LAYER.md)
- **Scheduler?** → [05-SCHEDULER-LAYER](./05-SCHEDULER-LAYER.md)
- **Check Diagrams?** → [02-SYSTEM-DIAGRAMS](../02-SYSTEM-DIAGRAMS.md)

---

**Version:** A | **Last Updated:** 2026-06-15
