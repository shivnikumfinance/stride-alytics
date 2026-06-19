import json
import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(
    title="StrideAlytics Mock API",
    description="Mock backend for the StrideAlytics Options Selling Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load mock data
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "mock_data.json")

def load_data():
    with open(DATA_PATH, "r") as f:
        return json.load(f)

data = load_data()

# ============================================================
# REGIME & MARKET ENDPOINTS
# ============================================================

@app.get("/api/v1/regime")
def get_regime():
    """Get current regime score, components, and history"""
    return {
        "success": True,
        "data": {
            "score": data["regime"]["score"],
            "state": data["regime"]["state"],
            "previous_state": data["regime"]["previous_state"],
            "mood": data["regime"]["mood"],
            "components": data["regime"]["components"],
            "allocation": data["regime"]["allocation"],
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
    }

@app.get("/api/v1/regime/history")
def get_regime_history():
    """Get regime score history"""
    return {
        "success": True,
        "data": data["regime"]["history"]
    }

@app.get("/api/v1/heat-dashboard")
def get_heat_dashboard():
    """Get heat dashboard with risk gauges, volatility, trend, breadth"""
    return {
        "success": True,
        "data": data["heat_dashboard"]
    }

# ============================================================
# MASTER GATE ENDPOINTS
# ============================================================

@app.get("/api/v1/master-gate")
def get_master_gate():
    """Get master gate status (CLEAR TO TRADE / BLOCKED)"""
    return {
        "success": True,
        "data": data["master_gate"]
    }

# ============================================================
# PORTFOLIO ENDPOINTS
# ============================================================

@app.get("/api/v1/portfolio")
def get_portfolio():
    """Get portfolio summary, sector exposure, capital bands"""
    return {
        "success": True,
        "data": data["portfolio"]
    }

@app.get("/api/v1/portfolio/capital-bands")
def get_capital_bands():
    """Get capital band allocation details"""
    return {
        "success": True,
        "data": data["portfolio"]["capital_bands"]
    }

@app.get("/api/v1/portfolio/sector-exposure")
def get_sector_exposure():
    """Get sector exposure breakdown"""
    return {
        "success": True,
        "data": data["portfolio"]["sector_exposure"]
    }

# ============================================================
# TRADES ENDPOINTS
# ============================================================

@app.get("/api/v1/trades/active")
def get_active_trades():
    """Get all active trades"""
    return {
        "success": True,
        "data": data["active_trades"]
    }

@app.get("/api/v1/trades/active/{trade_id}")
def get_active_trade(trade_id: str):
    """Get specific active trade"""
    for trade in data["active_trades"]:
        if trade["id"] == trade_id:
            return {"success": True, "data": trade}
    raise HTTPException(status_code=404, detail="Trade not found")

@app.get("/api/v1/trades/closed")
def get_closed_trades():
    """Get closed trades history"""
    return {
        "success": True,
        "data": data["closed_trades"]
    }

@app.get("/api/v1/trades/exit-alerts")
def get_exit_alerts():
    """Get exit alerts / recommendations"""
    return {
        "success": True,
        "data": data["exit_alerts"]
    }

# ============================================================
# WATCHLIST ENDPOINTS
# ============================================================

@app.get("/api/v1/watchlist")
def get_watchlist():
    """Get default watchlist with symbols and metrics"""
    return {
        "success": True,
        "data": data["watchlist"]["default"]
    }

@app.get("/api/v1/watchlist/{symbol}")
def get_watchlist_symbol(symbol: str):
    """Get specific symbol from watchlist"""
    for s in data["watchlist"]["default"]["symbols"]:
        if s["symbol"] == symbol.upper():
            return {"success": True, "data": s}
    raise HTTPException(status_code=404, detail="Symbol not found in watchlist")

# ============================================================
# OPTION CHAIN ENDPOINTS
# ============================================================

@app.get("/api/v1/option-chain/{symbol}")
def get_option_chain(symbol: str):
    """Get option chain for a symbol"""
    if symbol.upper() == data["option_chain"]["symbol"]:
        return {
            "success": True,
            "data": data["option_chain"]
        }
    # Return a generic chain for any symbol
    return {
        "success": True,
        "data": {
            "symbol": symbol.upper(),
            "price": 150.00,
            "expiry": "2026-07-17",
            "dte": 30,
            "iv": 25.0,
            "calls": [
                {"strike": s, "bid": round(5.0 - (s-148)*0.4, 2), "ask": round(5.2 - (s-148)*0.4, 2),
                 "delta": round(0.5 - (s-148)*0.03, 2), "theta": -0.35, "vega": 0.30, "open_interest": 50000}
                for s in range(145, 156, 1)
            ],
            "puts": [
                {"strike": s, "bid": round(2.0 + (s-148)*0.3, 2), "ask": round(2.2 + (s-148)*0.3, 2),
                 "delta": round(-0.3 - (s-148)*0.03, 2), "theta": 0.40, "vega": 0.35, "open_interest": 60000}
                for s in range(145, 156, 1)
            ]
        }
    }

# ============================================================
# WEEKLY PICKS ENDPOINTS
# ============================================================

@app.get("/api/v1/weekly-picks")
def get_weekly_picks():
    """Get weekly trade recommendations ranked by EV score"""
    return {
        "success": True,
        "data": data["weekly_picks"]
    }

# ============================================================
# POSITION SIZING ENDPOINTS
# ============================================================

@app.get("/api/v1/sizing-calculator")
def get_sizing_defaults():
    """Get position sizing calculator defaults"""
    return {
        "success": True,
        "data": data["sizing_calculator"]
    }

@app.post("/api/v1/sizing-calculator/calculate")
def calculate_position_size(
    portfolio_value: float = Query(87500),
    risk_percent: float = Query(1.2),
    credit: float = Query(1.50),
    regime: str = Query("NORMAL"),
    layer: str = Query("Base")
):
    """Calculate position size based on inputs"""
    risk_amount = portfolio_value * (risk_percent / 100)
    multiplier = data["sizing_calculator"]["regime_multipliers"].get(regime, 1.0)
    adjusted_risk = risk_amount * multiplier
    
    # Contract quantity = risk / (credit * 100)
    credit_total = credit * 100
    contracts = int(adjusted_risk / credit_total) if credit_total > 0 else 0
    total_risk = contracts * credit_total
    notional_exposure = total_risk * 100
    
    return {
        "success": True,
        "data": {
            "portfolio_value": portfolio_value,
            "risk_percent": risk_percent,
            "layer": layer,
            "regime": regime,
            "regime_multiplier": multiplier,
            "risk_amount": round(adjusted_risk, 2),
            "credit_received": credit,
            "contracts": max(contracts, 1),
            "total_risk": round(total_risk, 2),
            "notional_exposure": notional_exposure,
            "max_loss": round(contracts * credit_total, 2),
            "portfolio_percent": round((total_risk / portfolio_value) * 100, 2)
        }
    }

# ============================================================
# SCENARIO SIMULATION ENDPOINTS
# ============================================================

@app.get("/api/v1/scenarios")
def get_scenarios():
    """Get scenario stress test simulations"""
    return {
        "success": True,
        "data": data["scenario_simulations"]
    }

# ============================================================
# SIGNAL LOG ENDPOINTS
# ============================================================

@app.get("/api/v1/signal-log")
def get_signal_log():
    """Get signal log (rule-based regime shifts, DNT changes, etc.)"""
    return {
        "success": True,
        "data": data["signal_log"]
    }

# ============================================================
# SETTINGS ENDPOINTS
# ============================================================

@app.get("/api/v1/settings")
def get_settings():
    """Get all settings"""
    return {
        "success": True,
        "data": data["settings"]
    }

@app.get("/api/v1/settings/account")
def get_account_settings():
    """Get account settings"""
    return {
        "success": True,
        "data": data["settings"]["account"]
    }

@app.get("/api/v1/settings/risk")
def get_risk_settings():
    """Get risk defaults"""
    return {
        "success": True,
        "data": data["settings"]["risk_defaults"]
    }

@app.get("/api/v1/settings/dnt")
def get_dnt_settings():
    """Get DNT settings"""
    return {
        "success": True,
        "data": data["settings"]["dnt_settings"]
    }

@app.get("/api/v1/settings/preferences")
def get_preferences():
    """Get user preferences"""
    return {
        "success": True,
        "data": data["settings"]["preferences"]
    }

# ============================================================
# USER & AUTH ENDPOINTS
# ============================================================

@app.get("/api/v1/auth/me")
def get_current_user():
    """Get current authenticated user"""
    return {
        "success": True,
        "data": data["user"]
    }

@app.post("/api/v1/auth/login")
def login():
    """Mock login - always succeeds"""
    return {
        "success": True,
        "data": {
            "token": "mock_jwt_token_eyJhbGciOiJIUzI1NiJ9...",
            "user": data["user"],
            "expires_in": 3600
        }
    }

# ============================================================
# ADMIN ENDPOINTS
# ============================================================

@app.get("/api/v1/admin/users")
def get_admin_users():
    """Get all users (admin only)"""
    return {
        "success": True,
        "data": data["admin"]["users"]
    }

@app.get("/api/v1/admin/health")
def get_system_health():
    """Get system health status"""
    return {
        "success": True,
        "data": data["admin"]["system_health"]
    }

@app.get("/api/v1/admin/audit-log")
def get_audit_log():
    """Get admin audit log"""
    return {
        "success": True,
        "data": data["admin"]["audit_log"]
    }

# ============================================================
# DASHBOARD AGGREGATE ENDPOINT
# ============================================================

@app.get("/api/v1/dashboard")
def get_dashboard():
    """Get all dashboard data in one call"""
    return {
        "success": True,
        "data": {
            "regime": {
                "score": data["regime"]["score"],
                "state": data["regime"]["state"],
                "mood": data["regime"]["mood"]
            },
            "master_gate": data["master_gate"]["status"],
            "portfolio_summary": {
                "total_value": data["portfolio"]["total_value"],
                "margin_used": data["portfolio"]["margin_used"],
                "net_delta": data["portfolio"]["net_delta"],
                "total_risk": data["portfolio"]["total_risk"],
                "active_trades": len(data["active_trades"]),
                "total_pnl": sum(t["pnl"] for t in data["active_trades"])
            },
            "heat_dashboard": {
                "vix": data["heat_dashboard"]["volatility"]["vix"],
                "spy_price": data["heat_dashboard"]["trend"]["spy_price"],
                "iv_rank": data["heat_dashboard"]["volatility"]["iv_rank_overall"]
            },
            "top_picks": data["weekly_picks"][:3],
            "exit_alerts": data["exit_alerts"]
        }
    }

# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0", "timestamp": datetime.utcnow().isoformat() + "Z"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)