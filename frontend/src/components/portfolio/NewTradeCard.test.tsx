import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AxiosError, type AxiosResponse } from "axios";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithClient } from "../../test/utils";
import { NewTradeCard } from "./NewTradeCard";

vi.mock("../../api/endpoints", () => ({
  tradesApi: { create: vi.fn() },
  gateApi: { check: vi.fn() },
  sizingApi: { calculate: vi.fn() },
}));

import { gateApi, sizingApi, tradesApi } from "../../api/endpoints";

function blocked(reasons: { rule_id: string; message: string; kind: "block" | "data" }[]) {
  const res = {
    status: 409,
    data: { success: false, error: { message: "Trade blocked by Do-Not-Trade rules", details: { reasons } } },
  } as AxiosResponse;
  return new AxiosError("Request failed with status code 409", "ERR_BAD_REQUEST", undefined, undefined, res);
}

describe("NewTradeCard", () => {
  beforeEach(() => vi.clearAllMocks());

  it("shows every reason when an entry is blocked and says nothing was recorded", async () => {
    const user = userEvent.setup();
    vi.mocked(tradesApi.create).mockRejectedValue(
      blocked([
        { rule_id: "BR-017", message: "Bid/ask spread 15.0% is above 10%.", kind: "block" },
        { rule_id: "BR-018", message: "Data unavailable: could not verify open interest.", kind: "data" },
      ]),
    );
    renderWithClient(<NewTradeCard portfolioId="p1" />);

    await user.click(screen.getByRole("button", { name: "Add trade" }));

    expect(await screen.findByText(/BLOCKED — trade not recorded/)).toBeInTheDocument();
    expect(screen.getByText(/Bid\/ask spread 15.0% is above 10%/)).toBeInTheDocument();
    expect(screen.getByText(/could not verify open interest/)).toBeInTheDocument();
    expect(screen.getByText("(could not verify)")).toBeInTheDocument();
  });

  it("shows a plain error for failures that are not gate blocks", async () => {
    const user = userEvent.setup();
    vi.mocked(tradesApi.create).mockRejectedValue(new Error("Server exploded"));
    renderWithClient(<NewTradeCard portfolioId="p1" />);
    await user.click(screen.getByRole("button", { name: "Add trade" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Server exploded");
    expect(screen.queryByText(/BLOCKED/)).not.toBeInTheDocument();
  });

  it("sends the strategy fields with the trade", async () => {
    const user = userEvent.setup();
    vi.mocked(tradesApi.create).mockResolvedValue({} as never);
    renderWithClient(<NewTradeCard portfolioId="p1" />);

    await user.clear(screen.getByLabelText("Symbol"));
    await user.type(screen.getByLabelText("Symbol"), "msft");
    await user.type(screen.getByLabelText("Strike"), "400");
    await user.selectOptions(screen.getByLabelText("Layer"), "growth");
    await user.selectOptions(screen.getByLabelText("Band"), "B");
    await user.type(screen.getByLabelText("Capital at risk ($)"), "1250");
    await user.click(screen.getByRole("button", { name: "Add trade" }));

    await waitFor(() => expect(tradesApi.create).toHaveBeenCalledTimes(1));
    expect(tradesApi.create).toHaveBeenCalledWith(
      expect.objectContaining({
        portfolio_id: "p1",
        symbol: "MSFT",
        trade_type: "put",
        strike: 400,
        layer: "growth",
        band: "B",
        risk_amount: 1250,
        expiry: null,
      }),
    );
  });

  it("hides option fields for stock trades and sends no strike or expiry", async () => {
    const user = userEvent.setup();
    vi.mocked(tradesApi.create).mockResolvedValue({} as never);
    renderWithClient(<NewTradeCard portfolioId="p1" />);

    await user.type(screen.getByLabelText("Strike"), "400");
    await user.selectOptions(screen.getByLabelText("Type"), "stock");
    expect(screen.queryByLabelText("Strike")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Expiry")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Add trade" }));
    await waitFor(() =>
      expect(tradesApi.create).toHaveBeenCalledWith(expect.objectContaining({ strike: null, expiry: null })),
    );
  });

  it("Check gate runs a dry run and shows the verdict", async () => {
    const user = userEvent.setup();
    vi.mocked(gateApi.check).mockResolvedValue({
      clear: false,
      status: "BLOCKED",
      reasons: [{ rule_id: "BR-020", message: "Earnings on 2026-06-10 are within 14 days.", kind: "block" }],
      checked: [],
      not_evaluated: ["BR-013"],
    });
    renderWithClient(<NewTradeCard portfolioId="p1" />);

    await user.click(screen.getByRole("button", { name: "Check gate" }));

    await waitFor(() =>
      expect(gateApi.check).toHaveBeenCalledWith(
        expect.objectContaining({ symbol: "AAPL", trade_type: "put", layer: "base" }),
      ),
    );
    expect(await screen.findByText(/Earnings on 2026-06-10/)).toBeInTheDocument();
    expect(tradesApi.create).not.toHaveBeenCalled(); // a check never records a trade
  });

  it("Suggest size fills in the quantity and capital at risk", async () => {
    const user = userEvent.setup();
    vi.mocked(sizingApi.calculate).mockResolvedValue({
      mode: "max_loss",
      risk_pct: 1.25,
      risk_budget: 1250,
      quantity: 2,
      risk_amount: 1000,
      blocked: false,
      reasons: [],
      warnings: ["No band assigned: the band cap was not checked."],
      band: null,
      band_cap_pct: null,
      band_exposure_after_pct: null,
      account_size: 100000,
      regime_state: "NORMAL",
      layer_split: { base: 60, growth: 40 },
    });
    renderWithClient(<NewTradeCard portfolioId="p1" />);

    await user.type(screen.getByLabelText("Max loss per contract ($)"), "500");
    await user.click(screen.getByRole("button", { name: "Suggest size" }));

    await waitFor(() =>
      expect(sizingApi.calculate).toHaveBeenCalledWith({
        layer: "base",
        band: null,
        credit: null,
        max_loss_per_contract: 500,
      }),
    );
    expect(await screen.findByText(/Suggested/)).toHaveTextContent("Suggested 2 contract(s)");
    expect(screen.getByLabelText("Quantity")).toHaveValue(2);
    expect(screen.getByLabelText("Capital at risk ($)")).toHaveValue(1000);
    expect(screen.getByText(/band cap was not checked/)).toBeInTheDocument();
  });

  it("does not change the quantity when sizing is blocked", async () => {
    const user = userEvent.setup();
    vi.mocked(sizingApi.calculate).mockResolvedValue({
      mode: "none",
      risk_pct: 2.5,
      risk_budget: 0,
      quantity: 0,
      risk_amount: null,
      blocked: true,
      reasons: [{ rule_id: "BR-023", message: "The Growth layer is locked in a DEFENSIVE regime." }],
      warnings: [],
      band: null,
      band_cap_pct: null,
      band_exposure_after_pct: null,
      account_size: 100000,
      regime_state: "DEFENSIVE",
      layer_split: { base: 80, growth: 20 },
    });
    renderWithClient(<NewTradeCard portfolioId="p1" />);
    await user.selectOptions(screen.getByLabelText("Layer"), "growth");
    await user.click(screen.getByRole("button", { name: "Suggest size" }));

    expect(await screen.findByText(/Growth layer is locked/)).toBeInTheDocument();
    expect(screen.getByLabelText("Quantity")).toHaveValue(1);
  });
});
