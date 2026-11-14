/** Mirrors the append-only log endpoints (`backend/app/api/v1/endpoints/logs.py`). */

export interface SignalLogEntry {
  id: string;
  occurred_at: string;
  kind: string;
  symbol: string | null;
  rule_id: string | null;
  decision: "allowed" | "blocked" | "info";
  message: string | null;
  details: Record<string, unknown>;
}

export interface AuditLogEntry {
  id: string;
  occurred_at: string;
  action: string;
  entity: string;
  entity_id: string | null;
  before: Record<string, unknown> | null;
  after: Record<string, unknown> | null;
}

export interface LogPage<T> {
  success: boolean;
  data: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface LogFilters {
  symbol?: string;
  rule_id?: string;
  decision?: string;
  entity?: string;
  action?: string;
  limit?: number;
  offset?: number;
}
