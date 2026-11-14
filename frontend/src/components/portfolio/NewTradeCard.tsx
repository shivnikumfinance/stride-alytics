import { useState } from "react";

import { extractErrorMessage, extractGateReasons } from "../../api/errors";
import { useAddTrade, useGateCheck, useSizing } from "../../hooks/queries";
import { todayLocal } from "../../utils/date";
import type { Band, Direction, Layer, TradeType } from "../../types";
import { GateResultPanel } from "../gate";
import { Button, Card, Input, Select, Textarea } from "../ui";

const BANDS: Band[] = ["A", "B", "C", "D", "E"];
const num = (v: string) => (v.trim() === "" ? null : Number(v));

/** The Add-trade form: gate check, size suggestion, and the reasons when an entry is blocked. */
export function NewTradeCard({ portfolioId }: { portfolioId: string }) {
  const [symbol, setSymbol] = useState("AAPL");
  const [tradeType, setTradeType] = useState<TradeType>("put");
  const [direction, setDirection] = useState<Direction>("short");
  const [entryDate, setEntryDate] = useState(todayLocal());
  const [entryPrice, setEntryPrice] = useState("1.00");
  const [quantity, setQuantity] = useState("1");
  const [layer, setLayer] = useState<"" | Layer>("base");
  const [band, setBand] = useState<"" | Band>("");
  const [strike, setStrike] = useState("");
  const [expiry, setExpiry] = useState("");
  const [credit, setCredit] = useState("");
  const [maxLoss, setMaxLoss] = useState("");
  const [riskAmount, setRiskAmount] = useState("");
  const [notes, setNotes] = useState("");

  const add = useAddTrade(portfolioId);
  const gateCheck = useGateCheck();
  const sizing = useSizing();

  const isOption = tradeType !== "stock";
  const blockedReasons = add.isError ? extractGateReasons(add.error) : [];

  const check = () => {
    gateCheck.mutate({
      symbol,
      trade_type: tradeType,
      layer: layer || null,
      strike: isOption ? num(strike) : null,
      expiry: isOption && expiry ? expiry : null,
      entry_date: entryDate,
    });
  };

  const suggestSize = () => {
    if (!layer) return;
    sizing.mutate(
      { layer, band: band || null, credit: num(credit), max_loss_per_contract: num(maxLoss) },
      {
        onSuccess: (r) => {
          if (r.quantity > 0) setQuantity(String(r.quantity));
          if (r.risk_amount !== null) setRiskAmount(String(r.risk_amount));
        },
      },
    );
  };

  return (
    <Card title="Add trade" subtitle="New entries must pass the Do-Not-Trade gate.">
      <form
        aria-label="Add trade"
        onSubmit={(e) => {
          e.preventDefault();
          gateCheck.reset();
          add.mutate({
            portfolio_id: portfolioId,
            symbol,
            trade_type: tradeType,
            direction,
            entry_price: Number(entryPrice),
            quantity: Number(quantity),
            entry_date: entryDate,
            notes: notes || null,
            strike: isOption ? num(strike) : null,
            expiry: isOption && expiry ? expiry : null,
            layer: layer || null,
            band: band || null,
            credit: num(credit),
            risk_amount: num(riskAmount),
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
          <Input label="Entry date" type="date" value={entryDate} onChange={(e) => setEntryDate(e.target.value)} required />
        </div>
        {isOption && (
          <div className="grid grid-cols-2 gap-3">
            <Input label="Strike" type="number" step="0.5" value={strike} onChange={(e) => setStrike(e.target.value)} />
            <Input label="Expiry" type="date" value={expiry} onChange={(e) => setExpiry(e.target.value)} />
          </div>
        )}
        <div className="grid grid-cols-2 gap-3">
          <Select label="Layer" value={layer} onChange={(e) => setLayer(e.target.value as "" | Layer)}>
            <option value="">Not set</option>
            <option value="base">Base</option>
            <option value="growth">Growth</option>
          </Select>
          <Select label="Band" value={band} onChange={(e) => setBand(e.target.value as "" | Band)}>
            <option value="">Not set</option>
            {BANDS.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </Select>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Input label="Entry price" type="number" step="0.01" value={entryPrice} onChange={(e) => setEntryPrice(e.target.value)} />
          <Input label="Quantity" type="number" min="1" value={quantity} onChange={(e) => setQuantity(e.target.value)} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Input label="Credit per share" type="number" step="0.01" value={credit} onChange={(e) => setCredit(e.target.value)} />
          <Input label="Max loss per contract ($)" type="number" step="1" value={maxLoss} onChange={(e) => setMaxLoss(e.target.value)} />
        </div>
        <Input
          label="Capital at risk ($)"
          type="number"
          step="1"
          value={riskAmount}
          onChange={(e) => setRiskAmount(e.target.value)}
          hint="Counted against the band cap. Suggest size fills this in."
        />
        <Textarea label="Notes" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />

        <div className="flex gap-2">
          <Button type="button" variant="secondary" className="flex-1" onClick={check} loading={gateCheck.isPending}>
            Check gate
          </Button>
          <Button type="button" variant="secondary" className="flex-1" onClick={suggestSize} loading={sizing.isPending} disabled={!layer}>
            Suggest size
          </Button>
        </div>

        {gateCheck.data && (
          <GateResultPanel
            clear={gateCheck.data.clear}
            status={gateCheck.data.status}
            reasons={gateCheck.data.reasons}
            notEvaluated={gateCheck.data.not_evaluated}
            message={gateCheck.data.message}
          />
        )}

        {sizing.data && (
          <div className="rounded-md border border-gray-200 bg-gray-50 px-3 py-2 text-sm" aria-label="Size suggestion">
            {sizing.data.blocked ? (
              <ul className="list-disc pl-5 text-red-800">
                {sizing.data.reasons.map((r) => (
                  <li key={r.rule_id}>
                    <span className="font-mono text-xs mr-1">{r.rule_id}</span>
                    {r.message}
                  </li>
                ))}
              </ul>
            ) : (
              <p>
                Suggested <strong>{sizing.data.quantity}</strong> contract(s); risk budget $
                {sizing.data.risk_budget.toLocaleString()}.
              </p>
            )}
            {sizing.data.warnings.map((w) => (
              <p key={w} className="text-xs text-yellow-800 mt-1">
                {w}
              </p>
            ))}
          </div>
        )}

        {add.isError &&
          (blockedReasons.length > 0 ? (
            <GateResultPanel clear={false} status="BLOCKED — trade not recorded" reasons={blockedReasons} />
          ) : (
            <p role="alert" className="text-sm text-red-600">
              {extractErrorMessage(add.error, "Could not add the trade")}
            </p>
          ))}

        <Button type="submit" loading={add.isPending} className="w-full">
          Add trade
        </Button>
      </form>
    </Card>
  );
}
