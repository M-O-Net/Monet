import { findCyclesThrough } from "../../lib/cycles";
import type { RelationOut } from "../../lib/types";
import { Callout } from "./Callout";
import { CycleChain } from "./CycleChain";

export function LoopCallout({
  relations,
  currentObjectId,
}: {
  relations: RelationOut[];
  currentObjectId: string;
}) {
  const cycles = findCyclesThrough(relations, currentObjectId);
  if (cycles.length === 0) return null;

  const onlySelfLoops = cycles.every((cycle) => cycle.length === 1);
  const heading = cycles.length === 1 ? "This closes a loop" : "This closes loops";
  const lead = onlySelfLoops
    ? "Following this operation sends the object straight back to itself."
    : "Follow these operations and you arrive back where you started.";

  return (
    <Callout heading={heading} tone="pond">
      <p className="mb-3 text-sm text-ink-soft">{lead}</p>
      <ul className="space-y-2">
        {cycles.map((cycle) => (
          <li key={cycle.map((step) => step.relation.id).join(">")}>
            <CycleChain cycle={cycle} currentObjectId={currentObjectId} />
          </li>
        ))}
      </ul>
    </Callout>
  );
}
