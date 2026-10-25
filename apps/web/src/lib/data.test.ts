import { describe, expect, it } from "vitest";

import { sameData } from "./data";

const squarePlusOne = (variable: string) => ({
  poly: {
    var: variable,
    degree: 2,
    coeffs: { "0": { int: 1 }, "1": { int: 0 }, "2": { int: 1 } },
  },
});

describe("sameData", () => {
  it("ignores key order, which the database does not preserve", () => {
    const reordered = {
      poly: { coeffs: { "2": { int: 1 }, "1": { int: 0 }, "0": { int: 1 } }, degree: 2, var: "x" },
    };
    expect(sameData(squarePlusOne("x"), reordered)).toBe(true);
  });

  it("tells apart values that differ anywhere, including array order", () => {
    expect(sameData(squarePlusOne("x"), squarePlusOne("z"))).toBe(false);
    expect(
      sameData({ matrix: [[{ int: 1 }, { int: 0 }]] }, { matrix: [[{ int: 0 }, { int: 1 }]] }),
    ).toBe(false);
  });

  it("never matches an object that carries no data", () => {
    expect(sameData(null, null)).toBe(false);
    expect(sameData(undefined, squarePlusOne("x"))).toBe(false);
  });
});
