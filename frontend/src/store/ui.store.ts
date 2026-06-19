/** UI store — sidebar, modal, theme toggles. */

import { create } from "zustand";

interface UiStoreState {
  sidebarOpen: boolean;
  toasts: { id: string; kind: "success" | "error" | "info"; message: string }[];
  toggleSidebar: () => void;
  setSidebar: (open: boolean) => void;
  pushToast: (kind: "success" | "error" | "info", message: string) => void;
  dismissToast: (id: string) => void;
}

export const useUiStore = create<UiStoreState>((set) => ({
  sidebarOpen: false,
  toasts: [],
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebar: (open) => set({ sidebarOpen: open }),
  pushToast: (kind, message) =>
    set((s) => ({
      toasts: [...s.toasts, { id: crypto.randomUUID(), kind, message }],
    })),
  dismissToast: (id) =>
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}));
