import { useState } from "react";
import { Link } from "react-router-dom";

import { GateBanner } from "../components/gate";
import { Badge, Card, PageHeader, Select } from "../components/ui";
import { useStrategyMatrix } from "../hooks/queries";
import type { Availability, MatrixCell } from "../types";
import { classNames } from "../utils";

const LABEL: Record<Availability, string> = {
  available: "Available",
  limited: "Limited",
  blocked: "Blocked",
};
const ICON: Record<Availability, string> = { available: "🟢", limited: "🟡", blocked: "🔴" };
const TONE: Record<Availability, "green" | "yellow" | "red"> = {
  available: "green",
  limited: "yellow",
  blocked: "red",
};

const REGIME_LABEL: Record<string, string> = { DEFENSIVE: "Defensive", NORMAL: "Normal", GROWTH: "Growth" };

function Cell({ cell, strategy }: { cell: MatrixCell; strategy: string }) {
  const grey = cell.availability === "blocked" || cell.filtered;
  return (
    <td className={classNames("px-3 py-3 align-top border-l border-gray-100", cell.current && "bg-indigo-50/60")}>
      <Link
        to={`/screener?strategy=${encodeURIComponent(strategy)}`}
        aria-label={`${strategy}, ${cell.availability}${cell.filtered ? ", filtered out" : ""}`}
        className={classNames("block space-y-1 rounded-md p-1 hover:bg-gray-50", grey && "opacity-50")}
      >
        <Badge tone={TONE[cell.availability]}>
          {ICON[cell.availability]} {LABEL[cell.availability]}
        </Badge>
        {cell.availability !== "blocked" && (
          <p className="text-xs text-gray-600">
            {cell.layers.join(" / ")} · bands {cell.bands.join(", ")}
          </p>
        )}
        <p className="text-xs text-gray-500">{cell.note}</p>
        {cell.gate && (
          <p className={classNames("text-xs font-medium", cell.gate === "clear" ? "text-green-700" : "text-red-700")}>
            Gate: {cell.gate}
          </p>
        )}
      </Link>
    </td>
  );
}

export function StrategyMatrixPage() {
  const [layer, setLayer] = useState("");
  const [band, setBand] = useState("");
  const matrix = useStrategyMatrix(layer, band);
  const data = matrix.data;

  return (
    <div className="space-y-4">
      <PageHeader
        title="Strategy Design Matrix"
        subtitle="Which strategies suit each regime. The current regime is highlighted and follows the trade gate."
      />
      <GateBanner />

      <div className="flex flex-wrap items-end gap-3">
        <Select label="Layer" value={layer} onChange={(e) => setLayer(e.target.value)}>
          <option value="">All layers</option>
          <option value="base">Base</option>
          <option value="growth">Growth</option>
        </Select>
        <Select label="Capital band" value={band} onChange={(e) => setBand(e.target.value)}>
          <option value="">All bands</option>
          {["A", "B", "C", "D", "E"].map((b) => (
            <option key={b} value={b}>
              Band {b}
            </option>
          ))}
        </Select>
      </div>

      {matrix.isLoading ? (
        <p className="text-sm text-gray-500">Loading the matrix…</p>
      ) : matrix.isError || !data ? (
        <p role="alert" className="text-sm text-red-600">
          Could not load the matrix. Try refreshing.
        </p>
      ) : (
        <Card
          title={
            data.current_regime
              ? `Current regime: ${REGIME_LABEL[data.current_regime]}${data.regime_score !== null ? ` (${data.regime_score})` : ""}`
              : "Current regime unavailable"
          }
          subtitle={
            data.gate_clear === false
              ? "The trade gate is blocked, so every strategy in the current regime is blocked."
              : "Suitability is a design guide, not a forecast."
          }
          bodyClassName="p-0"
        >
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50 text-left text-xs font-semibold uppercase tracking-wider text-gray-600">
                <tr>
                  <th scope="col" className="px-4 py-3">
                    Strategy
                  </th>
                  {data.regimes.map((r) => (
                    <th key={r} scope="col" className="px-3 py-3 border-l border-gray-100">
                      {REGIME_LABEL[r]}
                      {r === data.current_regime && <span className="ml-1 text-indigo-600">(now)</span>}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data.rows.map((row) => (
                  <tr key={row.strategy}>
                    <th scope="row" className="px-4 py-3 text-left align-top font-medium text-gray-900">
                      {row.strategy}
                      <p className="mt-0.5 max-w-xs text-xs font-normal text-gray-500">{row.description}</p>
                    </th>
                    {data.regimes.map((r) => (
                      <Cell key={r} cell={row.cells[r]} strategy={row.strategy} />
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
