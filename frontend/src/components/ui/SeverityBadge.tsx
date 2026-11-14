import type { Severity } from "../../types";
import { Badge } from "./Badge";

const TONE = { normal: "green", watch: "blue", warning: "yellow", critical: "red" } as const;
const LABEL = { normal: "Normal", watch: "Watch", warning: "Warning", critical: "Critical" } as const;

/** Colour-coded alert severity (BR-095): Normal, Watch, Warning, Critical. */
export function SeverityBadge({ severity }: { severity: Severity }) {
  return <Badge tone={TONE[severity]}>{LABEL[severity]}</Badge>;
}
