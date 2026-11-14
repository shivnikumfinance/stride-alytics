import { AlertTriangle } from "lucide-react";

import { Badge, Card, PageHeader, SeverityBadge, Table } from "../components/ui";
import { useExitAlerts } from "../hooks/queries";
import { fmtUsd } from "../utils";
import type { PositionAlert, SuggestedAction } from "../types";

const ACTION_TONE: Record<SuggestedAction, "gray" | "green" | "yellow" | "blue"> = {
  hold: "gray",
  close: "green",
  roll: "yellow",
  hedge: "blue",
};

function contract(a: PositionAlert): string {
  if (a.trade_type === "stock") return "stock";
  const d = a.strategy_detail;
  return `${a.trade_type} ${d.strike ?? ""}${d.expiry ? ` · ${d.expiry}` : ""}`;
}

export function ActiveHoldingsPage() {
  const q = useExitAlerts("normal");
  const rows = q.data?.alerts ?? [];
  const priced = rows.filter((r) => r.pnl !== null);
  const totalPnl = priced.reduce((sum, r) => sum + (r.pnl ?? 0), 0);

  return (
    <div className="space-y-4">
      <PageHeader
        title="Active Holdings & Trade Alerts"
        subtitle="Every open position with its alert status, suggested action and Greeks."
      />

      {q.isError && (
        <p role="alert" className="text-sm text-red-600">
          Could not load your positions. Try refreshing.
        </p>
      )}

      <Card
        subtitle={
          q.data
            ? `${rows.length} open · total P&L ${fmtUsd(totalPnl)}${priced.length < rows.length ? " (some positions could not be priced)" : ""}`
            : undefined
        }
        bodyClassName="p-0"
      >
        <Table<PositionAlert>
          loading={q.isLoading}
          rows={rows}
          rowKey={(r) => r.trade_id}
          empty="No open positions. Add a trade on the Portfolio page."
          columns={[
            { key: "symbol", header: "Symbol", render: (r) => <span className="font-semibold text-blue-600">{r.symbol}</span> },
            { key: "contract", header: "Position", render: (r) => `${r.direction} ${r.quantity} × ${contract(r)}` },
            {
              key: "alert",
              header: "Alert",
              render: (r) => (
                <div className="flex items-center gap-1.5">
                  {r.severity !== "normal" && <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />}
                  <SeverityBadge severity={r.severity} />
                  <span className="text-xs text-gray-600">{r.reasons[0]?.message ?? "Within limits"}</span>
                </div>
              ),
            },
            {
              key: "pnl",
              header: "P&L",
              align: "right",
              render: (r) =>
                r.pnl === null ? (
                  "—"
                ) : (
                  <span className={r.pnl >= 0 ? "text-green-700" : "text-red-700"}>
                    {r.pnl >= 0 ? "+" : ""}
                    {fmtUsd(r.pnl)}
                  </span>
                ),
            },
            {
              key: "pct",
              header: "P&L %",
              align: "right",
              render: (r) => (r.pnl_pct === null ? "—" : `${(r.pnl_pct * 100).toFixed(1)}%`),
            },
            { key: "dte", header: "DTE", align: "right", render: (r) => r.dte ?? "—" },
            { key: "delta", header: "Delta", align: "right", render: (r) => (r.delta === null ? "—" : r.delta.toFixed(2)) },
            { key: "theta", header: "Theta", align: "right", render: (r) => (r.theta === null ? "—" : r.theta.toFixed(2)) },
            {
              key: "action",
              header: "Action",
              render: (r) => <Badge tone={ACTION_TONE[r.action]}>{r.action}</Badge>,
            },
          ]}
        />
      </Card>
    </div>
  );
}
