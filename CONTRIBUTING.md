# Development Workflow & Build Checks

## Pre-Commit Hook Setup

To ensure broken code never reaches the repository, we use **husky** pre-commit hooks that automatically run build checks before commits.

The hooks intelligently detect whether you changed frontend or backend files and run the appropriate checks.

### Installation (First Time Only)

```bash
# Run the setup script (installs dependencies and hooks)
bash scripts/setup-dev.sh
```

Or manually:
```bash
# Frontend
cd frontend
npm install
npx husky install

# Backend
cd backend
uv sync
```

### What Happens on Commit

When you run `git commit`:

**If frontend files changed:**
1. 📘 **TypeScript Check** — Validates all type definitions with `npm run type-check`
2. 🔧 **ESLint** — Checks code style and quality with `npm run lint`
3. 📦 **Frontend Build** — Full production build with `npm run build`

**If backend files changed:**
1. 🔧 **Ruff** — Lints code with `uv run ruff check .`
2. 🎨 **Black** — Checks/auto-formats code with `uv run black .`
3. 📘 **MyPy** — Type validation with `uv run mypy app`
4. 🧪 **Pytest** — Runs test suite with `uv run pytest tests`

**Result:**
- ✅ All checks pass → Commit succeeds
- ❌ Any check fails → Commit blocked, fix errors & retry

This prevents broken code, style violations, and test failures from reaching the repository.

---

## Manual Verification Before Committing

Run checks manually anytime without committing:

```bash
# Frontend checks
cd frontend
npm run type-check   # TypeScript validation
npm run lint         # ESLint style checking
npm run build        # Full production build

# Backend checks
cd backend
uv run ruff check .      # Ruff linting
uv run black --check .   # Black formatting check (no changes)
uv run black .           # Auto-format code
uv run mypy app          # MyPy type validation
uv run pytest tests      # Run full test suite
uv run pytest tests -k test_name  # Run specific test
```

---

## GitHub Actions CI/CD

Every push and pull request triggers automated checks via `.github/workflows/build-check.yml`:

**Frontend:**
- Node 18
- TypeScript type checking
- ESLint validation
- Production build

**Backend:**
- Python 3.12
- Ruff linting
- Black format checking
- MyPy type checking
- Pytest test suite

Workflow triggers:
- ✅ Push to `main` or `develop`
- ✅ Every pull request to `main` or `develop`

Check status at: https://github.com/yourorg/stride-alytics/actions

---

## Workflow: Local → Commit → GitHub

```
1. Make code changes (frontend, backend, or both)
   ↓
2. Test locally (optional)
   npm run build         # frontend
   uv run pytest tests   # backend
   ↓
3. Stage changes
   git add .
   ↓
4. Commit (pre-commit hook runs automatically)
   git commit -m "feat: add new feature"
   ↓
5. If checks fail → Fix → Retry commit
   ↓
6. If checks pass → Commit succeeds ✅
   ↓
7. Push to GitHub
   git push origin feature-branch
   ↓
8. GitHub Actions runs CI checks
   ↓
9. Create Pull Request
```

---

## Troubleshooting

**Hook not running?**
```bash
# Reinstall husky
cd frontend
npm install husky --save-dev
npx husky install
```

**Permission denied on pre-commit?**
```bash
chmod +x .husky/pre-commit
```

**Black auto-formatted on commit but commit failed?**
```bash
# Black auto-formats code, so you need to stage the changes
git add .
git commit -m "your message"
```

**Build passes locally but fails on GitHub?**
- Check Node/Python versions match GitHub Actions config
- Ensure `package-lock.json` and `uv.lock` are committed
- Check for environment variable differences

**Want to skip checks (emergency only)?**
```bash
git commit --no-verify -m "emergency fix"
```
⚠️ Not recommended — bypasses all safety checks.
