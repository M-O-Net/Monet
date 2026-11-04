import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createRouter, RouterProvider } from "@tanstack/react-router";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { ApiError } from "@monet/api-client";

import "./index.css";
import { routeTree } from "./routeTree.gen";

const MAX_RETRIES = 3;
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failures, error) =>
        failures < MAX_RETRIES && !(error instanceof ApiError && error.status < 500),
    },
  },
});
const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

const rootElement = document.getElementById("root");
if (!rootElement) throw new Error("missing #root element");

createRoot(rootElement).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
);
