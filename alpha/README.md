# StrideAlytics Alpha — Option Trading System

Daily option screening pipeline: loads raw screener data → scores options (0–9) → assigns bands (A–E) → applies daily filters → generates weekly watchlist → inserts into Supabase → pushes to Google Sheets.

Includes a Streamlit dashboard for real-time data visualization.

## Quick Start (Local Development)

```bash
cd alpha
cp .env.example .env   # fill in your keys (optional for core functionality)
uv sync
uv run test_local.py   # Test core pipeline without external services
```

For full pipeline with Supabase + Google Sheets integration:
```bash
# Fill in .env with your credentials, then:
uv run python app/main.py
streamlit run app/streamlit_app.py
```

## Structure

```
alpha/
├── app/                # Core application code
├── .env.example        # Environment variable template
├── pyproject.toml      # Project config (uv/pip)
├── Dockerfile          # Containerized run
└── README.md           # This file
```

See [Alpha.md](./Alpha.md) for full documentation.