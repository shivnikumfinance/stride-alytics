import { ExposureChart } from "../components/charts";
import { GateBanner } from "../components/gate";
import { Badge, Card, PageHeader, SeverityBadge } from "../components/ui";
import { useBands, useExitAlerts, usePortfolioRisk } from "../hooks/queries";
import type { Severity } from "../types";
import { classNames, fmtUsd } from "../utils";

/** A horizontal gauge: the fill is the value against its limit; it turns amber then red. */
function Gauge({ label, value, limit, detail }: { label: string; value: number | null; limit: number; detail: string }) {
  const ratio = value === null ? 0 : Math.min(value / limit, 1);
  const tone = value === null ? "bg-gray-300" : ratio >= 1 ? "bg-red-500" : ratio >= 0.8 ? "bg-amber-500" : "bg-green-500";
  const status = value === null ? "unavailable" : ratio >= 1 ? "at or over the limit" : ratio >= 0.8 ? "near the limit" : "within the limit";
  return (
    <div>
      <div className="mb-1 flex items-baseline justify-between text-sm">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium text-gray-900">{value === null ? "—" : `${value}%`} of {limit}% limit</span>
      </div>
      <div
        role="meter"
        aria-label={label}
        aria-valuemin={0}
        aria-valuemax={limit}
        aria-valuenow={value ?? 0}
        aria-valuetext={`${value === null ? "unavailable" : `${value}%`}, ${status}`}
        className="h-3 overflow-hidden rounded-full bg-gray-100"
      >
        <div className={classNames("h-full", tone)} style={{ width: `${ratio * 100}%` }} />
      </div>
      <p className="mt-1 text-xs text-gray-500">{detail}</p>
    </div>
  );
}

const ORDER: Severity[] = ["critical", "warning", "watch", "normal"];

export function HeatDashboardPage() {
  const risk = usePortfolioRisk();
  const bands = useBands();
  const alerts = useExitAlerts("normal");
  const r = risk.data;

  return (
    <div className="space-y-4">
      <PageHeader
        title="Heat Dashboard"
        subtitle="How hot is your portfolio? Risk against limits, exposure by sector and band, and position health."
      />
      <GateBanner />

      {risk.isLoading ? (
        <p className="text-sm text-gray-500">Loading risk…</p>
      ) : risk.isError || !r ? (
        <p role="alert" className="text-sm text-red-600">
          Could not load the portfolio risk. Try refreshing.
        </p>
      ) : (
        <>
          {r.breaches.length > 0 && (
            <ul role="alert" className="space-y-1 rounded-md border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-900">
              {r.breaches.map((b) => (
                <li key={b.code + b.message}>
                  <span className="mr-2 font-mono text-xs">{b.rule_id}</span>
                  {b.message}
                </li>
              ))}
            </ul>
          )}
          {r.unpriced_positions > 0 && (
            <p role="status" className="rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900">
              {r.unpriced_positions} position(s) could not be priced, so Net Delta leaves them out.
            </p>
          )}

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <Card title="Risk gauges" subtitle="Margin % is capital at risk as a share of equity (there is no broker margin feed).">
              <div className="space-y-5">
                <Gauge
                  label="Margin (capital at risk)"
                  value={r.margin_pct}
                  limit={r.limits.capital_at_risk_pct}
                  detail={`${fmtUsd(r.capital_at_risk)} at risk on ${r.open_positions} open position(s). New entries are blocked above the limit.`}
                />
                <Gauge
                  label="Net delta exposure"
                  value={r.net_delta_pct}
                  limit={r.limits.net_delta_pct}
                  detail={`Net delta ${r.net_delta} shares (${fmtUsd(r.net_delta_dollars)}). Positive means the book gains if prices rise.`}
                />
              </div>
            </Card>

            <Card title="Exposure by sector" subtitle={`Limit ${r.limits.sector_risk_pct}% of equity per sector.`}>
              {r.sectors.length === 0 ? (
                <p className="text-sm text-gray-600">No open positions, so no exposure.</p>
              ) : (
                <ExposureChart sectors={r.sectors} limitPct={r.limits.sector_risk_pct} />
              )}
            </Card>
          </div>
        </>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card title="Capital bands" subtitle="Capital at risk per band against its cap.">
          {bands.isLoading ? (
            <p className="text-sm text-gray-500">Loading…</p>
          ) : bands.isError ? (
            <p role="alert" className="text-sm text-red-600">
              Could not load band usage.
            </p>
          ) : (
            <ul className="space-y-2">
              {(bands.data ?? []).map((b) => (
                <li key={b.band} className="flex items-center justify-between text-sm">
                  <span>Band {b.band}</span>
                  <span className="text-gray-600">
                    {b.exposure_pct}% of {b.cap_pct}% cap{" "}
                    <Badge tone={b.status === "ok" ? "green" : b.status === "near" ? "yellow" : "red"}>{b.status}</Badge>
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Position health" subtitle="Open positions by alert level.">
          {alerts.isLoading ? (
            <p className="text-sm text-gray-500">Loading…</p>
          ) : alerts.isError || !alerts.data ? (
            <p role="alert" className="text-sm text-red-600">
              Could not load position health.
            </p>
          ) : alerts.data.open_positions === 0 ? (
            <p className="text-sm text-gray-600">No open positions.</p>
          ) : (
            <ul className="space-y-2">
              {ORDER.map((s) => (
                <li key={s} className="flex items-center justify-between text-sm">
                  <SeverityBadge severity={s} />
                  <span className="font-medium">{alerts.data!.summary[s]}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
