import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithClient } from "../test/utils";
import { ScenariosPage } from "./ScenariosPage";

vi.mock("../api/endpoints", () => ({
  analyticsApi: { runScenario: vi.fn(), scenarios: vi.fn(), saveScenario: vi.fn(), deleteScenario: vi.fn() },
}));

import { analyticsApi } from "../api/endpoints";

const position = (over = {}) => ({
  trade_id: "t1",
  symbol: "AAPL",
  trade_type: "put",
  direction: "short",
  quantity: 1,
  priced: true,
  current_pnl: 10,
  scenario_pnl: -190,
  change: -200,
  ...over,
});

const result = (over = {}) => ({
  shock: { spot_pct: -10, iv_shift: 0.05, days_forward: 0 },
  positions: [position()],
  total_change: -200,
  total_scenario_pnl: -190,
  priced: 1,
  unpriced: 0,
  ladder: [
    { spot_pct: -10, total_change: -200 },
    { spot_pct: 0, total_change: 0 },
    { spot_pct: 10, total_change: 40 },
  ],
  ...over,
});

const saved = { id: "s1", name: "Crash", params: { spot_pct: -20, iv_shift: 0.2, days_forward: 0 }, created_at: null };

describe("Scenarios page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(analyticsApi.scenarios).mockResolvedValue([]);
    vi.mocked(analyticsApi.runScenario).mockResolvedValue(result() as never);
  });

  it("runs the entered scenario (volatility points are sent as a fraction)", async () => {
    renderWithClient(<ScenariosPage />);
    await userEvent.click(screen.getByRole("button", { name: "Run scenario" }));
    await waitFor(() =>
      expect(analyticsApi.runScenario).toHaveBeenCalledWith({ spot_pct: -10, iv_shift: 0.05, days_forward: 0 }),
    );
    expect(await screen.findByText(/Total P&L change across 1 priced position/)).toBeInTheDocument();
    const table = screen.getByRole("table", { name: "" });
    expect(within(table).getByText("AAPL short put")).toBeInTheDocument();
  });

  it("lists positions it could not price and leaves them out of the totals", async () => {
    vi.mocked(analyticsApi.runScenario).mockResolvedValue(
      result({
        positions: [position(), position({ trade_id: "t2", symbol: "ZZZ", priced: false, change: null, current_pnl: null, scenario_pnl: null, reason: "no implied volatility" })],
        unpriced: 1,
      }) as never,
    );
    renderWithClient(<ScenariosPage />);
    await userEvent.click(screen.getByRole("button", { name: "Run scenario" }));
    expect(await screen.findByText(/1 position\(s\) could not be priced/)).toBeInTheDocument();
    expect(screen.getByText("Not priced: no implied volatility")).toBeInTheDocument();
  });

  it("applies a preset and runs it", async () => {
    renderWithClient(<ScenariosPage />);
    await userEvent.click(screen.getByRole("button", { name: "Crash -20%" }));
    await waitFor(() =>
      expect(analyticsApi.runScenario).toHaveBeenCalledWith({ spot_pct: -20, iv_shift: 0.2, days_forward: 0 }),
    );
    expect(screen.getByLabelText("Price move (%)")).toHaveValue(-20);
    expect(screen.getByLabelText("Volatility change (points)")).toHaveValue(20);
  });

  it("blocks out-of-range input with a message and does not call the API", async () => {
    renderWithClient(<ScenariosPage />);
    const spot = screen.getByLabelText("Price move (%)");
    await userEvent.clear(spot);
    await userEvent.type(spot, "-95");
    expect(screen.getByText("Price move must be between -90% and +200%.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Run scenario" })).toBeDisabled();
    expect(analyticsApi.runScenario).not.toHaveBeenCalled();
  });

  it("says so when there are no open positions", async () => {
    vi.mocked(analyticsApi.runScenario).mockResolvedValue(result({ positions: [], priced: 0, ladder: [] }) as never);
    renderWithClient(<ScenariosPage />);
    await userEvent.click(screen.getByRole("button", { name: "Run scenario" }));
    expect(await screen.findByText("You have no open positions.")).toBeInTheDocument();
  });

  it("shows an error when the run fails", async () => {
    vi.mocked(analyticsApi.runScenario).mockRejectedValue(new Error("boom"));
    renderWithClient(<ScenariosPage />);
    await userEvent.click(screen.getByRole("button", { name: "Run scenario" }));
    expect(await screen.findByText("Could not run the scenario. Try again.")).toBeInTheDocument();
  });

  it("saves the current scenario under a name, and needs a name first", async () => {
    vi.mocked(analyticsApi.saveScenario).mockResolvedValue(saved as never);
    renderWithClient(<ScenariosPage />);
    expect(screen.getByRole("button", { name: "Save current" })).toBeDisabled();
    await userEvent.type(screen.getByLabelText("Name"), "Earnings gap");
    await userEvent.click(screen.getByRole("button", { name: "Save current" }));
    await waitFor(() =>
      expect(analyticsApi.saveScenario).toHaveBeenCalledWith({
        spot_pct: -10,
        iv_shift: 0.05,
        days_forward: 0,
        name: "Earnings gap",
      }),
    );
  });

  it("lists, re-runs and deletes saved scenarios", async () => {
    vi.mocked(analyticsApi.scenarios).mockResolvedValue([saved] as never);
    vi.mocked(analyticsApi.deleteScenario).mockResolvedValue(undefined);
    renderWithClient(<ScenariosPage />);
    expect(await screen.findByText("Crash")).toBeInTheDocument();
    expect(screen.getByText("-20% price, 20 pts vol, 0 d")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Run" }));
    await waitFor(() =>
      expect(analyticsApi.runScenario).toHaveBeenCalledWith({ spot_pct: -20, iv_shift: 0.2, days_forward: 0 }),
    );
    await userEvent.click(screen.getByRole("button", { name: "Delete Crash" }));
    await waitFor(() => expect(analyticsApi.deleteScenario).toHaveBeenCalledWith("s1"));
  });

  it("shows an error when saving fails", async () => {
    vi.mocked(analyticsApi.saveScenario).mockRejectedValue(new Error("duplicate"));
    renderWithClient(<ScenariosPage />);
    await userEvent.type(screen.getByLabelText("Name"), "Crash");
    await userEvent.click(screen.getByRole("button", { name: "Save current" }));
    expect(await screen.findByText(/Could not save/)).toBeInTheDocument();
  });
});
