import { Link } from "@tanstack/react-router";

import { formatApiError } from "@monet/api-client";

import { Latex } from "../../components/Latex";
import { MemberList } from "../../components/MemberList";
import { api } from "../../lib/api";
import { TypeGraph } from "./TypeGraph";

const HEADING = "mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase";

export function SectionContents({ sectionId }: { sectionId: string }) {
  const section = api.useQuery("get", "/objects/{object_id}/section", {
    params: { path: { object_id: sectionId } },
  });
  if (section.isPending) return <p className="mb-7 text-sm text-ink-soft">Loading section…</p>;
  if (section.isError) {
    return <p className="mb-7 text-sm text-rust">{formatApiError(section.error)}</p>;
  }
  const { types, entries, subsections } = section.data;

  return (
    <>
      {types.length > 0 && (
        <section className="mb-7">
          <h2 className={HEADING}>Types ({types.length})</h2>
          <p className="mb-3 text-xs text-ink-soft">
            Broader types sit above narrower ones; a line joins a type to each type directly inside
            it.
          </p>
          <TypeGraph types={types} />
        </section>
      )}
      <MemberList title="Filed under this section" members={entries} />
      {subsections.map((subsection) => (
        <MemberList
          key={subsection.id}
          title={
            <Link
              to="/objects/$objectId"
              params={{ objectId: subsection.id }}
              className="hover:text-pond"
            >
              <Latex>{subsection.latex}</Latex>
            </Link>
          }
          members={subsection.entries}
        />
      ))}
    </>
  );
}
