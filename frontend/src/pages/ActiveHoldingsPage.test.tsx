import { screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { alert, reason, SUMMARY_COUNTS } from "../test/fixtures";
import { renderWithRouter } from "../test/utils";
import { ActiveHoldingsPage } from "./ActiveHoldingsPage";

vi.mock("../api/endpoints", () => ({
  alertsApi: { exits: vi.fn() },
}));

import { alertsApi } from "../api/endpoints";

const exits = (alerts: ReturnType<typeof alert>[]) =>
  ({ alerts, summary: SUMMARY_COUNTS, unacknowledged_critical: 0, open_positions: alerts.length }) as never;

const calm = alert({
  trade_id: "t2",
  symbol: "MSFT",
  trade_type: "call",
  direction: "long",
  quantity: 2,
  severity: "normal",
  action: "hold",
  reasons: [],
  pnl: 25,
  pnl_pct: 0.125,
  dte: 40,
  delta: 0.4,
  theta: -1.5,
  strategy_detail: { strike: 400, expiry: "2026-09-18", layer: "growth", band: "C", entry_price: 5, risk_amount: 800 },
  unacknowledged_critical: false,
});

describe("Active Holdings page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(alertsApi.exits).mockResolvedValue(exits([alert(), calm]));
  });

  it("asks for every position, including calm ones", async () => {
    renderWithRouter(<ActiveHoldingsPage />);
    await screen.findByText("AAPL");
    expect(alertsApi.exits).toHaveBeenCalledWith("normal");
  });

  it("shows each position's alert, P&L, Greeks and suggested action", async () => {
    renderWithRouter(<ActiveHoldingsPage />);
    const aapl = (await screen.findByText("AAPL")).closest("tr")!;
    expect(within(aapl).getByText("short 1 × put 190 · 2026-07-17")).toBeInTheDocument();
    expect(within(aapl).getByText(/assignment alarm/)).toBeInTheDocument();
    expect(within(aapl).getByText("roll")).toBeInTheDocument();
    expect(within(aapl).getByText("-$100.00")).toHaveClass("text-red-700");
    expect(within(aapl).getByText("-50.0%")).toBeInTheDocument();
    expect(within(aapl).getByText("-0.80")).toBeInTheDocument();

    const msft = screen.getByText("MSFT").closest("tr")!;
    expect(within(msft).getByText("long 2 × call 400 · 2026-09-18")).toBeInTheDocument();
    expect(within(msft).getByText("Within limits")).toBeInTheDocument();
    expect(within(msft).getByText("+$25.00")).toHaveClass("text-green-700");
    expect(within(msft).getByText("hold")).toBeInTheDocument();
  });

  it("totals P&L and says when some positions could not be priced", async () => {
    vi.mocked(alertsApi.exits).mockResolvedValue(
      exits([
        alert({ pnl: 100, pnl_pct: 0.1 }),
        alert({
          trade_id: "t9",
          symbol: "ZZZ",
          pnl: null,
          pnl_pct: null,
          delta: null,
          theta: null,
          dte: null,
          reasons: [reason({ code: "no_market_data", severity: "warning", message: "No market data." })],
        }),
      ]),
    );
    renderWithRouter(<ActiveHoldingsPage />);
    expect(
      await screen.findByText(/2 open · total P&L \$100\.00 \(some positions could not be priced\)/),
    ).toBeInTheDocument();
    const zzz = screen.getByText("ZZZ").closest("tr")!;
    expect(within(zzz).getAllByText("—").length).toBe(5); // P&L, P&L %, DTE, delta, theta
  });

  it("shows stock positions without strike or expiry", async () => {
    vi.mocked(alertsApi.exits).mockResolvedValue(
      exits([alert({ trade_type: "stock", direction: "long", quantity: 10, reasons: [], severity: "normal", action: "hold" })]),
    );
    renderWithRouter(<ActiveHoldingsPage />);
    expect(await screen.findByText("long 10 × stock")).toBeInTheDocument();
  });

  it("explains an empty book and an error", async () => {
    vi.mocked(alertsApi.exits).mockResolvedValue(exits([]));
    const { unmount } = renderWithRouter(<ActiveHoldingsPage />);
    expect(await screen.findByText(/No open positions/)).toBeInTheDocument();
    unmount();
    vi.mocked(alertsApi.exits).mockRejectedValue(new Error("boom"));
    renderWithRouter(<ActiveHoldingsPage />);
    expect(await screen.findByText("Could not load your positions. Try refreshing.")).toBeInTheDocument();
  });
});
