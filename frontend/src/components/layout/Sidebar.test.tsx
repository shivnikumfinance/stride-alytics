import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { SUMMARY_COUNTS } from "../../test/fixtures";
import { renderWithRouter } from "../../test/utils";
import { Sidebar } from "./Sidebar";

vi.mock("../../api/endpoints", () => ({
  alertsApi: { exits: vi.fn() },
}));

import { alertsApi } from "../../api/endpoints";

const exits = (n: number) =>
  ({ alerts: [], summary: SUMMARY_COUNTS, unacknowledged_critical: n, open_positions: n }) as never;

const render = (route = "/") => renderWithRouter(<Sidebar open onClose={() => {}} />, route);

describe("Sidebar", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(alertsApi.exits).mockResolvedValue(exits(0));
  });

  it("shows Home and the four primary sections", async () => {
    render();
    for (const name of ["Home", "Exit Alerts", "Weekly Picks", "Active Holdings", "Strategy Matrix"]) {
      expect(await screen.findByRole("link", { name })).toBeInTheDocument();
    }
  });

  it("keeps Tools & Analytics collapsed by default and toggles it", async () => {
    render();
    const toggle = await screen.findByRole("button", { name: /Tools & Analytics/ });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    expect(screen.queryByRole("link", { name: "Watchlist" })).not.toBeInTheDocument();

    await userEvent.click(toggle);
    expect(toggle).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByRole("link", { name: "Watchlist" })).toBeInTheDocument();

    await userEvent.click(toggle);
    expect(screen.queryByRole("link", { name: "Watchlist" })).not.toBeInTheDocument();
  });

  it("opens the tools group when you are on a tool page", async () => {
    render("/sizing");
    expect(await screen.findByRole("button", { name: /Tools & Analytics/ })).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByRole("link", { name: "Position Sizing" })).toBeInTheDocument();
  });

  it("badges Exit Alerts with the number of unacknowledged critical alerts", async () => {
    vi.mocked(alertsApi.exits).mockResolvedValue(exits(2));
    render();
    expect(await screen.findByLabelText("2 critical alerts to acknowledge")).toHaveTextContent("2");
    expect(alertsApi.exits).toHaveBeenCalledWith("critical");
  });

  it("shows no badge when nothing needs acknowledgement", async () => {
    render();
    await screen.findByRole("link", { name: "Exit Alerts" });
    expect(screen.queryByLabelText(/critical alert/)).not.toBeInTheDocument();
  });
});
