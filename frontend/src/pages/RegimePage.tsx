import { RegimePanel } from "../components/regime";

export function RegimePage() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-gray-900">Market Regime</h1>
        <p className="text-sm text-gray-500">Classify the broad market as bull, bear, or ranging.</p>
      </header>
      <RegimePanel />
    </div>
  );
}
