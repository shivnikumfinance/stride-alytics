import { PageHeader } from "../components/ui";
import { PortfolioView } from "../components/portfolio";

export function PortfolioPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Portfolio" subtitle="Track trades, P&L, and win-rate per portfolio." />
      <PortfolioView />
    </div>
  );
}
