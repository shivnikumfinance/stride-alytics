import { Card } from "../components/ui";

export function OptionChainPage() {
  const underlying = 548.32;
  const strikes = [];
  
  // Generate option chain data
  for (let i = 15; i >= -15; i--) {
    const strike = underlying + (i * 5);
    strikes.push({
      strike,
      callBid: (Math.random() * 8 + 0.5).toFixed(2),
      callAsk: (Math.random() * 8 + 0.7).toFixed(2),
      callVol: Math.floor(Math.random() * 5000 + 100),
      callOI: Math.floor(Math.random() * 50000 + 1000),
      putBid: (Math.random() * 2 + 0.1).toFixed(2),
      putAsk: (Math.random() * 2 + 0.2).toFixed(2),
      putVol: Math.floor(Math.random() * 3000 + 50),
      putOI: Math.floor(Math.random() * 30000 + 500),
    });
  }

  const atmIndex = 15; // Middle of the strikes array

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-slate-900">Option Chain</h1>
        <p className="text-sm text-slate-500 mt-1">
          SPY — Jul 17, 2026 (30 DTE) — Underlying: ${underlying.toFixed(2)}
        </p>
      </header>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200">
                <th colSpan={5} className="text-center py-2 text-xs font-semibold text-green-700 uppercase bg-green-50">
                  Calls
                </th>
                <th className="text-center py-2 text-xs font-semibold text-slate-900 bg-slate-100 border-x border-slate-200">
                  Strike
                </th>
                <th colSpan={5} className="text-center py-2 text-xs font-semibold text-red-700 uppercase bg-red-50">
                  Puts
                </th>
              </tr>
              <tr className="border-b border-slate-200 text-xs">
                <th className="text-left py-2 px-2 text-slate-600">Bid</th>
                <th className="text-left py-2 px-2 text-slate-600">Ask</th>
                <th className="text-right py-2 px-2 text-slate-600">Vol</th>
                <th className="text-right py-2 px-2 text-slate-600">OI</th>
                <th className="text-right py-2 px-2 text-slate-600">IV</th>
                <th className="text-center py-2 px-2 text-slate-900 font-semibold border-x border-slate-200">Price</th>
                <th className="text-right py-2 px-2 text-slate-600">IV</th>
                <th className="text-right py-2 px-2 text-slate-600">OI</th>
                <th className="text-right py-2 px-2 text-slate-600">Vol</th>
                <th className="text-left py-2 px-2 text-slate-600">Ask</th>
                <th className="text-left py-2 px-2 text-slate-600">Bid</th>
              </tr>
            </thead>
            <tbody>
              {strikes.map((opt, idx) => (
                <tr 
                  key={idx} 
                  className={`border-b border-slate-100 hover:bg-slate-50 ${
                    idx === atmIndex ? "bg-blue-50" : ""
                  }`}
                >
                  <td className="py-1.5 px-2 text-green-700 font-mono text-xs">{opt.callBid}</td>
                  <td className="py-1.5 px-2 text-green-700 font-mono text-xs">{opt.callAsk}</td>
                  <td className="py-1.5 px-2 text-right text-slate-600 text-xs">{opt.callVol.toLocaleString()}</td>
                  <td className="py-1.5 px-2 text-right text-slate-600 text-xs">{opt.callOI.toLocaleString()}</td>
                  <td className="py-1.5 px-2 text-right text-slate-500 text-xs">{(Math.random() * 30 + 15).toFixed(1)}%</td>
                  
                  <td className={`py-1.5 px-3 text-center font-bold border-x border-slate-200 ${
                    idx === atmIndex ? "text-blue-700 bg-blue-100" : "text-slate-900"
                  }`}>
                    {opt.strike.toFixed(2)}
                  </td>
                  
                  <td className="py-1.5 px-2 text-right text-slate-500 text-xs">{(Math.random() * 30 + 15).toFixed(1)}%</td>
                  <td className="py-1.5 px-2 text-right text-slate-600 text-xs">{opt.putOI.toLocaleString()}</td>
                  <td className="py-1.5 px-2 text-right text-slate-600 text-xs">{opt.putVol.toLocaleString()}</td>
                  <td className="py-1.5 px-2 text-red-700 font-mono text-xs">{opt.putAsk}</td>
                  <td className="py-1.5 px-2 text-red-700 font-mono text-xs">{opt.putBid}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
