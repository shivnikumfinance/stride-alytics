import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { PageHeader, Card } from "../components/ui";

export function WatchlistPage() {
  const watchlist = [
    { symbol: "SPY", price: 548.32, change: 1.24, changePercent: 0.23, iv: 18.5, ivRank: 45, trend: "bullish", band: "A", volume: "58.2M", dnt: "No" },
    { symbol: "QQQ", price: 485.67, change: -2.15, changePercent: -0.44, iv: 22.3, ivRank: 62, trend: "bearish", band: "B", volume: "42.1M", dnt: "No" },
    { symbol: "IWM", price: 198.45, change: 0.89, changePercent: 0.45, iv: 25.1, ivRank: 78, trend: "bullish", band: "A", volume: "31.5M", dnt: "No" },
    { symbol: "AAPL", price: 178.72, change: 3.45, changePercent: 1.97, iv: 32.5, ivRank: 89, trend: "bullish", band: "B", volume: "65.3M", dnt: "Earnings" },
    { symbol: "TSLA", price: 245.89, change: -8.32, changePercent: -3.27, iv: 45.2, ivRank: 95, trend: "bearish", band: "C", volume: "98.7M", dnt: "No" },
    { symbol: "NVDA", price: 875.43, change: 12.56, changePercent: 1.45, iv: 38.9, ivRank: 82, trend: "bullish", band: "A", volume: "85.4M", dnt: "No" },
    { symbol: "META", price: 502.18, change: -1.23, changePercent: -0.24, iv: 28.4, ivRank: 55, trend: "ranging", band: "B", volume: "28.9M", dnt: "No" },
    { symbol: "MSFT", price: 415.67, change: 2.87, changePercent: 0.69, iv: 19.2, ivRank: 38, trend: "bullish", band: "A", volume: "25.1M", dnt: "No" },
    { symbol: "GOOGL", price: 165.34, change: 0.56, changePercent: 0.34, iv: 21.8, ivRank: 48, trend: "ranging", band: "B", volume: "22.3M", dnt: "No" },
    { symbol: "AMZN", price: 185.79, change: -0.92, changePercent: -0.49, iv: 24.6, ivRank: 52, trend: "bearish", band: "C", volume: "35.6M", dnt: "No" },
  ];

  const getTrendIcon = (trend: string) => {
    if (trend === "bullish") return <TrendingUp className="w-4 h-4 text-green-600" />;
    if (trend === "bearish") return <TrendingDown className="w-4 h-4 text-red-600" />;
    return <Minus className="w-4 h-4 text-slate-400" />;
  };

  const getBandColor = (band: string): string => {
    const colors: Record<string, string> = {
      A: "bg-green-100 text-green-800 border-green-200",
      B: "bg-blue-100 text-blue-800 border-blue-200",
      C: "bg-yellow-100 text-yellow-800 border-yellow-200",
      D: "bg-orange-100 text-orange-800 border-orange-200",
      E: "bg-red-100 text-red-800 border-red-200",
    };
    return colors[band] ?? "bg-slate-100 text-slate-800 border-slate-200";
  };

  return (
    <div className="space-y-6">
      <PageHeader title="Watchlist" subtitle="Primary Watchlist — 10 symbols tracked" />

      <Card bodyClassName="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3">Symbol</th>
                <th className="px-4 py-3 text-right">Price</th>
                <th className="px-4 py-3 text-right">Chg %</th>
                <th className="px-4 py-3 text-right">IV</th>
                <th className="px-4 py-3 text-right">IV Rank</th>
                <th className="px-4 py-3">Trend</th>
                <th className="px-4 py-3">Band</th>
                <th className="px-4 py-3 text-right">Volume</th>
                <th className="px-4 py-3">DNT</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {watchlist.map((stock, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className="font-semibold text-blue-600 cursor-pointer">
                      {stock.symbol}
                    </span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-mono">${stock.price.toFixed(2)}</td>
                  <td className={`px-4 py-3 whitespace-nowrap text-right text-sm font-medium font-mono ${stock.change >= 0 ? "text-green-700" : "text-red-700"}`}>
                    {stock.change >= 0 ? "+" : ""}{stock.changePercent.toFixed(2)}%
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-slate-700">{stock.iv.toFixed(1)}%</td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-slate-700">{stock.ivRank}%</td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="flex items-center gap-1.5">
                      {getTrendIcon(stock.trend)}
                      <span className="text-xs capitalize text-slate-600">{stock.trend}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`inline-block px-2 py-1 rounded text-xs font-medium border ${getBandColor(stock.band)}`}>
                      {stock.band}
                    </span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-right text-sm text-slate-700">{stock.volume}</td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    {stock.dnt === "No" ? (
                      <span className="text-xs text-slate-400">—</span>
                    ) : (
                      <span className="text-xs font-medium text-amber-700 bg-amber-50 px-2 py-1 rounded border border-amber-200">
                        {stock.dnt}
                      </span>
                    )}
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
