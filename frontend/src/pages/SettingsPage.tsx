import { PageHeader, Card, Button } from "../components/ui";
import { useAuthStore } from "../store";
import { useScreenerLimits } from "../hooks/queries";

export function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const limits = useScreenerLimits();

  return (
    <div className="space-y-4">
      <PageHeader title="Settings" subtitle="Manage your account." />

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

      <Card title="Danger zone">
        <Button variant="danger" onClick={logout}>
          Sign out
        </Button>
      </Card>
    </div>
  );
}
