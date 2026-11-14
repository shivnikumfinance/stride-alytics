import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactElement } from "react";
import { MemoryRouter } from "react-router-dom";

function makeClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 }, mutations: { retry: false } },
  });
}

/** Render with a fresh React Query client (no retries, so failures show up immediately). */
export function renderWithClient(ui: ReactElement) {
  return render(<QueryClientProvider client={makeClient()}>{ui}</QueryClientProvider>);
}

/** Same, inside a router (for components that use links or the current route). */
export function renderWithRouter(ui: ReactElement, route = "/") {
  return render(
    <QueryClientProvider client={makeClient()}>
      <MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>
    </QueryClientProvider>,
  );
}
