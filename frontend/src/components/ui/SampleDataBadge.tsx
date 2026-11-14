import { Badge } from "./Badge";

/** Marks values that came from a placeholder fallback, not live market data. */
export function SampleDataBadge({ source }: { source?: string }) {
  if (!source || source === "live") return null;
  return (
    <Badge tone="yellow" className="uppercase" >
      Sample data — not live
    </Badge>
  );
}
