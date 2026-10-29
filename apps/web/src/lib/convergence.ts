import type { RelationGroupOut, RelationOut } from "./types";

export interface Convergence {
  routes: RelationGroupOut[];
  distinctOperators: number;
}

const inputKey = (relation: RelationOut): string =>
  relation.inputs.map((slot) => slot.object.id).join(",");

export function findConvergence(asOutput: readonly RelationGroupOut[]): Convergence | null {
  if (asOutput.length >= 2) return { routes: [...asOutput], distinctOperators: asOutput.length };

  const only = asOutput.at(0);
  if (only === undefined) return null;
  const distinctInputs = new Set(only.relations.map(inputKey));
  if (distinctInputs.size < 2) return null;
  return { routes: [only], distinctOperators: 1 };
}
