import { useState } from "react";
import { Card, Input, Badge, Button } from "../ui";
import { useRegime } from "../../hooks/queries";
import { fmtPct } from "../../utils";
import type { Regime } from "../../types";

const tone: Record<Regime, "green" | "red" | "gray"> = {
  bull: "green",
  bear: "red",
  ranging: "gray",
};

export function RegimePanel() {
  const [symbol, setSymbol] = useState("SPY");
  const [submitted, setSubmitted] = useState("SPY");
  const [lookback, setLookback] = useState(30);
  const q = useRegime(submitted, lookback);

  return (
    <Card
      title="Market Regime"
      subtitle="Classify the broad market direction"
      actions={
        <form
          onSubmit={(e) => {
            e.preventDefault();
            setSubmitted(symbol.toUpperCase());
          }}
          className="flex items-end gap-2"
        >
          <Input label="Symbol" value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} />
          <Input label="Lookback (days)" type="number" value={lookback} onChange={(e) => setLookback(Number(e.target.value))} />
          <Button type="submit" loading={q.isFetching}>
            Detect
          </Button>
        </form>
      }
    >
      {q.isLoading ? (
        <p className="text-sm text-gray-500">Loading…</p>
      ) : q.isError ? (
        <p className="text-sm text-red-600">Failed to load regime.</p>
      ) : q.data ? (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <Badge tone={tone[q.data.regime]} className="text-sm px-3 py-1 uppercase">
              {q.data.regime}
            </Badge>
            <span className="text-sm text-gray-600">
              Confidence: <strong>{(q.data.confidence * 100).toFixed(0)}%</strong>
            </span>
          </div>
          <dl className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt className="text-gray-500">Lookback</dt>
              <dd className="font-medium">{q.data.lookback_days} days</dd>
            </div>
            <div>
              <dt className="text-gray-500">Price return</dt>
              <dd className={`font-medium ${q.data.price_return >= 0 ? "text-green-700" : "text-red-700"}`}>
                {fmtPct(q.data.price_return, 2)}
              </dd>
            </div>
            <div>
              <dt className="text-gray-500">As of</dt>
              <dd className="font-medium">{q.data.as_of}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Symbol</dt>
              <dd className="font-medium">{q.data.symbol}</dd>
            </div>
          </dl>
        </div>
      ) : (
        <p className="text-sm text-gray-500">Enter a symbol to detect regime.</p>
      )}
    </Card>
  );
}
