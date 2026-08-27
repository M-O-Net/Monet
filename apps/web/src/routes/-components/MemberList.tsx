import { Link } from "@tanstack/react-router";

import { Latex } from "../../components/Latex";
import { api } from "../../lib/api";
import type { ObjectOut } from "../../lib/types";

const PAGE = 50;

function PageLink({ objectId, page, label }: { objectId: string; page: number; label: string }) {
  return (
    <Link
      to="/objects/$objectId"
      params={{ objectId }}
      search={page > 1 ? { page } : {}}
      className="rounded-sm border border-mist px-2.5 py-1 text-xs text-ink-soft hover:bg-paper-deep"
    >
      {label}
    </Link>
  );
}

export function MemberList({
  objectId,
  firstPage,
  total,
  page,
}: {
  objectId: string;
  firstPage: ObjectOut[];
  total: number;
  page: number;
}) {
  const later = api.useQuery(
    "get",
    "/objects/{object_id}/members",
    { params: { path: { object_id: objectId }, query: { offset: (page - 1) * PAGE, limit: PAGE } } },
    { enabled: page > 1 },
  );

  if (firstPage.length === 0) return null;
  const members = page > 1 ? (later.data ?? []) : firstPage;
  const pages = Math.ceil(total / PAGE);
  const first = (page - 1) * PAGE + 1;

  return (
    <div className="mb-7">
      <h2 className="mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase">
        Filed under this section
      </h2>
      {page > 1 && later.isPending ? (
        <p className="text-sm text-ink-soft italic">Loading…</p>
      ) : (
        <ul className="divide-y divide-mist rounded-sm border border-mist bg-white/40 shadow-[0_1px_3px_rgba(35,50,43,0.06)]">
          {members.map((member) => (
            <li key={member.id}>
              <Link
                to="/objects/$objectId"
                params={{ objectId: member.id }}
                className="flex items-baseline gap-3 border-l-2 border-l-transparent px-4 py-2.5 transition-colors hover:border-l-gold hover:bg-gold-soft/40"
              >
                <span className="min-w-0 flex-1 text-sm text-ink">
                  <Latex>{member.latex}</Latex>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
      {pages > 1 && (
        <div className="mt-1.5 flex flex-wrap items-center gap-2">
          {page > 1 && <PageLink objectId={objectId} page={page - 1} label="← previous" />}
          {page < pages && <PageLink objectId={objectId} page={page + 1} label="next →" />}
          <span className="text-xs text-ink-soft">
            {first}–{Math.min(first + members.length - 1, total)} of {total} · page {page} of {pages}
          </span>
        </div>
      )}
    </div>
  );
}
