import { describe, expect, it } from "vitest";

import { filenameFromDisposition } from "./download";

describe("filenameFromDisposition", () => {
  it("reads quoted and unquoted filenames", () => {
    expect(filenameFromDisposition('attachment; filename="trades.csv"', "x.csv")).toBe("trades.csv");
    expect(filenameFromDisposition("attachment; filename=watchlist.csv", "x.csv")).toBe("watchlist.csv");
  });

  it("falls back when the header is missing or has no filename", () => {
    expect(filenameFromDisposition(undefined, "fallback.csv")).toBe("fallback.csv");
    expect(filenameFromDisposition("attachment", "fallback.csv")).toBe("fallback.csv");
  });
});
