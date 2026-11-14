import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";

// jsdom has no ResizeObserver, which recharts' ResponsiveContainer needs. A no-op is enough:
// charts render with no size in tests, so tests check the surrounding text and aria labels.
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
globalThis.ResizeObserver ??= ResizeObserverStub as unknown as typeof ResizeObserver;

afterEach(() => cleanup());
