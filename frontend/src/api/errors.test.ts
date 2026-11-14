import { AxiosError, type AxiosResponse } from "axios";
import { describe, expect, it } from "vitest";

import { extractErrorMessage, extractGateReasons } from "./errors";

function axiosError(data: unknown, status = 409) {
  return new AxiosError("Request failed", "ERR_BAD_REQUEST", undefined, undefined, { status, data } as AxiosResponse);
}

describe("extractGateReasons", () => {
  it("reads the reasons from a blocked-trade response", () => {
    const reasons = [{ rule_id: "BR-021", message: "AAPL has a news flag set.", kind: "block" }];
    const err = axiosError({ success: false, error: { message: "Trade blocked", details: { reasons } } });
    expect(extractGateReasons(err)).toEqual(reasons);
    expect(extractErrorMessage(err)).toBe("Trade blocked");
  });

  it("is empty for any other error shape", () => {
    expect(extractGateReasons(new Error("x"))).toEqual([]);
    expect(extractGateReasons(axiosError({ error: { message: "nope" } }, 500))).toEqual([]);
    expect(extractGateReasons(axiosError({ error: { details: { reasons: "bad" } } }))).toEqual([]);
    expect(extractGateReasons("string")).toEqual([]);
  });
});
