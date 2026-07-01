import { useState } from "react";
import { Card, Input, Select, Button, Table, Textarea, Badge } from "../ui";
import {
  usePortfolios,
  useCreatePortfolio,
  usePortfolioSummary,
  useTrades,
  useAddTrade,
  useCloseTrade,
} from "../../hooks/queries";
import { fmtDate, fmtUsd, fmtPct } from "../../utils";
import type { TradeOut, TradeType, Direction } from "../../types";

export function PortfolioView() {
  const { data: portfoliosData } = usePortfolios();
  const portfolios = portfoliosData?.data ?? [];
  const [selectedId, setSelectedId] = useState<string | undefined>(undefined);
  const activeId = selectedId ?? portfolios[0]?.id;
  const summary = usePortfolioSummary(activeId);
  const trades = useTrades(activeId);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <PortfoliosList
          portfolios={portfolios.map((p) => ({ id: p.id, name: p.name }))}
          selectedId={activeId}
          onSelect={setSelectedId}
        />
        <NewPortfolioCard />
      </div>

      {activeId && summary.data && (
        <Card title="Summary" subtitle={summary.data.name}>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <Stat label="Total trades" value={summary.data.total_trades} />
            <Stat label="Open" value={summary.data.open_trades} />
            <Stat label="Closed" value={summary.data.closed_trades} />
            <Stat
              label="Total P&L"
              value={fmtUsd(summary.data.total_pnl)}
              tone={summary.data.total_pnl >= 0 ? "green" : "red"}
            />
            <Stat label="Win rate" value={fmtPct(summary.data.win_rate, 1)} />
            <Stat label="Winners" value={summary.data.winners} />
            <Stat label="Losers" value={summary.data.losers} />
          </div>
        </Card>
      )}

      {activeId && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <NewTradeCard portfolioId={activeId} />
          <TradesList trades={trades.data ?? []} portfolioId={activeId} />
        </div>
      )}
    </div>
  );
}

function Stat({ label, value, tone }: { label: string; value: React.ReactNode; tone?: "green" | "red" }) {
  return (
    <div className="rounded-md bg-gray-50 p-3">
      <p className="text-xs text-gray-500">{label}</p>
      <p className={`text-lg font-semibold ${tone === "green" ? "text-green-700" : tone === "red" ? "text-red-700" : "text-gray-900"}`}>
        {value}
      </p>
    </div>
  );
}

function PortfoliosList({
  portfolios,
  selectedId,
  onSelect,
}: {
  portfolios: { id: string; name: string }[];
  selectedId?: string;
  onSelect: (id: string) => void;
}) {
  return (
    <Card title="Portfolios" subtitle="Select a portfolio to view">
      {portfolios.length === 0 ? (
        <p className="text-sm text-gray-500">No portfolios yet — create one →</p>
      ) : (
        <ul className="divide-y divide-gray-100">
          {portfolios.map((p) => (
            <li
              key={p.id}
              className={`px-3 py-2 cursor-pointer rounded-md text-sm ${selectedId === p.id ? "bg-indigo-50 text-indigo-700" : "hover:bg-gray-50"}`}
              onClick={() => onSelect(p.id)}
            >
              {p.name}
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}

function NewPortfolioCard() {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const create = useCreatePortfolio();
  return (
    <Card title="New portfolio">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          create.mutate(
            { name, description: description || null },
            {
              onSuccess: () => {
                setName("");
                setDescription("");
              },
            },
          );
        }}
        className="space-y-3"
      >
        <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} required />
        <Textarea label="Description" rows={2} value={description} onChange={(e) => setDescription(e.target.value)} />
        <Button type="submit" loading={create.isPending} className="w-full">
          Create portfolio
        </Button>
      </form>
    </Card>
  );
}

function NewTradeCard({ portfolioId }: { portfolioId: string }) {
  const [symbol, setSymbol] = useState("AAPL");
  const [tradeType, setTradeType] = useState<"call" | "put" | "stock">("call");
  const [direction, setDirection] = useState<"long" | "short">("long");
  const [entryPrice, setEntryPrice] = useState(1.0);
  const [quantity, setQuantity] = useState(1);
  const [notes, setNotes] = useState("");
  const add = useAddTrade(portfolioId);

  return (
    <Card title="Add trade">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          add.mutate({
            portfolio_id: portfolioId,
            symbol,
            trade_type: tradeType,
            direction,
            entry_price: Number(entryPrice),
            quantity: Number(quantity),
            entry_date: new Date().toISOString().slice(0, 10),
            notes: notes || null,
          });
        }}
        className="space-y-3"
      >
        <div className="grid grid-cols-2 gap-3">
          <Input label="Symbol" value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} required />
          <Select label="Type" value={tradeType} onChange={(e) => setTradeType(e.target.value as TradeType)}>
            <option value="call">Call</option>
            <option value="put">Put</option>
            <option value="stock">Stock</option>
          </Select>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Select label="Direction" value={direction} onChange={(e) => setDirection(e.target.value as Direction)}>
            <option value="long">Long</option>
            <option value="short">Short</option>
          </Select>
          <Input label="Quantity" type="number" value={quantity} onChange={(e) => setQuantity(Number(e.target.value))} />
        </div>
        <Input label="Entry price" type="number" step="0.01" value={entryPrice} onChange={(e) => setEntryPrice(Number(e.target.value))} />
        <Textarea label="Notes" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />
        <Button type="submit" loading={add.isPending} className="w-full">
          Add trade
        </Button>
      </form>
    </Card>
  );
}

function TradesList({ trades, portfolioId }: { trades: TradeOut[]; portfolioId: string }) {
  const close = useCloseTrade(portfolioId);
  return (
    <Card title="Trades" subtitle={`${trades.length} total`}>
      <Table
        columns={[
          { key: "symbol", header: "Symbol" },
          {
            key: "type",
            header: "Type",
            render: (t) => <Badge tone={t.trade_type === "call" ? "indigo" : "purple"}>{t.trade_type}</Badge>,
          },
          { key: "dir", header: "Dir" },
          { key: "qty", header: "Qty", align: "right" },
          { key: "entry", header: "Entry", align: "right", render: (t) => fmtUsd(t.entry_price) },
          { key: "exit", header: "Exit", align: "right", render: (t) => fmtUsd(t.exit_price) },
          {
            key: "pnl",
            header: "P&L",
            align: "right",
            render: (t) => (
              <span className={t.pnl >= 0 ? "text-green-700" : "text-red-700"}>{fmtUsd(t.pnl)}</span>
            ),
          },
          { key: "entry_date", header: "Opened", render: (t) => fmtDate(t.entry_date) },
          {
            key: "action",
            header: "",
            render: (t) =>
              t.open ? (
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() =>
                    close.mutate({
                      tradeId: t.trade_id,
                      body: { exit_price: Number((t.entry_price * 1.1).toFixed(2)), exit_date: new Date().toISOString().slice(0, 10) },
                    })
                  }
                >
                  Close
                </Button>
              ) : (
                <Badge tone="gray">Closed</Badge>
              ),
          },
        ]}
        rows={trades}
        rowKey={(t) => t.trade_id}
        empty="No trades yet — add the first one →"
      />
    </Card>
  );
}
