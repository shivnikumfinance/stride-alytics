import { GreeksForm } from "../components/greeks";

export function GreeksPage() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-gray-900">Greeks Calculator</h1>
        <p className="text-sm text-gray-500">Black-Scholes pricing and risk sensitivities (Δ, Γ, Θ, ν, ρ).</p>
      </header>
      <GreeksForm />
    </div>
  );
}
