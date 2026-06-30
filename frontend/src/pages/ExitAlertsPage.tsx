import { useState } from "react";
import { AlertTriangle, Info, AlertCircle } from "lucide-react";
import { Card, Badge } from "../components/ui";

export function ExitAlertsPage() {
  const [filter, setFilter] = useState<"all" | "critical" | "warning" | "info">("all");

  // Mock data - replace with real API call
  const alerts = [
    { id: 1, severity: "warning" as const, symbol: "SPY", strategy: "Covered Call", message: "Approaching max profit zone - consider closing", time: "2 min ago" },
    { id: 2, severity: "critical" as const, symbol: "QQQ", strategy: "Iron Condor", message: "Price breaching upper resistance - exit recommended", time: "5 min ago" },
    { id: 3, severity: "info" as const, symbol: "IWM", strategy: "Cash-Secured Put", message: " earnings in 3 days - monitor volatility", time: "12 min ago" },
    { id: 4, severity: "warning" as const, symbol: "AAPL", strategy: "Long Call", message: "Approaching earnings - consider taking profits", time: "18 min ago" },
  ];

  const filteredAlerts = filter === "all" ? alerts : alerts.filter(a => a.severity === filter);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-slate-900">Exit Alerts & Recommendations</h1>
        <p className="text-sm text-slate-500 mt-1">Real-time exit signals, severity-filtered with suggested actions</p>
      </header>

      <Card>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-slate-900">Active Alerts</h3>
          <div className="flex gap-2">
            {(["all", "critical", "warning", "info"] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`
                  px-3 py-1.5 text-xs font-medium rounded-md transition-colors
                  ${filter === f 
                    ? "bg-slate-900 text-white" 
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"}
                `}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-3">
          {filteredAlerts.length === 0 ? (
            <p className="text-sm text-slate-500 text-center py-8">No alerts matching current filter</p>
          ) : (
            filteredAlerts.map((alert) => (
              <div
                key={alert.id}
                className={`
                  p-4 rounded-lg border flex items-start gap-3
                  ${alert.severity === "critical" 
                    ? "bg-red-50 border-red-200" 
                    : alert.severity === "warning"
                    ? "bg-amber-50 border-amber-200"
                    : "bg-blue-50 border-blue-200"}
                `}
              >
                {alert.severity === "critical" ? (
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                ) : alert.severity === "warning" ? (
                  <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                ) : (
                  <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                )}
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-semibold text-slate-900">{alert.symbol}</span>
                    <Badge tone={
                      alert.severity === "critical" ? "red" :
                      alert.severity === "warning" ? "yellow" : "blue"
                    }>
                      {alert.severity}
                    </Badge>
                    <span className="text-xs text-slate-500 ml-auto">{alert.time}</span>
                  </div>
                  <p className="text-sm text-slate-700 mb-1">{alert.message}</p>
                  <p className="text-xs text-slate-500">Strategy: {alert.strategy}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>

      <Card>
        <h3 className="text-sm font-semibold text-slate-900 mb-3">Alert History</h3>
        <p className="text-xs text-slate-500">No recent alert history.</p>
      </Card>
    </div>
  );
}
