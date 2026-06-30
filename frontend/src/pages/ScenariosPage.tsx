export function ScenariosPage() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-slate-900">Scenario Simulations</h1>
        <p className="text-sm text-slate-500 mt-1">What-if analysis and stress testing</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-2">Bull Market Rally</h3>
          <p className="text-xs text-slate-600 mb-3">SPY +5% scenario</p>
          <div className="mb-2">
            <span className="text-xs text-slate-500">Probability: </span>
            <span className="text-sm font-bold">32%</span>
          </div>
          <p className="text-lg font-bold text-green-700">+8.5%</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-2">Bear Market Drop</h3>
          <p className="text-xs text-slate-600 mb-3">SPY -8% scenario</p>
          <div className="mb-2">
            <span className="text-xs text-slate-500">Probability: </span>
            <span className="text-sm font-bold">18%</span>
          </div>
          <p className="text-lg font-bold text-red-700">-12.3%</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-2">Range Bound</h3>
          <p className="text-xs text-slate-600 mb-3">IV crush environment</p>
          <div className="mb-2">
            <span className="text-xs text-slate-500">Probability: </span>
            <span className="text-sm font-bold">45%</span>
          </div>
          <p className="text-lg font-bold text-green-700">+3.2%</p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg p-6">
        <h3 className="text-sm font-semibold text-slate-900 mb-4">Portfolio Stress Test</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-xs text-slate-500 mb-2">Bear Market (-20%)</p>
            <p className="text-2xl font-bold text-green-700">-8.3%</p>
            <div className="mt-2 h-2 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-green-500" style={{ width: "92%" }}></div>
            </div>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-2">Volatility Spike</p>
            <p className="text-2xl font-bold text-yellow-600">-15.2%</p>
            <div className="mt-2 h-2 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-yellow-500" style={{ width: "85%" }}></div>
            </div>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-2">Value at Risk (95%)</p>
            <p className="text-2xl font-bold text-red-700">$4,250</p>
            <p className="text-xs text-slate-500 mt-2">Maximum expected loss</p>
          </div>
        </div>
      </div>
    </div>
  );
}
