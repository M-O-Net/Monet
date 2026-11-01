import { createRootRoute, Outlet } from "@tanstack/react-router";

import { Header } from "../components/Header";
import { SuggestionBox } from "./-components/SuggestionBox";

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <Header />
      <Outlet />
      <SuggestionBox />
    </div>
  );
}
