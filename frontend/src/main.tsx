import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { useAuthStore } from "./store/auth.store";
import { AUTH_LOGOUT_EVENT } from "./api/client";
import "./index.css";

// Wire the axios client's 401 event to the auth store. Done here (not in
// client.ts) to avoid the circular import: auth.store -> api/client.
if (typeof window !== "undefined") {
  window.addEventListener(AUTH_LOGOUT_EVENT, () => {
    useAuthStore.getState().logout();
  });
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);