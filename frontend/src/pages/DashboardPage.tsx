import { Link } from "react-router-dom";

import { GateBanner } from "../components/gate";
import { Badge, Card, PageHeader, SeverityBadge } from "../components/ui";
import { useDashboardSummary } from "../hooks/queries";
import { fmtUsd } from "../utils";
import type { RegimeState, Severity } from "../types";

const REGIME_TONE: Record<RegimeState, "red" | "blue" | "green" | "gray"> = {
  DEFENSIVE: "red",
  NORMAL: "blue",
  GROWTH: "green",
  UNKNOWN: "gray",
};
const SEVERITIES: Severity[] = ["critical", "warning", "watch"];

function FullScreenLink({ to }: { to: string }) {
  return (
    <Link to={to} className="text-sm text-indigo-600 hover:underline">
      View full screen →
    </Link>
  );
}

function MetricCard({ label, value, note, tone }: { label: string; value: string; note: string; tone?: "green" | "red" }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <p className="text-xs text-gray-500">{label}</p>
      <p className={`mt-1 text-2xl font-bold ${tone === "green" ? "text-green-700" : tone === "red" ? "text-red-700" : "text-gray-900"}`}>
        {value}
      </p>
      <p className="mt-1 text-xs text-gray-500">{note}</p>
    </div>
  );
}

export function DashboardPage() {
  const summary = useDashboardSummary();
  const d = summary.data;

  return (
    <div className="space-y-4">
      <PageHeader title="Home" subtitle="Your command center: gate, risk and what needs attention." />
      <GateBanner />

      {summary.isLoading ? (
        <p className="text-sm text-gray-500">Loading your summary…</p>
      ) : summary.isError || !d ? (
        <p role="alert" className="text-sm text-red-600">
          Could not load your summary. Try refreshing.
        </p>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <MetricCard
              label="Portfolio Value"
              value={fmtUsd(d.metrics.portfolio_value)}
              note={`Cash available ${fmtUsd(d.metrics.cash_available)}${d.metrics.unrealized_complete ? "" : " · some positions could not be priced"}`}
            />
            <MetricCard
              label="Total P&L (Active)"
              value={fmtUsd(d.metrics.unrealized_pnl)}
              note={`${d.metrics.open_trades} open trade${d.metrics.open_trades === 1 ? "" : "s"} · realised ${fmtUsd(d.metrics.realized_pnl)}`}
              tone={d.metrics.unrealized_pnl >= 0 ? "green" : "red"}
            />
            <MetricCard
              label="Options Buying Power"
              value={fmtUsd(d.metrics.options_buying_power)}
              note={
                d.metrics.utilization_pct === null
                  ? "Utilisation unavailable"
                  : `${d.metrics.utilization_pct}% utilised · ${fmtUsd(d.metrics.capital_at_risk)} at risk`
              }
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card title="Exit Alerts & Recommendations" actions={<FullScreenLink to="/exit-alerts" />}>
              <div className="flex flex-wrap gap-2 mb-3">
                {SEVERITIES.map((s) => (
                  <span key={s} className="inline-flex items-center gap-1 text-sm">
                    <SeverityBadge severity={s} /> {d.alerts.summary[s]}
                  </span>
                ))}
              </div>
              {d.alerts.unacknowledged_critical > 0 && (
                <p role="alert" className="mb-2 text-sm font-medium text-red-700">
                  {d.alerts.unacknowledged_critical} critical alert(s) need acknowledgement.
                </p>
              )}
              {d.alerts.top.length === 0 ? (
                <p className="text-sm text-gray-500">No alerts right now.</p>
              ) : (
                <ul className="space-y-2 text-sm">
                  {d.alerts.top.map((a) => (
                    <li key={a.trade_id} className="flex items-start gap-2">
                      <SeverityBadge severity={a.severity} />
                      <span>
                        <strong>{a.symbol}</strong> — {a.reasons[0]?.message}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            <Card
              title="Top Weekly Picks"
              subtitle={d.picks.week_of ? `Week of ${d.picks.week_of}` : undefined}
              actions={<FullScreenLink to="/picks" />}
            >
              {d.picks.top.length === 0 ? (
                <p className="text-sm text-gray-500">No picks yet. They are generated weekly.</p>
              ) : (
                <ul className="space-y-2 text-sm">
                  {d.picks.top.map((p) => (
                    <li key={p.id} className="flex items-center justify-between">
                      <span>
                        <strong>{p.symbol}</strong> {p.side.toUpperCase()}
                        {p.strike ? ` ${p.strike}` : ""}
                        {p.expiry ? ` · ${p.expiry}` : ""}
                      </span>
                      <Badge tone="indigo">{Math.round(p.confidence * 100)}%</Badge>
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            <Card title="Active Holdings & Trade Alerts" actions={<FullScreenLink to="/active-holdings" />}>
              {d.holdings.length === 0 ? (
                <p className="text-sm text-gray-500">No open positions.</p>
              ) : (
                <ul className="space-y-2 text-sm">
                  {d.holdings.map((h) => (
                    <li key={h.trade_id} className="flex items-center justify-between gap-2">
                      <span>
                        <strong>{h.symbol}</strong> {h.trade_type === "stock" ? "stock" : `${h.trade_type} ${h.strategy_detail.strike ?? ""}`}
                      </span>
                      <span className="flex items-center gap-2">
                        <span className={(h.pnl ?? 0) >= 0 ? "text-green-700" : "text-red-700"}>
                          {h.pnl === null ? "—" : fmtUsd(h.pnl)}
                        </span>
                        <SeverityBadge severity={h.severity} />
                      </span>
                    </li>
                  ))}
                </ul>
              )}
              {d.metrics.open_trades > d.holdings.length && (
                <p className="mt-2 text-xs text-gray-500">+ {d.metrics.open_trades - d.holdings.length} more</p>
              )}
            </Card>

            <Card title="Strategy Design Matrix" actions={<FullScreenLink to="/strategy-matrix" />}>
              <div className="flex items-center gap-2 text-sm">
                <span>Regime</span>
                <Badge tone={REGIME_TONE[d.regime.state]}>{d.regime.state}</Badge>
                {d.regime.score !== null && <span className="text-gray-500">score {d.regime.score}</span>}
              </div>
              <p className="mt-3 text-sm">
                Base / Growth split <strong>{d.regime.layer_split.base}</strong> / <strong>{d.regime.layer_split.growth}</strong>
              </p>
              {d.regime.growth_locked && (
                <p className="mt-1 text-sm text-red-700">The Growth layer is locked in this regime.</p>
              )}
              <p className="mt-3 text-xs text-gray-500">
                The full strategy × regime grid is on its own page.
              </p>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
