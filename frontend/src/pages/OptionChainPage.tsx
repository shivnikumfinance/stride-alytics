import { useState } from "react";

import { Badge, Button, Card, Input, PageHeader, SampleDataBadge, Select } from "../components/ui";
import { useOptionChain } from "../hooks/queries";
import type { ChainSide } from "../types";
import { classNames } from "../utils";

const num = (v: number | null | undefined, digits = 2) => (v === null || v === undefined ? "—" : v.toFixed(digits));
const pct = (v: number | null) => (v === null ? "—" : `${Math.round(v * 100)}%`);

function SideCells({ side, mirror }: { side: ChainSide | null; mirror?: boolean }) {
  const cells = side
    ? [num(side.bid), num(side.ask), num(side.iv * 100, 1) + "%", num(side.delta), pct(side.pop_short), String(side.open_interest)]
    : Array(6).fill("—");
  return (
    <>
      {(mirror ? [...cells].reverse() : cells).map((c, i) => (
        <td key={i} className="px-2 py-1.5 text-right tabular-nums">
          {c}
        </td>
      ))}
    </>
  );
}

export function OptionChainPage() {
  const [input, setInput] = useState("AAPL");
  const [symbol, setSymbol] = useState("AAPL");
  const [expiry, setExpiry] = useState<string | undefined>(undefined);
  const chain = useOptionChain(symbol, expiry);
  const data = chain.data;

  const head = ["Bid", "Ask", "IV", "Delta", "PoP", "OI"];

  return (
    <div className="space-y-4">
      <PageHeader
        title="Option Chain"
        subtitle="Calls and puts by strike with Greeks and probability of profit for a short position."
      />
      <Card>
        <form
          className="flex flex-wrap items-end gap-3"
          onSubmit={(e) => {
            e.preventDefault();
            setSymbol(input.trim().toUpperCase());
            setExpiry(undefined);
          }}
        >
          <Input label="Symbol" value={input} onChange={(e) => setInput(e.target.value.toUpperCase())} />
          {data && (
            <Select label="Expiry" value={data.expiry} onChange={(e) => setExpiry(e.target.value)}>
              {data.expiries.map((x) => (
                <option key={x} value={x}>
                  {x}
                </option>
              ))}
            </Select>
          )}
          <Button type="submit" loading={chain.isFetching}>
            Load chain
          </Button>
        </form>
      </Card>

      {chain.isLoading ? (
        <p className="text-sm text-gray-500">Loading the chain…</p>
      ) : chain.isError || !data ? (
        <p role="alert" className="text-sm text-red-600">
          Could not load a chain for {symbol}. Check the symbol and try again.
        </p>
      ) : (
        <Card
          title={`${data.symbol} · spot ${data.spot.toFixed(2)}`}
          subtitle={`Expiry ${data.expiry} (${data.dte} days)`}
          actions={<SampleDataBadge source={data.source} />}
          bodyClassName="p-0"
        >
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50 text-xs font-semibold uppercase tracking-wider text-gray-600">
                <tr>
                  <th colSpan={6} className="px-2 py-2 text-center">
                    Calls
                  </th>
                  <th rowSpan={2} scope="col" className="px-3 py-2 text-center">
                    Strike
                  </th>
                  <th colSpan={6} className="px-2 py-2 text-center">
                    Puts
                  </th>
                </tr>
                <tr>
                  {head.map((h) => (
                    <th key={`c${h}`} scope="col" className="px-2 py-1 text-right">
                      {h}
                    </th>
                  ))}
                  {[...head].reverse().map((h) => (
                    <th key={`p${h}`} scope="col" className="px-2 py-1 text-right">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data.strikes.map((s) => {
                  const nearest = Math.abs(s.strike - data.spot) / data.spot < 0.01;
                  return (
                    <tr key={s.strike} className={classNames(nearest && "bg-indigo-50/60")}>
                      <SideCells side={s.call} />
                      <th scope="row" className="px-3 py-1.5 text-center font-semibold text-gray-900">
                        {s.strike}
                        {nearest && <Badge tone="indigo" className="ml-1">ATM</Badge>}
                      </th>
                      <SideCells side={s.put} mirror />
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="px-4 py-3 text-xs text-gray-500">
            PoP is the chance a short option at that strike expires worthless, estimated as 1 − |delta|. Greeks use
            Black-Scholes from the quoted implied volatility.
          </p>
        </Card>
      )}
    </div>
  );
}
