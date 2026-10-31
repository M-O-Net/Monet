import { createFileRoute } from "@tanstack/react-router";

import { formatApiError } from "@monet/api-client";

import { api } from "../lib/api";
import { ContentsTree } from "./-components/ContentsTree";

export const Route = createFileRoute("/")({
  component: TopLevelObjectList,
});

function TopLevelObjectList() {
  const sections = api.useQuery("get", "/contents");

  return (
    <div>
      <h1 className="mb-1 font-display text-xl font-medium text-ink">Contents</h1>
      <p className="mb-5 text-sm text-ink-soft">
        Every specimen and operation catalogued so far, filed under one of the sections below.
      </p>

      {sections.isPending && <p className="text-sm text-ink-soft">Gathering sections…</p>}
      {sections.isError && <p className="text-sm text-rust">{formatApiError(sections.error)}</p>}

      {sections.data && <ContentsTree sections={sections.data} />}
    </div>
  );
}
