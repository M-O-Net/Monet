import { Link } from "@tanstack/react-router";
import { useState } from "react";

import { Latex } from "../../components/Latex";
import { api } from "../../lib/api";
import type { ObjectOut } from "../../lib/types";

const PAGE = 50;

export function MemberList({
  objectId,
  members,
  total,
}: {
  objectId: string;
  members: ObjectOut[];
  total: number;
}) {
  const [pages, setPages] = useState(0);
  const next = api.useQuery(
    "get",
    "/objects/{object_id}/members",
    { params: { path: { object_id: objectId }, query: { offset: PAGE, limit: pages * PAGE } } },
    { enabled: pages > 0 },
  );

  if (members.length === 0) return null;
  const shown = [...members, ...(next.data ?? [])];

  return (
    <div className="mb-7">
      <h2 className="mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase">
        Filed under this section
      </h2>
      <ul className="divide-y divide-mist rounded-sm border border-mist bg-white/40 shadow-[0_1px_3px_rgba(35,50,43,0.06)]">
        {shown.map((member) => (
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
      {total > shown.length && (
        <div className="mt-1.5 flex items-center gap-3">
          <button
            type="button"
            disabled={next.isPending && pages > 0}
            onClick={() => {
              setPages(pages + 1);
            }}
            className="rounded-sm border border-mist px-2.5 py-1 text-xs text-ink-soft hover:bg-paper-deep disabled:opacity-50"
          >
            {next.isPending && pages > 0 ? "Loading…" : `Show ${String(PAGE)} more`}
          </button>
          <span className="text-xs text-ink-soft">
            showing {shown.length} of {total}
          </span>
        </div>
      )}
    </div>
  );
}
