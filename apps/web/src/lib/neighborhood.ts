import type { HiddenRelationsOut, ObjectOut } from "./types";

export interface HiddenNote {
  operator: ObjectOut;
  count: number;
}

export function hiddenByOperator(hidden: readonly HiddenRelationsOut[]): HiddenNote[] {
  const notes = new Map<string, HiddenNote>();
  for (const { operator, count } of hidden) {
    const note = notes.get(operator.id);
    if (note === undefined) notes.set(operator.id, { operator, count });
    else note.count += count;
  }
  return [...notes.values()].sort(
    (a, b) => b.count - a.count || a.operator.latex.localeCompare(b.operator.latex),
  );
}
