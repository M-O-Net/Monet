import { Link } from "@tanstack/react-router";

import { Latex } from "../../components/Latex";
import type { RelationOut } from "../../lib/types";

export function RelationList({ title, relations }: { title: string; relations: RelationOut[] }) {
  if (relations.length === 0) return null;
  return (
    <div className="mb-7">
      <h2 className="mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase">{title}</h2>
      <ul className="space-y-2">
        {relations.map((rel) => (
          <li
            key={rel.id}
            className="rounded-sm border border-mist bg-white/40 px-3 py-2.5 text-sm shadow-[0_1px_3px_rgba(35,50,43,0.06)]"
          >
            <div className="flex flex-wrap items-center gap-x-1.5 gap-y-1">
              {rel.inputs.map((slot, i) => (
                <span key={`${rel.id}-in-${String(slot.position)}`} className="flex items-center">
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
              <span className="mx-1 inline-flex items-center gap-1 text-ink-soft">
                <span aria-hidden className="text-mist">
                  ──
                </span>
                {/* The operator is an object like any other (README: "operators are objects
                    too"), so it links to its own page exactly as the operands do — it used to
                    be the one object reference in the UI that was a dead end. */}
                <Link
                  to="/objects/$objectId"
                  params={{ objectId: rel.operator.id }}
                  className="rounded-sm border border-gold/40 bg-gold-soft px-2 py-0.5 text-xs font-medium tracking-wide text-ink transition-colors hover:bg-gold-soft/60"
                >
                  <Latex>{rel.operator.latex}</Latex>
                </Link>
                <span aria-hidden className="text-mist">
                  ──▸
                </span>
              </span>
              {rel.outputs.map((slot, i) => (
                <span key={`${rel.id}-out-${String(slot.position)}`} className="flex items-center">
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
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
