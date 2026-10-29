import { keepPreviousData } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { type ReactNode, useState } from "react";

import { formatApiError } from "@monet/api-client";

import { api } from "../lib/api";
import type { ObjectOut, ObjectQuery } from "../lib/types";
import { Latex } from "./Latex";

const MAX_MEMBERS = 50;
const PAGE = 50;
const PAGER_CLASS = "hover:text-pond disabled:opacity-40 disabled:hover:text-ink-soft";

export function MemberList({
  title,
  members,
  footer,
}: {
  title: string;
  members: ObjectOut[];
  footer?: ReactNode;
}) {
  if (members.length === 0) return null;
  const shown = members.slice(0, MAX_MEMBERS);

  return (
    <div className="mb-7">
      <h2 className="mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase">{title}</h2>
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
              {member.description && (
                <span className="truncate text-xs text-ink-soft">{member.description}</span>
              )}
            </Link>
          </li>
        ))}
      </ul>
      {footer ??
        (members.length > shown.length && (
          <p className="mt-1.5 text-xs text-ink-soft">
            showing {shown.length} of {members.length}
          </p>
        ))}
    </div>
  );
}

type ListFilter = Omit<ObjectQuery, "offset" | "limit">;

export function QueriedMemberList({
  title,
  query,
  pending = null,
  empty = null,
}: {
  title: (total: number) => string;
  query: ListFilter;
  pending?: ReactNode;
  empty?: ReactNode;
}) {
  const [page, setPage] = useState(0);
  const found = api.useQuery(
    "get",
    "/objects",
    { params: { query: { ...query, offset: page * PAGE, limit: PAGE } } },
    { placeholderData: keepPreviousData },
  );
  if (found.isError) return <p className="text-sm text-rust">{formatApiError(found.error)}</p>;
  if (found.data === undefined) return pending;

  const { items, total } = found.data;
  if (total === 0) return empty;
  const first = page * PAGE + 1;
  const last = page * PAGE + items.length;
  const pager =
    total > PAGE ? (
      <p className="mt-1.5 flex items-center gap-3 text-xs text-ink-soft">
        <button
          type="button"
          disabled={page === 0}
          onClick={() => {
            setPage(page - 1);
          }}
          className={PAGER_CLASS}
        >
          ← previous
        </button>
        <span>
          {first}–{last} of {total}
        </span>
        <button
          type="button"
          disabled={last >= total}
          onClick={() => {
            setPage(page + 1);
          }}
          className={PAGER_CLASS}
        >
          next →
        </button>
      </p>
    ) : undefined;

  return <MemberList title={title(total)} members={items} footer={pager} />;
}
