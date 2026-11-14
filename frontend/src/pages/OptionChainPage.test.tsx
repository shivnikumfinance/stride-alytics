import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithClient } from "../test/utils";
import { OptionChainPage } from "./OptionChainPage";

vi.mock("../api/endpoints", () => ({
  analyticsApi: { chain: vi.fn() },
}));

import { analyticsApi } from "../api/endpoints";

const side = (over = {}) => ({
  bid: 1.0,
  ask: 1.2,
  last: 1.1,
  iv: 0.3,
  delta: -0.25,
  gamma: 0.01,
  theta: -0.05,
  vega: 0.1,
  open_interest: 500,
  volume: 20,
  pop_short: 0.75,
  ...over,
});

const chain = (over = {}) => ({
  symbol: "AAPL",
  spot: 201,
  source: "live",
  expiry: "2026-07-17",
  dte: 30,
  expiries: ["2026-07-17", "2026-08-21"],
  strikes: [
    { strike: 190, call: side({ delta: 0.75, pop_short: 0.25 }), put: side() },
    { strike: 200, call: side({ delta: 0.5, pop_short: 0.5 }), put: null },
  ],
  ...over,
});

describe("Option Chain page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(analyticsApi.chain).mockResolvedValue(chain() as never);
  });

  it("loads the chain and shows strikes with Greeks and PoP", async () => {
    renderWithClient(<OptionChainPage />);
    expect(await screen.findByText("AAPL · spot 201.00")).toBeInTheDocument();
    expect(screen.getByText("Expiry 2026-07-17 (30 days)")).toBeInTheDocument();
    const row190 = screen.getByRole("rowheader", { name: /190/ }).closest("tr")!;
    expect(within(row190).getByText("75%")).toBeInTheDocument(); // put PoP
    expect(within(row190).getByText("-0.25")).toBeInTheDocument();
    expect(analyticsApi.chain).toHaveBeenCalledWith("AAPL", undefined);
  });

  it("shows a dash for a missing side and flags the at-the-money strike", async () => {
    renderWithClient(<OptionChainPage />);
    const row200 = (await screen.findByRole("rowheader", { name: /200/ })).closest("tr")!;
    expect(within(row200).getAllByText("—")).toHaveLength(6);
    expect(within(row200).getByText("ATM")).toBeInTheDocument();
  });

  it("loads another symbol and another expiry", async () => {
    renderWithClient(<OptionChainPage />);
    await screen.findByText("AAPL · spot 201.00");
    const symbol = screen.getByLabelText("Symbol");
    await userEvent.clear(symbol);
    await userEvent.type(symbol, "msft");
    await userEvent.click(screen.getByRole("button", { name: "Load chain" }));
    await waitFor(() => expect(analyticsApi.chain).toHaveBeenCalledWith("MSFT", undefined));

    await userEvent.selectOptions(await screen.findByLabelText("Expiry"), "2026-08-21");
    await waitFor(() => expect(analyticsApi.chain).toHaveBeenCalledWith("MSFT", "2026-08-21"));
  });

  it("labels synthetic data", async () => {
    vi.mocked(analyticsApi.chain).mockResolvedValue(chain({ source: "synthetic" }) as never);
    renderWithClient(<OptionChainPage />);
    expect(await screen.findByText("Sample data — not live")).toBeInTheDocument();
  });

  it("shows live data without a sample label", async () => {
    renderWithClient(<OptionChainPage />);
    await screen.findByText("AAPL · spot 201.00");
    expect(screen.queryByText("Sample data — not live")).not.toBeInTheDocument();
  });

  it("shows an error for an unknown symbol", async () => {
    vi.mocked(analyticsApi.chain).mockRejectedValue(new Error("404"));
    renderWithClient(<OptionChainPage />);
    expect(await screen.findByText(/Could not load a chain for AAPL/)).toBeInTheDocument();
  });
});
