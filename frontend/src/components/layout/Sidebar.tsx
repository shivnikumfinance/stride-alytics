import { NavLink, useNavigate } from "react-router-dom";
import {
  Activity,
  Calculator,
  Compass,
  LineChart,
  LogOut,
  Menu,
  Sparkles,
  Wallet,
} from "lucide-react";

import { useAuthStore } from "../../store";
import { classNames } from "../../utils";
import { Button } from "../ui";

const navItems = [
  { to: "/", label: "Dashboard", icon: Activity, end: true },
  { to: "/screener", label: "Screener", icon: LineChart },
  { to: "/greeks", label: "Greeks", icon: Calculator },
  { to: "/regime", label: "Regime", icon: Compass },
  { to: "/picks", label: "Weekly Picks", icon: Sparkles },
  { to: "/portfolio", label: "Portfolio", icon: Wallet },
];

export function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <>
      {/* Mobile backdrop */}
      <div
        onClick={onClose}
        className={classNames(
          "fixed inset-0 z-30 bg-gray-900/50 transition-opacity lg:hidden",
          open ? "opacity-100" : "opacity-0 pointer-events-none",
        )}
      />
      <aside
        className={classNames(
          "fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200 flex flex-col",
          "transform transition-transform lg:static lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="px-5 py-4 border-b border-gray-200 flex items-center gap-2">
          <div className="w-8 h-8 rounded-md bg-indigo-600 grid place-items-center text-white font-bold">
            S
          </div>
          <span className="text-lg font-semibold text-gray-900">StrideAlytics</span>
        </div>

        <nav className="flex-1 px-2 py-4 space-y-1">
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={onClose}
              className={({ isActive }) =>
                classNames(
                  "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium",
                  isActive
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-gray-700 hover:bg-gray-100",
                )
              }
            >
              <Icon className="w-4 h-4" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-3 border-t border-gray-200">
          {user && (
            <div className="px-3 py-2 mb-2">
              <p className="text-sm font-medium text-gray-900 truncate">{user.email || user.id}</p>
              <p className="text-xs text-gray-500 capitalize">{user.subscription_plan} plan</p>
            </div>
          )}
          <Button variant="ghost" size="sm" className="w-full justify-start" onClick={handleLogout} icon={<LogOut className="w-4 h-4" />}>
            Sign out
          </Button>
        </div>
      </aside>
    </>
  );
}

export function Topbar({ onMenu }: { onMenu: () => void }) {
  return (
    <header className="sticky top-0 z-20 bg-white/90 backdrop-blur border-b border-gray-200 px-4 lg:px-8 h-14 flex items-center">
      <button
        type="button"
        onClick={onMenu}
        className="lg:hidden mr-2 p-2 rounded-md text-gray-700 hover:bg-gray-100"
        aria-label="Open menu"
      >
        <Menu className="w-5 h-5" />
      </button>
      <h1 className="text-sm font-medium text-gray-700">Options Trading Analytics</h1>
    </header>
  );
}
