import { screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithRouter } from "../test/utils";
import { ActiveTradesPage } from "./ActiveTradesPage";

vi.mock("../api/endpoints", () => ({
  tradesApi: { listAll: vi.fn() },
}));

import { tradesApi } from "../api/endpoints";

const trade = (over = {}) => ({
  trade_id: "t1",
  portfolio_id: "p1",
  symbol: "AAPL",
  trade_type: "put",
  direction: "short",
  entry_price: 2,
  exit_price: null,
  quantity: 1,
  entry_date: "2026-06-01",
  exit_date: null,
  strike: 190,
  expiry: "2026-07-17",
  layer: "base",
  band: "A",
  risk_amount: 1000,
  ...over,
});

const page = (data: unknown[]) => ({ success: true, data, total: data.length }) as never;

describe("Active Trades page", () => {
  beforeEach(() => vi.clearAllMocks());

  it("asks for open trades only and totals the capital at risk", async () => {
    vi.mocked(tradesApi.listAll).mockResolvedValue(
      page([trade(), trade({ trade_id: "t2", symbol: "MSFT", risk_amount: 500 }), trade({ trade_id: "t3", symbol: "XOM", risk_amount: null })]),
    );
    renderWithRouter(<ActiveTradesPage />);
    expect(await screen.findByText("3 open · $1,500.00 capital at risk")).toBeInTheDocument();
    expect(tradesApi.listAll).toHaveBeenCalledWith({ status: "open", sort: "entry_date", limit: 200 });
  });

  it("shows trade details, with dashes for missing values", async () => {
    vi.mocked(tradesApi.listAll).mockResolvedValue(
      page([
        trade(),
        trade({ trade_id: "t3", symbol: "XOM", trade_type: "stock", strike: null, expiry: null, layer: null, band: null, risk_amount: null }),
      ]),
    );
    renderWithRouter(<ActiveTradesPage />);
    const aapl = (await screen.findByText("AAPL")).closest("tr")!;
    for (const text of ["put", "short", "$2.00", "190", "2026-07-17", "base", "A", "$1,000.00"]) {
      expect(within(aapl).getByText(text)).toBeInTheDocument();
    }
    const xom = screen.getByText("XOM").closest("tr")!;
    expect(within(xom).getAllByText("—")).toHaveLength(5); // strike, expiry, layer, band, at risk
  });

  it("links to Portfolio to add or close trades", async () => {
    vi.mocked(tradesApi.listAll).mockResolvedValue(page([]));
    renderWithRouter(<ActiveTradesPage />);
    expect(await screen.findByRole("link", { name: /Add or close trades in Portfolio/ })).toHaveAttribute("href", "/portfolio");
    expect(await screen.findByText("No open trades.")).toBeInTheDocument();
  });

  it("shows an error when trades cannot load", async () => {
    vi.mocked(tradesApi.listAll).mockRejectedValue(new Error("boom"));
    renderWithRouter(<ActiveTradesPage />);
    expect(await screen.findByText("Could not load your trades. Try refreshing.")).toBeInTheDocument();
  });
});
