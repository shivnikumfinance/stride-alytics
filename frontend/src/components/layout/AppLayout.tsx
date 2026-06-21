import { Outlet } from "react-router-dom";
import { useState } from "react";
import { Sidebar, Topbar } from "./Sidebar";
import { Toaster } from "../ui/Toaster";

export function AppLayout() {
  const [open, setOpen] = useState(false);
  return (
    <div className="min-h-screen flex bg-gray-50">
      <Sidebar open={open} onClose={() => setOpen(false)} />
      <div className="flex-1 flex flex-col min-w-0">
        <Topbar onMenu={() => setOpen((o) => !o)} />
        <main className="flex-1 py-6">
          <Outlet />
        </main>
      </div>
      <Toaster />
    </div>
  );
}
