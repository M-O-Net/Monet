import { describe, expect, it } from "vitest";

import { findCyclesThrough } from "./cycles";
import type { ObjectOut, RelationOut } from "./types";

const id = (n: number) => `${String(n).padStart(8, "0")}-0000-4000-8000-000000000000`;

const object = (n: number, latex: string): ObjectOut => ({
  id: id(n),
  latex,
  description: null,
});

const P = object(1, "x^{2} - 1");
const D = object(2, "\\begin{pmatrix}0&1\\\\1&0\\end{pmatrix}");
const A = object(3, "\\begin{pmatrix}2&1\\\\1&2\\end{pmatrix}");
const CHARPOLY = object(4, "\\text{Characteristic Polynomial}");
const COMPANION = object(5, "\\text{Companion Matrix}");
const INVERSE = object(6, "\\text{Inverse}");
const ELEMENT_OF = object(7, "\\text{Element Of}");
const MATRICES = object(8, "\\text{Matrices}");

let next = 100;
function relation(
  operator: ObjectOut,
  inputs: ObjectOut[],
  outputs: ObjectOut[],
  membership = false,
): RelationOut {
  return {
    id: id((next += 1)),
    operator,
    inputs: inputs.map((object, position) => ({ position, object })),
    outputs: outputs.map((object, position) => ({ position, object })),
    display: { template: null, hidden_by_default: false, is_membership: membership },
  };
}

describe("findCyclesThrough", () => {
  it("finds the two-step companion-matrix loop", () => {
    const relations = [relation(COMPANION, [P], [D]), relation(CHARPOLY, [D], [P])];
    const cycles = findCyclesThrough(relations, P.id);
    expect(cycles).toHaveLength(1);
    expect(cycles[0].map((step) => step.relation.operator.id)).toEqual([COMPANION.id, CHARPOLY.id]);
    expect(cycles[0].at(-1)?.to.id).toBe(P.id);
  });

  it("keeps a self-loop, which an object being its own inverse really is", () => {
    const cycles = findCyclesThrough([relation(INVERSE, [D], [D])], D.id);
    expect(cycles).toHaveLength(1);
    expect(cycles[0]).toHaveLength(1);
    expect(cycles[0][0].from.id).toBe(D.id);
    expect(cycles[0][0].to.id).toBe(D.id);
  });

  it("does not join two objects merely because one operator produced both", () => {
    const relations = [relation(CHARPOLY, [A], [P]), relation(CHARPOLY, [D], [P])];
    expect(findCyclesThrough(relations, A.id)).toEqual([]);
    expect(findCyclesThrough(relations, P.id)).toEqual([]);
  });

  it("ignores membership relations, so a shared section is not a loop", () => {
    const relations = [
      relation(ELEMENT_OF, [A], [MATRICES], true),
      relation(ELEMENT_OF, [MATRICES], [A], true),
    ];
    expect(findCyclesThrough(relations, A.id)).toEqual([]);
  });

  it("walks every input of a relation that takes more than one", () => {
    const relations = [relation(COMPANION, [A, P], [D]), relation(CHARPOLY, [D], [A])];
    expect(findCyclesThrough(relations, A.id)).toHaveLength(1);
  });

  it("stops at the length bound rather than walking a long chain", () => {
    const chain = [object(20, "a"), object(21, "b"), object(22, "c")];
    const relations = [
      relation(CHARPOLY, [P], [chain[0]]),
      relation(CHARPOLY, [chain[0]], [chain[1]]),
      relation(CHARPOLY, [chain[1]], [chain[2]]),
      relation(CHARPOLY, [chain[2]], [P]),
    ];
    expect(findCyclesThrough(relations, P.id, { maxLength: 3 })).toEqual([]);
    expect(findCyclesThrough(relations, P.id, { maxLength: 4 })).toHaveLength(1);
  });

  it("returns no more than the requested number of cycles", () => {
    const relations = [
      relation(COMPANION, [P], [D]),
      relation(CHARPOLY, [D], [P]),
      relation(INVERSE, [P], [A]),
      relation(CHARPOLY, [A], [P]),
    ];
    expect(findCyclesThrough(relations, P.id, { maxCycles: 1 })).toHaveLength(1);
    expect(findCyclesThrough(relations, P.id)).toHaveLength(2);
  });
});
