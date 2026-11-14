import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

/** Portfolio P&L change across a range of underlying moves (the "P&L curve"). */
export function ScenarioCurve({ ladder }: { ladder: { spot_pct: number; total_change: number }[] }) {
  const data = ladder.map((p) => ({ move: `${p.spot_pct > 0 ? "+" : ""}${p.spot_pct}%`, change: p.total_change }));
  return (
    <div role="img" aria-label="Portfolio P&L change across underlying price moves from minus 20 to plus 20 percent" className="h-56">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="move" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} width={56} tickFormatter={(v: number) => `$${v}`} />
          <Tooltip formatter={(v: number) => [`$${v.toFixed(2)}`, "P&L change"]} />
          <ReferenceLine y={0} stroke="#6b7280" />
          <Line type="monotone" dataKey="change" stroke="#4f46e5" strokeWidth={2} dot={{ r: 3 }} name="P&L change" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
