import { useEffect, useState } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  Briefcase,
  Calculator,
  ChevronDown,
  Compass,
  Eye,
  FileText,
  Home,
  LayoutDashboard,
  LineChart,
  List,
  LogOut,
  Ruler,
  Settings,
  Sparkles,
  Thermometer,
  TrendingUp,
  Wallet,
} from "lucide-react";

import { useExitAlerts } from "../../hooks/queries";
import { useAuthStore } from "../../store";
import { classNames } from "../../utils";
import { Button } from "../ui";

interface NavItem {
  to: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  end?: boolean;
}

// FR-1040: HOME, PRIMARY SECTIONS, and a collapsible TOOLS & ANALYTICS group.
const HOME: NavItem = { to: "/", label: "Home", icon: Home, end: true };

const PRIMARY: NavItem[] = [
  { to: "/exit-alerts", label: "Exit Alerts", icon: AlertTriangle },
  { to: "/picks", label: "Weekly Picks", icon: Sparkles },
  { to: "/active-holdings", label: "Active Holdings", icon: Briefcase },
  { to: "/strategy-matrix", label: "Strategy Matrix", icon: LayoutDashboard },
];

const TOOLS: NavItem[] = [
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
];

const isToolPath = (pathname: string) =>
  TOOLS.some((t) => pathname === t.to || pathname.startsWith(`${t.to}/`));

function NavItemLink({ item, badge, onClick }: { item: NavItem; badge?: number; onClick: () => void }) {
  const Icon = item.icon;
  return (
    <NavLink
      to={item.to}
      end={item.end}
      onClick={onClick}
      className={({ isActive }) =>
        classNames(
          "flex items-center gap-2.5 px-2 py-1.5 rounded-md text-sm font-medium transition-colors",
          isActive
            ? "bg-slate-100 text-blue-600 border-l-[3px] border-l-blue-600"
            : "text-slate-600 hover:bg-slate-50 hover:text-slate-900 border-l-[3px] border-l-transparent",
        )
      }
    >
      <Icon className="w-4 h-4 flex-shrink-0" />
      <span className="flex-1">{item.label}</span>
      {badge ? (
        <span
          aria-label={`${badge} critical alert${badge === 1 ? "" : "s"} to acknowledge`}
          className="ml-auto bg-red-500 text-white text-[10px] font-semibold px-1.5 py-0.5 rounded-full"
        >
          {badge}
        </span>
      ) : null}
    </NavLink>
  );
}

function GroupLabel({ children }: { children: React.ReactNode }) {
  return <p className="px-2 pt-3 pb-1 text-[10px] font-semibold uppercase tracking-wider text-slate-400">{children}</p>;
}

export function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const { pathname } = useLocation();

  // Unacknowledged critical alerts show as a badge on Exit Alerts.
  const critical = useExitAlerts("critical");
  const needsAck = critical.data?.unacknowledged_critical ?? 0;

  // Collapsed by default (FR-1050). It opens when you land on a tool page so the active link is visible.
  const [toolsOpen, setToolsOpen] = useState(() => isToolPath(pathname));
  useEffect(() => {
    if (isToolPath(pathname)) setToolsOpen(true);
  }, [pathname]);

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
          "fixed inset-y-0 left-0 z-40 w-56 bg-white border-r border-slate-200 flex flex-col",
          "transform transition-transform lg:static lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="h-14 px-3 border-b border-slate-200 flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-md bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-[10px]">
            SA
          </div>
          <span className="text-sm font-semibold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
            StrideAlytics
          </span>
        </div>

        <nav aria-label="Main" className="flex-1 overflow-y-auto py-2 px-2 space-y-1">
          <GroupLabel>Home</GroupLabel>
          <NavItemLink item={HOME} onClick={onClose} />

          <GroupLabel>Primary sections</GroupLabel>
          {PRIMARY.map((item) => (
            <NavItemLink key={item.to} item={item} onClick={onClose} badge={item.to === "/exit-alerts" ? needsAck : undefined} />
          ))}

          <button
            type="button"
            aria-expanded={toolsOpen}
            aria-controls="tools-group"
            onClick={() => setToolsOpen((o) => !o)}
            className="mt-3 flex w-full items-center justify-between rounded-md px-2 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-slate-400 hover:bg-slate-50"
          >
            Tools &amp; Analytics
            <ChevronDown className={classNames("w-3.5 h-3.5 transition-transform", toolsOpen && "rotate-180")} />
          </button>
          {toolsOpen && (
            <div id="tools-group" className="space-y-1">
              {TOOLS.map((item) => (
                <NavItemLink key={item.to} item={item} onClick={onClose} />
              ))}
            </div>
          )}
        </nav>

        <div className="p-2.5 border-t border-slate-200">
          {user && (
            <div className="px-2 py-1.5 mb-1.5">
              <p className="text-sm font-medium text-slate-900 truncate">{user.email || user.id}</p>
            </div>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start text-slate-600 hover:text-slate-900"
            onClick={handleLogout}
            icon={<LogOut className="w-3.5 h-3.5" />}
          >
            Sign out
          </Button>
        </div>
      </aside>
    </>
  );
}
