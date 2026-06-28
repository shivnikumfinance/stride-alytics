import { useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster as HotToaster } from "react-hot-toast";

import { AppLayout } from "./components/layout";
import { useAuthStore } from "./store";
import {
  ActiveHoldingsPage,
  ActiveTradesPage,
  AdminPage,
  DashboardPage,
  ExitAlertsPage,
  GreeksPage,
  HeatDashboardPage,
  LoginPage,
  OptionChainPage,
  PicksPage,
  PortfolioPage,
  RegimePage,
  ScenariosPage,
  ScreenerPage,
  SettingsPage,
  SignalLogPage,
  SignupPage,
  SizingPage,
  StrategyMatrixPage,
  WatchlistPage,
} from "./pages";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      gcTime: 30 * 60 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function AuthBootstrap({ children }: { children: React.ReactNode }) {
  const hydrate = useAuthStore((s) => s.hydrate);
  useEffect(() => {
    hydrate();
  }, [hydrate]);
  return <>{children}</>;
}

function RequireAuth({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token);
  const location = useLocation();
  if (!token) return <Navigate to="/login" replace state={{ from: location }} />;
  return <>{children}</>;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthBootstrap>
          <HotToaster position="top-right" />
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />

            <Route
              element={
                <RequireAuth>
                  <AppLayout />
                </RequireAuth>
              }
            >
              <Route index element={<DashboardPage />} />
              <Route path="screener" element={<ScreenerPage />} />
              <Route path="greeks" element={<GreeksPage />} />
              <Route path="regime" element={<RegimePage />} />
              <Route path="picks" element={<PicksPage />} />
              <Route path="portfolio" element={<PortfolioPage />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="exit-alerts" element={<ExitAlertsPage />} />
              <Route path="active-holdings" element={<ActiveHoldingsPage />} />
              <Route path="strategy-matrix" element={<StrategyMatrixPage />} />
              <Route path="watchlist" element={<WatchlistPage />} />
              <Route path="option-chain" element={<OptionChainPage />} />
              <Route path="active-trades" element={<ActiveTradesPage />} />
              <Route path="sizing" element={<SizingPage />} />
              <Route path="scenarios" element={<ScenariosPage />} />
              <Route path="heat-dashboard" element={<HeatDashboardPage />} />
              <Route path="signal-log" element={<SignalLogPage />} />
              <Route path="admin" element={<AdminPage />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthBootstrap>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
