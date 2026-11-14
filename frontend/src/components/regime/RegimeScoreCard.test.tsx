import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithClient } from "../../test/utils";
import { RegimeScoreCard } from "./RegimeScoreCard";

vi.mock("../../api/endpoints", () => ({
  regimeApi: { score: vi.fn(), history: vi.fn(), get: vi.fn() },
}));

import { regimeApi } from "../../api/endpoints";
import type { RegimeScoreData } from "../../types";

const base: RegimeScoreData = {
  score: 74.2,
  state: "GROWTH",
  components: { trend: 100, vix: 80.5, iv_rank: 40 },
  weights: { trend: 40, vix: 30, iv_rank: 30 },
  missing: [],
  market_down: false,
  vix: 16.1,
  iv_rank: 40,
  as_of: "2026-06-01",
  source: "live",
};

describe("RegimeScoreCard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(regimeApi.history).mockResolvedValue([
      { as_of: "2026-05-29", score: 38.5, state: "DEFENSIVE", vix: 27, iv_rank: 80, market_down: false, source: "live" },
      { as_of: "2026-05-28", score: 55, state: "NORMAL", vix: 19, iv_rank: 50, market_down: false, source: "live" },
    ]);
  });

  it("shows the score, state, sub-scores and history", async () => {
    vi.mocked(regimeApi.score).mockResolvedValue(base);
    renderWithClient(<RegimeScoreCard />);

    expect(await screen.findByText("74.2")).toBeInTheDocument();
    expect(screen.getAllByText("GROWTH").length).toBeGreaterThan(0);
    expect(screen.getByText("100 / 100")).toBeInTheDocument();
    expect(screen.getByText("80.5 / 100")).toBeInTheDocument();
    expect(screen.getByText(/VIX 16.1/)).toBeInTheDocument();
    expect(await screen.findByText("2026-05-29")).toBeInTheDocument();
    expect(screen.getByText("38.5")).toBeInTheDocument();
    expect(screen.queryByText(/Last stored value/)).not.toBeInTheDocument();
  });

  it("flags a stored value and a market below its 200-day average", async () => {
    vi.mocked(regimeApi.score).mockResolvedValue({ ...base, source: "stored", market_down: true, state: "DEFENSIVE", score: 22 });
    renderWithClient(<RegimeScoreCard />);
    expect(await screen.findByText(/Last stored value/)).toBeInTheDocument();
    expect(screen.getByText(/SPY below 200-day average/)).toBeInTheDocument();
  });

  it("says plainly when the score cannot be computed, with no made-up number", async () => {
    vi.mocked(regimeApi.score).mockResolvedValue({
      ...base,
      score: null,
      state: "UNKNOWN",
      components: { trend: null, vix: null, iv_rank: null },
      vix: null,
      iv_rank: null,
      missing: ["trend", "vix", "iv_rank"],
      source: "unavailable",
    });
    renderWithClient(<RegimeScoreCard />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/market data is unavailable/);
    expect(screen.getByText("—")).toBeInTheDocument();
    expect(screen.getAllByText("unavailable")).toHaveLength(3);
  });

  it("handles a failed request", async () => {
    vi.mocked(regimeApi.score).mockRejectedValue(new Error("boom"));
    renderWithClient(<RegimeScoreCard />);
    expect(await screen.findByText(/Could not load the regime score/)).toBeInTheDocument();
  });
});
