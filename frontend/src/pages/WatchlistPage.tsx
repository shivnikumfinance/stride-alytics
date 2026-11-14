import { useState } from "react";
import toast from "react-hot-toast";
import { Download, Trash2 } from "lucide-react";

import { downloadFile } from "../api/download";
import { Button, Card, Input, PageHeader, SampleDataBadge, Table } from "../components/ui";
import {
  useAddSymbol,
  useCreateWatchlist,
  useDeleteWatchlist,
  useQuotes,
  useRemoveSymbol,
  useWatchlists,
} from "../hooks/queries";
import type { RawTicker } from "../types/market";

interface Row {
  symbol: string;
  quote?: RawTicker;
}

export function WatchlistPage() {
  const { data: watchlists = [], isLoading } = useWatchlists();
  const [selectedId, setSelectedId] = useState<string | undefined>();
  const selected = watchlists.find((w) => w.id === selectedId) ?? watchlists[0];

  const [newName, setNewName] = useState("");
  const [newSymbol, setNewSymbol] = useState("");
  const createList = useCreateWatchlist();
  const deleteList = useDeleteWatchlist();
  const addSymbol = useAddSymbol();
  const removeSymbol = useRemoveSymbol();
  const quotes = useQuotes(selected?.symbols ?? []);

  const rows: Row[] = (selected?.symbols ?? []).map((symbol) => ({
    symbol,
    quote: quotes.data?.data?.[symbol],
  }));

  return (
    <div className="space-y-4">
      <PageHeader title="Watchlist" subtitle="Your symbol lists. Quotes refresh every minute." />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card title="Watchlists" className="lg:col-span-1">
          {isLoading ? (
            <p className="text-sm text-gray-500">Loading…</p>
          ) : watchlists.length === 0 ? (
            <p className="text-sm text-gray-500 mb-3">No watchlists yet. Create one below.</p>
          ) : (
            <ul className="divide-y divide-gray-100 mb-4">
              {watchlists.map((w) => (
                <li key={w.id} className="flex items-center justify-between py-1">
                  <button
                    type="button"
                    onClick={() => setSelectedId(w.id)}
                    className={`flex-1 text-left px-2 py-1.5 rounded-md text-sm ${
                      selected?.id === w.id ? "bg-indigo-50 text-indigo-700" : "hover:bg-gray-50"
                    }`}
                  >
                    {w.name} <span className="text-gray-400">({w.symbols.length})</span>
                  </button>
                  <button
                    type="button"
                    aria-label={`Delete ${w.name}`}
                    className="p-1.5 text-gray-400 hover:text-red-600"
                    onClick={() => {
                      if (window.confirm(`Delete watchlist "${w.name}"?`)) deleteList.mutate(w.id);
                    }}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </li>
              ))}
            </ul>
          )}
          <form
            className="flex items-end gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              const name = newName.trim();
              if (!name) return;
              createList.mutate({ name }, { onSuccess: () => setNewName("") });
            }}
          >
            <Input
              label="New watchlist"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="e.g. Core"
              className="flex-1"
            />
            <Button type="submit" loading={createList.isPending}>
              Create
            </Button>
          </form>
        </Card>

        <Card
          className="lg:col-span-2"
          title={selected ? selected.name : "Symbols"}
          subtitle={selected ? `${selected.symbols.length} symbols` : "Create a watchlist to start"}
          actions={
            selected && (
              <>
                <SampleDataBadge source={quotes.data?.source} />
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() =>
                    downloadFile(`/watchlists/${selected.id}/export.csv`, "watchlist.csv").catch(() =>
                      toast.error("Could not export the watchlist"),
                    )
                  }
                >
                  <Download className="w-4 h-4 mr-1" /> Export CSV
                </Button>
              </>
            )
          }
        >
          {selected ? (
            <div className="space-y-4">
              <form
                className="flex items-end gap-2"
                onSubmit={(e) => {
                  e.preventDefault();
                  const symbol = newSymbol.trim().toUpperCase();
                  if (!symbol) return;
                  addSymbol.mutate({ id: selected.id, symbol }, { onSuccess: () => setNewSymbol("") });
                }}
              >
                <Input
                  label="Add symbol"
                  value={newSymbol}
                  onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
                  placeholder="AAPL"
                  className="w-40"
                  maxLength={16}
                />
                <Button type="submit" loading={addSymbol.isPending}>
                  Add
                </Button>
              </form>

              <Table<Row>
                rows={rows}
                rowKey={(r) => r.symbol}
                empty="This watchlist is empty. Add a symbol above."
                columns={[
                  { key: "symbol", header: "Symbol", render: (r) => <span className="font-semibold">{r.symbol}</span> },
                  {
                    key: "price",
                    header: "Price",
                    align: "right",
                    render: (r) => (r.quote ? r.quote.price : "—"),
                  },
                  {
                    key: "change",
                    header: "Change %",
                    align: "right",
                    render: (r) => {
                      if (!r.quote) return "—";
                      const pct = parseFloat(r.quote.changePercent);
                      return (
                        <span className={pct >= 0 ? "text-green-700" : "text-red-700"}>
                          {pct >= 0 ? "+" : ""}
                          {r.quote.changePercent}%
                        </span>
                      );
                    },
                  },
                  {
                    key: "remove",
                    header: "",
                    align: "right",
                    render: (r) => (
                      <button
                        type="button"
                        aria-label={`Remove ${r.symbol}`}
                        className="p-1.5 text-gray-400 hover:text-red-600"
                        onClick={() => removeSymbol.mutate({ id: selected.id, symbol: r.symbol })}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    ),
                  },
                ]}
              />
            </div>
          ) : (
            <p className="text-sm text-gray-500">No watchlist selected.</p>
          )}
        </Card>
      </div>
    </div>
  );
}
