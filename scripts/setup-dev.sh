#!/bin/bash
# Setup development environment with pre-commit hooks for both frontend and backend

echo "🚀 Setting up StrideAlytics development environment..."

# Frontend setup
echo ""
echo "📦 Installing frontend dependencies..."
cd frontend
npm install

echo "🔗 Installing husky pre-commit hooks..."
npx husky install

cd ..

# Backend setup
echo ""
echo "📦 Installing backend dependencies..."
cd backend
uv sync

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Pre-commit checks now active for:"
echo ""
echo "   FRONTEND:"
echo "   ✓ TypeScript type validation"
echo "   ✓ ESLint code quality checks"
echo "   ✓ Production build verification"
echo ""
echo "   BACKEND:"
echo "   ✓ Ruff linting (style & quality)"
echo "   ✓ Black code formatting"
echo "   ✓ MyPy type checking"
echo "   ✓ Pytest test suite"
echo ""
echo "🎯 Workflow:"
echo "   1. Make your changes (frontend, backend, or both)"
echo "   2. Run: git add ."
echo "   3. Run: git commit -m 'your message'"
echo "   4. Pre-commit hooks auto-run relevant checks"
echo "   5. Commit succeeds ✅ or blocked ❌ if checks fail"
echo ""
echo "💡 Run checks manually anytime:"
echo ""
echo "   FRONTEND:"
echo "   npm run type-check    # TypeScript validation"
echo "   npm run lint          # ESLint"
echo "   npm run build         # Full build"
echo ""
echo "   BACKEND:"
echo "   uv run ruff check .       # Ruff linting"
echo "   uv run black --check .    # Black format check"
echo "   uv run black .            # Auto-format code"
echo "   uv run mypy app           # MyPy type checking"
echo "   uv run pytest tests       # Run tests"
