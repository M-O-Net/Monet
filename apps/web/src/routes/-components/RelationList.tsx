import { Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";

import { Latex } from "../../components/Latex";
import { buildTemplateHtml } from "../../lib/relationTemplate";
import type { ObjectOut, RelationOut } from "../../lib/types";
import { RelationExpression } from "./RelationExpression";

function OperatorLink({ operator }: { operator: ObjectOut }) {
  return (
    <Link
      to="/objects/$objectId"
      params={{ objectId: operator.id }}
      // The card-catalog tag, kept as it was, moved above the mathematics so that every formula
      // in a list starts at the same left edge whatever its operator is called.
      //
      // Set in the operator's own notation, at its own case: an object *is* its rendered
      // notation here, so uppercasing it restyles the object rather than its label. The tag is
      // also where gold belongs — gold ink is #be8f3e on #eaefe4 paper, around 2.4:1, which
      // small text cannot carry, while ink on a gold-soft tag reads cleanly.
      className="inline-block rounded-sm border border-gold/40 bg-gold-soft px-2 py-0.5 text-xs text-ink transition-colors hover:bg-gold-soft/60"
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

  // Every row reads the same way: which operator, then what it did. Naming the operator is what
  // makes a templated row legible at all — "A + B = E" does not say that the plus is Matrix
  // Addition specifically, and there are many additions in mathematics.
  //
  // The name sits above rather than beside the mathematics so that every formula in a list
  // starts at the same left edge. Beside it, each row's formula began wherever that operator's
  // name happened to end, and a column of relations no longer lined up to be read down.
  return (
    <li className="rounded-sm border border-mist bg-white/40 px-3 py-2 shadow-[0_1px_3px_rgba(35,50,43,0.06)]">
      <OperatorLink operator={relation.operator} />
      <div className="mt-1 text-sm">
        {templated ? (
          <RelationExpression relation={relation} template={template} />
        ) : (
          <span className="flex flex-wrap items-center gap-x-1.5 gap-y-1">
            <Slots relation={relation} slots={relation.inputs} />
            <span aria-hidden className="mx-1 text-mist">
              ──▸
            </span>
            <Slots relation={relation} slots={relation.outputs} />
          </span>
        )}
      </div>
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
