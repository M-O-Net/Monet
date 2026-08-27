import { describe, expect, it } from "vitest";

import { searchKey, searchObjects } from "./search";
import type { ObjectOut } from "./types";

const id = (n: number) => `${String(n).padStart(8, "0")}-0000-4000-8000-000000000000`;
const object = (n: number, latex: string, description: string | null = null): ObjectOut => ({
  id: id(n),
  latex,
  description,
});

const CHARPOLY = object(1, "\\text{Characteristic Polynomial}");
const P = object(2, "x^{2} - 4 x + 3");
const A = object(3, "\\begin{pmatrix}2&1\\\\1&2\\end{pmatrix}", "A symmetric matrix.");
const TREFOIL = object(4, "\\mathrm{3}_{1}", "The trefoil — the simplest knot.");

const all = [CHARPOLY, P, A, TREFOIL];

describe("searchKey", () => {
  it("strips the macro wrapper so the words inside are searchable", () => {
    expect(searchKey("\\text{Characteristic Polynomial}")).toBe("characteristic polynomial");
  });

  it("keeps the algebra of a polynomial readable", () => {
    expect(searchKey("x^{2} - 4 x + 3")).toBe("x^2 - 4 x + 3");
  });

  it("reduces a matrix to its entries", () => {
    expect(searchKey("\\begin{pmatrix}2&1\\\\1&2\\end{pmatrix}")).toBe("pmatrix2 1 1 2 pmatrix");
  });
});

describe("searchObjects", () => {
  it("finds an operator by a word inside its \\text{}", () => {
    expect(searchObjects(all, "characteristic")).toEqual([CHARPOLY]);
  });

  it("finds a polynomial by a power written with braces", () => {
    expect(searchObjects(all, "x^{2}")).toContain(P);
  });

  it("finds an object by its description", () => {
    expect(searchObjects(all, "trefoil")).toContain(TREFOIL);
  });

  it("is case insensitive", () => {
    expect(searchObjects(all, "POLYNOMIAL")).toContain(CHARPOLY);
  });

  it("ranks a prefix above a mid-word match", () => {
    const pair = [object(5, "\\text{Polynomial}"), object(6, "\\text{Characteristic Polynomial}")];
    expect(searchObjects(pair, "poly")[0].latex).toBe("\\text{Polynomial}");
  });

  it("returns everything, capped, for an empty query", () => {
    expect(searchObjects(all, "")).toHaveLength(4);
    expect(searchObjects(all, "", 2)).toHaveLength(2);
  });

  it("returns nothing when there is no match at all", () => {
    expect(searchObjects(all, "zzzz")).toEqual([]);
  });
});
