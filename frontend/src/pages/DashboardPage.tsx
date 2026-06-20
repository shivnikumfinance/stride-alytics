import { Card, Badge } from "../components/ui";
import { useScreenerLimits, useRegime } from "../hooks/queries";

export function DashboardPage() {
  const limits = useScreenerLimits();
  const regime = useRegime("SPY", 30);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500">Market snapshot and quick access to all tools.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title="Account" subtitle="Current plan & limits">
          {limits.data ? (
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Plan</span>
                <Badge tone="indigo" className="capitalize">{limits.data.data.plan}</Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Max screener results</span>
                <span className="font-medium">{limits.data.data.max_results_per_call.toLocaleString()}</span>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-500">Loading account…</p>
          )}
        </Card>

        <Card title="Market Regime (SPY)" subtitle="Last 30 trading days">
          {regime.data ? (
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-gray-500">Regime</span>
                <Badge
                  tone={regime.data.regime === "bull" ? "green" : regime.data.regime === "bear" ? "red" : "gray"}
                  className="uppercase"
                >
                  {regime.data.regime}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Confidence</span>
                <span className="font-medium">{(regime.data.confidence * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Return</span>
                <span
                  className={`font-medium ${regime.data.price_return >= 0 ? "text-green-700" : "text-red-700"}`}
                >
                  {(regime.data.price_return * 100).toFixed(2)}%
                </span>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-500">Loading regime…</p>
          )}
        </Card>

        <Card title="Quick actions">
          <ul className="text-sm space-y-2">
            <li>→ <a className="text-indigo-600 hover:underline" href="/screener">Run screener</a></li>
            <li>→ <a className="text-indigo-600 hover:underline" href="/greeks">Calculate Greeks</a></li>
            <li>→ <a className="text-indigo-600 hover:underline" href="/portfolio">View portfolio</a></li>
            <li>→ <a className="text-indigo-600 hover:underline" href="/picks">See weekly picks</a></li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
