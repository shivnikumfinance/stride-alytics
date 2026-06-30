import { useRunScreener } from "../../hooks/queries";
import { useScreenerStore } from "../../store";
import { Badge, Card, Table } from "../ui";
import { fmtIv, fmtNum, fmtUsd } from "../../utils";
import type { ScreenerRow } from "../../types";

const columns = [
  { key: "symbol", header: "Symbol" },
  { key: "strike", header: "Strike", align: "right" as const, render: (r: ScreenerRow) => fmtUsd(r.strike) },
  { key: "expiry", header: "Expiry" },
  {
    key: "option_type",
    header: "Type",
    render: (r: ScreenerRow) => (
      <Badge tone={r.option_type === "call" ? "indigo" : "purple"}>{r.option_type.toUpperCase()}</Badge>
    ),
  },
  { key: "last_price", header: "Last", align: "right" as const, render: (r: ScreenerRow) => fmtUsd(r.last_price) },
  { key: "bid", header: "Bid", align: "right" as const, render: (r: ScreenerRow) => fmtUsd(r.bid) },
  { key: "ask", header: "Ask", align: "right" as const, render: (r: ScreenerRow) => fmtUsd(r.ask) },
  { key: "implied_vol", header: "IV", align: "right" as const, render: (r: ScreenerRow) => fmtIv(r.implied_vol) },
  { key: "delta", header: "Δ", align: "right" as const, render: (r: ScreenerRow) => fmtNum(r.delta, 3) },
  { key: "volume", header: "Vol", align: "right" as const, render: (r: ScreenerRow) => r.volume.toLocaleString() },
  { key: "open_interest", header: "OI", align: "right" as const, render: (r: ScreenerRow) => r.open_interest.toLocaleString() },
];

export function ResultsTable() {
  const results = useScreenerStore((s) => s.results);
  const spot = useScreenerStore((s) => s.spot);
  const setResults = useScreenerStore((s) => s.setResults);
  const setLoading = useScreenerStore((s) => s.setLoading);
  const loading = useScreenerStore((s) => s.loading);
  const filters = useScreenerStore((s) => s.filters);

  const mutation = useRunScreener();

  // Auto-trigger when the consumer wires a "Run" button into the page.
  // Here we expose the trigger via a hidden form-less invocation.
  // Callers should call `run(filters)` from a button.
  const run = async () => {
    setLoading(true);
    try {
      const data = await mutation.mutateAsync(filters);
      setResults(data.results, data.spot);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card
      title={spot ? `${filters.symbol} (spot $${spot.toFixed(2)})` : "Results"}
      subtitle={results.length ? `${results.length} contracts` : "Run a search to see results"}
      actions={
        <button
          type="button"
          onClick={run}
          className="px-3 py-1.5 rounded-md bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700"
        >
          Run
        </button>
      }
    >
      <Table<ScreenerRow>
        columns={columns}
        rows={results}
        rowKey={(r) => `${r.symbol}-${r.strike}-${r.expiry}-${r.option_type}`}
        loading={loading}
        empty="No contracts match the current filters."
      />
    </Card>
  );
}
