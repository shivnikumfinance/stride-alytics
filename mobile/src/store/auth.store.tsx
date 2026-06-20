import { create } from "zustand";
import client, { tokenStore } from "../api/client";

const useAuthStore = create((set) => ({
  user: null,
  token: null,
  loading: false,
  error: null,

  hydrate: async () => {
    const t = await tokenStore.get();
    if (t) set({ token: t });
  },

  login: async ({ email, password }) => {
    set({ loading: true, error: null });
    try {
      const response = await client.post("/auth/login", { email, password });
      const data = response.data;
      await tokenStore.set(data.access_token);
      set({
        user: { id: data.user_id, email: data.email, subscription_plan: data.subscription_plan },
        token: data.access_token,
        loading: false,
      });
    } catch (err) {
      set({
        loading: false,
        error: err?.response?.data?.detail || err?.response?.data?.error?.message || "Login failed",
      });
      throw err;
    }
  },

  signup: async ({ email, password, full_name }) => {
    set({ loading: true, error: null });
    try {
      const response = await client.post("/auth/signup", { email, password, full_name });
      const data = response.data;
      await tokenStore.set(data.access_token);
      set({
        user: { id: data.user_id, email: data.email, subscription_plan: data.subscription_plan },
        token: data.access_token,
        loading: false,
      });
    } catch (err) {
      set({
        loading: false,
        error: err?.response?.data?.detail || err?.response?.data?.error?.message || "Signup failed",
      });
      throw err;
    }
  },

  logout: async () => {
    await tokenStore.clear();
    set({ user: null, token: null });
  },
}));

export { useAuthStore };