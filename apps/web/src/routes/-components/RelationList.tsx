import { Link } from "@tanstack/react-router";
import { useState } from "react";

import { formatApiError } from "@monet/api-client";

import { Latex } from "../../components/Latex";
import { api } from "../../lib/api";
import { buildRelationHtml } from "../../lib/relationTemplate";
import type { ObjectOut, RelationGroupOut, RelationOut } from "../../lib/types";
import { Credits } from "./Credits";
import { Provenance } from "./Provenance";
import { RelationExpression } from "./RelationExpression";

const TAG_CLASS = "relation-tag inline-block rounded-sm px-2 py-0.5 text-xs";

function OperatorLink({ operator, isCurrent }: { operator: ObjectOut; isCurrent: boolean }) {
  if (isCurrent) {
    return (
      <span className={`${TAG_CLASS} is-current`}>
        <Latex>{operator.latex}</Latex>
      </span>
    );
  }
  return (
    <Link to="/objects/$objectId" params={{ objectId: operator.id }} className={TAG_CLASS}>
      <Latex>{operator.latex}</Latex>
    </Link>
  );
}

function markLinked(row: HTMLElement, href: string | null) {
  for (const anchor of row.querySelectorAll("a")) {
    anchor.classList.toggle("is-linked", href !== null && anchor.getAttribute("href") === href);
  }
}

function RelationRow({
  relation,
  currentObjectId,
}: {
  relation: RelationOut;
  currentObjectId: string;
}) {
  const html = buildRelationHtml(relation, relation.display?.template ?? null, currentObjectId);

  return (
    <li
      className="relation-row rounded-sm border border-mist bg-white/40 px-3 pt-2 pb-3 shadow-[0_1px_3px_rgba(35,50,43,0.06)]"
      onMouseOver={(event) => {
        markLinked(
          event.currentTarget,
          (event.target as HTMLElement).closest("a")?.getAttribute("href") ?? null,
        );
      }}
      onMouseLeave={(event) => {
        markLinked(event.currentTarget, null);
      }}
    >
      <div className="-ml-2">
        <OperatorLink
          operator={relation.operator}
          isCurrent={relation.operator.id === currentObjectId}
        />
      </div>
      <div className="mt-1 text-sm">
        <RelationExpression html={html} />
      </div>
      <Provenance provenance={relation.provenance} />
      <Credits references={relation.references} />
    </li>
  );
}

const PAGE = 20;

type Side = "operator" | "input" | "output";

function LaterPage({
  objectId,
  side,
  operatorId,
  offset,
}: {
  objectId: string;
  side: Side;
  operatorId: string;
  offset: number;
}) {
  const page = api.useQuery("get", "/objects/{object_id}/relations", {
    params: {
      path: { object_id: objectId },
      query: { side, operator_id: operatorId, offset, limit: PAGE },
    },
  });
  if (page.isPending) return <li className="text-xs text-ink-soft italic">Loading…</li>;
  if (page.isError) return <li className="text-xs text-rust">{formatApiError(page.error)}</li>;
  return page.data.items.map((relation) => (
    <RelationRow key={relation.id} relation={relation} currentObjectId={objectId} />
  ));
}

function GroupRows({
  group,
  side,
  currentObjectId,
}: {
  group: RelationGroupOut;
  side: Side;
  currentObjectId: string;
}) {
  const [pages, setPages] = useState(group.relations.length === 0 ? 1 : 0);
  const loaded = group.relations.length + pages * PAGE;
  const left = group.total - loaded;

  return (
    <>
      {group.relations.map((relation) => (
        <RelationRow key={relation.id} relation={relation} currentObjectId={currentObjectId} />
      ))}
      {Array.from({ length: pages }, (_, index) => (
        <LaterPage
          key={index}
          objectId={currentObjectId}
          side={side}
          operatorId={group.operator.id}
          offset={group.relations.length + index * PAGE}
        />
      ))}
      {left > 0 && (
        <li>
          <button
            type="button"
            onClick={() => {
              setPages(pages + 1);
            }}
            className="flex items-center gap-1.5 text-xs text-ink-soft hover:text-pond"
          >
            <span aria-hidden>+</span>
            {`show ${String(Math.min(left, PAGE))} more of ${String(group.total)}`}
            <span className="rounded-sm border border-gold/30 bg-gold-soft/60 px-1.5 py-0.5 text-[11px]">
              <Latex>{group.operator.latex}</Latex>
            </span>
          </button>
        </li>
      )}
    </>
  );
}

function CollapsedGroup({
  group,
  side,
  currentObjectId,
}: {
  group: RelationGroupOut;
  side: Side;
  currentObjectId: string;
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="mt-2">
      {open && (
        <ul className="mb-1.5 space-y-2">
          <GroupRows group={group} side={side} currentObjectId={currentObjectId} />
        </ul>
      )}
      <button
        type="button"
        onClick={() => {
          setOpen(!open);
        }}
        className="flex items-center gap-1.5 text-xs text-ink-soft hover:text-pond"
      >
        <span aria-hidden>{open ? "−" : "+"}</span>
        {open ? "hide" : `show ${String(group.total)}`}
        <span className="rounded-sm border border-gold/30 bg-gold-soft/60 px-1.5 py-0.5 text-[11px]">
          <Latex>{group.operator.latex}</Latex>
        </span>
      </button>
    </div>
  );
}

export function RelationList({
  title,
  groups,
  side,
  currentObjectId,
  collapseHidden = true,
}: {
  title: string;
  groups: RelationGroupOut[];
  side: Side;
  currentObjectId: string;
  collapseHidden?: boolean;
}) {
  if (groups.length === 0) return null;
  const isCollapsed = (group: RelationGroupOut) =>
    group.relations.length === 0 ||
    (collapseHidden && group.relations.some((relation) => relation.display?.hidden_by_default));
  const open = groups.filter((group) => !isCollapsed(group));
  const collapsed = groups.filter(isCollapsed);
  const total = groups.reduce((sum, group) => sum + group.total, 0);

  return (
    <div className="mb-7">
      <h2 className="mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase">
        {title}
        {total > 1 && <span className="ml-1.5 font-normal normal-case">({total})</span>}
      </h2>
      <ul className="space-y-2">
        {open.map((group) => (
          <GroupRows
            key={group.operator.id}
            group={group}
            side={side}
            currentObjectId={currentObjectId}
          />
        ))}
      </ul>
      {collapsed.map((group) => (
        <CollapsedGroup
          key={group.operator.id}
          group={group}
          side={side}
          currentObjectId={currentObjectId}
        />
      ))}
    </div>
  );
}
