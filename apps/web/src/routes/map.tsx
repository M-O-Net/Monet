import { createFileRoute } from "@tanstack/react-router";

import { formatApiError } from "@monet/api-client";

import { api } from "../lib/api";
import { NetworkMap } from "./-components/NetworkMap";

export const Route = createFileRoute("/map")({
  component: NetworkMapPage,
  validateSearch: (search: Record<string, unknown>): { focus?: string } => {
    const focus = search.focus;
    return typeof focus === "string" ? { focus } : {};
  },
});

function NetworkMapPage() {
  const { focus } = Route.useSearch();
  const relations = api.useQuery("get", "/relations");

  return (
    <div>
      <h1 className="font-display text-2xl text-ink">The network</h1>
      <p className="mt-1 mb-5 text-sm text-ink-soft">
        Every object some operation reaches, and the operations reaching them. Filing under sections
        is left out, and so is anything not yet joined to something else. Drag to pan, scroll to
        zoom, click anything to open it.
      </p>

      {relations.isPending && <p className="text-sm text-ink-soft italic">Drawing the network…</p>}
      {relations.isError && <p className="text-sm text-rust">{formatApiError(relations.error)}</p>}

      {relations.data && <NetworkMap relations={relations.data} focusId={focus ?? null} />}
    </div>
  );
}
