import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithClient } from "../../test/utils";
import { GateBanner } from "./GateBanner";

vi.mock("../../api/endpoints", () => ({ gateApi: { master: vi.fn(), check: vi.fn() } }));

import { gateApi } from "../../api/endpoints";
import type { MasterGate } from "../../types";

const regime = {
  score: 62.5,
  state: "NORMAL" as const,
  components: {},
  weights: {},
  missing: [],
  market_down: false,
  vix: 18,
  iv_rank: 55,
  as_of: "2026-06-01",
  source: "live",
};

const clear: MasterGate = {
  clear: true,
  status: "CLEAR TO TRADE",
  reasons: [],
  checked: ["BR-010"],
  not_evaluated: ["BR-011", "BR-013"],
  regime,
  equity: 98500,
  min_equity: 0,
  enforce_gate: true,
  layer_split: { base: 60, growth: 40 },
  growth_locked: false,
};

describe("GateBanner", () => {
  beforeEach(() => vi.clearAllMocks());

  it("shows CLEAR TO TRADE with the regime, split and equity", async () => {
    vi.mocked(gateApi.master).mockResolvedValue(clear);
    renderWithClient(<GateBanner />);
    expect(await screen.findByText("CLEAR TO TRADE")).toBeInTheDocument();
    expect(screen.getByText(/NORMAL \(62.5\)/)).toBeInTheDocument();
    expect(screen.getByText(/Base\/Growth 60\/40/)).toBeInTheDocument();
    expect(screen.getByText(/\$98,500/)).toBeInTheDocument();
    expect(screen.getByText(/Not evaluated yet: BR-011, BR-013/)).toBeInTheDocument();
    expect(screen.queryByText(/enforcement is OFF/)).not.toBeInTheDocument();
  });

  it("shows BLOCKED with every reason, and says when a reason is unverified data", async () => {
    vi.mocked(gateApi.master).mockResolvedValue({
      ...clear,
      clear: false,
      status: "BLOCKED",
      growth_locked: true,
      reasons: [
        { rule_id: "BR-010", message: "The broader market is down.", kind: "block" },
        { rule_id: "BR-015", message: "Data unavailable: regime.", kind: "data" },
      ],
    });
    renderWithClient(<GateBanner />);
    expect(await screen.findByText("BLOCKED")).toBeInTheDocument();
    expect(screen.getByText(/The broader market is down\./)).toBeInTheDocument();
    expect(screen.getByText(/Data unavailable: regime\./)).toBeInTheDocument();
    expect(screen.getByText("(could not verify)")).toBeInTheDocument();
    expect(screen.getByText(/Growth layer locked/)).toBeInTheDocument();
  });

  it("treats a gate it cannot load as BLOCKED, never as clear", async () => {
    vi.mocked(gateApi.master).mockRejectedValue(new Error("network down"));
    renderWithClient(<GateBanner />);
    // The query retries once (with a short delay) before giving up, so allow for that.
    expect(await screen.findByText("BLOCKED", {}, { timeout: 4000 })).toBeInTheDocument();
    expect(screen.getByText(/treated as blocked/)).toBeInTheDocument();
    expect(screen.queryByText("CLEAR TO TRADE")).not.toBeInTheDocument();
  });

  it("warns when enforcement is switched off in Settings", async () => {
    vi.mocked(gateApi.master).mockResolvedValue({ ...clear, enforce_gate: false });
    renderWithClient(<GateBanner />);
    expect(await screen.findByText(/enforcement is OFF/)).toBeInTheDocument();
  });
});
