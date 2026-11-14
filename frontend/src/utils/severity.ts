import type { Severity } from "../types";

/** Left-border colour classes used on alert cards and rows. */
export const SEVERITY_BORDER: Record<Severity, string> = {
  normal: "border-l-green-400",
  watch: "border-l-blue-400",
  warning: "border-l-yellow-400",
  critical: "border-l-red-500",
};
