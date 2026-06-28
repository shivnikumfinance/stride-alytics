/** Mirrors `backend/app/api/v1/schemas/auth.py`. */

import type { SubscriptionPlan } from "./common";

export interface User {
  id: string;
  email: string;
  full_name?: string;
  subscription_plan: SubscriptionPlan;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string | null;
  token_type: "bearer";
  expires_in: number;
  user_id: string;
  email?: string;
  subscription_plan: SubscriptionPlan;
}
