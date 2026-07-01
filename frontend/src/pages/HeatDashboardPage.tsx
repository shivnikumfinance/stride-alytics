import { PageHeader, Card, Badge } from "../components/ui";

export function HeatDashboardPage() {
  return (
    <div className="space-y-4">
      <PageHeader title="Heat Dashboard" subtitle="Market health, risk gauges, and trend indicators" />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card title="Risk Gauges">
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-slate-600">Portfolio Risk</span>
                <span className="text-sm font-semibold text-amber-600">Moderate</span>
              </div>
              <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-green-500 via-amber-500 to-red-500" style={{ width: "45%" }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-slate-600">Margin Utilization</span>
                <span className="text-sm font-semibold text-green-600">32%</span>
              </div>
              <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-green-500" style={{ width: "32%" }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-slate-600">Concentration Risk</span>
                <span className="text-sm font-semibold text-yellow-600">Elevated</span>
              </div>
              <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-yellow-500" style={{ width: "68%" }}></div>
              </div>
            </div>
          </div>
        </Card>

        <Card title="Market Breadth">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-slate-500 mb-1">Advancing</p>
              <p className="text-xl font-bold text-green-700">2,847</p>
              <p className="text-xs text-slate-500">+12.3%</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-1">Declining</p>
              <p className="text-xl font-bold text-red-700">1,245</p>
              <p className="text-xs text-slate-500">-8.7%</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-1">New Highs</p>
              <p className="text-xl font-bold text-green-700">185</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-1">New Lows</p>
              <p className="text-xl font-bold text-red-700">42</p>
            </div>
          </div>
          <div className="mt-4 p-3 bg-slate-50 rounded-lg border border-slate-200">
            <p className="text-sm text-slate-600">
              <span className="font-semibold">Breadth Ratio:</span> 2.29 (Bullish)
            </p>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card title="Volatility">
          <div className="space-y-3">
            <div>
              <p className="text-xs text-slate-500 mb-1">VIX</p>
              <p className="text-2xl font-bold text-slate-900">18.42</p>
              <p className="text-xs text-green-600">-2.3% today</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-1">VIX Term Structure</p>
              <p className="text-sm text-slate-700">Contango (Bullish)</p>
              <div className="flex gap-1 mt-2">
                <div className="flex-1 h-8 bg-green-100 rounded"></div>
                <div className="flex-1 h-8 bg-green-200 rounded"></div>
                <div className="flex-1 h-8 bg-green-300 rounded"></div>
              </div>
            </div>
          </div>
        </Card>

        <Card title="Trend">
          <div className="space-y-3">
            <div>
              <p className="text-xs text-slate-500 mb-1">Primary Trend</p>
              <Badge tone="green" className="text-sm">Bullish</Badge>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-1">Intermediate Trend</p>
              <Badge tone="yellow" className="text-sm">Ranging</Badge>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-1">Short-term Momentum</p>
              <Badge tone="green" className="text-sm">Bullish</Badge>
            </div>
          </div>
        </Card>

        <Card title="Macro">
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-600">10Y Treasury</span>
              <span className="text-sm font-semibold">4.28%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-600">Fed Funds Rate</span>
              <span className="text-sm font-semibold">5.25%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-600">CPI (YoY)</span>
              <span className="text-sm font-semibold">3.2%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-600">Unemployment</span>
              <span className="text-sm font-semibold">3.8%</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
