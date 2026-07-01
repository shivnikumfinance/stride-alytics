import { useState } from "react";
import { PageHeader, Card, Badge } from "../components/ui";

export function StrategyMatrixPage() {
  const [layer, setLayer] = useState("all");
  const [band, setBand] = useState("all");

  const strategies = [
    { name: "Covered Call", layer: "Base", defensive: "Available", normal: "Available", growth: "Limited" },
    { name: "Cash-Secured Put", layer: "Base", defensive: "Blocked", normal: "Available", growth: "Available" },
    { name: "Iron Condor", layer: "Base", defensive: "Available", normal: "Available", growth: "Limited" },
    { name: "Long Call", layer: "Growth", defensive: "Blocked", normal: "Limited", growth: "Available" },
    { name: "Long Put", layer: "Growth", defensive: "Available", normal: "Blocked", growth: "Blocked" },
    { name: "Diagonal Spread", layer: "Growth", defensive: "Limited", normal: "Available", growth: "Available" },
  ];

  const filtered = strategies.filter(s => layer === "all" || s.layer === layer);

  return (
    <div className="space-y-6">
      <PageHeader title="Strategy Design Matrix" subtitle="Interactive strategy × regime grid — filter by layer and band" />

      <Card>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-slate-900">Strategy × Regime Suitability</h3>
          <div className="flex gap-3">
            <select value={layer} onChange={e => setLayer(e.target.value)} className="text-xs border rounded px-2 py-1">
              <option value="all">All Layers</option>
              <option value="Base">Base</option>
              <option value="Growth">Growth</option>
            </select>
            <select value={band} onChange={e => setBand(e.target.value)} className="text-xs border rounded px-2 py-1">
              <option value="all">All Bands</option>
              <option value="A">A</option>
              <option value="B">B</option>
              <option value="C">C</option>
              <option value="D">D</option>
              <option value="E">E</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-3 text-xs font-semibold text-slate-600">Strategy</th>
                <th className="text-center py-2 px-3 text-xs font-semibold text-slate-600">Layer</th>
                <th className="text-center py-2 px-3 text-xs font-semibold text-red-600">Defensive</th>
                <th className="text-center py-2 px-3 text-xs font-semibold text-amber-600">Normal</th>
                <th className="text-center py-2 px-3 text-xs font-semibold text-green-600">Growth</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((s, i) => (
                <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="py-2 px-3 font-medium">{s.name}</td>
                  <td className="text-center py-2 px-3">
                    <Badge tone={s.layer === "Base" ? "blue" : "purple"}>{s.layer}</Badge>
                  </td>
                  <td className="text-center py-2 px-3">
                    <span className={`px-2 py-1 rounded text-xs ${s.defensive === "Available" ? "bg-green-50 text-green-700 border border-green-200" : s.defensive === "Limited" ? "bg-yellow-50 text-yellow-700 border border-yellow-200" : "bg-red-50 text-red-700 border border-red-200"}`}>
                      {s.defensive}
                    </span>
                  </td>
                  <td className="text-center py-2 px-3">
                    <span className={`px-2 py-1 rounded text-xs ${s.normal === "Available" ? "bg-green-50 text-green-700 border border-green-200" : s.normal === "Limited" ? "bg-yellow-50 text-yellow-700 border border-yellow-200" : "bg-red-50 text-red-700 border border-red-200"}`}>
                      {s.normal}
                    </span>
                  </td>
                  <td className="text-center py-2 px-3">
                    <span className={`px-2 py-1 rounded text-xs ${s.growth === "Available" ? "bg-green-50 text-green-700 border border-green-200" : s.growth === "Limited" ? "bg-yellow-50 text-yellow-700 border border-yellow-200" : "bg-red-50 text-red-700 border border-red-200"}`}>
                      {s.growth}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 flex gap-4 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-green-100 border border-green-200"></div>
            <span>Available</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-yellow-100 border border-yellow-200"></div>
            <span>Limited</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-red-100 border border-red-200"></div>
            <span>Blocked</span>
          </div>
        </div>
      </Card>
    </div>
  );
}
