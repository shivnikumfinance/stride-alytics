/**
 * Centralized API client for the mobile app.
 * Uses axios with JWT stored in expo-secure-store.
 */
import axios from "axios";
import * as SecureStore from "expo-secure-store";
import Constants from "expo-constants";

const API_BASE = Constants.expoConfig?.extra?.apiUrl || "http://localhost:8000";
const TOKEN_KEY = "stride_token";

export const tokenStore = {
  get: () => SecureStore.getItemAsync(TOKEN_KEY),
  set: (t) => SecureStore.setItemAsync(TOKEN_KEY, t),
  clear: () => SecureStore.deleteItemAsync(TOKEN_KEY),
};

export const client = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 20_000,
});

// Request interceptor — attach JWT
client.interceptors.request.use(async (config) => {
  try {
    const token = await tokenStore.get();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch {}
  return config;
});

// Response interceptor — trigger logout on 401
client.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) {
      await tokenStore.clear();
    }
    return Promise.reject(error);
  }
);

export default client;