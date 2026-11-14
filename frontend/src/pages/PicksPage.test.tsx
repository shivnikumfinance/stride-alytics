import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithRouter } from "../test/utils";
import { PicksPage } from "./PicksPage";

vi.mock("../api/endpoints", () => ({
  picksApi: { list: vi.fn() },
  gateApi: { check: vi.fn() },
}));

import { gateApi, picksApi } from "../api/endpoints";

const pick = (over = {}) => ({
  id: "p1",
  symbol: "NVDA",
  side: "call",
  strike: 900,
  expiry: "2026-07-17",
  entry_price: 5,
  target_price: 8,
  stop_loss: 3,
  rationale: "Momentum",
  confidence: 0.82,
  week_of: "2026-06-01",
  ...over,
});

describe("Weekly Picks page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(picksApi.list).mockResolvedValue({ success: true, data: [pick()], week_of: "2026-06-01" } as never);
  });

  it("lists picks with confidence", async () => {
    renderWithRouter(<PicksPage />);
    expect(await screen.findByText("NVDA CALL 900")).toBeInTheDocument();
    expect(screen.getByText("82% confidence")).toBeInTheDocument();
    expect(screen.getByText(/week of 2026-06-01/)).toBeInTheDocument();
  });

  it("shows the expected value of each pick, or a dash when it cannot be computed", async () => {
    vi.mocked(picksApi.list).mockResolvedValue({
      success: true,
      data: [pick({ ev: 80 }), pick({ id: "p2", symbol: "AMD", ev: -25 }), pick({ id: "p3", symbol: "TSLA", ev: null })],
      week_of: "2026-06-01",
    } as never);
    renderWithRouter(<PicksPage />);
    expect(await screen.findByText("$80.00")).toHaveClass("text-green-700");
    expect(screen.getByText("-$25.00")).toHaveClass("text-red-700");
    expect(screen.getAllByText("Expected value")).toHaveLength(3);
  });

  it("explains when there are no picks", async () => {
    vi.mocked(picksApi.list).mockResolvedValue({ success: true, data: [], week_of: null } as never);
    renderWithRouter(<PicksPage />);
    expect(await screen.findByText(/No picks yet/)).toBeInTheDocument();
  });

  it("checks the gate for a pick and shows a block with reasons", async () => {
    vi.mocked(gateApi.check).mockResolvedValue({
      clear: false,
      status: "BLOCKED",
      reasons: [{ rule_id: "BR-017", message: "Earnings in 5 days." }],
      not_evaluated: [],
    } as never);
    renderWithRouter(<PicksPage />);
    await userEvent.click(await screen.findByRole("button", { name: "Check gate" }));
    expect(await screen.findByText(/Earnings in 5 days/)).toBeInTheDocument();
    expect(gateApi.check).toHaveBeenCalledWith({
      symbol: "NVDA",
      trade_type: "call",
      strike: 900,
      expiry: "2026-07-17",
    });
  });

  it("shows an error when the gate check fails", async () => {
    vi.mocked(gateApi.check).mockRejectedValue(new Error("boom"));
    renderWithRouter(<PicksPage />);
    await userEvent.click(await screen.findByRole("button", { name: "Check gate" }));
    expect(await screen.findByText("Could not check the gate. Try again.")).toBeInTheDocument();
  });

  it("shows an error when picks cannot load", async () => {
    vi.mocked(picksApi.list).mockRejectedValue(new Error("boom"));
    renderWithRouter(<PicksPage />);
    expect(await screen.findByText("Could not load the picks. Try refreshing.")).toBeInTheDocument();
  });
});
