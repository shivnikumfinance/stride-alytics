import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { calmGate } from "../test/fixtures";
import { renderWithRouter } from "../test/utils";
import { StrategyMatrixPage } from "./StrategyMatrixPage";

vi.mock("../api/endpoints", () => ({
  analyticsApi: { matrix: vi.fn() },
  gateApi: { master: vi.fn() },
}));

import { analyticsApi, gateApi } from "../api/endpoints";

const cell = (availability: string, over = {}) => ({
  availability,
  base_availability: availability,
  layers: ["base"],
  bands: ["A", "B"],
  note: "A note.",
  gate: null,
  current: false,
  filtered: false,
  ...over,
});

const matrix = (over = {}) => ({
  regimes: ["DEFENSIVE", "NORMAL", "GROWTH"],
  current_regime: "NORMAL",
  gate_clear: true,
  gate_reasons: [],
  regime_score: 55,
  rows: [
    {
      strategy: "Iron Condor",
      description: "Range strategy.",
      cells: {
        DEFENSIVE: cell("limited"),
        NORMAL: cell("available", { current: true, gate: "clear" }),
        GROWTH: cell("blocked"),
      },
    },
    {
      strategy: "Butterfly",
      description: "Pin strategy.",
      cells: {
        DEFENSIVE: cell("blocked"),
        NORMAL: cell("limited", { current: true, gate: "clear", filtered: true }),
        GROWTH: cell("blocked"),
      },
    },
  ],
  ...over,
});

describe("Strategy Matrix page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(gateApi.master).mockResolvedValue(calmGate);
    vi.mocked(analyticsApi.matrix).mockResolvedValue(matrix() as never);
  });

  it("shows strategies as rows and regimes as columns, marking the current regime", async () => {
    renderWithRouter(<StrategyMatrixPage />);
    expect(await screen.findByText("Current regime: Normal (55)")).toBeInTheDocument();
    for (const h of ["Strategy", "Defensive", "Normal", "Growth"]) {
      expect(screen.getByRole("columnheader", { name: new RegExp(h) })).toBeInTheDocument();
    }
    expect(screen.getByRole("columnheader", { name: /Normal.*\(now\)/ })).toBeInTheDocument();
    expect(screen.getByRole("rowheader", { name: /Iron Condor/ })).toBeInTheDocument();
    expect(screen.getByRole("rowheader", { name: /Butterfly/ })).toBeInTheDocument();
  });

  it("describes each cell's availability, layers, bands and gate status", async () => {
    renderWithRouter(<StrategyMatrixPage />);
    const row = (await screen.findByRole("rowheader", { name: /Iron Condor/ })).closest("tr")!;
    const cells = within(row).getAllByRole("link");
    expect(cells.map((c) => c.getAttribute("aria-label"))).toEqual([
      "Iron Condor, limited",
      "Iron Condor, available",
      "Iron Condor, blocked",
    ]);
    expect(within(cells[1]).getByText("Gate: clear")).toBeInTheDocument();
    expect(within(cells[1]).getByText(/base · bands A, B/)).toBeInTheDocument();
    expect(within(cells[2]).queryByText(/bands/)).not.toBeInTheDocument(); // blocked: no layers/bands
  });

  it("marks filtered-out cells", async () => {
    renderWithRouter(<StrategyMatrixPage />);
    expect(await screen.findByLabelText("Butterfly, limited, filtered out")).toBeInTheDocument();
  });

  it("re-queries with the layer and band filters", async () => {
    renderWithRouter(<StrategyMatrixPage />);
    await screen.findByText("Current regime: Normal (55)");
    await userEvent.selectOptions(screen.getByLabelText("Layer"), "growth");
    await waitFor(() => expect(analyticsApi.matrix).toHaveBeenCalledWith({ layer: "growth", band: undefined }));
    await userEvent.selectOptions(screen.getByLabelText("Capital band"), "C");
    await waitFor(() => expect(analyticsApi.matrix).toHaveBeenCalledWith({ layer: "growth", band: "C" }));
  });

  it("explains when the gate has blocked everything", async () => {
    vi.mocked(analyticsApi.matrix).mockResolvedValue(matrix({ gate_clear: false }) as never);
    renderWithRouter(<StrategyMatrixPage />);
    expect(await screen.findByText(/every strategy in the current regime is blocked/)).toBeInTheDocument();
  });

  it("handles an unknown regime and a load error", async () => {
    vi.mocked(analyticsApi.matrix).mockResolvedValue(matrix({ current_regime: null, regime_score: null }) as never);
    const { unmount } = renderWithRouter(<StrategyMatrixPage />);
    expect(await screen.findByText("Current regime unavailable")).toBeInTheDocument();
    unmount();
    vi.mocked(analyticsApi.matrix).mockRejectedValue(new Error("boom"));
    renderWithRouter(<StrategyMatrixPage />);
    expect(await screen.findByText("Could not load the matrix. Try refreshing.")).toBeInTheDocument();
  });
});
