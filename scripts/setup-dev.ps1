# Setup development environment with pre-commit hooks for both frontend and backend
# Run from project root: .\scripts\setup-dev.ps1

Write-Host "🚀 Setting up StrideAlytics development environment..." -ForegroundColor Green
Write-Host ""

# Frontend setup
Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Cyan
Push-Location frontend
npm install

Write-Host "🔗 Installing husky pre-commit hooks..." -ForegroundColor Cyan
npx husky install

Pop-Location

# Backend setup
Write-Host ""
Write-Host "📦 Installing backend dependencies..." -ForegroundColor Cyan
Push-Location backend
uv sync

Pop-Location

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Pre-commit checks now active for:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   FRONTEND:" -ForegroundColor Cyan
Write-Host "   ✓ TypeScript type validation"
Write-Host "   ✓ ESLint code quality checks"
Write-Host "   ✓ Production build verification"
Write-Host ""
Write-Host "   BACKEND:" -ForegroundColor Cyan
Write-Host "   ✓ Ruff linting (style & quality)"
Write-Host "   ✓ Black code formatting"
Write-Host "   ✓ MyPy type checking"
Write-Host "   ✓ Pytest test suite"
Write-Host ""
Write-Host "🎯 Workflow:" -ForegroundColor Yellow
Write-Host "   1. Make your changes (frontend, backend, or both)"
Write-Host "   2. Run: git add ."
Write-Host "   3. Run: git commit -m 'your message'"
Write-Host "   4. Pre-commit hooks auto-run relevant checks"
Write-Host "   5. Commit succeeds ✅ or blocked ❌ if checks fail"
Write-Host ""
Write-Host "💡 Run checks manually anytime:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   FRONTEND:" -ForegroundColor Cyan
Write-Host "   npm run type-check    # TypeScript validation"
Write-Host "   npm run lint          # ESLint"
Write-Host "   npm run build         # Full build"
Write-Host ""
Write-Host "   BACKEND:" -ForegroundColor Cyan
Write-Host "   uv run ruff check .       # Ruff linting"
Write-Host "   uv run black --check .    # Black format check"
Write-Host "   uv run black .            # Auto-format code"
Write-Host "   uv run mypy app           # MyPy type checking"
Write-Host "   uv run pytest tests       # Run tests"
