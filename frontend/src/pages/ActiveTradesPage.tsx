import { PageHeader, Badge } from "../components/ui";

export function ActiveTradesPage() {
  const trades = [
    { id: "TRD-001", symbol: "SPY", strategy: "Covered Call", layer: "Base", band: "A", dte: 18, delta: 0.65, theta: -12.3, pnl: 245.50, pnlPercent: 12.4, status: "active" },
    { id: "TRD-002", symbol: "QQQ", strategy: "Iron Condor", layer: "Base", band: "B", dte: 24, delta: 0.12, theta: 8.7, pnl: -89.20, pnlPercent: -4.2, status: "active" },
    { id: "TRD-003", symbol: "IWM", strategy: "Cash-Secured Put", layer: "Base", band: "A", dte: 32, delta: -0.45, theta: -5.2, pnl: 156.80, pnlPercent: 6.8, status: "active" },
    { id: "TRD-004", symbol: "AAPL", strategy: "Long Call", layer: "Growth", band: "B", dte: 12, delta: 0.82, theta: -18.9, pnl: 320.00, pnlPercent: 24.5, status: "active" },
    { id: "TRD-005", symbol: "TSLA", strategy: "Put Credit Spread", layer: "Base", band: "C", dte: 21, delta: -0.38, theta: -9.4, pnl: 178.90, pnlPercent: 15.2, status: "active" },
    { id: "TRD-006", symbol: "NVDA", strategy: "Covered Call", layer: "Base", band: "A", dte: 15, delta: 0.71, theta: -15.6, pnl: -45.30, pnlPercent: -2.1, status: "review" },
  ];

  return (
    <div className="space-y-4">
      <PageHeader title="Active Trades" subtitle="6 open positions — Total P&L: +$600.00" />
      <div className="overflow-x-auto border border-slate-200 rounded-lg bg-white">
        <table className="w-full text-sm">
          <thead>
            <tr>
              <th>ID</th>
              <th>Symbol</th>
              <th>Strategy</th>
              <th>Layer</th>
              <th>Band</th>
              <th className="text-right">DTE</th>
              <th className="text-right">Delta</th>
              <th className="text-right">Theta</th>
              <th className="text-right">P&L</th>
              <th className="text-right">P&L %</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((t) => (
              <tr key={t.id}>
                <td className="text-xs font-mono text-slate-500">{t.id}</td>
                <td><span className="font-semibold text-blue-600">{t.symbol}</span></td>
                <td className="text-sm">{t.strategy}</td>
                <td><Badge tone={t.layer === "Base" ? "blue" : "purple"}>{t.layer}</Badge></td>
                <td><Badge tone={t.band === "A" ? "green" : t.band === "B" ? "blue" : "yellow"}>{t.band}</Badge></td>
                <td className="text-right text-sm">{t.dte}</td>
                <td className={`text-right text-sm font-mono ${Math.abs(t.delta) > 0.7 ? "text-red-600 font-semibold" : ""}`}>{t.delta.toFixed(2)}</td>
                <td className={`text-right text-sm font-mono ${t.theta < -15 ? "text-red-600 font-semibold" : ""}`}>{t.theta.toFixed(1)}</td>
                <td className={`text-right text-sm font-medium font-mono ${t.pnl >= 0 ? "text-green-700" : "text-red-700"}`}>{t.pnl >= 0 ? "+" : ""}{t.pnl.toFixed(2)}</td>
                <td className={`text-right text-sm font-medium font-mono ${t.pnlPercent >= 0 ? "text-green-700" : "text-red-700"}`}>{t.pnlPercent >= 0 ? "+" : ""}{t.pnlPercent.toFixed(1)}%</td>
                <td><Badge tone={t.status === "active" ? "green" : "yellow"}>{t.status}</Badge></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
