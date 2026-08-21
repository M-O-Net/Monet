import { describe, expect, it } from "vitest";

import { findConvergence } from "./convergence";
import type { ObjectOut, RelationOut } from "./types";

const id = (n: number) => `${String(n).padStart(8, "0")}-0000-4000-8000-000000000000`;
const object = (n: number, latex: string): ObjectOut => ({ id: id(n), latex, description: null });

const PHI6 = object(1, "x^{2} - x + 1");
const ALEXANDER = object(2, "\\text{Alexander Polynomial}");
const CYCLOTOMIC = object(3, "\\text{Cyclotomic Polynomial}");
const CHARPOLY = object(4, "\\text{Characteristic Polynomial}");
const V3 = object(5, "\\begin{pmatrix}-1&1\\\\0&-1\\end{pmatrix}");
const SIX = object(6, "6");
const A = object(7, "A");

let next = 100;
const relation = (operator: ObjectOut, inputs: ObjectOut[], output: ObjectOut): RelationOut => ({
  id: id((next += 1)),
  operator,
  inputs: inputs.map((object, position) => ({ position, object })),
  outputs: [{ position: 0, object: output }],
  display: null,
});

describe("findConvergence", () => {
  it("reports every operator when two different ones produce the object", () => {
    const found = findConvergence([
      relation(ALEXANDER, [V3], PHI6),
      relation(CYCLOTOMIC, [SIX], PHI6),
    ]);
    expect(found?.distinctOperators).toBe(2);
    expect(found?.routes.map((route) => route.operator.id)).toEqual([ALEXANDER.id, CYCLOTOMIC.id]);
  });

  it("groups several relations that share an operator into one route", () => {
    const found = findConvergence([
      relation(ALEXANDER, [V3], PHI6),
      relation(CYCLOTOMIC, [SIX], PHI6),
      relation(CHARPOLY, [A], PHI6),
      relation(CHARPOLY, [V3], PHI6),
    ]);
    expect(found?.distinctOperators).toBe(3);
    expect(
      found?.routes.find((route) => route.operator.id === CHARPOLY.id)?.relations,
    ).toHaveLength(2);
  });

  it("still reports one operator reached from two different inputs", () => {
    const found = findConvergence([relation(CHARPOLY, [A], PHI6), relation(CHARPOLY, [V3], PHI6)]);
    expect(found?.distinctOperators).toBe(1);
    expect(found?.routes).toHaveLength(1);
  });

  it("says nothing when one operator produced it from one input", () => {
    expect(findConvergence([relation(CYCLOTOMIC, [SIX], PHI6)])).toBeNull();
  });

  it("says nothing about an object nothing produces", () => {
    expect(findConvergence([])).toBeNull();
  });
});
