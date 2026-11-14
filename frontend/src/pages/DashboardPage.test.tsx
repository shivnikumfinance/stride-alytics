import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { calmGate, summary } from "../test/fixtures";
import { renderWithRouter } from "../test/utils";
import { DashboardPage } from "./DashboardPage";

vi.mock("../api/endpoints", () => ({
  dashboardApi: { summary: vi.fn() },
  gateApi: { master: vi.fn(), check: vi.fn() },
}));

import { dashboardApi, gateApi } from "../api/endpoints";

describe("Home hub", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(gateApi.master).mockResolvedValue(calmGate);
    vi.mocked(dashboardApi.summary).mockResolvedValue(summary());
  });

  it("shows the three metric cards", async () => {
    renderWithRouter(<DashboardPage />);
    expect(await screen.findByText("Portfolio Value")).toBeInTheDocument();
    expect(screen.getByText("$99,910.00")).toBeInTheDocument();
    expect(screen.getByText(/Cash available \$94,900\.00/)).toBeInTheDocument();
    expect(screen.getByText("Total P&L (Active)")).toBeInTheDocument();
    expect(screen.getByText(/2 open trades · realised -\$100\.00/)).toBeInTheDocument();
    expect(screen.getByText("Options Buying Power")).toBeInTheDocument();
    expect(screen.getByText(/5% utilised · \$5,000\.00 at risk/)).toBeInTheDocument();
  });

  it("has exactly the four core sections, each linking to its full page", async () => {
    renderWithRouter(<DashboardPage />);
    await screen.findByText("Portfolio Value");
    for (const title of [
      "Exit Alerts & Recommendations",
      "Top Weekly Picks",
      "Active Holdings & Trade Alerts",
      "Strategy Design Matrix",
    ]) {
      expect(screen.getByText(title)).toBeInTheDocument();
    }
    const links = screen.getAllByRole("link", { name: /View full screen/ });
    expect(links.map((l) => l.getAttribute("href"))).toEqual([
      "/exit-alerts",
      "/picks",
      "/active-holdings",
      "/strategy-matrix",
    ]);
  });

  it("summarises alerts, picks, holdings and the regime", async () => {
    renderWithRouter(<DashboardPage />);
    expect(await screen.findByText(/1 critical alert\(s\) need acknowledgement/)).toBeInTheDocument();
    expect(screen.getAllByText(/assignment alarm/).length).toBeGreaterThan(0);
    expect(screen.getByText("82%")).toBeInTheDocument(); // pick confidence
    expect(screen.getByText("NVDA")).toBeInTheDocument();
    expect(screen.getByText("MSFT")).toBeInTheDocument(); // a holding
    expect(screen.getByText(/Base \/ Growth split/)).toHaveTextContent("60 / 40");
    expect(screen.queryByText(/Growth layer is locked/)).not.toBeInTheDocument();
  });

  it("explains empty sections", async () => {
    vi.mocked(dashboardApi.summary).mockResolvedValue(
      summary({
        alerts: { summary: { normal: 0, watch: 0, warning: 0, critical: 0 }, unacknowledged_critical: 0, top: [] },
        holdings: [],
        picks: { week_of: null, top: [] },
        metrics: { ...summary().metrics, open_trades: 0 },
      }),
    );
    renderWithRouter(<DashboardPage />);
    expect(await screen.findByText("No alerts right now.")).toBeInTheDocument();
    expect(screen.getByText(/No picks yet/)).toBeInTheDocument();
    expect(screen.getByText("No open positions.")).toBeInTheDocument();
    expect(screen.queryByText(/need acknowledgement/)).not.toBeInTheDocument();
  });

  it("says when some positions could not be priced and when Growth is locked", async () => {
    vi.mocked(dashboardApi.summary).mockResolvedValue(
      summary({
        metrics: { ...summary().metrics, unrealized_complete: false, utilization_pct: null },
        regime: { score: 30, state: "DEFENSIVE", layer_split: { base: 80, growth: 20 }, growth_locked: true },
      }),
    );
    renderWithRouter(<DashboardPage />);
    expect(await screen.findByText(/some positions could not be priced/)).toBeInTheDocument();
    expect(screen.getByText("Utilisation unavailable")).toBeInTheDocument();
    expect(screen.getByText(/Growth layer is locked/)).toBeInTheDocument();
  });

  it("shows an error, but still the gate, when the summary fails", async () => {
    vi.mocked(dashboardApi.summary).mockRejectedValue(new Error("boom"));
    renderWithRouter(<DashboardPage />);
    expect(await screen.findByText(/Could not load your summary/)).toBeInTheDocument();
    expect(await screen.findByText("CLEAR TO TRADE")).toBeInTheDocument();
  });
});
