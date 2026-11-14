import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { calmGate, SUMMARY_COUNTS } from "../test/fixtures";
import { renderWithRouter } from "../test/utils";
import { HeatDashboardPage } from "./HeatDashboardPage";

vi.mock("../api/endpoints", () => ({
  analyticsApi: { risk: vi.fn() },
  portfolioApi: { bands: vi.fn() },
  alertsApi: { exits: vi.fn() },
  gateApi: { master: vi.fn() },
}));

import { alertsApi, analyticsApi, gateApi, portfolioApi } from "../api/endpoints";

const risk = (over = {}) => ({
  equity: 100000,
  capital_at_risk: 20000,
  margin_pct: 20,
  net_delta: 45,
  net_delta_dollars: 9000,
  net_delta_pct: 9,
  unpriced_positions: 0,
  open_positions: 3,
  sectors: [{ sector: "Technology", capital_at_risk: 15000, pct_of_equity: 15, pct_of_risk: 75 }],
  breaches: [],
  limits: { capital_at_risk_pct: 50, sector_risk_pct: 25, net_delta_pct: 100 },
  regime_score: 62,
  regime_state: "NORMAL",
  ...over,
});

describe("Heat Dashboard page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(gateApi.master).mockResolvedValue(calmGate);
    vi.mocked(analyticsApi.risk).mockResolvedValue(risk() as never);
    vi.mocked(portfolioApi.bands).mockResolvedValue([
      { band: "A", exposure: 5000, exposure_pct: 5, cap_pct: 30, status: "ok" },
      { band: "B", exposure: 21000, exposure_pct: 21, cap_pct: 25, status: "near" },
    ] as never);
    vi.mocked(alertsApi.exits).mockResolvedValue({
      alerts: [],
      summary: SUMMARY_COUNTS,
      unacknowledged_critical: 0,
      open_positions: 3,
    } as never);
  });

  it("shows risk gauges against their limits", async () => {
    renderWithRouter(<HeatDashboardPage />);
    const margin = await screen.findByRole("meter", { name: "Margin (capital at risk)" });
    expect(margin).toHaveAttribute("aria-valuenow", "20");
    expect(margin).toHaveAttribute("aria-valuemax", "50");
    expect(margin).toHaveAttribute("aria-valuetext", "20%, within the limit");
    expect(screen.getByRole("meter", { name: "Net delta exposure" })).toHaveAttribute("aria-valuenow", "9");
    expect(screen.getByText(/\$20,000\.00 at risk on 3 open position/)).toBeInTheDocument();
  });

  it("describes a gauge that is near or over its limit in words, not only colour", async () => {
    vi.mocked(analyticsApi.risk).mockResolvedValue(risk({ margin_pct: 42 }) as never);
    const { unmount } = renderWithRouter(<HeatDashboardPage />);
    expect(await screen.findByRole("meter", { name: "Margin (capital at risk)" })).toHaveAttribute(
      "aria-valuetext",
      "42%, near the limit",
    );
    unmount();
    vi.mocked(analyticsApi.risk).mockResolvedValue(risk({ margin_pct: 55 }) as never);
    renderWithRouter(<HeatDashboardPage />);
    expect(await screen.findByRole("meter", { name: "Margin (capital at risk)" })).toHaveAttribute(
      "aria-valuetext",
      "55%, at or over the limit",
    );
  });

  it("lists limit breaches with their rule ids", async () => {
    vi.mocked(analyticsApi.risk).mockResolvedValue(
      risk({ breaches: [{ rule_id: "BR-081", code: "total_risk", message: "Capital at risk is 55% of equity (limit 50%)." }] }) as never,
    );
    renderWithRouter(<HeatDashboardPage />);
    expect(await screen.findByText(/Capital at risk is 55% of equity/)).toBeInTheDocument();
    expect(screen.getByText("BR-081")).toBeInTheDocument();
  });

  it("says when positions could not be priced", async () => {
    vi.mocked(analyticsApi.risk).mockResolvedValue(risk({ unpriced_positions: 2 }) as never);
    renderWithRouter(<HeatDashboardPage />);
    expect(await screen.findByText(/2 position\(s\) could not be priced/)).toBeInTheDocument();
  });

  it("shows band usage and position health", async () => {
    renderWithRouter(<HeatDashboardPage />);
    expect(await screen.findByText(/21% of 25% cap/)).toBeInTheDocument();
    expect(screen.getByText("near")).toBeInTheDocument();
    expect(await screen.findByText("Position health")).toBeInTheDocument();
  });

  it("handles an empty portfolio", async () => {
    vi.mocked(analyticsApi.risk).mockResolvedValue(
      risk({ sectors: [], open_positions: 0, capital_at_risk: 0, margin_pct: 0, net_delta_pct: 0 }) as never,
    );
    renderWithRouter(<HeatDashboardPage />);
    expect(await screen.findByText("No open positions, so no exposure.")).toBeInTheDocument();
  });

  it("shows an error when risk cannot load, but the rest of the page still renders", async () => {
    vi.mocked(analyticsApi.risk).mockRejectedValue(new Error("boom"));
    renderWithRouter(<HeatDashboardPage />);
    expect(await screen.findByText("Could not load the portfolio risk. Try refreshing.")).toBeInTheDocument();
    expect(await screen.findByText("Capital bands")).toBeInTheDocument();
  });
});
