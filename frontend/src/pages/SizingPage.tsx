import { useState } from "react";

import { GateBanner } from "../components/gate";
import { Badge, Button, Card, Input, PageHeader, Select, Table } from "../components/ui";
import { useBands, useSizing } from "../hooks/queries";
import { fmtUsd } from "../utils";
import type { Band, BandUsage, Layer } from "../types";

const BANDS: Band[] = ["A", "B", "C", "D", "E"];
const STATUS_TONE = { ok: "green", near: "yellow", over: "red" } as const;

export function SizingPage() {
  const sizing = useSizing();
  const bands = useBands();

  const [layer, setLayer] = useState<Layer>("base");
  const [basis, setBasis] = useState<"max_loss" | "credit">("max_loss");
  const [amount, setAmount] = useState("");
  const [band, setBand] = useState<"" | Band>("");
  const [riskPct, setRiskPct] = useState("");
  const [error, setError] = useState<string | null>(null);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const value = Number(amount);
    if (!(value > 0)) {
      setError(basis === "max_loss" ? "Enter the max loss per contract in dollars." : "Enter the credit per share in dollars.");
      return;
    }
    const risk = riskPct.trim() === "" ? null : Number(riskPct);
    if (risk !== null && !(risk > 0 && risk <= 10)) {
      setError("Risk % must be above 0 and at most 10.");
      return;
    }
    setError(null);
    sizing.mutate({
      layer,
      band: band || null,
      risk_pct: risk,
      ...(basis === "max_loss" ? { max_loss_per_contract: value } : { credit: value }),
    });
  };

  const result = sizing.data;

  return (
    <div className="space-y-4">
      <PageHeader
        title="Position Sizing Calculator"
        subtitle="Contracts and capital at risk from your account size, risk %, the regime and band caps."
      />
      <GateBanner />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card title="Parameters" subtitle="Account size and risk % come from Settings.">
          <form onSubmit={submit} className="space-y-3" aria-label="Sizing parameters">
            <Select label="Layer" value={layer} onChange={(e) => setLayer(e.target.value as Layer)}>
              <option value="base">Base (1–1.5% risk)</option>
              <option value="growth">Growth (2–3% risk)</option>
            </Select>
            <Select label="Size by" value={basis} onChange={(e) => setBasis(e.target.value as "max_loss" | "credit")}>
              <option value="max_loss">Max loss per contract (recommended)</option>
              <option value="credit">Credit per share (Risk / Credit)</option>
            </Select>
            <Input
              label={basis === "max_loss" ? "Max loss per contract ($)" : "Credit per share ($)"}
              type="number"
              step="0.01"
              min="0"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
            <Select label="Band" value={band} onChange={(e) => setBand(e.target.value as "" | Band)}>
              <option value="">Not assigned</option>
              {BANDS.map((b) => (
                <option key={b} value={b}>
                  Band {b}
                </option>
              ))}
            </Select>
            <Input
              label="Risk % override (optional)"
              type="number"
              step="0.05"
              value={riskPct}
              onChange={(e) => setRiskPct(e.target.value)}
              hint="Leave empty to use your Settings."
            />
            {error && (
              <p role="alert" className="text-sm text-red-600">
                {error}
              </p>
            )}
            <Button type="submit" className="w-full" loading={sizing.isPending}>
              Calculate
            </Button>
          </form>
        </Card>

        <div className="lg:col-span-2 space-y-4">
          {sizing.isError && (
            <p role="alert" className="text-sm text-red-600">
              Could not calculate the size. Try again.
            </p>
          )}
          {!result ? (
            <Card>
              <p className="text-sm text-gray-500">Enter the numbers and press Calculate.</p>
            </Card>
          ) : (
            <>
              {result.blocked && (
                <div role="alert" className="rounded-md border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-900">
                  <p className="font-semibold">Cannot size this trade</p>
                  <ul className="mt-1 list-disc pl-5">
                    {result.reasons.map((r) => (
                      <li key={r.rule_id}>
                        <span className="font-mono text-xs mr-1">{r.rule_id}</span>
                        {r.message}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Stat label="Risk budget" value={fmtUsd(result.risk_budget)} note={`${result.risk_pct}% of ${fmtUsd(result.account_size)}`} />
                <Stat label="Contracts" value={String(result.quantity)} note={result.mode === "none" ? "No price given" : `by ${result.mode === "max_loss" ? "max loss" : "credit"}`} />
                <Stat label="Capital at risk" value={result.risk_amount === null ? "—" : fmtUsd(result.risk_amount)} note={result.risk_amount === null ? "Needs max loss" : "quantity × max loss"} />
                <Stat
                  label="Band use after"
                  value={result.band_exposure_after_pct === null ? "—" : `${result.band_exposure_after_pct}%`}
                  note={result.band_cap_pct === null ? "No band cap checked" : `cap ${result.band_cap_pct}%`}
                />
              </div>

              <p className="text-xs text-gray-500">
                Regime {result.regime_state} · Base/Growth split {result.layer_split.base}/{result.layer_split.growth}
              </p>

              {result.warnings.length > 0 && (
                <div className="rounded-md border border-yellow-300 bg-yellow-50 px-3 py-2 text-sm text-yellow-900">
                  <p className="font-semibold">Warnings</p>
                  <ul className="mt-1 list-disc pl-5">
                    {result.warnings.map((w) => (
                      <li key={w}>{w}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}

          <Card title="Capital band usage" subtitle="Capital at risk in open trades vs each band's cap.">
            <Table<BandUsage>
              loading={bands.isLoading}
              rows={bands.data ?? []}
              rowKey={(r) => r.band}
              columns={[
                { key: "band", header: "Band", render: (r) => <span className="font-semibold">{r.band}</span> },
                { key: "exposure", header: "At risk", align: "right", render: (r) => fmtUsd(r.exposure) },
                { key: "pct", header: "% of account", align: "right", render: (r) => `${r.exposure_pct}%` },
                { key: "cap", header: "Cap", align: "right", render: (r) => `${r.cap_pct}%` },
                { key: "status", header: "Status", render: (r) => <Badge tone={STATUS_TONE[r.status]}>{r.status}</Badge> },
              ]}
            />
          </Card>
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-4">
      <p className="text-xs text-slate-500 mb-1">{label}</p>
      <p className="text-2xl font-bold text-slate-900">{value}</p>
      <p className="text-xs text-slate-500 mt-1">{note}</p>
    </div>
  );
}
