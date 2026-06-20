import { FilterPanel, ResultsTable } from "../components/screener";

export function ScreenerPage() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-gray-900">Options Screener</h1>
        <p className="text-sm text-gray-500">Filter the chain by strike, expiry, IV, volume, and Greeks.</p>
      </header>
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <FilterPanel />
        </div>
        <div className="lg:col-span-3">
          <ResultsTable />
        </div>
      </div>
    </div>
  );
}
