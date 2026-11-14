import type { GateReason } from "../../types";

interface Props {
  clear: boolean;
  status?: string;
  reasons: GateReason[];
  notEvaluated?: string[];
  message?: string;
}

/** Shows one gate result: CLEAR TO TRADE / BLOCKED and every reason. */
export function GateResultPanel({ clear, status, reasons, notEvaluated = [], message }: Props) {
  const label = status ?? (clear ? "CLEAR TO TRADE" : "BLOCKED");
  const tone = clear
    ? "border-green-300 bg-green-50 text-green-900"
    : "border-red-300 bg-red-50 text-red-900";
  return (
    <div role="status" className={`rounded-md border px-3 py-2 text-sm ${tone}`}>
      <p className="font-semibold tracking-wide">{label}</p>
      {message && <p className="mt-1">{message}</p>}
      {reasons.length > 0 && (
        <ul className="mt-1 list-disc pl-5 space-y-0.5">
          {reasons.map((r, i) => (
            <li key={`${r.rule_id}-${i}`}>
              <span className="font-mono text-xs mr-1">{r.rule_id}</span>
              {r.message}
              {r.kind === "data" && <span className="ml-1 text-xs italic">(could not verify)</span>}
            </li>
          ))}
        </ul>
      )}
      {notEvaluated.length > 0 && (
        <p className="mt-1 text-xs opacity-75">Not evaluated yet: {notEvaluated.join(", ")}</p>
      )}
    </div>
  );
}
