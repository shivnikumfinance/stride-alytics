/**
 * Market data types.
 *
 * Wire shape mirrors ``backend/app/api/v1/schemas/market.py`` (Pydantic).
 * ``TickerData`` adds a client‑side ``timestamp`` that the backend never
 * sends — the service layer stamps it after a successful fetch.
 *
 * Backend resource: GET /api/v1/market/tickers
 * Frontend consumer: src/api/services/ticker.service.ts
 */

/** Exact wire shape returned by `/market/tickers` for one symbol. */
export interface RawTicker {
  symbol: string;
  price: string;
  change: string;
  changePercent: string;
}

/** Exact wire envelope: `{ success: true, data: { SYM: RawTicker } }`. */
export interface TickerPayload {
  success: boolean;
  data: Record<string, RawTicker>;
}

/** Client‑side view: same as RawTicker plus a ``timestamp`` set by the service. */
export interface TickerData extends RawTicker {
  timestamp: Date;
}
