import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithClient } from "../test/utils";
import { SizingPage } from "./SizingPage";

vi.mock("../api/endpoints", () => ({
  sizingApi: { calculate: vi.fn() },
  gateApi: { master: vi.fn(), check: vi.fn() },
  portfolioApi: { bands: vi.fn() },
}));

import { gateApi, portfolioApi, sizingApi } from "../api/endpoints";
import type { SizingResult } from "../types";

const result: SizingResult = {
  mode: "max_loss",
  risk_pct: 1.25,
  risk_budget: 1250,
  quantity: 2,
  risk_amount: 1000,
  blocked: false,
  reasons: [],
  warnings: ["Regime is DEFENSIVE: risk budget cut to 50% of normal."],
  band: "A",
  band_cap_pct: 30,
  band_exposure_after_pct: 12.5,
  account_size: 100000,
  regime_state: "NORMAL",
  layer_split: { base: 60, growth: 40 },
};

describe("SizingPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(gateApi.master).mockRejectedValue(new Error("not needed here"));
    vi.mocked(portfolioApi.bands).mockResolvedValue([
      { band: "A", exposure: 12500, exposure_pct: 12.5, cap_pct: 30, status: "ok" },
      { band: "B", exposure: 21000, exposure_pct: 21, cap_pct: 25, status: "near" },
    ]);
    vi.mocked(sizingApi.calculate).mockResolvedValue(result);
  });

  it("calculates from max loss and shows the quantity, risk and warnings", async () => {
    const user = userEvent.setup();
    renderWithClient(<SizingPage />);

    await user.type(screen.getByLabelText("Max loss per contract ($)"), "500");
    await user.selectOptions(screen.getByLabelText("Band"), "A");
    await user.click(screen.getByRole("button", { name: "Calculate" }));

    await waitFor(() =>
      expect(sizingApi.calculate).toHaveBeenCalledWith({
        layer: "base",
        band: "A",
        risk_pct: null,
        max_loss_per_contract: 500,
      }),
    );
    expect(await screen.findByText(/^\$1,250/)).toBeInTheDocument(); // risk budget
    expect(screen.getByText(/^\$1,000/)).toBeInTheDocument(); // capital at risk
    expect(screen.getAllByText("12.5%")).toHaveLength(2); // band use after (result card + band table)
    expect(screen.getByText("cap 30%")).toBeInTheDocument();
    expect(screen.getByText(/cut to 50% of normal/)).toBeInTheDocument();
    expect(screen.getByText(/Regime NORMAL/)).toBeInTheDocument();
  });

  it("can size by credit instead, and sends the risk override", async () => {
    const user = userEvent.setup();
    renderWithClient(<SizingPage />);

    await user.selectOptions(screen.getByLabelText("Size by"), "credit");
    await user.selectOptions(screen.getByLabelText("Layer"), "growth");
    await user.type(screen.getByLabelText("Credit per share ($)"), "2.5");
    await user.type(screen.getByLabelText("Risk % override (optional)"), "2.75");
    await user.click(screen.getByRole("button", { name: "Calculate" }));

    await waitFor(() =>
      expect(sizingApi.calculate).toHaveBeenCalledWith({
        layer: "growth",
        band: null,
        risk_pct: 2.75,
        credit: 2.5,
      }),
    );
  });

  it("validates before calling the API", async () => {
    const user = userEvent.setup();
    renderWithClient(<SizingPage />);

    await user.click(screen.getByRole("button", { name: "Calculate" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(/max loss per contract/i);

    await user.type(screen.getByLabelText("Max loss per contract ($)"), "500");
    await user.type(screen.getByLabelText("Risk % override (optional)"), "50");
    await user.click(screen.getByRole("button", { name: "Calculate" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(/Risk % must be above 0 and at most 10/);
    expect(sizingApi.calculate).not.toHaveBeenCalled();
  });

  it("explains why a trade cannot be sized", async () => {
    const user = userEvent.setup();
    vi.mocked(sizingApi.calculate).mockResolvedValue({
      ...result,
      blocked: true,
      quantity: 0,
      risk_amount: null,
      reasons: [{ rule_id: "BR-023", message: "The Growth layer is locked in a DEFENSIVE regime." }],
    });
    renderWithClient(<SizingPage />);
    await user.type(screen.getByLabelText("Max loss per contract ($)"), "500");
    await user.click(screen.getByRole("button", { name: "Calculate" }));

    expect(await screen.findByText("Cannot size this trade")).toBeInTheDocument();
    expect(screen.getByText(/Growth layer is locked/)).toBeInTheDocument();
  });

  it("lists capital band usage with status", async () => {
    renderWithClient(<SizingPage />);
    expect(await screen.findByText("near")).toBeInTheDocument();
    expect(screen.getByText("ok")).toBeInTheDocument();
    expect(screen.getByText("21%")).toBeInTheDocument();
  });
});
