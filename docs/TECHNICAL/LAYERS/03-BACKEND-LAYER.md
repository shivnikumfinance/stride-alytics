# StrideAlytics — Backend Layer

**FastAPI Python backend API architecture**

---

## Overview

The **Backend Layer** provides the core REST API for StrideAlytics, handling business logic, data aggregation, calculations, and integrations with external services.

**Key Characteristics:**
- ✅ RESTful API design
- ✅ Async/await for performance
- ✅ Type validation with Pydantic
- ✅ JWT-based authentication
- ✅ Structured logging
- ✅ Error handling & middleware
- ✅ Rate limiting & caching
- ✅ Production-ready deployment

---

## 1. Technology Stack

| Tool | Purpose | Version |
|------|---------|---------|
| **FastAPI** | Web framework | 0.100+ |
| **Uvicorn** | ASGI server | Latest |
| **Pydantic** | Data validation | v2 |
| **Supabase Python** | Database client | Latest |
| **python-jose** | JWT handling | Latest |
| **Pandas** | Data processing | Latest |
| **yfinance** | Market data | Latest |
| **pytest** | Testing | Latest |
| **Docker** | Containerization | Latest |

---

## 2. Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # Configuration
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py              # Main router
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py          # V1 routes
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py        # Auth endpoints
│   │   │   │   ├── screener.py    # Screener endpoints
│   │   │   │   ├── greeks.py      # Greeks endpoints
│   │   │   │   ├── regime.py      # Regime endpoints
│   │   │   │   ├── portfolio.py   # Portfolio endpoints
│   │   │   │   └── health.py      # Health checks
│   │   │   └── schemas/
│   │   │       ├── auth.py
│   │   │       ├── screener.py
│   │   │       └── portfolio.py
│   │   └── middleware/
│   │       ├── auth.py            # JWT middleware
│   │       ├── logging.py         # Request logging
│   │       └── error_handler.py   # Error handling
│   │
│   ├── services/                  # Business logic
│   │   ├── screener.py
│   │   ├── greeks.py
│   │   ├── regime.py
│   │   ├── data_fetch.py
│   │   └── auth.py
│   │
│   ├── database/
│   │   ├── client.py              # Supabase client
│   │   ├── queries/
│   │   │   ├── user.py
│   │   │   ├── portfolio.py
│   │   │   └── options.py
│   │   └── migrations/
│   │
│   └── utils/
│       ├── logger.py
│       ├── validators.py
│       └── helpers.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 3. FastAPI Application Setup

### Main Application

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.api.middleware.error_handler import global_exception_handler
from app.api.middleware.auth import AuthMiddleware
from app.config import settings

app = FastAPI(
    title="StrideAlytics API",
    description="Multi-platform analytics API",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(AuthMiddleware)

# Global exception handlers
app.add_exception_handler(Exception, global_exception_handler)

# Include routers
app.include_router(router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok"}
```

### Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "StrideAlytics"
    
    # Database
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Auth
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "https://stridealytics.vercel.app"]
    
    # External APIs
    YFINANCE_API_URL: str = "https://query1.finance.yahoo.com"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 4. API Endpoints

### Authentication Endpoints

```python
# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.schemas.auth import LoginRequest, TokenResponse
from app.services.auth import authenticate_user, create_access_token

router = APIRouter(tags=["auth"], prefix="/auth")

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """Login user and return JWT token"""
    user = await authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, token_type="bearer")

@router.post("/signup", response_model=TokenResponse)
async def signup(data: SignupRequest):
    """Create new user account"""
    user = await create_user(data.email, data.password)
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, token_type="bearer")
```

### Screener Endpoints

```python
# app/api/v1/endpoints/screener.py
from fastapi import APIRouter, Depends, Query
from app.api.v1.schemas.screener import ScreenerFilter, ScreenerResponse
from app.services.screener import filter_options
from app.api.middleware.auth import get_current_user

router = APIRouter(tags=["screener"], prefix="/screener")

@router.get("/", response_model=ScreenerResponse)
async def get_screener_results(
    filters: ScreenerFilter = Depends(),
    current_user = Depends(get_current_user),
):
    """Get filtered options based on criteria"""
    results = await filter_options(filters, current_user.id)
    return ScreenerResponse(data=results, total=len(results))

@router.get("/{option_id}")
async def get_option_detail(
    option_id: str,
    current_user = Depends(get_current_user),
):
    """Get detailed information about an option"""
    option = await get_option_by_id(option_id)
    return option
```

### Greeks Endpoints

```python
# app/api/v1/endpoints/greeks.py
from fastapi import APIRouter, Depends
from app.api.v1.schemas.greeks import GreeksInput, GreeksOutput
from app.services.greeks import calculate_greeks
from app.api.middleware.auth import get_current_user

router = APIRouter(tags=["greeks"], prefix="/greeks")

@router.post("/calculate", response_model=GreeksOutput)
async def calculate(
    inputs: GreeksInput,
    current_user = Depends(get_current_user),
):
    """Calculate option Greeks"""
    result = await calculate_greeks(inputs)
    return result

@router.get("/surface/{symbol}")
async def get_iv_surface(
    symbol: str,
    current_user = Depends(get_current_user),
):
    """Get IV surface for symbol"""
    surface = await get_iv_surface_data(symbol)
    return surface
```

---

## 5. Services (Business Logic)

### Screener Service

```python
# app/services/screener.py
from app.database.client import supabase
from app.external.yfinance import fetch_market_data

async def filter_options(filters, user_id):
    """Apply filters and return matching options"""
    query = supabase.table("options").select("*")
    
    # Apply filters
    if filters.symbol:
        query = query.eq("symbol", filters.symbol)
    if filters.min_price:
        query = query.gte("price", filters.min_price)
    if filters.max_price:
        query = query.lte("price", filters.max_price)
    
    result = query.execute()
    return result.data

async def get_option_by_id(option_id):
    """Fetch option details from database"""
    result = supabase.table("options").select("*").eq("id", option_id).execute()
    return result.data[0] if result.data else None
```

### Greeks Service

```python
# app/services/greeks.py
from scipy.stats import norm
import math

async def calculate_greeks(inputs):
    """Calculate option Greeks using Black-Scholes"""
    S = inputs.spot_price
    K = inputs.strike
    T = inputs.time_to_expiry / 365
    r = inputs.risk_free_rate
    sigma = inputs.volatility
    
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    delta = norm.cdf(d1) if inputs.option_type == "call" else norm.cdf(d1) - 1
    gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
    vega = S * norm.pdf(d1) * math.sqrt(T) / 100
    theta = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T)) - r * K * math.exp(-r * T) * norm.cdf(d2)) / 365
    
    return {
        "delta": delta,
        "gamma": gamma,
        "vega": vega,
        "theta": theta,
    }
```

---

## 6. Schemas (Request/Response)

### Pydantic Models

```python
# app/api/v1/schemas/auth.py
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: str

# app/api/v1/schemas/screener.py
from pydantic import BaseModel
from typing import Optional

class ScreenerFilter(BaseModel):
    symbol: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    limit: int = 50
    offset: int = 0

class ScreenerResponse(BaseModel):
    data: list
    total: int
```

---

## 7. Authentication & Authorization

### JWT Middleware

```python
# app/api/middleware/auth.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from app.services.auth import verify_token

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)):
    token = credentials.credentials
    try:
        user_id = verify_token(token)
        return {"id": user_id}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### JWT Token Management

```python
# app/services/auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.config import settings

def create_access_token(user_id: str):
    expires = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub": user_id, "exp": expires}
    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
```

---

## 8. Database Access

### Supabase Client

```python
# app/database/client.py
from supabase import create_client, Client
from app.config import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

async def get_user(user_id: str):
    result = supabase.table("users").select("*").eq("id", user_id).execute()
    return result.data[0] if result.data else None
```

### Query Functions

```python
# app/database/queries/portfolio.py
from app.database.client import supabase

async def get_user_portfolio(user_id: str):
    result = supabase.table("portfolios").select("*").eq("user_id", user_id).execute()
    return result.data

async def create_portfolio(user_id: str, name: str):
    data = {"user_id": user_id, "name": name}
    result = supabase.table("portfolios").insert(data).execute()
    return result.data[0]
```

---

## 9. Error Handling

### Global Exception Handler

```python
# app/api/middleware/error_handler.py
from fastapi import Request
from fastapi.responses import JSONResponse
from app.utils.logger import logger

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred",
        },
    )
```

---

## 10. Testing

### Unit Tests

```python
# tests/unit/test_greeks.py
import pytest
from app.services.greeks import calculate_greeks

@pytest.mark.asyncio
async def test_calculate_greeks():
    inputs = {
        "spot_price": 100,
        "strike": 100,
        "time_to_expiry": 30,
        "risk_free_rate": 0.05,
        "volatility": 0.2,
        "option_type": "call",
    }
    result = await calculate_greeks(inputs)
    assert "delta" in result
    assert "gamma" in result
```

### Integration Tests

```python
# tests/integration/test_screener_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_screener_endpoint():
    response = client.get(
        "/api/v1/screener",
        headers={"Authorization": "Bearer fake_token"},
    )
    assert response.status_code == 401
```

---

## 11. Logging & Monitoring

### Structured Logging

```python
# app/utils/logger.py
import structlog

logger = structlog.get_logger()

def log_request(method, path, status_code):
    logger.info("http_request", method=method, path=path, status_code=status_code)
```

---

## 12. Performance

### Caching Example

```python
# app/utils/cache.py
from functools import lru_cache

@lru_cache(maxsize=128)
async def get_cached_symbol_data(symbol: str):
    """Cached market data retrieval"""
    return await fetch_from_yfinance(symbol)
```

---

## 13. Deployment

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
# .env
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
JWT_SECRET=your_secret
```

---

## 14. Best Practices

✅ **DO:**
- Use async/await for I/O operations
- Validate input with Pydantic
- Implement proper error handling
- Use dependency injection
- Write unit tests
- Log important events
- Document endpoints with docstrings

❌ **DON'T:**
- Hardcode configuration
- Ignore type hints
- Block event loop with sync operations
- Store secrets in code
- Skip input validation
- Mix business logic with endpoints

---

## Next Steps

- **View Diagrams?** → [02-SYSTEM-DIAGRAMS](../02-SYSTEM-DIAGRAMS.md)
- **Database Layer?** → [04-DATABASE-LAYER](./04-DATABASE-LAYER.md)
- **Deployment?** → [06-DEPLOYMENT-LAYER](./06-DEPLOYMENT-LAYER.md)

---

**Version:** A | **Last Updated:** 2026-06-15
