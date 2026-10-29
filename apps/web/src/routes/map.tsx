import { keepPreviousData } from "@tanstack/react-query";
import { createFileRoute, Link } from "@tanstack/react-router";

import { formatApiError } from "@monet/api-client";

import { api } from "../lib/api";
import { NetworkMap } from "./-components/NetworkMap";

interface MapSearch {
  focus?: string;
  open?: string[];
}

export const Route = createFileRoute("/map")({
  component: NetworkMapPage,
  validateSearch: (search: Record<string, unknown>): MapSearch => {
    const { focus, open } = search;
    const opened = Array.isArray(open)
      ? open.filter((id): id is string => typeof id === "string")
      : [];
    return {
      ...(typeof focus === "string" ? { focus } : {}),
      ...(opened.length > 0 ? { open: opened } : {}),
    };
  },
});

const CENTRES = ["the busiest objects", "the object in focus", "the objects opened"];

function NetworkMapPage() {
  const { focus, open = [] } = Route.useSearch();
  const navigate = Route.useNavigate();
  const centres = focus === undefined ? [] : [focus, ...open];
  const map = api.useQuery(
    "get",
    "/relations",
    { params: { query: centres.length > 0 ? { focus: centres } : {} } },
    { placeholderData: keepPreviousData },
  );

  return (
    <div>
      <h1 className="font-display text-2xl text-ink">The network</h1>
      <p className="mt-1 mb-5 text-sm text-ink-soft">
        {focus === undefined
          ? "Its busiest corner: the objects the most relations touch, and what they reach. Click an object to centre the map on it"
          : "Everything one operation away from the object in focus. Click an object to open out what surrounds it"}
        , or its ↗ to visit it. Drag to pan, scroll to zoom.
      </p>

      {map.isPending && <p className="text-sm text-ink-soft italic">Drawing the network…</p>}
      {map.isError && <p className="text-sm text-rust">{formatApiError(map.error)}</p>}

      {map.data && (
        <>
          <NetworkMap
            relations={map.data.relations}
            focusId={focus ?? null}
            openIds={open}
            onOpen={(id) => {
              if (focus === undefined) void navigate({ search: { focus: id } });
              else if (id !== focus && !open.includes(id))
                void navigate({ search: { focus, open: [...open, id] } });
            }}
          />
          <p className="mt-2 text-xs text-ink-soft">
            {map.data.relations.length} relations drawn
            {map.data.omitted > 0 &&
              `; ${String(map.data.omitted)} more touching ${CENTRES[Math.min(centres.length, 2)] ?? ""} are left out to keep it legible`}
            .{" "}
            {open.length > 0 && (
              <Link
                to="/map"
                search={{ focus }}
                className="underline decoration-dotted underline-offset-2 hover:text-pond"
              >
                Close everything opened
              </Link>
            )}
          </p>
        </>
      )}
    </div>
  );
}
