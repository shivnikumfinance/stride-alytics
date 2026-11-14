import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithClient } from "../../test/utils";
import { RegimeHistoryChart } from "./RegimeHistoryChart";

vi.mock("../../api/endpoints", () => ({
  regimeApi: { history: vi.fn() },
}));

import { regimeApi } from "../../api/endpoints";

const row = (as_of: string, score: number | null, state = "NORMAL") => ({
  as_of,
  score,
  state,
  vix: 17,
  iv_rank: 40,
  market_down: false,
  source: "live",
});

describe("RegimeHistoryChart", () => {
  beforeEach(() => vi.clearAllMocks());

  it("describes the latest score for screen readers (history arrives newest first)", async () => {
    vi.mocked(regimeApi.history).mockResolvedValue([row("2026-06-03", 72, "GROWTH"), row("2026-06-02", 55), row("2026-06-01", 41)] as never);
    renderWithClient(<RegimeHistoryChart days={30} />);
    expect(await screen.findByRole("img", { name: /over 3 days, latest 72 \(GROWTH\)/ })).toBeInTheDocument();
    expect(regimeApi.history).toHaveBeenCalledWith(30);
  });

  it("ignores days without a score", async () => {
    vi.mocked(regimeApi.history).mockResolvedValue([row("2026-06-03", 60), row("2026-06-02", null, "UNKNOWN"), row("2026-06-01", 50)] as never);
    renderWithClient(<RegimeHistoryChart />);
    expect(await screen.findByRole("img", { name: /over 2 days, latest 60/ })).toBeInTheDocument();
  });

  it("explains when there is not enough history", async () => {
    vi.mocked(regimeApi.history).mockResolvedValue([row("2026-06-01", 50)] as never);
    renderWithClient(<RegimeHistoryChart />);
    expect(await screen.findByText(/Not enough history yet/)).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("shows an error when the history cannot load", async () => {
    vi.mocked(regimeApi.history).mockRejectedValue(new Error("boom"));
    renderWithClient(<RegimeHistoryChart />);
    expect(await screen.findByText("Could not load the regime history.")).toBeInTheDocument();
  });
});
