/** Mirrors the watchlist endpoints (`backend/app/api/v1/endpoints/watchlists.py`). */

export interface Watchlist {
  id: string;
  name: string;
  symbols: string[];
  created_at: string | null;
}
