import { PageHeader } from "../components/ui";
import { RegimePanel } from "../components/regime";

export function RegimePage() {
  return (
    <div className="space-y-4">
      <PageHeader title="Market Regime" subtitle="Classify the broad market as bull, bear, or ranging." />
      <RegimePanel />
    </div>
  );
}
