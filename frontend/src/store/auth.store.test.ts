import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/endpoints", () => ({
  authApi: { me: vi.fn(), login: vi.fn(), signup: vi.fn() },
}));

import { authApi } from "../api/endpoints";
import { tokenStore } from "../api/client";
import { useAuthStore } from "./auth.store";

const reset = () => useAuthStore.setState({ user: null, token: null, loading: false, error: null });

describe("auth store hydrate", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    reset();
  });

  it("does nothing without a stored token", async () => {
    await useAuthStore.getState().hydrate();
    expect(useAuthStore.getState()).toMatchObject({ user: null, token: null });
    expect(authApi.me).not.toHaveBeenCalled();
  });

  it("restores the token and who is signed in after a reload", async () => {
    tokenStore.set("abc");
    vi.mocked(authApi.me).mockResolvedValue({ success: true, data: { user_id: "u1", email: "me@example.com" } });
    await useAuthStore.getState().hydrate();
    expect(useAuthStore.getState()).toMatchObject({ token: "abc", user: { id: "u1", email: "me@example.com" } });
  });

  it("keeps the token and an empty user when /auth/me fails for another reason", async () => {
    tokenStore.set("abc");
    vi.mocked(authApi.me).mockRejectedValue(new Error("network"));
    await useAuthStore.getState().hydrate();
    expect(useAuthStore.getState()).toMatchObject({ token: "abc", user: null });
  });

  it("uses an empty email when the token has none", async () => {
    tokenStore.set("abc");
    vi.mocked(authApi.me).mockResolvedValue({ success: true, data: { user_id: "u1", email: null } });
    await useAuthStore.getState().hydrate();
    expect(useAuthStore.getState().user).toEqual({ id: "u1", email: "" });
  });
});
