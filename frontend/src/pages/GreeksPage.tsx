import { PageHeader } from "../components/ui";
import { GreeksForm } from "../components/greeks";

export function GreeksPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Greeks Calculator" subtitle="Black-Scholes pricing and risk sensitivities (Δ, Γ, Θ, ν, ρ)." />
      <GreeksForm />
    </div>
  );
}
