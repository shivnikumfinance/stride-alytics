import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithClient } from "../../test/utils";
import { PortfolioView } from "./PortfolioView";

vi.mock("../../api/endpoints", () => ({
  portfolioApi: { list: vi.fn(), summary: vi.fn(), create: vi.fn() },
  tradesApi: { list: vi.fn(), create: vi.fn(), close: vi.fn() },
  gateApi: { master: vi.fn(), check: vi.fn() },
  sizingApi: { calculate: vi.fn() },
}));
vi.mock("../../api/download", () => ({ downloadFile: vi.fn().mockResolvedValue(undefined) }));

import { gateApi, portfolioApi, tradesApi } from "../../api/endpoints";

const openTrade = {
  trade_id: "t1",
  symbol: "AAPL",
  trade_type: "call" as const,
  direction: "long" as const,
  quantity: 1,
  entry_price: 2,
  exit_price: null,
  entry_date: "2026-01-05",
  exit_date: null,
  pnl: 0,
  open: true,
};

function localToday(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

describe("PortfolioView close-trade flow", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(portfolioApi.list).mockResolvedValue({
      success: true,
      data: [{ id: "p1", name: "Main", description: null }],
    });
    vi.mocked(portfolioApi.summary).mockResolvedValue({
      portfolio_id: "p1",
      name: "Main",
      total_trades: 1,
      open_trades: 1,
      closed_trades: 0,
      total_pnl: 0,
      win_rate: 0,
      winners: 0,
      losers: 0,
    });
    vi.mocked(gateApi.master).mockResolvedValue({
      clear: true,
      status: "CLEAR TO TRADE",
      reasons: [],
      checked: [],
      not_evaluated: [],
      regime: { score: 80, state: "GROWTH", components: {}, weights: {}, missing: [], market_down: false, vix: 15, iv_rank: 50, as_of: "2026-06-01", source: "live" },
      equity: 100000,
      min_equity: 0,
      enforce_gate: true,
      layer_split: { base: 40, growth: 60 },
      growth_locked: false,
    });
    vi.mocked(tradesApi.list).mockResolvedValue([openTrade]);
    vi.mocked(tradesApi.close).mockResolvedValue({ ...openTrade, exit_price: 3.25, open: false });
  });

  it("closes at the price the user typed, not an invented one", async () => {
    const user = userEvent.setup();
    renderWithClient(<PortfolioView />);

    await screen.findByText("AAPL");
    await user.click(screen.getByRole("button", { name: "Close" }));

    const confirm = screen.getByRole("button", { name: "Confirm" });
    expect(confirm).toBeDisabled(); // no price yet

    await user.type(screen.getByLabelText("Exit price"), "3.25");
    expect(confirm).toBeEnabled();
    await user.click(confirm);

    await waitFor(() => expect(tradesApi.close).toHaveBeenCalledTimes(1));
    expect(tradesApi.close).toHaveBeenCalledWith("t1", {
      exit_price: 3.25, // not entry_price * 1.1 (= 2.2), the old bug
      exit_date: localToday(),
    });
  });

  it("does nothing when the price is empty or not positive, and Cancel backs out", async () => {
    const user = userEvent.setup();
    renderWithClient(<PortfolioView />);

    await screen.findByText("AAPL");
    await user.click(screen.getByRole("button", { name: "Close" }));
    await user.type(screen.getByLabelText("Exit price"), "0");
    expect(screen.getByRole("button", { name: "Confirm" })).toBeDisabled();

    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(screen.getByRole("button", { name: "Close" })).toBeInTheDocument();
    expect(tradesApi.close).not.toHaveBeenCalled();
  });

  it("supports Enter to confirm and Escape to cancel", async () => {
    const user = userEvent.setup();
    renderWithClient(<PortfolioView />);

    await screen.findByText("AAPL");
    await user.click(screen.getByRole("button", { name: "Close" }));
    await user.type(screen.getByLabelText("Exit price"), "{Escape}");
    expect(screen.getByRole("button", { name: "Close" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Close" }));
    await user.type(screen.getByLabelText("Exit price"), "2.5{Enter}");
    await waitFor(() => expect(tradesApi.close).toHaveBeenCalledWith("t1", expect.objectContaining({ exit_price: 2.5 })));
  });
});
