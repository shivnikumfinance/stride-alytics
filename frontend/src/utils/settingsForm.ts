/** Settings form model and validation (mirrors the API rules in `schemas/settings.py`). */

import type { BandCaps, RegimeWeights, UserSettings } from "../types";

export const BANDS = ["A", "B", "C", "D", "E"] as const;
export const WEIGHTS = [
  ["trend", "Trend (SPY vs 50/200-day average)"],
  ["vix", "VIX level"],
  ["iv_rank", "IV rank"],
] as const;

export interface SettingsForm {
  account_size: string;
  base_risk_pct: string;
  growth_risk_pct: string;
  min_equity: string;
  enforce_gate: boolean;
  band_caps: Record<keyof BandCaps, string>;
  regime_weights: Record<keyof RegimeWeights, string>;
}

export function toForm(s: UserSettings): SettingsForm {
  return {
    account_size: String(s.account_size),
    base_risk_pct: String(s.base_risk_pct),
    growth_risk_pct: String(s.growth_risk_pct),
    min_equity: String(s.min_equity),
    enforce_gate: s.enforce_gate,
    band_caps: Object.fromEntries(BANDS.map((b) => [b, String(s.band_caps[b])])) as SettingsForm["band_caps"],
    regime_weights: Object.fromEntries(
      WEIGHTS.map(([k]) => [k, String(s.regime_weights[k])]),
    ) as SettingsForm["regime_weights"],
  };
}

/** Returns an error message, or null when the form is valid. */
export function validateForm(f: SettingsForm): string | null {
  const n = (v: string) => (v.trim() === "" ? NaN : Number(v));
  if (!(n(f.account_size) >= 0)) return "Account size must be 0 or more.";
  if (!(n(f.min_equity) >= 0)) return "Minimum equity must be 0 or more.";
  for (const [label, v] of [
    ["Base risk %", f.base_risk_pct],
    ["Growth risk %", f.growth_risk_pct],
  ] as const) {
    if (!(n(v) > 0 && n(v) <= 10)) return `${label} must be above 0 and at most 10.`;
  }
  for (const b of BANDS) {
    const cap = n(f.band_caps[b]);
    if (!(cap >= 0 && cap <= 100)) return `Band ${b} cap must be between 0 and 100.`;
  }
  const weights = WEIGHTS.map(([k]) => n(f.regime_weights[k]));
  if (weights.some((w) => !(w >= 0)) || weights.reduce((a, b) => a + b, 0) <= 0) {
    return "Regime weights must be 0 or more, and not all zero.";
  }
  return null;
}
