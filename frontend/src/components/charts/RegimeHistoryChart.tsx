import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { useRegimeHistory } from "../../hooks/queries";
import { Card } from "../ui";

/** Daily regime score with the 40 / 70 state boundaries (DEFENSIVE below 40, GROWTH from 70). */
export function RegimeHistoryChart({ days = 60 }: { days?: number }) {
  const history = useRegimeHistory(days);
  // The API returns newest first; the chart reads left to right in time.
  const points = [...(history.data ?? [])]
    .filter((r) => r.score !== null)
    .reverse()
    .map((r) => ({ date: r.as_of, score: r.score as number, state: r.state }));

  return (
    <Card title="Regime score history" subtitle={`Last ${days} days. Lines mark the 40 and 70 boundaries.`}>
      {history.isLoading ? (
        <p className="text-sm text-gray-500">Loading history…</p>
      ) : history.isError ? (
        <p role="alert" className="text-sm text-red-600">
          Could not load the regime history.
        </p>
      ) : points.length < 2 ? (
        <p className="text-sm text-gray-600">
          Not enough history yet. A point is stored each day the score is computed.
        </p>
      ) : (
        <div
          role="img"
          aria-label={`Regime score over ${points.length} days, latest ${points[points.length - 1].score} (${points[points.length - 1].state})`}
          className="h-64"
        >
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={points} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={24} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} width={32} />
              <Tooltip />
              <ReferenceLine y={40} stroke="#dc2626" strokeDasharray="4 4" />
              <ReferenceLine y={70} stroke="#16a34a" strokeDasharray="4 4" />
              <Line type="monotone" dataKey="score" stroke="#4f46e5" strokeWidth={2} dot={false} name="Score" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}
