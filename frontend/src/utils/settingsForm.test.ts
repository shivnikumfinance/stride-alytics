import { describe, expect, it } from "vitest";

import type { UserSettings } from "../types";
import { toForm, validateForm } from "./settingsForm";

const settings: UserSettings = {
  notify_weekly_picks: true,
  notify_market_regime: false,
  default_symbol: "SPY",
  theme: "light",
  screener_preset: {},
  account_size: 100000,
  base_risk_pct: 1.25,
  growth_risk_pct: 2.5,
  min_equity: 0,
  band_caps: { A: 30, B: 25, C: 20, D: 15, E: 10 },
  regime_weights: { trend: 40, vix: 30, iv_rank: 30 },
  widget_toggles: {},
  enforce_gate: true,
  disclaimer_accepted_at: null,
};

describe("settings form", () => {
  it("accepts the defaults", () => {
    expect(validateForm(toForm(settings))).toBeNull();
  });

  it.each([
    ["account_size", "-5", /Account size/],
    ["account_size", "", /Account size/],
    ["min_equity", "-1", /Minimum equity/],
    ["base_risk_pct", "0", /Base risk/],
    ["growth_risk_pct", "11", /Growth risk/],
  ])("rejects %s = %j", (field, value, message) => {
    const form = { ...toForm(settings), [field]: value };
    expect(validateForm(form)).toMatch(message);
  });

  it("rejects a band cap outside 0-100", () => {
    const form = toForm(settings);
    form.band_caps.C = "120";
    expect(validateForm(form)).toMatch(/Band C/);
  });

  it("rejects regime weights that are negative or all zero", () => {
    const zero = toForm(settings);
    zero.regime_weights = { trend: "0", vix: "0", iv_rank: "0" };
    expect(validateForm(zero)).toMatch(/Regime weights/);

    const negative = toForm(settings);
    negative.regime_weights.vix = "-1";
    expect(validateForm(negative)).toMatch(/Regime weights/);
  });
});
