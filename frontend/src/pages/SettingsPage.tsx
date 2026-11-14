import { useEffect, useState } from "react";

import { Button, Card, Input, PageHeader } from "../components/ui";
import { useScreenerLimits, useSettings, useUpdateSettings } from "../hooks/queries";
import { useAuthStore } from "../store";
import type { BandCaps, RegimeWeights } from "../types";
import { BANDS, WEIGHTS, toForm, validateForm, type SettingsForm } from "../utils/settingsForm";

export function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const limits = useScreenerLimits();
  const settings = useSettings();
  const update = useUpdateSettings();

  const [form, setForm] = useState<SettingsForm | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (settings.data) setForm(toForm(settings.data));
  }, [settings.data]);

  const save = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form) return;
    const problem = validateForm(form);
    setError(problem);
    setSaved(false);
    if (problem) return;
    update.mutate(
      {
        account_size: Number(form.account_size),
        base_risk_pct: Number(form.base_risk_pct),
        growth_risk_pct: Number(form.growth_risk_pct),
        min_equity: Number(form.min_equity),
        enforce_gate: form.enforce_gate,
        band_caps: Object.fromEntries(BANDS.map((b) => [b, Number(form.band_caps[b])])) as BandCaps,
        regime_weights: Object.fromEntries(
          WEIGHTS.map(([k]) => [k, Number(form.regime_weights[k])]),
        ) as RegimeWeights,
      },
      { onSuccess: () => setSaved(true) },
    );
  };

  return (
    <div className="space-y-4">
      <PageHeader title="Settings" subtitle="Your account, risk budget and trading rules." />

      <Card title="Account">
        {user ? (
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Email</span>
              <span className="font-medium">{user.email || user.id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Screener limit</span>
              <span className="font-medium">
                {limits.data?.data.max_results_per_call.toLocaleString() ?? "—"}
              </span>
            </div>
          </div>
        ) : (
          <p className="text-sm text-gray-500">Not signed in.</p>
        )}
      </Card>

      <form onSubmit={save} className="space-y-4" aria-label="Risk and rules">
        <Card title="Risk budget" subtitle="Used for position sizing and the equity guardrail.">
          {!form ? (
            <p className="text-sm text-gray-500">{settings.isError ? "Could not load settings." : "Loading…"}</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Account size ($)"
                type="number"
                min="0"
                value={form.account_size}
                onChange={(e) => setForm({ ...form, account_size: e.target.value })}
              />
              <Input
                label="Minimum equity guardrail ($)"
                type="number"
                min="0"
                hint="New trades are blocked if equity falls below this."
                value={form.min_equity}
                onChange={(e) => setForm({ ...form, min_equity: e.target.value })}
              />
              <Input
                label="Base layer risk per trade (%)"
                type="number"
                step="0.05"
                value={form.base_risk_pct}
                onChange={(e) => setForm({ ...form, base_risk_pct: e.target.value })}
              />
              <Input
                label="Growth layer risk per trade (%)"
                type="number"
                step="0.05"
                value={form.growth_risk_pct}
                onChange={(e) => setForm({ ...form, growth_risk_pct: e.target.value })}
              />
              <label className="flex items-center gap-2 text-sm sm:col-span-2">
                <input
                  type="checkbox"
                  checked={form.enforce_gate}
                  onChange={(e) => setForm({ ...form, enforce_gate: e.target.checked })}
                />
                Enforce the Do-Not-Trade gate when adding trades
              </label>
            </div>
          )}
        </Card>

        {form && (
          <>
            <Card title="Capital band caps (%)" subtitle="Maximum share of capital per band.">
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
                {BANDS.map((b) => (
                  <Input
                    key={b}
                    label={`Band ${b}`}
                    type="number"
                    min="0"
                    max="100"
                    value={form.band_caps[b]}
                    onChange={(e) =>
                      setForm({ ...form, band_caps: { ...form.band_caps, [b]: e.target.value } })
                    }
                  />
                ))}
              </div>
            </Card>

            <Card title="Regime score weights" subtitle="Relative weight of each input (they are normalised).">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {WEIGHTS.map(([k, label]) => (
                  <Input
                    key={k}
                    label={label}
                    type="number"
                    min="0"
                    value={form.regime_weights[k]}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        regime_weights: { ...form.regime_weights, [k]: e.target.value },
                      })
                    }
                  />
                ))}
              </div>
            </Card>

            <div className="flex items-center gap-3">
              <Button type="submit" loading={update.isPending}>
                Save settings
              </Button>
              {error && (
                <p role="alert" className="text-sm text-red-600">
                  {error}
                </p>
              )}
              {saved && !error && <p className="text-sm text-green-700">Saved.</p>}
            </div>
          </>
        )}
      </form>

      <Card title="Danger zone">
        <Button variant="danger" onClick={logout}>
          Sign out
        </Button>
      </Card>
    </div>
  );
}
