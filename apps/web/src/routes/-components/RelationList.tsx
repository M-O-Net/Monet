import { Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";

import { Latex } from "../../components/Latex";
import { buildRelationHtml } from "../../lib/relationTemplate";
import type { ObjectOut, RelationOut } from "../../lib/types";
import { RelationExpression } from "./RelationExpression";

const TAG_CLASS = "relation-tag inline-block rounded-sm px-2 py-0.5 text-xs";

function OperatorLink({ operator, isCurrent }: { operator: ObjectOut; isCurrent: boolean }) {
  // On the operator's own page the tag is not a link either — it would lead back to here.
  if (isCurrent) {
    return (
      <span className={`${TAG_CLASS} is-current`}>
        <Latex>{operator.latex}</Latex>
      </span>
    );
  }
  return (
    <Link
      to="/objects/$objectId"
      params={{ objectId: operator.id }}
      // The card-catalog tag, moved above the mathematics so that every formula in a list starts
      // at the same left edge whatever its operator is called.
      //
      // Set in the operator's own notation, at its own case: an object *is* its rendered
      // notation here, so uppercasing it restyles the object rather than its label. It carries
      // no hover styling of its own — the row marks it, so that it and the operator's notation
      // inside the formula always light up together.
      className={TAG_CLASS}
    >
      <Latex>{operator.latex}</Latex>
    </Link>
  );
}

// Marks every link in the row that points where the hovered one does — the operator's tag and
// its notation inside the formula alike. Done to the DOM rather than through state because half
// of these are anchors KaTeX put into the layout, not elements we render; the tag carries no
// colour utilities of its own so that this one pass can style it too.
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
  // One rendering path for every relation. A relation with no template of its own gets a
  // generated one — operands, arrow, results — so the arrow is typeset alongside the
  // mathematics instead of being drawn next to it out of box-characters, which never did line
  // up with the baseline either side.
  const html = buildRelationHtml(relation, relation.display?.template ?? null, currentObjectId);

  // The operator is named above rather than beside the mathematics so that every formula in a
  // list starts at the same left edge, whatever its operator happens to be called.
  return (
    <li
      className="relation-row rounded-sm border border-mist bg-white/40 px-3 pt-2 pb-3 shadow-[0_1px_3px_rgba(35,50,43,0.06)]"
      // Pointing anywhere at an object marks every link to it in this row — so the operator's
      // tag and its notation inside the formula light up together, either way round, and a
      // notation split either side of its operand (det( ... )) reads as the one thing it is.
      onMouseOver={(event) => {
        markLinked(
          event.currentTarget,
          (event.target as HTMLElement).closest("a")?.getAttribute("href") ?? null,
        );
      }}
      // mouseleave, not mouseout: mouseout bubbles up from each child span KaTeX nests inside
      // an anchor, so it fired as the pointer crossed between them and cleared the mark that
      // mouseover had just set.
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
  // False on the "used as operator in" list: an operator marked hidden-by-default would
  // otherwise collapse its own page to nothing, and that page is where those rows are the point.
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
      {/* Grouped per operator rather than one lump count: you already decided this particular
          operator was noise, so the disclosure says which one it is hiding. */}
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
