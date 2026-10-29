import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";

import { formatApiError } from "@monet/api-client";

import { api } from "../lib/api";
import type { EventKind } from "../lib/types";
import { FeedEntry } from "./-components/feed/FeedEntry";

const PAGE = 50;

const KINDS: { kind: EventKind | undefined; label: string }[] = [
  { kind: undefined, label: "Everything" },
  { kind: "object_created", label: "New objects" },
  { kind: "relation_created", label: "New relations" },
  { kind: "comment_created", label: "Comments" },
];

const EVENT_KINDS: readonly string[] = ["object_created", "relation_created", "comment_created"];

function isEventKind(value: unknown): value is EventKind {
  return typeof value === "string" && EVENT_KINDS.includes(value);
}

interface FeedSearch {
  contributor?: string;
  kind?: EventKind;
}

export const Route = createFileRoute("/feed")({
  component: FeedPage,
  validateSearch: (search: Record<string, unknown>): FeedSearch => ({
    ...(typeof search.contributor === "string" && search.contributor !== ""
      ? { contributor: search.contributor }
      : {}),
    ...(isEventKind(search.kind) ? { kind: search.kind } : {}),
  }),
});

function FeedSlice({
  search,
  before,
  isLast,
  onOlder,
}: {
  search: FeedSearch;
  before: string | undefined;
  isLast: boolean;
  onOlder: (before: string) => void;
}) {
  const events = api.useQuery("get", "/events", {
    params: { query: { ...search, limit: PAGE, ...(before === undefined ? {} : { before }) } },
  });
  const oldest = events.data?.at(-1);

  return (
    <>
      {events.isPending && <p className="text-sm text-ink-soft italic">Gathering activity…</p>}
      {events.isError && <p className="text-sm text-rust">{formatApiError(events.error)}</p>}
      {before === undefined && events.data?.length === 0 && (
        <p className="text-sm text-ink-soft italic">
          Nothing here yet. New objects, relations and comments appear here as they are added —{" "}
          <Link to="/contribute" className="underline underline-offset-2 hover:text-pond">
            contribute one
          </Link>
          .
        </p>
      )}
      {events.data && events.data.length > 0 && (
        <ul className="mb-2 space-y-2">
          {events.data.map((event) => (
            <FeedEntry key={event.id} event={event} />
          ))}
        </ul>
      )}
      {isLast && oldest !== undefined && events.data?.length === PAGE && (
        <button
          type="button"
          onClick={() => {
            onOlder(oldest.id);
          }}
          className="mt-2 text-xs text-ink-soft underline decoration-dotted underline-offset-2 hover:text-pond"
        >
          Show older
        </button>
      )}
    </>
  );
}

function FeedSlices({ search }: { search: FeedSearch }) {
  const [cursors, setCursors] = useState<(string | undefined)[]>([undefined]);
  return cursors.map((before, index) => (
    <FeedSlice
      key={before ?? "newest"}
      search={search}
      before={before}
      isLast={index === cursors.length - 1}
      onOlder={(older) => {
        setCursors([...cursors, older]);
      }}
    />
  ));
}

function FeedPage() {
  const { contributor, kind } = Route.useSearch();

  return (
    <div>
      <h1 className="font-display text-2xl text-ink">
        {contributor === undefined ? "Recent activity" : `Contributions by ${contributor}`}
      </h1>
      <p className="mt-1 mb-5 text-sm text-ink-soft">
        What was added to the network, and by whom, newest first.
        {contributor !== undefined && (
          <>
            {" "}
            <Link
              to="/feed"
              search={kind ? { kind } : {}}
              className="underline decoration-dotted underline-offset-2 hover:text-pond"
            >
              Show everyone's
            </Link>
          </>
        )}
      </p>

      <nav className="mb-5 flex flex-wrap gap-1.5">
        {KINDS.map((option) => (
          <Link
            key={option.label}
            to="/feed"
            search={{
              ...(contributor ? { contributor } : {}),
              ...(option.kind ? { kind: option.kind } : {}),
            }}
            className={`rounded-full px-3 py-1 text-xs ${
              option.kind === kind
                ? "bg-pond text-paper"
                : "bg-willow/15 text-ink hover:bg-willow/30"
            }`}
          >
            {option.label}
          </Link>
        ))}
      </nav>

      <FeedSlices
        key={`${contributor ?? ""}:${kind ?? ""}`}
        search={{ ...(contributor ? { contributor } : {}), ...(kind ? { kind } : {}) }}
      />
    </div>
  );
}
