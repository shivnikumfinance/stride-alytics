import { PageHeader } from "../components/ui";
import { RegimePanel, RegimeScoreCard } from "../components/regime";

export function RegimePage() {
  return (
    <div className="space-y-4">
      <PageHeader
        title="Market Regime"
        subtitle="The 0–100 regime score that drives the Base/Growth split, sizing and the trade gate."
      />
      <RegimeScoreCard />
      <RegimePanel />
    </div>
  );
}
