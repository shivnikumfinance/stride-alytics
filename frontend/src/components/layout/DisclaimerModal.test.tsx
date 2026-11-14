import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithClient } from "../../test/utils";
import { DisclaimerModal } from "./DisclaimerModal";

vi.mock("../../api/endpoints", () => ({
  settingsApi: { get: vi.fn(), acceptDisclaimer: vi.fn() },
}));

import { settingsApi } from "../../api/endpoints";

const settings = (accepted: string | null) => ({ disclaimer_accepted_at: accepted }) as never;

describe("DisclaimerModal", () => {
  beforeEach(() => vi.clearAllMocks());

  it("is shown until accepted, then goes away", async () => {
    vi.mocked(settingsApi.get).mockResolvedValue(settings(null));
    vi.mocked(settingsApi.acceptDisclaimer).mockResolvedValue(settings("2026-06-01T00:00:00Z"));
    renderWithClient(<DisclaimerModal />);
    expect(await screen.findByRole("dialog", { name: "Before you start" })).toBeInTheDocument();
    expect(screen.getByText(/not financial advice/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "I understand" }));
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
    expect(settingsApi.acceptDisclaimer).toHaveBeenCalledTimes(1);
  });

  it("stays visible with an error when saving fails", async () => {
    vi.mocked(settingsApi.get).mockResolvedValue(settings(null));
    vi.mocked(settingsApi.acceptDisclaimer).mockRejectedValue(new Error("nope"));
    renderWithClient(<DisclaimerModal />);
    await userEvent.click(await screen.findByRole("button", { name: "I understand" }));
    expect(await screen.findByText("Could not save your acceptance. Try again.")).toBeInTheDocument();
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  it("is not shown once accepted", async () => {
    vi.mocked(settingsApi.get).mockResolvedValue(settings("2026-06-01T00:00:00Z"));
    renderWithClient(<DisclaimerModal />);
    await waitFor(() => expect(settingsApi.get).toHaveBeenCalled());
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("never blocks the app when settings fail to load", async () => {
    vi.mocked(settingsApi.get).mockRejectedValue(new Error("down"));
    renderWithClient(<DisclaimerModal />);
    await waitFor(() => expect(settingsApi.get).toHaveBeenCalled());
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
