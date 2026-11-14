import { useState } from "react";

import { Badge, Button, Card, Input, PageHeader, Select, Table } from "../components/ui";
import { useAuditLog, useSignalLog } from "../hooks/queries";
import type { AuditLogEntry, SignalLogEntry } from "../types";

const PAGE_SIZE = 25;
type Tab = "signals" | "audit";

const decisionTone = { allowed: "green", blocked: "red", info: "blue" } as const;

function when(iso: string): string {
  return new Date(iso).toLocaleString();
}

function Pager({ offset, total, onChange }: { offset: number; total: number; onChange: (o: number) => void }) {
  const from = total === 0 ? 0 : offset + 1;
  const to = Math.min(offset + PAGE_SIZE, total);
  return (
    <div className="flex items-center justify-between pt-3 text-sm text-gray-600">
      <span>
        {from}–{to} of {total}
      </span>
      <div className="flex gap-2">
        <Button variant="secondary" size="sm" disabled={offset === 0} onClick={() => onChange(Math.max(0, offset - PAGE_SIZE))}>
          Previous
        </Button>
        <Button variant="secondary" size="sm" disabled={offset + PAGE_SIZE >= total} onClick={() => onChange(offset + PAGE_SIZE)}>
          Next
        </Button>
      </div>
    </div>
  );
}

export function SignalLogPage() {
  const [tab, setTab] = useState<Tab>("signals");
  const [symbol, setSymbol] = useState("");
  const [decision, setDecision] = useState("");
  const [entity, setEntity] = useState("");
  const [offset, setOffset] = useState(0);

  const signals = useSignalLog({
    symbol: symbol || undefined,
    decision: decision || undefined,
    limit: PAGE_SIZE,
    offset,
  });
  const audit = useAuditLog({ entity: entity || undefined, limit: PAGE_SIZE, offset });

  const switchTab = (next: Tab) => {
    setTab(next);
    setOffset(0);
  };

  return (
    <div className="space-y-4">
      <PageHeader
        title="Signal & Audit Log"
        subtitle="Append-only history: every rule decision (including blocked signals) and every change. It cannot be edited or deleted."
      />

      <div className="flex gap-2">
        {(["signals", "audit"] as const).map((t) => (
          <Button key={t} variant={tab === t ? "primary" : "secondary"} size="sm" onClick={() => switchTab(t)}>
            {t === "signals" ? "Signals" : "Audit trail"}
          </Button>
        ))}
      </div>

      {tab === "signals" ? (
        <Card
          title="Rule decisions"
          actions={
            <div className="flex items-end gap-2">
              <Input
                label="Symbol"
                value={symbol}
                onChange={(e) => {
                  setSymbol(e.target.value.toUpperCase());
                  setOffset(0);
                }}
                className="w-28"
              />
              <Select
                label="Decision"
                value={decision}
                onChange={(e) => {
                  setDecision(e.target.value);
                  setOffset(0);
                }}
              >
                <option value="">All</option>
                <option value="allowed">Allowed</option>
                <option value="blocked">Blocked</option>
                <option value="info">Info</option>
              </Select>
            </div>
          }
        >
          <Table<SignalLogEntry>
            loading={signals.isLoading}
            rows={signals.data?.data ?? []}
            rowKey={(r) => r.id}
            empty="No signals recorded yet. Blocked and allowed trade entries will appear here."
            columns={[
              { key: "when", header: "When", render: (r) => when(r.occurred_at) },
              { key: "symbol", header: "Symbol", render: (r) => r.symbol ?? "—" },
              { key: "rule", header: "Rule", render: (r) => r.rule_id ?? "—" },
              {
                key: "decision",
                header: "Decision",
                render: (r) => <Badge tone={decisionTone[r.decision]}>{r.decision}</Badge>,
              },
              { key: "message", header: "Detail", render: (r) => r.message ?? "" },
            ]}
          />
          <Pager offset={offset} total={signals.data?.total ?? 0} onChange={setOffset} />
        </Card>
      ) : (
        <Card
          title="Changes"
          actions={
            <Select
              label="Entity"
              value={entity}
              onChange={(e) => {
                setEntity(e.target.value);
                setOffset(0);
              }}
            >
              <option value="">All</option>
              <option value="trade">Trades</option>
              <option value="portfolio">Portfolios</option>
              <option value="watchlist">Watchlists</option>
              <option value="settings">Settings</option>
              <option value="symbol">Symbols</option>
            </Select>
          }
        >
          <Table<AuditLogEntry>
            loading={audit.isLoading}
            rows={audit.data?.data ?? []}
            rowKey={(r) => r.id}
            empty="No changes recorded yet."
            columns={[
              { key: "when", header: "When", render: (r) => when(r.occurred_at) },
              { key: "action", header: "Action", render: (r) => <span className="font-mono text-xs">{r.action}</span> },
              { key: "entity", header: "Entity", render: (r) => r.entity },
              {
                key: "change",
                header: "Change",
                render: (r) => (
                  <span className="text-xs text-gray-600">
                    {r.before ? JSON.stringify(r.before) : "—"} → {r.after ? JSON.stringify(r.after) : "—"}
                  </span>
                ),
              },
            ]}
          />
          <Pager offset={offset} total={audit.data?.total ?? 0} onChange={setOffset} />
        </Card>
      )}
    </div>
  );
}
