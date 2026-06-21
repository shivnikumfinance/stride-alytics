/** Auth store — holds the JWT, current user, and login/logout actions. */

import { create } from "zustand";
import { authApi } from "../api/endpoints";
import { tokenStore } from "../api/client";
import type { LoginRequest, SignupRequest, TokenResponse, User } from "../types";

interface AuthStoreState {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  hydrate: () => void;
  login: (body: LoginRequest) => Promise<void>;
  signup: (body: SignupRequest) => Promise<void>;
  logout: () => void;
  devAdminLogin: () => void;
}

function persist(token: TokenResponse): User {
  tokenStore.set(token.access_token);
  return {
    id: token.user_id,
    email: token.email ?? "",
    subscription_plan: token.subscription_plan,
  };
}

export const adminUser: User = {
  id: "00000000-0000-0000-0000-000000000000",
  email: "admin@stridealytics.com",
  subscription_plan: "pro",
};

export const useAuthStore = create<AuthStoreState>((set) => ({
  user: null,
  token: null,
  loading: false,
  error: null,

  hydrate: () => {
    const t = tokenStore.get();
    if (t) set({ token: t });
  },

  login: async (body) => {
    set({ loading: true, error: null });
    try {
      const token = await authApi.login(body);
      const user = persist(token);
      set({ user, token: token.access_token, loading: false });
    } catch (err: any) {
      set({ loading: false, error: err?.response?.data?.error?.message ?? "Login failed" });
      throw err;
    }
  },

  signup: async (body) => {
    set({ loading: true, error: null });
    try {
      const token = await authApi.signup(body);
      const user = persist(token);
      set({ user, token: token.access_token, loading: false });
    } catch (err: any) {
      set({ loading: false, error: err?.response?.data?.error?.message ?? "Signup failed" });
      throw err;
    }
  },

  logout: () => {
    tokenStore.clear();
    set({ user: null, token: null });
  },

  devAdminLogin: () => {
    tokenStore.set("dev-admin-token");
    set({ user: adminUser, token: "dev-admin-token", loading: false, error: null });
  },
}));
