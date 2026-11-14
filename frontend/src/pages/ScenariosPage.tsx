import { useState } from "react";

import { ScenarioCurve } from "../components/charts";
import { Badge, Button, Card, Input, PageHeader, Table } from "../components/ui";
import { useDeleteScenario, useRunScenario, useSaveScenario, useScenarios } from "../hooks/queries";
import type { SavedScenario, ScenarioParams, ScenarioPosition } from "../types";
import { fmtUsd } from "../utils";

const PRESETS: { name: string; params: ScenarioParams }[] = [
  { name: "Market -10%", params: { spot_pct: -10, iv_shift: 0.05, days_forward: 0 } },
  { name: "Crash -20%", params: { spot_pct: -20, iv_shift: 0.2, days_forward: 0 } },
  { name: "Rally +10%", params: { spot_pct: 10, iv_shift: -0.03, days_forward: 0 } },
  { name: "Two weeks pass", params: { spot_pct: 0, iv_shift: 0, days_forward: 14 } },
];

const money = (v: number | null) => (v === null ? "—" : fmtUsd(v));

export function ScenariosPage() {
  const [spot, setSpot] = useState("-10");
  const [iv, setIv] = useState("5"); // shown in points; the API takes a fraction
  const [days, setDays] = useState("0");
  const [name, setName] = useState("");

  const run = useRunScenario();
  const save = useSaveScenario();
  const saved = useScenarios();
  const remove = useDeleteScenario();

  const spotN = Number(spot);
  const ivN = Number(iv);
  const daysN = Number(days);
  const problem =
    !Number.isFinite(spotN) || spotN < -90 || spotN > 200
      ? "Price move must be between -90% and +200%."
      : !Number.isFinite(ivN) || ivN < -50 || ivN > 100
        ? "Volatility change must be between -50 and +100 points."
        : !Number.isInteger(daysN) || daysN < 0 || daysN > 365
          ? "Days must be a whole number from 0 to 365."
          : null;

  const params = (): ScenarioParams => ({ spot_pct: spotN, iv_shift: ivN / 100, days_forward: daysN });
  const load = (p: ScenarioParams) => {
    setSpot(String(p.spot_pct));
    setIv(String(Math.round(p.iv_shift * 1000) / 10));
    setDays(String(p.days_forward));
    run.mutate(p);
  };
  const result = run.data;

  return (
    <div className="space-y-4">
      <PageHeader
        title="Scenarios"
        subtitle="Stress-test your open positions: what if the price moves, volatility changes or time passes?"
      />

      <Card title="Define a scenario" subtitle="Options are repriced with Black-Scholes; positions without prices are listed, not guessed.">
        <form
          className="grid grid-cols-1 gap-3 sm:grid-cols-4 sm:items-end"
          onSubmit={(e) => {
            e.preventDefault();
            if (!problem) run.mutate(params());
          }}
        >
          <Input label="Price move (%)" type="number" step="any" value={spot} onChange={(e) => setSpot(e.target.value)} />
          <Input label="Volatility change (points)" type="number" step="any" value={iv} onChange={(e) => setIv(e.target.value)} />
          <Input label="Days forward" type="number" value={days} onChange={(e) => setDays(e.target.value)} />
          <Button type="submit" loading={run.isPending} disabled={problem !== null}>
            Run scenario
          </Button>
        </form>
        {problem && (
          <p role="alert" className="mt-2 text-sm text-red-600">
            {problem}
          </p>
        )}
        <div className="mt-3 flex flex-wrap gap-2">
          {PRESETS.map((p) => (
            <Button key={p.name} size="sm" variant="secondary" onClick={() => load(p.params)}>
              {p.name}
            </Button>
          ))}
        </div>
        {run.isError && (
          <p role="alert" className="mt-2 text-sm text-red-600">
            Could not run the scenario. Try again.
          </p>
        )}
      </Card>

      {result && (
        <>
          <Card
            title="Result"
            actions={
              <Badge tone={result.total_change >= 0 ? "green" : "red"}>
                {result.total_change >= 0 ? "+" : ""}
                {fmtUsd(result.total_change)}
              </Badge>
            }
          >
            <p className="text-sm text-gray-700">
              Total P&amp;L change across {result.priced} priced position{result.priced === 1 ? "" : "s"}:{" "}
              <strong>{fmtUsd(result.total_change)}</strong>. Scenario P&amp;L: <strong>{fmtUsd(result.total_scenario_pnl)}</strong>.
            </p>
            {result.unpriced > 0 && (
              <p role="status" className="mt-2 text-sm text-amber-800">
                {result.unpriced} position(s) could not be priced and are not in the totals.
              </p>
            )}
            {result.positions.length === 0 && <p className="mt-2 text-sm text-gray-600">You have no open positions.</p>}
          </Card>

          {result.positions.length > 0 && (
            <Card title="By position" bodyClassName="p-0">
              <Table<ScenarioPosition>
                rows={result.positions}
                rowKey={(r) => r.trade_id}
                columns={[
                  { key: "sym", header: "Position", render: (r) => `${r.symbol} ${r.direction} ${r.trade_type}` },
                  { key: "cur", header: "P&L now", align: "right", render: (r) => money(r.current_pnl) },
                  { key: "scn", header: "P&L in scenario", align: "right", render: (r) => money(r.scenario_pnl) },
                  {
                    key: "chg",
                    header: "Change",
                    align: "right",
                    render: (r) =>
                      r.priced ? (
                        <span className={(r.change ?? 0) >= 0 ? "text-green-700" : "text-red-700"}>{money(r.change)}</span>
                      ) : (
                        <span className="text-amber-700">Not priced: {r.reason}</span>
                      ),
                  },
                ]}
              />
            </Card>
          )}

          {result.ladder.length > 0 && result.priced > 0 && (
            <Card title="P&L curve" subtitle="Total change for different price moves, with the same volatility and time shocks.">
              <ScenarioCurve ladder={result.ladder} />
            </Card>
          )}
        </>
      )}

      <Card title="Saved scenarios">
        <form
          className="mb-3 flex flex-wrap items-end gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            if (!problem && name.trim()) save.mutate({ ...params(), name: name.trim() }, { onSuccess: () => setName("") });
          }}
        >
          <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Earnings gap" />
          <Button type="submit" variant="secondary" loading={save.isPending} disabled={problem !== null || !name.trim()}>
            Save current
          </Button>
          {save.isError && (
            <span role="alert" className="text-sm text-red-600">
              Could not save (is the name already used?).
            </span>
          )}
        </form>
        <Table<SavedScenario>
          loading={saved.isLoading}
          rows={saved.data ?? []}
          rowKey={(r) => r.id}
          empty="No saved scenarios yet."
          columns={[
            { key: "name", header: "Name", render: (r) => r.name },
            {
              key: "p",
              header: "Shock",
              render: (r) =>
                `${r.params.spot_pct}% price, ${Math.round(r.params.iv_shift * 1000) / 10} pts vol, ${r.params.days_forward} d`,
            },
            {
              key: "a",
              header: "",
              align: "right",
              render: (r) => (
                <span className="inline-flex gap-2">
                  <Button size="sm" variant="secondary" onClick={() => load(r.params)}>
                    Run
                  </Button>
                  <Button size="sm" variant="ghost" aria-label={`Delete ${r.name}`} onClick={() => remove.mutate(r.id)}>
                    Delete
                  </Button>
                </span>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
}
