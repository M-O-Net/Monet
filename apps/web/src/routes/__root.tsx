import { createRootRoute, Outlet } from "@tanstack/react-router";

import { Header } from "../components/Header";

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  return (
    <div className="mx-auto max-w-2xl px-6 py-12">
      <Header />
      <Outlet />
    </div>
  );
}
