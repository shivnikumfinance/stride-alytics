FROM python:3.12-slim

# Install uv (official Astral image)
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /uvx /bin/

WORKDIR /app

# Copy dependency manifests first for Docker layer caching
COPY pyproject.toml uv.lock ./

# Copy the local ta-lib wheel(s) — uv.lock references them as
# `wheels/ta_lib-0.6.5-*.whl` (relative to pyproject.toml). Without this
# COPY the lockfile path resolves to nothing and `uv sync --frozen`
# fails on Linux with "distribution not found".
COPY wheels/ ./wheels/

# Sync exact locked dependencies into the system Python (no dev, no project)
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application
COPY . .

# Install the project itself
RUN uv sync --frozen --no-dev

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
