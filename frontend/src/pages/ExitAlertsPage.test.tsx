import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { alert, reason, SUMMARY_COUNTS } from "../test/fixtures";
import { renderWithRouter } from "../test/utils";
import { ExitAlertsPage } from "./ExitAlertsPage";

vi.mock("../api/endpoints", () => ({
  alertsApi: { exits: vi.fn(), ack: vi.fn(), acks: vi.fn() },
}));

import { alertsApi } from "../api/endpoints";

const exits = (alerts = [alert()], over = {}) => ({
  alerts,
  summary: SUMMARY_COUNTS,
  unacknowledged_critical: alerts.filter((a) => a.unacknowledged_critical).length,
  open_positions: alerts.length,
  ...over,
});

describe("Exit Alerts page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(alertsApi.exits).mockResolvedValue(exits() as never);
    vi.mocked(alertsApi.acks).mockResolvedValue({ data: [] } as never);
    vi.mocked(alertsApi.ack).mockResolvedValue({} as never);
  });

  it("lists alerts with the suggested action and the unacknowledged banner", async () => {
    renderWithRouter(<ExitAlertsPage />);
    expect(await screen.findByLabelText("AAPL critical alert")).toBeInTheDocument();
    expect(screen.getByText("Consider rolling")).toBeInTheDocument();
    expect(screen.getByText(/assignment alarm/)).toBeInTheDocument();
    expect(screen.getByText(/1 critical alert\(s\) need your acknowledgement/)).toBeInTheDocument();
  });

  it("acknowledges every pending critical/warning reason of a position", async () => {
    const two = alert({
      reasons: [reason(), reason({ code: "itm", severity: "warning", rule_id: "BR-051", message: "In the money." })],
    });
    vi.mocked(alertsApi.exits).mockResolvedValue(exits([two]) as never);
    renderWithRouter(<ExitAlertsPage />);
    await userEvent.click(await screen.findByRole("button", { name: "Acknowledge (2)" }));
    await waitFor(() => expect(alertsApi.ack).toHaveBeenCalledTimes(2));
    expect(alertsApi.ack).toHaveBeenCalledWith({ trade_id: "t1", code: "assignment_risk" });
    expect(alertsApi.ack).toHaveBeenCalledWith({ trade_id: "t1", code: "itm" });
  });

  it("hides the acknowledge button once reasons are acknowledged", async () => {
    const done = alert({ reasons: [reason({ acknowledged: true })], unacknowledged_critical: false });
    vi.mocked(alertsApi.exits).mockResolvedValue(exits([done]) as never);
    renderWithRouter(<ExitAlertsPage />);
    expect(await screen.findByText("Acknowledged")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Acknowledge/ })).not.toBeInTheDocument();
    expect(screen.queryByText(/need your acknowledgement/)).not.toBeInTheDocument();
  });

  it("shows an error when an acknowledgement fails", async () => {
    vi.mocked(alertsApi.ack).mockRejectedValue(new Error("nope"));
    renderWithRouter(<ExitAlertsPage />);
    await userEvent.click(await screen.findByRole("button", { name: "Acknowledge" }));
    expect(await screen.findByText("Could not acknowledge. Try again.")).toBeInTheDocument();
  });

  it("re-queries with the chosen severity filter", async () => {
    renderWithRouter(<ExitAlertsPage />);
    await screen.findByLabelText("AAPL critical alert");
    await userEvent.selectOptions(screen.getByLabelText("Show"), "critical");
    await waitFor(() => expect(alertsApi.exits).toHaveBeenCalledWith("critical"));
  });

  it("explains empty states differently for no positions vs no alerts", async () => {
    vi.mocked(alertsApi.exits).mockResolvedValue(exits([], { open_positions: 0 }) as never);
    const { unmount } = renderWithRouter(<ExitAlertsPage />);
    expect(await screen.findByText(/no open positions/)).toBeInTheDocument();
    unmount();
    vi.mocked(alertsApi.exits).mockResolvedValue(exits([], { open_positions: 3 }) as never);
    renderWithRouter(<ExitAlertsPage />);
    expect(await screen.findByText(/No alerts at this level/)).toBeInTheDocument();
  });

  it("shows an error when alerts cannot load", async () => {
    vi.mocked(alertsApi.exits).mockRejectedValue(new Error("boom"));
    renderWithRouter(<ExitAlertsPage />);
    expect(await screen.findByText("Could not load alerts. Try refreshing.")).toBeInTheDocument();
  });
});
