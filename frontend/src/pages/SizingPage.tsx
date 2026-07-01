import { PageHeader, Input, Button } from "../components/ui";

export function SizingPage() {
  return (
    <div className="space-y-4">
      <PageHeader title="Position Sizing Calculator" subtitle="Calculate contract quantities and risk exposure" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white border border-slate-200 rounded-lg p-5">
            <h3 className="text-sm font-semibold text-slate-900 mb-4">Parameters</h3>
            
            <div className="space-y-3">
              <Input label="Account Size" type="text" defaultValue="100000" />
              <Input label="Risk % Per Trade" type="text" defaultValue="2" />
              <Input label="Option Price" type="text" defaultValue="2.45" />
              <Input label="Delta" type="text" defaultValue="0.65" />
              <Button type="button" className="w-full mt-4">
                Calculate
              </Button>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white border border-slate-200 rounded-lg p-4">
              <p className="text-xs text-slate-500 mb-1">Risk Amount</p>
              <p className="text-2xl font-bold text-red-700">$2,000</p>
              <p className="text-xs text-slate-500 mt-1">2% of account</p>
            </div>
            
            <div className="bg-white border border-slate-200 rounded-lg p-4">
              <p className="text-xs text-slate-500 mb-1">Contracts</p>
              <p className="text-2xl font-bold text-slate-900">3</p>
              <p className="text-xs text-slate-500 mt-1">Recommended</p>
            </div>
            
            <div className="bg-white border border-slate-200 rounded-lg p-4">
              <p className="text-xs text-slate-500 mb-1">Total Cost</p>
              <p className="text-2xl font-bold text-slate-900">$735</p>
              <p className="text-xs text-slate-500 mt-1">0.74% of account</p>
            </div>
            
            <div className="bg-white border border-slate-200 rounded-lg p-4">
              <p className="text-xs text-slate-500 mb-1">Position Delta</p>
              <p className="text-2xl font-bold text-slate-900">195</p>
              <p className="text-xs text-slate-500 mt-1">Per $1 move</p>
            </div>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-lg p-5">
            <h3 className="text-sm font-semibold text-slate-900 mb-3">Risk Analysis</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-slate-600">If expires worthless:</p>
                <p className="text-sm font-semibold text-red-700">-$735.00</p>
              </div>
              <div>
                <p className="text-xs text-slate-600">Max gain (2:1 RR):</p>
                <p className="text-sm font-semibold text-green-700">+$4,000.00</p>
              </div>
              <div>
                <p className="text-xs text-slate-600">Breakeven move:</p>
                <p className="text-sm font-semibold text-slate-700">±0.89%</p>
              </div>
              <div>
                <p className="text-xs text-slate-600">Days to expiry:</p>
                <p className="text-sm font-semibold text-slate-700">30 DTE</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
