/** Mirrors `backend/app/api/v1/schemas/portfolio.py`. */

export interface PortfolioSummary {
  portfolio_id: string;
  name: string;
  total_trades: number;
  open_trades: number;
  closed_trades: number;
  total_pnl: number;
  win_rate: number;
  winners: number;
  losers: number;
}

export interface PortfolioListItem {
  id: string;
  name: string;
  description?: string | null;
}

export interface PortfolioCreate {
  name: string;
  description?: string | null;
}
