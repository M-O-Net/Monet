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
  const relations = api.useQuery("get", "/relations", {
    params: { query: focus ? { focus, depth: 3 } : { limit: 120 } },
  });

  return (
    <div>
      <h1 className="font-display text-2xl text-ink">The network</h1>
      <p className="mt-1 mb-5 text-sm text-ink-soft">
        {focus
          ? "The neighbourhood around one object: what reaches it, and what it reaches."
          : "A sample of the network. It is far too large to draw at once — open any object and follow “see it on the network map” to recentre on it."}{" "}
        Filing under sections is left out. Drag to pan, scroll to zoom, click anything to open it.
      </p>

      {relations.isPending && <p className="text-sm text-ink-soft italic">Drawing the network…</p>}
      {relations.isError && <p className="text-sm text-rust">{formatApiError(relations.error)}</p>}

      {relations.data && <NetworkMap relations={relations.data} focusId={focus ?? null} />}
    </div>
  );
}
