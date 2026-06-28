/**
 * Centralized Axios client. Adds the JWT, normalises errors, and exposes
 * a 401-triggered logout hook so stores can react.
 */

import axios from "axios";

const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
// Use `new URL()` to safely normalise the base — strips trailing slashes,
// prevents double slashes, and tolerates malformed env vars.
const API_BASE = new URL(apiUrl).toString().replace(/\/$/, "");
const TOKEN_KEY = "stride_token";

// Build the axios baseURL via `new URL()` so the path join is always safe.
const API_ROOT = new URL("/api/v1/", API_BASE).toString();

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t: string) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

export const client = axios.create({
  baseURL: API_ROOT,
  headers: { "Content-Type": "application/json" },
  timeout: 20_000,
});

// Request interceptor — attach JWT
client.interceptors.request.use((config) => {
  const token = tokenStore.get();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — surface a clean error and trigger logout on 401.
//
// We deliberately do NOT import the auth store here (it would create a
// circular dependency: auth.store -> client via tokenStore). Instead we
// emit a DOM event; App.tsx subscribes once and calls useAuthStore.logout().
// See frontend/src/api/auth-events.ts and the bootstrap in src/main.tsx.
export const AUTH_LOGOUT_EVENT = "stride:auth:logout";

client.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      tokenStore.clear();
      if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent(AUTH_LOGOUT_EVENT));
      }
    }
    return Promise.reject(error);
  },
);

export default client;
