import { Badge } from "../components/ui";

export function AdminPage() {
  const users = [
    { name: "John Trader", email: "john@example.com", role: "Admin", tier: "PRO", status: "Active", joined: "2024-01-10" },
    { name: "Jane Smith", email: "jane@example.com", role: "User", tier: "PRO", status: "Active", joined: "2024-01-12" },
    { name: "Bob Wilson", email: "bob@example.com", role: "User", tier: "Free", status: "Active", joined: "2024-01-14" },
    { name: "Alice Brown", email: "alice@example.com", role: "User", tier: "Free", status: "Inactive", joined: "2024-01-15" },
    { name: "Charlie Davis", email: "charlie@example.com", role: "User", tier: "PRO", status: "Active", joined: "2024-01-16" },
  ];

  const auditLog = [
    { timestamp: "2024-01-15 14:32:45", admin: "System", action: "Auto-upgrade", detail: "User jane@example.com upgraded to PRO" },
    { timestamp: "2024-01-15 13:20:11", admin: "John Trader", action: "Settings change", detail: "Updated regime parameters" },
    { timestamp: "2024-01-15 11:05:33", admin: "System", action: "Backup", detail: "Daily database backup completed" },
    { timestamp: "2024-01-15 09:15:22", admin: "System", action: "Alert", detail: "High memory usage detected" },
  ];

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-slate-900">Admin Panel</h1>
        <p className="text-sm text-slate-500 mt-1">System health, user management, and audit log</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <p className="text-xs text-slate-500 mb-1">API Status</p>
          <p className="text-lg font-bold text-green-700">🟢 Healthy</p>
          <p className="text-xs text-slate-500">142ms latency</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <p className="text-xs text-slate-500 mb-1">Database</p>
          <p className="text-lg font-bold text-green-700">🟢 Healthy</p>
          <p className="text-xs text-slate-500">Last backup: 2h ago</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <p className="text-xs text-slate-500 mb-1">Users (24h)</p>
          <p className="text-2xl font-bold text-slate-900">5</p>
          <p className="text-xs text-slate-500">Active now</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <p className="text-xs text-slate-500 mb-1">PRO / Free</p>
          <p className="text-lg font-bold text-slate-900">3 / 2</p>
          <p className="text-xs text-slate-500">Total: 5 users</p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200">
          <h3 className="text-sm font-semibold text-slate-900">User Management</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Tier</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Joined</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {users.map((user, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap font-medium text-slate-900">{user.name}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm">{user.email}</td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <Badge tone={user.role === "Admin" ? "purple" : "blue"}>{user.role}</Badge>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <Badge tone={user.tier === "PRO" ? "indigo" : "gray"}>{user.tier}</Badge>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <Badge tone={user.status === "Active" ? "green" : "red"}>{user.status}</Badge>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-slate-600">{user.joined}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200">
          <h3 className="text-sm font-semibold text-slate-900">Audit Log</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3">Timestamp</th>
                <th className="px-4 py-3">Admin</th>
                <th className="px-4 py-3">Action</th>
                <th className="px-4 py-3">Detail</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {auditLog.map((log, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap text-xs font-mono text-slate-500">{log.timestamp}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-slate-900">{log.admin}</td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <Badge tone={
                      log.action === "Auto-upgrade" ? "green" :
                      log.action === "Alert" ? "red" :
                      "blue"
                    }>
                      {log.action}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-600">{log.detail}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
