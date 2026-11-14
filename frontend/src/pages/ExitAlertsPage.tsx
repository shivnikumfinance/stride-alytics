import { useState } from "react";

import { AlertCard } from "../components/alerts";
import { Badge, Card, PageHeader, Select, SeverityBadge, Table } from "../components/ui";
import { useAlertHistory, useExitAlerts } from "../hooks/queries";
import type { AckRecord, Severity } from "../types";

const FILTERS: { value: Severity; label: string }[] = [
  { value: "watch", label: "Watch and above" },
  { value: "warning", label: "Warning and above" },
  { value: "critical", label: "Critical only" },
];

export function ExitAlertsPage() {
  const [minSeverity, setMinSeverity] = useState<Severity>("watch");
  const alerts = useExitAlerts(minSeverity);
  const history = useAlertHistory(10);
  const data = alerts.data;

  return (
    <div className="space-y-4">
      <PageHeader
        title="Exit Alerts & Recommendations"
        subtitle="Open positions that need attention, with a suggested action. Critical alerts must be acknowledged."
      />

      {data && data.unacknowledged_critical > 0 && (
        <p role="alert" className="rounded-md border border-red-300 bg-red-50 px-3 py-2 text-sm font-medium text-red-900">
          {data.unacknowledged_critical} critical alert(s) need your acknowledgement.
        </p>
      )}

      <div className="flex flex-wrap items-end justify-between gap-3">
        <Select label="Show" value={minSeverity} onChange={(e) => setMinSeverity(e.target.value as Severity)}>
          {FILTERS.map((f) => (
            <option key={f.value} value={f.value}>
              {f.label}
            </option>
          ))}
        </Select>
        {data && (
          <p className="text-sm text-gray-600">
            {data.open_positions} open position{data.open_positions === 1 ? "" : "s"} ·{" "}
            {(["critical", "warning", "watch"] as const).map((s) => (
              <span key={s} className="mr-2 inline-flex items-center gap-1">
                <SeverityBadge severity={s} /> {data.summary[s]}
              </span>
            ))}
          </p>
        )}
      </div>

      {alerts.isLoading ? (
        <p className="text-sm text-gray-500">Loading alerts…</p>
      ) : alerts.isError || !data ? (
        <p role="alert" className="text-sm text-red-600">
          Could not load alerts. Try refreshing.
        </p>
      ) : data.alerts.length === 0 ? (
        <Card>
          <p className="text-sm text-gray-600">
            {data.open_positions === 0
              ? "You have no open positions, so there is nothing to alert on."
              : "No alerts at this level. Your open positions are within their limits."}
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          {data.alerts.map((a) => (
            <AlertCard key={a.trade_id} alert={a} />
          ))}
        </div>
      )}

      <Card title="Acknowledgement history" subtitle="An acknowledgement is resolved when the alert clears or the position closes.">
        <Table<AckRecord>
          loading={history.isLoading}
          rows={history.data?.data ?? []}
          rowKey={(r) => r.id}
          empty="Nothing acknowledged yet."
          columns={[
            { key: "when", header: "When", render: (r) => new Date(r.acknowledged_at).toLocaleString() },
            { key: "code", header: "Alert", render: (r) => <span className="font-mono text-xs">{r.code}</span> },
            { key: "sev", header: "Severity", render: (r) => <SeverityBadge severity={r.severity} /> },
            {
              key: "status",
              header: "Status",
              render: (r) => (r.resolved_at ? <Badge tone="gray">Resolved</Badge> : <Badge tone="green">Active</Badge>),
            },
          ]}
        />
      </Card>
    </div>
  );
}
