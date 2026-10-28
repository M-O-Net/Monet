import { describe, expect, it } from "vitest";

import { hiddenByOperator } from "./neighborhood";
import type { ObjectOut } from "./types";

const operator = (id: string, latex: string): ObjectOut => ({
  id,
  latex,
  description: null,
  facets: [],
});

const DET = operator("det", "\\text{Determinant}");
const TRACE = operator("trace", "\\text{Trace}");
const ROOTS = operator("roots", "\\text{Roots}");

describe("hiddenByOperator", () => {
  it("adds up an operator's hidden relations across sides", () => {
    expect(
      hiddenByOperator([
        { operator: DET, side: "output", count: 4 },
        { operator: DET, side: "input", count: 2 },
      ]),
    ).toEqual([{ operator: DET, count: 6 }]);
  });

  it("puts the operator hiding the most first, then by name", () => {
    const notes = hiddenByOperator([
      { operator: TRACE, side: "output", count: 2 },
      { operator: ROOTS, side: "output", count: 2 },
      { operator: DET, side: "output", count: 9 },
    ]);
    expect(notes.map((note) => note.operator.id)).toEqual(["det", "roots", "trace"]);
  });

  it("is empty when nothing was hidden", () => {
    expect(hiddenByOperator([])).toEqual([]);
  });
});
