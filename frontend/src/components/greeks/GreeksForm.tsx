import { useState } from "react";
import { Card, Input, Select, Button, Table } from "../ui";
import { useCalculateGreeks } from "../../hooks/queries";
import { fmtNum, fmtUsd } from "../../utils";
import type { GreeksResult } from "../../types";

export function GreeksForm() {
  const [spot, setSpot] = useState(100);
  const [strike, setStrike] = useState(100);
  const [dte, setDte] = useState(30);
  const [rate, setRate] = useState(0.05);
  const [iv, setIv] = useState(0.3);
  const [type, setType] = useState<"call" | "put">("call");

  const mutation = useCalculateGreeks();
  const result: GreeksResult | undefined = mutation.data;

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      spot: Number(spot),
      strike: Number(strike),
      time_to_expiry: Number(dte) / 365,
      risk_free_rate: Number(rate),
      volatility: Number(iv),
      option_type: type,
    });
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Card title="Inputs" subtitle="Black-Scholes parameters">
        <form onSubmit={submit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Input label="Spot" type="number" step="0.01" value={spot} onChange={(e) => setSpot(Number(e.target.value))} />
            <Input label="Strike" type="number" step="0.01" value={strike} onChange={(e) => setStrike(Number(e.target.value))} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Days to expiry" type="number" value={dte} onChange={(e) => setDte(Number(e.target.value))} />
            <Select label="Type" value={type} onChange={(e) => setType(e.target.value as "call" | "put")}>
              <option value="call">Call</option>
              <option value="put">Put</option>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Risk-free rate" type="number" step="0.001" value={rate} onChange={(e) => setRate(Number(e.target.value))} hint="0.05 = 5%" />
            <Input label="Implied volatility" type="number" step="0.01" value={iv} onChange={(e) => setIv(Number(e.target.value))} hint="0.30 = 30%" />
          </div>
          <Button type="submit" loading={mutation.isPending} className="w-full">
            Calculate
          </Button>
        </form>
      </Card>

      <Card title="Results" subtitle={result ? `Inputs: spot ${result.inputs.spot} · strike ${result.inputs.strike}` : "Awaiting input"}>
        {result ? (
          <Table<GreeksRow>
            columns={GREEKS_COLUMNS}
            rows={[
              { metric: "Delta (Δ)", value: fmtNum(result.delta) },
              { metric: "Gamma (Γ)", value: fmtNum(result.gamma, 6) },
              { metric: "Theta (Θ)", value: fmtNum(result.theta) },
              { metric: "Vega (ν)", value: fmtNum(result.vega) },
              { metric: "Rho (ρ)", value: fmtNum(result.rho) },
              { metric: "Call price", value: fmtUsd(result.price_call) },
              { metric: "Put price", value: fmtUsd(result.price_put) },
            ]}
            rowKey={(r) => r.metric}
          />
        ) : (
          <p className="text-sm text-gray-500">Enter inputs and click Calculate.</p>
        )}
      </Card>
    </div>
  );
}

interface GreeksRow {
  metric: string;
  value: string;
}

const GREEKS_COLUMNS = [
  { key: "metric", header: "Metric" },
  { key: "value", header: "Value", align: "right" as const },
];
