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
  const roots = api.useQuery("get", "/top-level-objects", {}, { enabled: !focus });
  const centre = focus ?? roots.data?.at(0)?.id;
  const relations = api.useQuery(
    "get",
    "/relations",
    { params: { query: { focus: centre, depth: 2 } } },
    { enabled: Boolean(centre) },
  );

  return (
    <div>
      <h1 className="font-display text-2xl text-ink">The network</h1>
      <p className="mt-1 mb-5 text-sm text-ink-soft">
        The neighbourhood around one object: what reaches it, and what it reaches. The network is
        far too large to draw at once, so open any object and follow &ldquo;see it on the network
        map&rdquo; to recentre. Drag to pan, scroll to zoom, click anything to open it.
      </p>

      {relations.isPending && <p className="text-sm text-ink-soft italic">Drawing the network…</p>}
      {relations.isError && <p className="text-sm text-rust">{formatApiError(relations.error)}</p>}

      {relations.data && <NetworkMap relations={relations.data} focusId={centre ?? null} />}
    </div>
  );
}
