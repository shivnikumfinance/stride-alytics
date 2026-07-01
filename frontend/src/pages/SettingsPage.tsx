import { PageHeader, Card, Button, Badge } from "../components/ui";
import { useAuthStore } from "../store";
import { useScreenerLimits } from "../hooks/queries";

export function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const limits = useScreenerLimits();

  return (
    <div className="space-y-4">
      <PageHeader title="Settings" subtitle="Manage your account and subscription." />

      <Card title="Account">
        {user ? (
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Email</span>
              <span className="font-medium">{user.email || user.id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Plan</span>
              <Badge tone="indigo" className="capitalize">{user.subscription_plan}</Badge>
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

      <Card title="Subscription">
        <p className="text-sm text-gray-600 mb-3">
          Upgrade to Pro for unlimited screener results, hourly regime updates, and trade P&amp;L tracking.
        </p>
        <Button variant="primary" disabled>
          Upgrade to Pro ($19/mo) — coming soon
        </Button>
      </Card>

      <Card title="Danger zone">
        <Button variant="danger" onClick={logout}>
          Sign out
        </Button>
      </Card>
    </div>
  );
}
