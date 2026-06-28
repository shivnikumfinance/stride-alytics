import { NavLink, useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  BarChart3,
  Briefcase,
  Calculator,
  Compass,
  Eye,
  FileText,
  Home,
  LayoutDashboard,
  LineChart,
  List,
  LogOut,
  Menu,
  Ruler,
  Settings,
  Settings2,
  Sparkles,
  Thermometer,
  TrendingUp,
  Wallet,
} from "lucide-react";

import { useAuthStore } from "../../store";
import { classNames } from "../../utils";
import { Button } from "../ui";

const navItems = [
  { to: "/", label: "Home", icon: Home, end: true },
  { to: "/exit-alerts", label: "Exit Alerts", icon: AlertTriangle },
  { to: "/picks", label: "Weekly Picks", icon: Sparkles },
  { to: "/active-holdings", label: "Active Holdings", icon: Briefcase, badge: "6" },
  { to: "/strategy-matrix", label: "Strategy Matrix", icon: LayoutDashboard },
  { to: "/watchlist", label: "Watchlist", icon: Eye },
  { to: "/option-chain", label: "Option Chain", icon: List },
  { to: "/active-trades", label: "Active Trades", icon: TrendingUp },
  { to: "/sizing", label: "Position Sizing", icon: Ruler },
  { to: "/scenarios", label: "Scenarios", icon: Compass },
  { to: "/heat-dashboard", label: "Heat Dashboard", icon: Thermometer },
  { to: "/signal-log", label: "Signal Log", icon: FileText },
  { to: "/screener", label: "Screener", icon: LineChart },
  { to: "/greeks", label: "Greeks", icon: Calculator },
  { to: "/regime", label: "Regime", icon: Compass },
  { to: "/portfolio", label: "Portfolio", icon: Wallet },
  { to: "/settings", label: "Settings", icon: Settings },
  { to: "/admin", label: "Admin", icon: Settings2 },
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
      <div
        onClick={onClose}
        className={classNames(
          "fixed inset-0 z-30 bg-gray-900/50 transition-opacity lg:hidden",
          open ? "opacity-100" : "opacity-0 pointer-events-none",
        )}
      />
      <aside
        className={classNames(
          "fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-slate-200 flex flex-col",
          "transform transition-transform lg:static lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="h-16 px-5 border-b border-slate-200 flex items-center gap-3">
          <div className="w-8 h-8 rounded-md bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs">
            SA
          </div>
          <span className="text-sm font-semibold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
            StrideAlytics
          </span>
        </div>

        <nav className="flex-1 overflow-y-auto py-3 px-3 space-y-1">
          {navItems.map(({ to, label, icon: Icon, end, badge }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={onClose}
              className={({ isActive }) =>
                classNames(
                  "flex items-center gap-2.5 px-2.5 py-2 rounded-md text-[13px] font-medium transition-colors",
                  isActive
                    ? "bg-slate-100 text-blue-600 border-l-[3px] border-l-blue-600"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900 border-l-[3px] border-l-transparent",
                )
              }
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              <span className="flex-1">{label}</span>
              {badge && (
                <span className="ml-auto bg-red-500 text-white text-[10px] font-semibold px-1.5 py-0.5 rounded-full">
                  {badge}
                </span>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="p-3 border-t border-slate-200">
          {user && (
            <div className="px-2.5 py-2 mb-2">
              <p className="text-sm font-medium text-slate-900 truncate">{user.email || user.id}</p>
              <span className="inline-block mt-1 text-[10px] font-semibold text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded">
                {user.subscription_plan?.toUpperCase() || "FREE"} Plan
              </span>
            </div>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start text-slate-600 hover:text-slate-900"
            onClick={handleLogout}
            icon={<LogOut className="w-4 h-4" />}
          >
            Sign out
          </Button>
        </div>
      </aside>
    </>
  );
}

export function Topbar({ onMenu }: { onMenu: () => void }) {
  return (
    <header className="sticky top-0 z-20 bg-white/90 backdrop-blur border-b border-slate-200 px-4 lg:px-8 h-14 flex items-center">
      <button
        type="button"
        onClick={onMenu}
        className="lg:hidden mr-2 p-2 rounded-md text-slate-700 hover:bg-slate-100"
        aria-label="Open menu"
      >
        <Menu className="w-5 h-5" />
      </button>
      <h1 className="text-sm font-medium text-slate-700">Options Trading Analytics</h1>
    </header>
  );
}
