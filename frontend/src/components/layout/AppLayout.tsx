import { Outlet } from "react-router-dom";
import { useState } from "react";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { Toaster } from "../ui/Toaster";

export function AppLayout() {
  const [open, setOpen] = useState(false);
  return (
    <div className="min-h-screen flex bg-gray-50">
      <Sidebar open={open} onClose={() => setOpen(false)} />
      <div className="flex-1 flex flex-col min-w-0">
        <Header onMenu={() => setOpen((o) => !o)} />
        <main className="flex-1 py-6 px-4 lg:px-6">
          <Outlet />
        </main>
      </div>
      <Toaster />
    </div>
  );
}
