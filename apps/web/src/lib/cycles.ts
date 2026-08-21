import type { ObjectOut, RelationOut } from "./types";

export const MAX_CYCLE_LENGTH = 6;
export const MAX_CYCLES_SHOWN = 3;

export interface CycleStep {
  relation: RelationOut;
  from: ObjectOut;
  to: ObjectOut;
}

export type Cycle = CycleStep[];

export const isMembership = (relation: RelationOut): boolean =>
  relation.display?.is_membership ?? false;

function stepsOutOf(relations: readonly RelationOut[]): Map<string, CycleStep[]> {
  const outgoing = new Map<string, CycleStep[]>();
  for (const relation of relations) {
    if (isMembership(relation)) continue;
    for (const input of relation.inputs) {
      const from = input.object;
      const steps = outgoing.get(from.id) ?? [];
      for (const output of relation.outputs) {
        steps.push({ relation, from, to: output.object });
      }
      outgoing.set(from.id, steps);
    }
  }
  return outgoing;
}

export function findCyclesThrough(
  relations: readonly RelationOut[],
  objectId: string,
  { maxLength = MAX_CYCLE_LENGTH, maxCycles = MAX_CYCLES_SHOWN } = {},
): Cycle[] {
  const outgoing = stepsOutOf(relations);
  const found: Cycle[] = [];
  const seen = new Set<string>();

  const walk = (nodeId: string, path: Cycle) => {
    if (found.length >= maxCycles || path.length >= maxLength) return;
    for (const step of outgoing.get(nodeId) ?? []) {
      if (step.to.id === objectId) {
        const cycle = [...path, step];
        const key = cycle.map((s) => s.relation.id).join(">");
        if (!seen.has(key)) {
          seen.add(key);
          found.push(cycle);
        }
        if (found.length >= maxCycles) return;
        continue;
      }
      if (path.some((s) => s.to.id === step.to.id)) continue;
      walk(step.to.id, [...path, step]);
      if (found.length >= maxCycles) return;
    }
  };

  walk(objectId, []);
  return found;
}
