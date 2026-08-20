import { Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";

import { Latex } from "../../components/Latex";
import { buildTemplateHtml } from "../../lib/relationTemplate";
import type { ObjectOut, RelationOut } from "../../lib/types";
import { RelationExpression } from "./RelationExpression";

function OperatorLink({ operator, subdued }: { operator: ObjectOut; subdued?: boolean }) {
  return (
    <Link
      to="/objects/$objectId"
      params={{ objectId: operator.id }}
      className={
        subdued
          ? "shrink-0 text-[11px] text-ink-soft transition-colors hover:text-pond"
          : "rounded-sm border border-gold/40 bg-gold-soft px-2 py-0.5 text-xs font-medium tracking-wide text-ink transition-colors hover:bg-gold-soft/60"
      }
    >
      <Latex>{operator.latex}</Latex>
    </Link>
  );
}

function Slots({ relation, slots }: { relation: RelationOut; slots: RelationOut["inputs"] }) {
  return (
    <>
      {slots.map((slot, i) => (
        <span
          key={`${relation.id}-${String(slot.position)}-${slot.object.id}`}
          className="flex items-center"
        >
          {i > 0 && <span className="mr-1.5 text-ink-soft">,</span>}
          <Link
            to="/objects/$objectId"
            params={{ objectId: slot.object.id }}
            className="rounded-sm px-0.5 hover:bg-gold-soft/50"
          >
            <Latex>{slot.object.latex}</Latex>
          </Link>
        </span>
      ))}
    </>
  );
}

function RelationRow({ relation }: { relation: RelationOut }) {
  // A template only renders if it can represent this relation exactly; otherwise the row falls
  // back to the plain layout rather than show a partial or wrong equation.
  const template = relation.display?.template ?? null;
  const templated = template !== null && buildTemplateHtml(template, relation) !== null;

  return (
    <li className="rounded-sm border border-mist bg-white/40 px-3 py-2.5 text-sm shadow-[0_1px_3px_rgba(35,50,43,0.06)]">
      {templated ? (
        // The template has no slot for the operator, so it keeps its own link at the end of the
        // row — otherwise a nicer-looking relation would be the one you could not navigate from.
        <div className="flex items-baseline justify-between gap-3">
          <RelationExpression relation={relation} template={template} />
          <OperatorLink operator={relation.operator} subdued />
        </div>
      ) : (
        <div className="flex flex-wrap items-center gap-x-1.5 gap-y-1">
          <Slots relation={relation} slots={relation.inputs} />
          <span className="mx-1 inline-flex items-center gap-1 text-ink-soft">
            <span aria-hidden className="text-mist">
              ──
            </span>
            <OperatorLink operator={relation.operator} />
            <span aria-hidden className="text-mist">
              ──▸
            </span>
          </span>
          <Slots relation={relation} slots={relation.outputs} />
        </div>
      )}
    </li>
  );
}

export function RelationList({
  title,
  relations,
  collapseHidden = true,
}: {
  title: string;
  relations: RelationOut[];
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
          <RelationRow key={relation.id} relation={relation} />
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
                  <RelationRow key={relation.id} relation={relation} />
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
