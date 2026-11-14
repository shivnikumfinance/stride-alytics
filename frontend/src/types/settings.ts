/** Mirrors `backend/app/api/v1/schemas/settings.py`. */

export type BandCaps = Record<"A" | "B" | "C" | "D" | "E", number>;
export type RegimeWeights = Record<"trend" | "vix" | "iv_rank", number>;

export interface UserSettings {
  notify_weekly_picks: boolean;
  notify_market_regime: boolean;
  default_symbol: string;
  theme: "light" | "dark" | "system";
  screener_preset: Record<string, unknown>;
  account_size: number;
  base_risk_pct: number;
  growth_risk_pct: number;
  min_equity: number;
  band_caps: BandCaps;
  regime_weights: RegimeWeights;
  widget_toggles: Record<string, boolean>;
  enforce_gate: boolean;
  disclaimer_accepted_at: string | null;
}

export type SettingsUpdate = Partial<Omit<UserSettings, "disclaimer_accepted_at">>;
