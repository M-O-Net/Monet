import { keepPreviousData } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";

import { formatApiError } from "@monet/api-client";

import { api } from "../lib/api";
import { NetworkMap } from "./-components/NetworkMap";

export const Route = createFileRoute("/map")({
  component: NetworkMapPage,
  validateSearch: (search: Record<string, unknown>): { expand?: string } => {
    const expand = search.expand;
    return typeof expand === "string" && expand !== "" ? { expand } : {};
  },
});

function NetworkMapPage() {
  const { expand } = Route.useSearch();
  const opened = expand ? expand.split(",") : [];
  const relations = api.useQuery(
    "get",
    "/relations",
    { params: { query: { contents: true, focus: opened, depth: 1 } } },
    { placeholderData: keepPreviousData },
  );

  return (
    <div>
      <h1 className="font-display text-2xl text-ink">The network</h1>
      <p className="mt-1 mb-5 text-sm text-ink-soft">
        The contents page, drawn. Click anything to open it out and see what it reaches — the
        address bar remembers where you are. Drag to pan, scroll to zoom.
      </p>

      {relations.isError && <p className="text-sm text-rust">{formatApiError(relations.error)}</p>}

      {relations.data === undefined ? (
        <p className="text-sm text-ink-soft italic">Drawing the network…</p>
      ) : (
        <NetworkMap
          relations={relations.data}
          opened={opened}
          busy={relations.isFetching}
          contents
        />
      )}
    </div>
  );
}
