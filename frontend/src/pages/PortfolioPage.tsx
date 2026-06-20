import { PortfolioView } from "../components/portfolio";

export function PortfolioPage() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-gray-900">Portfolio</h1>
        <p className="text-sm text-gray-500">Track trades, P&amp;L, and win-rate per portfolio.</p>
      </header>
      <PortfolioView />
    </div>
  );
}
