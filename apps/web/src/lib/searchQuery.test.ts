import { describe, expect, it } from "vitest";

import { asObjectId, type SearchCriteria, toQueryParams } from "./searchQuery";
import type { ObjectOut } from "./types";

const object = (id: string, latex: string): ObjectOut => ({
  id,
  latex,
  description: null,
  facets: [],
});
const DET = object("det", "\\text{Determinant}");
const THREE = object("three", "3");

const nothing: SearchCriteria = {
  typeId: "",
  includeSubtypes: true,
  value: null,
  ignoreVariable: false,
  properties: [],
  description: "",
};

const squarePlusOne = (variable: string) => ({
  poly: {
    var: variable,
    degree: 2,
    coeffs: { "0": { int: 1 }, "1": { int: 0 }, "2": { int: 1 } },
  },
});

describe("toQueryParams", () => {
  it("asks for nothing when nothing is chosen", () => {
    expect(toQueryParams(nothing)).toBeNull();
    expect(toQueryParams({ ...nothing, description: "   " })).toBeNull();
  });

  it("matches a value exactly unless told to ignore the variable", () => {
    const exact = toQueryParams({ ...nothing, value: squarePlusOne("z") });
    expect(exact).toEqual({ data_equals: JSON.stringify(squarePlusOne("z")) });

    const loose = toQueryParams({ ...nothing, value: squarePlusOne("z"), ignoreVariable: true });
    expect(loose?.data_equals).toBeUndefined();
    expect(JSON.parse(loose?.data_contains ?? "{}")).toEqual({
      poly: { degree: 2, coeffs: squarePlusOne("z").poly.coeffs },
    });
  });

  it("falls back to an exact match when the value has no variable to ignore", () => {
    const params = toQueryParams({ ...nothing, value: { int: 17 }, ignoreVariable: true });
    expect(params).toEqual({ data_equals: JSON.stringify({ int: 17 }) });
  });

  it("combines a type, finished property filters and a description", () => {
    const params = toQueryParams({
      ...nothing,
      typeId: "t",
      includeSubtypes: false,
      properties: [
        { operator: DET, value: THREE },
        { operator: DET, value: null },
      ],
      description: " singular ",
    });
    expect(params).toEqual({
      member_of: "t",
      transitive: false,
      where: ["det:three"],
      description_contains: "singular",
    });
  });
});

describe("asObjectId", () => {
  it("recognises a pasted object id and nothing else", () => {
    expect(asObjectId(" 5D0C9773-D4C5-497C-A157-4D3B2310E917 ")).toBe(
      "5d0c9773-d4c5-497c-a157-4d3b2310e917",
    );
    expect(asObjectId("x^2 + 1")).toBeNull();
  });
});
