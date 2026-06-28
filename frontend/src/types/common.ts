/** Shared enums + cross‑cutting API envelope. */

export type SubscriptionPlan = "free" | "pro";
export type OptionType = "call" | "put";
export type TradeType = "call" | "put" | "stock";
export type Direction = "long" | "short";
export type Regime = "bull" | "bear" | "ranging";

export interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  error?: { type: string; status: number; message: string; details?: unknown };
}
