import { useMasterGate } from "../../hooks/queries";
import { fmtUsd } from "../../utils";
import { GateResultPanel } from "./GateResultPanel";

/**
 * The Master Gate: CLEAR TO TRADE or BLOCKED, with every reason (docs: "gate-forward interface").
 * If the gate cannot be determined it is shown as BLOCKED — never assumed clear.
 */
export function GateBanner() {
  const gate = useMasterGate();

  if (gate.isLoading) {
    return (
      <div className="rounded-md border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-500">
        Checking the Do-Not-Trade gate…
      </div>
    );
  }
  if (gate.isError || !gate.data) {
    return (
      <GateResultPanel
        clear={false}
        reasons={[{ rule_id: "GATE", message: "The gate could not be determined, so trading is treated as blocked.", kind: "data" }]}
      />
    );
  }

  const g = gate.data;
  return (
    <div className="space-y-1">
      <GateResultPanel
        clear={g.clear}
        status={g.status}
        reasons={g.reasons}
        notEvaluated={g.not_evaluated}
      />
      <p className="text-xs text-gray-500">
        Regime{" "}
        <strong>
          {g.regime.state}
          {g.regime.score !== null && ` (${g.regime.score})`}
        </strong>
        {" · "}Base/Growth {g.layer_split.base}/{g.layer_split.growth}
        {g.growth_locked && " · Growth layer locked"}
        {" · "}Equity {fmtUsd(g.equity)}
        {!g.enforce_gate && " · Gate enforcement is OFF in Settings"}
      </p>
    </div>
  );
}
