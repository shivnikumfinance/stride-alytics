import { AlertTriangle } from "lucide-react";
import { PageHeader, Card, Badge } from "../components/ui";

export function ActiveHoldingsPage() {
  // Mock data - replace with real API call
  const holdings = [
    {
      symbol: "SPY",
      strategy: "Covered Call",
      alert: "Near max profit",
      pnl: 245.50,
      pnlPercent: 12.4,
      dte: 18,
      delta: 0.65,
      theta: -12.3,
      action: "Consider closing"
    },
    {
      symbol: "QQQ",
      strategy: "Iron Condor",
      alert: "Price approaching upper leg",
      pnl: -89.20,
      pnlPercent: -4.2,
      dte: 24,
      delta: 0.12,
      theta: 8.7,
      action: "Monitor closely"
    },
    {
      symbol: "IWM",
      strategy: "Cash-Secured Put",
      alert: "Stable",
      pnl: 156.80,
      pnlPercent: 6.8,
      dte: 32,
      delta: -0.45,
      theta: -5.2,
      action: "Hold"
    },
    {
      symbol: "AAPL",
      strategy: "Long Call",
      alert: "Earnings soon",
      pnl: 320.00,
      pnlPercent: 24.5,
      dte: 12,
      delta: 0.82,
      theta: -18.9,
      action: "Take profits"
    },
    {
      symbol: "TSLA",
      strategy: "Put Credit Spread",
      alert: "High IV",
      pnl: 178.90,
      pnlPercent: 15.2,
      dte: 21,
      delta: -0.38,
      theta: -9.4,
      action: "Hold"
    },
    {
      symbol: "NVDA",
      strategy: "Covered Call",
      alert: "Over extended",
      pnl: -45.30,
      pnlPercent: -2.1,
      dte: 15,
      delta: 0.71,
      theta: -15.6,
      action: "Review position"
    },
  ];

  return (
    <div className="space-y-4">
      <PageHeader title="Active Trade & Alerts" subtitle="Enriched positions view with per-position alerts, suggested actions & Greeks monitoring" />

      <Card bodyClassName="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3">Symbol</th>
                <th className="px-4 py-3">Strategy</th>
                <th className="px-4 py-3">Alert</th>
                <th className="px-4 py-3 text-right">P&L</th>
                <th className="px-4 py-3 text-right">P&L %</th>
                <th className="px-4 py-3 text-right">DTE</th>
                <th className="px-4 py-3 text-right">Delta</th>
                <th className="px-4 py-3 text-right">Theta</th>
                <th className="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {holdings.map((holding, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className="font-semibold text-blue-600">{holding.symbol}</span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm">{holding.strategy}</td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="flex items-center gap-1.5">
                      {holding.alert !== "Stable" && (
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                      )}
                      <span className={`text-xs ${
                        holding.alert === "Stable" ? "text-slate-500" :
                        holding.alert.includes("earnings") ? "text-amber-600" :
                        holding.alert.includes("approaching") ? "text-amber-600" :
                        "text-red-600"
                      }`}>
                        {holding.alert}
                      </span>
                    </div>
                  </td>
                  <td className={`px-4 py-3 whitespace-nowrap text-right text-sm font-medium font-mono ${
                    holding.pnl >= 0 ? "text-green-700" : "text-red-700"
                  }`}>
                    {holding.pnl >= 0 ? "+" : ""}{holding.pnl.toFixed(2)}
                  </td>
                  <td className={`px-4 py-3 whitespace-nowrap text-right text-sm font-medium font-mono ${
                    holding.pnlPercent >= 0 ? "text-green-700" : "text-red-700"
                  }`}>
                    {holding.pnlPercent >= 0 ? "+" : ""}{holding.pnlPercent.toFixed(1)}%
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-slate-700">{holding.dte}</td>
                  <td className={`px-4 py-3 whitespace-nowrap text-right text-sm font-mono ${
                    Math.abs(holding.delta) > 0.7 ? "text-red-600 font-semibold" :
                    Math.abs(holding.delta) > 0.5 ? "text-amber-600" :
                    "text-slate-700"
                  }`}>
                    {holding.delta.toFixed(2)}
                  </td>
                  <td className={`px-4 py-3 whitespace-nowrap text-right text-sm font-mono ${
                    holding.theta < -15 ? "text-red-600 font-semibold" :
                    holding.theta < -10 ? "text-amber-600" :
                    "text-slate-700"
                  }`}>
                    {holding.theta.toFixed(1)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <Badge tone={
                      holding.action === "Take profits" ? "green" :
                      holding.action === "Review position" ? "yellow" :
                      holding.action === "Monitor closely" ? "yellow" :
                      "blue"
                    }>
                      {holding.action}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
