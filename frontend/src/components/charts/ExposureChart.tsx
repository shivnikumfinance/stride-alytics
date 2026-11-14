import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { SectorExposure } from "../../types";

/** Capital at risk per sector, as a share of equity. Bars over the limit turn red. */
export function ExposureChart({ sectors, limitPct }: { sectors: SectorExposure[]; limitPct: number }) {
  const data = sectors.map((s) => ({ sector: s.sector, pct: s.pct_of_equity ?? 0, dollars: s.capital_at_risk }));
  return (
    <div role="img" aria-label={`Capital at risk in ${data.length} sector(s), limit ${limitPct}% of equity`} className="h-56">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, bottom: 0, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" horizontal={false} />
          <XAxis type="number" unit="%" tick={{ fontSize: 11 }} domain={[0, (max: number) => Math.max(max, limitPct)]} />
          <YAxis type="category" dataKey="sector" tick={{ fontSize: 11 }} width={110} />
          <Tooltip formatter={(v: number) => `${v}% of equity`} />
          <Bar dataKey="pct" name="Share of equity" radius={[0, 3, 3, 0]}>
            {data.map((d) => (
              <Cell key={d.sector} fill={d.pct > limitPct ? "#dc2626" : "#4f46e5"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
