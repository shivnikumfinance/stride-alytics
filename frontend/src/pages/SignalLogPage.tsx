import { Badge, Card } from "../components/ui";

interface Signal {
  timestamp: string;
  type: "entry" | "exit" | "regime" | "alert";
  rule: string;
  details: string;
}

type BadgeTone = React.ComponentProps<typeof Badge>["tone"];

const BADGE_CONFIG: Record<Signal["type"], { tone: BadgeTone; label: string }> = {
  entry: { tone: "green", label: "Entry" },
  exit: { tone: "red", label: "Exit" },
  regime: { tone: "blue", label: "Regime" },
  alert: { tone: "yellow", label: "Alert" },
};

export function SignalLogPage() {
  const signals: Signal[] = [
    { timestamp: "2024-01-15 14:32:45", type: "exit", rule: "Max Profit Threshold", details: "SPY Covered Call reached 85% max profit" },
    { timestamp: "2024-01-15 14:28:12", type: "regime", rule: "Regime Detector", details: "Market shifted from NORMAL to GROWTH regime (confidence: 0.78)" },
    { timestamp: "2024-01-15 13:45:33", type: "entry", rule: "IV Percentile Entry", details: "QQQ IV Rank crossed 70% threshold - entering Iron Condor" },
    { timestamp: "2024-01-15 12:15:21", type: "alert", rule: "Earnings Warning", details: "AAPL earnings in 3 days - reducing position size by 50%" },
    { timestamp: "2024-01-15 11:02:55", type: "exit", rule: "Stop Loss Trigger", details: "TSLA Put Credit Spread delta limit exceeded (-0.65)" },
    { timestamp: "2024-01-15 10:30:18", type: "entry", rule: "Regime Aligned Entry", details: "Normal regime confirmed - entering NVDA Covered Call" },
    { timestamp: "2024-01-15 09:45:02", type: "alert", rule: "Gamma Squeeze Detector", details: "High gamma exposure detected in meme stocks" },
    { timestamp: "2024-01-14 16:05:44", type: "exit", rule: "End of Day", details: "All positions within risk parameters - holding overnight" },
  ];

  const getTypeBadge = (type: Signal["type"]) => {
    const { tone, label } = BADGE_CONFIG[type];
    return <Badge tone={tone}>{label}</Badge>;
  };

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-slate-900">Signal Log</h1>
        <p className="text-sm text-slate-500 mt-1">
          Immutable record of rule-based decisions and regime shifts
        </p>
      </header>

      <Card bodyClassName="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3">Timestamp</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Rule</th>
                <th className="px-4 py-3">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {signals.map((signal, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap text-xs font-mono text-slate-500">
                    {signal.timestamp}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">{getTypeBadge(signal.type)}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-slate-900">{signal.rule}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">{signal.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
