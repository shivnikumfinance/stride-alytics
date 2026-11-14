import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithClient } from "../test/utils";
import { WatchlistPage } from "./WatchlistPage";

vi.mock("../api/endpoints", () => ({
  watchlistApi: {
    list: vi.fn(),
    create: vi.fn(),
    remove: vi.fn(),
    addSymbol: vi.fn(),
    removeSymbol: vi.fn(),
  },
  marketApi: { tickers: vi.fn() },
  symbolsApi: { flags: vi.fn(), setFlag: vi.fn() },
}));
vi.mock("../api/download", () => ({ downloadFile: vi.fn().mockResolvedValue(undefined) }));

import { marketApi, symbolsApi, watchlistApi } from "../api/endpoints";

const list = { id: "w1", name: "Core", symbols: ["AAPL", "MSFT"], created_at: null };

describe("WatchlistPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(watchlistApi.list).mockResolvedValue([list]);
    vi.mocked(watchlistApi.addSymbol).mockResolvedValue({ ...list, symbols: [...list.symbols, "NVDA"] });
    vi.mocked(watchlistApi.removeSymbol).mockResolvedValue({ ...list, symbols: ["MSFT"] });
    vi.mocked(watchlistApi.create).mockResolvedValue({ id: "w2", name: "Swing", symbols: [], created_at: null });
    vi.mocked(symbolsApi.flags).mockResolvedValue({ MSFT: { news_flag: true, note: null } });
    vi.mocked(symbolsApi.setFlag).mockResolvedValue({ symbol: "AAPL", news_flag: true, note: null });
    vi.mocked(marketApi.tickers).mockResolvedValue({
      success: true,
      source: "live",
      data: { AAPL: { symbol: "AAPL", price: "190.10", change: "-1.2", changePercent: "-0.63" } },
    });
  });

  it("shows quotes, and a dash where a quote is missing", async () => {
    renderWithClient(<WatchlistPage />);
    expect(await screen.findByText("190.10")).toBeInTheDocument();
    expect(screen.getByText("-0.63%")).toBeInTheDocument();
    expect(screen.getByText("MSFT")).toBeInTheDocument();
    expect(screen.getAllByText("—").length).toBeGreaterThan(0);
    expect(screen.queryByText(/Sample data/)).not.toBeInTheDocument();
    expect(marketApi.tickers).toHaveBeenCalledWith(["AAPL", "MSFT"]);
  });

  it("labels placeholder quotes as sample data", async () => {
    vi.mocked(marketApi.tickers).mockResolvedValue({ success: true, source: "fallback", data: {} });
    renderWithClient(<WatchlistPage />);
    expect(await screen.findByText(/Sample data — not live/)).toBeInTheDocument();
  });

  it("adds a symbol upper-cased and removes one", async () => {
    const user = userEvent.setup();
    renderWithClient(<WatchlistPage />);
    await screen.findByText("MSFT");

    await user.type(screen.getByLabelText("Add symbol"), "nvda");
    await user.click(screen.getByRole("button", { name: "Add" }));
    await waitFor(() => expect(watchlistApi.addSymbol).toHaveBeenCalledWith("w1", "NVDA"));

    await user.click(screen.getByRole("button", { name: "Remove AAPL" }));
    await waitFor(() => expect(watchlistApi.removeSymbol).toHaveBeenCalledWith("w1", "AAPL"));
  });

  it("creates a watchlist and ignores a blank name", async () => {
    const user = userEvent.setup();
    renderWithClient(<WatchlistPage />);
    await screen.findByText("MSFT");

    await user.click(screen.getByRole("button", { name: "Create" }));
    expect(watchlistApi.create).not.toHaveBeenCalled();

    await user.type(screen.getByLabelText("New watchlist"), "Swing");
    await user.click(screen.getByRole("button", { name: "Create" }));
    await waitFor(() => expect(watchlistApi.create).toHaveBeenCalledWith("Swing", undefined));
  });

  it("shows and toggles the news flag that blocks a symbol", async () => {
    const user = userEvent.setup();
    renderWithClient(<WatchlistPage />);
    await screen.findByText("MSFT");

    // MSFT is already flagged and says so; AAPL is not.
    expect(await screen.findByLabelText("News flag MSFT")).toBeChecked();
    expect(screen.getByText("blocked")).toBeInTheDocument();
    expect(screen.getByLabelText("News flag AAPL")).not.toBeChecked();

    await user.click(screen.getByLabelText("News flag AAPL"));
    await waitFor(() => expect(symbolsApi.setFlag).toHaveBeenCalledWith("AAPL", true));
  });
});
