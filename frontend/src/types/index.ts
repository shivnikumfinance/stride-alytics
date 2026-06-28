/**
 * Barrel for shared TypeScript types.
 *
 * Types live in per‑domain files (auth.ts, greeks.ts, screener.ts, …) so they
 * can be imported directly when you only need a slice:
 *
 *   import type { GreeksInputs } from "../types/greeks";
 *
 * This file re‑exports everything for callers that prefer a single import:
 *
 *   import type { LoginRequest, ScreenerFilters } from "../types";
 *
 * These types mirror `backend/app/api/v1/schemas/*` and (where applicable)
 * `shared/types/index.ts`.
 */

export * from "./common";
export * from "./auth";
export * from "./greeks";
export * from "./screener";
export * from "./regime";
export * from "./portfolio";
export * from "./trades";
export * from "./market";
