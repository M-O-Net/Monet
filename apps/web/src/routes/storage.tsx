import { createFileRoute } from "@tanstack/react-router";

import { formatApiError } from "@monet/api-client";

import { api } from "../lib/api";
import { StorageBreakdown } from "./-components/storage/StorageBreakdown";

export const Route = createFileRoute("/storage")({
  component: StoragePage,
});

function StoragePage() {
  const stats = api.useQuery("get", "/stats/storage");

  return (
    <div>
      <h1 className="font-display text-2xl text-ink">Storage</h1>
      <p className="mt-1 mb-6 text-sm text-ink-soft">
        How much room the database takes up right now, and what it spends it on.
      </p>

      {stats.isPending && <p className="text-sm text-ink-soft italic">Measuring…</p>}
      {stats.isError && <p className="text-sm text-rust">{formatApiError(stats.error)}</p>}

      {stats.data && <StorageBreakdown stats={stats.data} />}
    </div>
  );
}
