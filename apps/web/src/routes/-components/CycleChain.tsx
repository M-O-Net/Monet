import { Link } from "@tanstack/react-router";

import { Latex } from "../../components/Latex";
import type { Cycle } from "../../lib/cycles";

const NODE_CLASS = "rounded-sm px-1.5 py-0.5";

function Node({ id, latex, isCurrent }: { id: string; latex: string; isCurrent: boolean }) {
  if (isCurrent) {
    return (
      <span className={`${NODE_CLASS} is-current`}>
        <Latex>{latex}</Latex>
      </span>
    );
  }
  return (
    <Link
      to="/objects/$objectId"
      params={{ objectId: id }}
      className={`${NODE_CLASS} relation-tag`}
    >
      <Latex>{latex}</Latex>
    </Link>
  );
}

export function CycleChain({ cycle, currentObjectId }: { cycle: Cycle; currentObjectId: string }) {
  const start = cycle.at(0)?.from;
  if (start === undefined) return null;

  return (
    <p className="flex flex-wrap items-center gap-x-1.5 gap-y-2 text-sm">
      <Node id={start.id} latex={start.latex} isCurrent={start.id === currentObjectId} />
      {cycle.map((step) => (
        <span key={step.relation.id} className="flex flex-wrap items-center gap-x-1.5 gap-y-2">
          <Link
            to="/objects/$objectId"
            params={{ objectId: step.relation.operator.id }}
            className="text-xs text-ink-soft underline decoration-dotted underline-offset-2 hover:text-pond"
          >
            <Latex>{step.relation.operator.latex}</Latex>
          </Link>
          <span aria-hidden className="text-ink-soft">
            →
          </span>
          <Node id={step.to.id} latex={step.to.latex} isCurrent={step.to.id === currentObjectId} />
        </span>
      ))}
    </p>
  );
}
