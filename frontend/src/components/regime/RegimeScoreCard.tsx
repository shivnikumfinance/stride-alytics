import { Badge, Card, Table } from "../ui";
import { useRegimeHistory, useRegimeScore } from "../../hooks/queries";
import type { RegimeHistoryRow, RegimeState } from "../../types";

const TONE: Record<RegimeState, "red" | "blue" | "green" | "gray"> = {
  DEFENSIVE: "red",
  NORMAL: "blue",
  GROWTH: "green",
  UNKNOWN: "gray",
};

const COMPONENT_LABELS: Record<string, string> = {
  trend: "Trend (SPY vs 50/200-day)",
  vix: "VIX level",
  iv_rank: "IV rank",
};

/** Position of the score on a 0-100 bar, split at the 40 and 70 state boundaries. */
function ScoreBar({ score }: { score: number | null }) {
  return (
    <div className="relative h-3 w-full rounded-full overflow-hidden flex" aria-hidden="true">
      <div className="bg-red-200" style={{ width: "40%" }} />
      <div className="bg-blue-200" style={{ width: "30%" }} />
      <div className="bg-green-200" style={{ width: "30%" }} />
      {score !== null && (
        <div
          className="absolute top-0 h-3 w-1 bg-gray-900"
          style={{ left: `calc(${Math.max(0, Math.min(100, score))}% - 2px)` }}
        />
      )}
    </div>
  );
}

export function RegimeScoreCard() {
  const score = useRegimeScore();
  const history = useRegimeHistory(14);

  return (
    <Card
      title="Regime score"
      subtitle="0–100 from trend, VIX and IV rank. DEFENSIVE below 40, NORMAL 40–70, GROWTH 70 and above."
    >
      {score.isLoading ? (
        <p className="text-sm text-gray-500">Loading…</p>
      ) : score.isError || !score.data ? (
        <p className="text-sm text-red-600">Could not load the regime score.</p>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <span className="text-4xl font-bold tabular-nums">
              {score.data.score === null ? "—" : score.data.score.toFixed(1)}
            </span>
            <Badge tone={TONE[score.data.state]} className="text-sm px-3 py-1">
              {score.data.state}
            </Badge>
            {score.data.source === "stored" && (
              <Badge tone="yellow">Last stored value — live data unavailable</Badge>
            )}
            {score.data.market_down && <Badge tone="red">SPY below 200-day average</Badge>}
          </div>

          {score.data.state === "UNKNOWN" ? (
            <p className="text-sm text-gray-600" role="alert">
              The score cannot be computed because market data is unavailable. Trading is treated as
              blocked until it is.
            </p>
          ) : (
            <ScoreBar score={score.data.score} />
          )}

          <dl className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
            {Object.entries(COMPONENT_LABELS).map(([key, label]) => (
              <div key={key}>
                <dt className="text-gray-500">{label}</dt>
                <dd className="font-medium">
                  {score.data.components?.[key] == null ? "unavailable" : `${score.data.components[key]} / 100`}
                </dd>
              </div>
            ))}
          </dl>
          <p className="text-xs text-gray-500">
            VIX {score.data.vix ?? "—"} · IV rank {score.data.iv_rank ?? "—"} · as of {score.data.as_of}.
            Weights are set in Settings.
          </p>
        </div>
      )}

      <div className="mt-6">
        <h4 className="text-sm font-semibold text-gray-900 mb-2">Recent history</h4>
        <Table<RegimeHistoryRow>
          loading={history.isLoading}
          rows={history.data ?? []}
          rowKey={(r) => r.as_of}
          empty="History builds up as the score is recorded each day."
          columns={[
            { key: "as_of", header: "Date" },
            { key: "score", header: "Score", align: "right", render: (r) => r.score?.toFixed(1) ?? "—" },
            { key: "state", header: "State", render: (r) => <Badge tone={TONE[r.state]}>{r.state}</Badge> },
            { key: "vix", header: "VIX", align: "right", render: (r) => r.vix ?? "—" },
          ]}
        />
      </div>
    </Card>
  );
}
