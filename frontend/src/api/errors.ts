/**
 * API error helpers — single source of truth for turning thrown values
 * into human-readable messages.
 *
 * The backend follows the envelope defined in
 * docs/TECHNICAL/RULES/api-flow/API-FLOW.md § 9:
 *
 *   {
 *     "success": false,
 *     "error": {
 *       "type": "VALIDATION_ERROR",
 *       "status": 422,
 *       "message": "Invalid parameters",
 *       "details": { "symbol": "Symbol is required" }
 *     }
 *   }
 *
 * Use {@link extractErrorMessage} everywhere UI surfaces a backend error.
 * Use {@link withApiErrorLogging} in React Query `onError` handlers when
 * the call site doesn't need to display the message but does need to log
 * it once instead of letting it bubble into a React warning.
 */

import axios from "axios";

/**
 * Convert any thrown value into a human-readable message.
 *
 * Resolution order:
 *   1. Backend envelope `error.message` (when axios + our envelope shape)
 *   2. Axios `err.message` (network errors, timeouts, etc.)
 *   3. Generic `Error.message`
 *   4. The provided `fallback`
 *
 * Never returns an empty string — the worst case is `fallback`.
 */
export function extractErrorMessage(err: unknown, fallback = "Request failed"): string {
  if (axios.isAxiosError(err)) {
    const body = err.response?.data as { error?: { message?: string } } | undefined;
    const fromEnvelope = body?.error?.message?.trim();
    if (fromEnvelope) return fromEnvelope;
    if (err.message) return err.message;
    return fallback;
  }
  if (err instanceof Error && err.message) return err.message;
  return fallback;
}

/**
 * Wrap a React Query `onError` handler so failures are logged with the
 * extracted message instead of being silently swallowed.
 *
 *   onError: withApiErrorLogging("screener.run")
 */
export function withApiErrorLogging(
  context: string,
  fallback = "Request failed",
): (err: unknown) => void {
  return (err) => {
    console.error(`[${context}]`, extractErrorMessage(err, fallback));
  };
}
