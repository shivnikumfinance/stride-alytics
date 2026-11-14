import { Link } from "react-router-dom";

import { Badge, Card, PageHeader, Table } from "../components/ui";
import { useOpenTrades } from "../hooks/queries";
import { fmtUsd } from "../utils";
import type { TradeOut } from "../types";

export function ActiveTradesPage() {
  const q = useOpenTrades();
  const trades = q.data?.data ?? [];
  const atRisk = trades.reduce((sum, t) => sum + (t.risk_amount ?? 0), 0);

  return (
    <div className="space-y-4">
      <PageHeader
        title="Active Trades"
        subtitle={q.data ? `${q.data.total} open · ${fmtUsd(atRisk)} capital at risk` : "Your open positions"}
      />
      {q.isError && (
        <p role="alert" className="text-sm text-red-600">
          Could not load your trades. Try refreshing.
        </p>
      )}
      <Card
        bodyClassName="p-0"
        actions={
          <Link to="/portfolio" className="text-sm text-indigo-600 hover:underline">
            Add or close trades in Portfolio →
          </Link>
        }
      >
        <Table<TradeOut>
          loading={q.isLoading}
          rows={trades}
          rowKey={(t) => t.trade_id}
          empty="No open trades."
          columns={[
            { key: "symbol", header: "Symbol", render: (t) => <span className="font-semibold">{t.symbol}</span> },
            { key: "type", header: "Type", render: (t) => <Badge tone={t.trade_type === "call" ? "indigo" : t.trade_type === "put" ? "purple" : "gray"}>{t.trade_type}</Badge> },
            { key: "dir", header: "Dir", render: (t) => t.direction },
            { key: "qty", header: "Qty", align: "right", render: (t) => t.quantity },
            { key: "entry", header: "Entry", align: "right", render: (t) => fmtUsd(t.entry_price) },
            { key: "strike", header: "Strike", align: "right", render: (t) => t.strike ?? "—" },
            { key: "expiry", header: "Expiry", render: (t) => t.expiry ?? "—" },
            { key: "layer", header: "Layer", render: (t) => t.layer ?? "—" },
            { key: "band", header: "Band", render: (t) => t.band ?? "—" },
            { key: "risk", header: "At risk", align: "right", render: (t) => (t.risk_amount === null || t.risk_amount === undefined ? "—" : fmtUsd(t.risk_amount)) },
          ]}
        />
      </Card>
    </div>
  );
}
