# Alpha — Full Documentation

> See [docs/TECHNICAL/ALPHA.md](../docs/TECHNICAL/ALPHA.md) for complete documentation.

## Folder Layout

```
alpha/
│── README.md
│── Alpha.md
│── pyproject.toml
│── .env.example
│── raw_screener.csv
│── service_account.example.json
│── Dockerfile
│
├── app/
│   │── main.py
│   │── streamlit_app.py
│   │── supabase_schema.sql
│   │── make_zip.py
│   │
│   ├── utils/
│   │   └── load_data.py
│   │
│   ├── screener/
│   │   ├── compute_option_score.py
│   │   ├── apply_filters.py
│   │   ├── weekly_watchlist.py
│   │   └── band_pipeline.py
│   │
│   ├── database/
│   │   ├── supabase_client.py
│   │   └── insert_daily.py
│   │
│   ├── sheets/
│   │   └── push_to_sheets.py
│   │
│   └── data_sources/
│       ├── polygon.py
│       ├── yfinance_data.py
│       └── fmp_fundamentals.py
│
└── .github/
    └── workflows/
        └── daily_run.yml
```

## Quick Reference

- **Pipeline:** `python app/main.py`
- **Dashboard:** `streamlit run app/streamlit_app.py`
- **Schema:** Run `app/supabase_schema.sql` in Supabase SQL editor
- **Package zip:** `python app/make_zip.py`