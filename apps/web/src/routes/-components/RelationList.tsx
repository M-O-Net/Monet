import { Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";

import { Latex } from "../../components/Latex";
import { buildRelationHtml } from "../../lib/relationTemplate";
import type { ObjectOut, RelationOut } from "../../lib/types";
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
    </li>
  );
}

export function RelationList({
  title,
  relations,
  currentObjectId,
  collapseHidden = true,
}: {
  title: string;
  relations: RelationOut[];
  currentObjectId: string;
  collapseHidden?: boolean;
}) {
  const [expanded, setExpanded] = useState<ReadonlySet<string>>(new Set());

  const { shown, hiddenGroups } = useMemo(() => {
    const visible: RelationOut[] = [];
    const groups = new Map<string, { operator: ObjectOut; relations: RelationOut[] }>();
    for (const relation of relations) {
      if (collapseHidden && relation.display?.hidden_by_default === true) {
        const group = groups.get(relation.operator.id) ?? {
          operator: relation.operator,
          relations: [],
        };
        group.relations.push(relation);
        groups.set(relation.operator.id, group);
      } else {
        visible.push(relation);
      }
    }
    return { shown: visible, hiddenGroups: [...groups.values()] };
  }, [relations, collapseHidden]);

  if (relations.length === 0) return null;

  return (
    <div className="mb-7">
      <h2 className="mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase">{title}</h2>
      <ul className="space-y-2">
        {shown.map((relation) => (
          <RelationRow key={relation.id} relation={relation} currentObjectId={currentObjectId} />
        ))}
      </ul>
      {hiddenGroups.map((group) => {
        const open = expanded.has(group.operator.id);
        return (
          <div key={group.operator.id} className={shown.length > 0 ? "mt-2" : ""}>
            {open && (
              <ul className="mb-1.5 space-y-2">
                {group.relations.map((relation) => (
                  <RelationRow
                    key={relation.id}
                    relation={relation}
                    currentObjectId={currentObjectId}
                  />
                ))}
              </ul>
            )}
            <button
              type="button"
              onClick={() => {
                setExpanded((previous) => {
                  const next = new Set(previous);
                  if (next.has(group.operator.id)) next.delete(group.operator.id);
                  else next.add(group.operator.id);
                  return next;
                });
              }}
              className="flex items-center gap-1.5 text-xs text-ink-soft hover:text-pond"
            >
              <span aria-hidden>{open ? "−" : "+"}</span>
              {open ? "hide" : `show ${String(group.relations.length)} more`}
              <span className="rounded-sm border border-gold/30 bg-gold-soft/60 px-1.5 py-0.5 text-[11px]">
                <Latex>{group.operator.latex}</Latex>
              </span>
            </button>
          </div>
        );
      })}
    </div>
  );
}
