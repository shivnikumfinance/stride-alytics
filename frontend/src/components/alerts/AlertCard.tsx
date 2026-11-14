import { Link } from "react-router-dom";

import { useAckAlerts } from "../../hooks/queries";
import { fmtUsd } from "../../utils";
import type { PositionAlert, SuggestedAction } from "../../types";
import { SEVERITY_BORDER } from "../../utils/severity";
import { Badge, Button, SeverityBadge } from "../ui";

const ACTION_LABEL: Record<SuggestedAction, string> = {
  hold: "Hold",
  roll: "Consider rolling",
  close: "Consider closing",
  hedge: "Consider hedging",
};

function describe(a: PositionAlert): string {
  const d = a.strategy_detail;
  const kind = a.trade_type === "stock" ? "stock" : `${a.trade_type}${d.strike ? ` ${d.strike}` : ""}`;
  return `${a.direction} ${a.quantity} × ${kind}${d.expiry ? ` · exp ${d.expiry}` : ""}`;
}

/** One position with its alerts, suggested action and acknowledgement (BR-095–098). */
export function AlertCard({ alert }: { alert: PositionAlert }) {
  const ack = useAckAlerts();

  // Critical reasons still need an explicit acknowledgement; warnings can also be acknowledged.
  const pending = alert.reasons.filter((r) => (r.severity === "critical" || r.severity === "warning") && r.acknowledged === false);

  return (
    <article
      aria-label={`${alert.symbol} ${alert.severity} alert`}
      className={`rounded-lg border border-gray-200 border-l-4 bg-white p-4 ${SEVERITY_BORDER[alert.severity]}`}
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 className="text-base font-semibold text-gray-900">
            {alert.symbol} <SeverityBadge severity={alert.severity} />
          </h3>
          <p className="text-sm text-gray-500">{describe(alert)}</p>
        </div>
        <div className="text-right text-sm">
          <Badge tone={alert.action === "hold" ? "gray" : "indigo"}>{ACTION_LABEL[alert.action]}</Badge>
          {alert.severity === "critical" && alert.unacknowledged_critical && (
            <p className="mt-1 text-xs font-medium text-red-700">Needs acknowledgement</p>
          )}
        </div>
      </div>

      <ul className="mt-3 space-y-1 text-sm">
        {alert.reasons.map((r) => (
          <li key={r.code} className="flex items-start gap-2">
            <SeverityBadge severity={r.severity} />
            <span className="flex-1">
              {r.message}
              {r.rule_id && <span className="ml-1 font-mono text-xs text-gray-400">{r.rule_id}</span>}
            </span>
            {r.acknowledged === true && <span className="text-xs text-green-700">Acknowledged</span>}
          </li>
        ))}
      </ul>

      <dl className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs text-gray-600">
        <div>
          <dt>P&amp;L</dt>
          <dd className={`font-medium ${(alert.pnl ?? 0) >= 0 ? "text-green-700" : "text-red-700"}`}>
            {alert.pnl === null ? "—" : fmtUsd(alert.pnl)}
          </dd>
        </div>
        <div>
          <dt>Days to expiry</dt>
          <dd className="font-medium">{alert.dte ?? "—"}</dd>
        </div>
        <div>
          <dt>Delta</dt>
          <dd className="font-medium">{alert.delta === null ? "—" : alert.delta.toFixed(2)}</dd>
        </div>
        <div>
          <dt>Theta / day</dt>
          <dd className="font-medium">{alert.theta === null ? "—" : fmtUsd(alert.theta)}</dd>
        </div>
      </dl>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        {pending.length > 0 && (
          <Button
            size="sm"
            variant={alert.severity === "critical" ? "danger" : "secondary"}
            loading={ack.isPending}
            onClick={() =>
              ack.mutate(pending.map((r) => ({ trade_id: alert.trade_id, code: r.code })))
            }
          >
            Acknowledge{pending.length > 1 ? ` (${pending.length})` : ""}
          </Button>
        )}
        <Link to="/portfolio" className="text-sm text-indigo-600 hover:underline">
          Open in Portfolio to close
        </Link>
        {ack.isError && (
          <span role="alert" className="text-sm text-red-600">
            Could not acknowledge. Try again.
          </span>
        )}
      </div>
    </article>
  );
}
