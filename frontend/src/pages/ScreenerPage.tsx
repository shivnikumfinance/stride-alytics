import { PageHeader } from "../components/ui";
import { FilterPanel, ResultsTable } from "../components/screener";

export function ScreenerPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Options Screener" subtitle="Filter the chain by strike, expiry, IV, volume, and Greeks." />
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
