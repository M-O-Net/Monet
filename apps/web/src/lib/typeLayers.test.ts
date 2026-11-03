import { describe, expect, it } from "vitest";

import { typeFamilies, typeLayers } from "./typeLayers";

const ids = (layers: { id: string }[][]) => layers.map((layer) => layer.map((node) => node.id));

describe("typeLayers", () => {
  it("puts each type one row below its lowest supertype", () => {
    const layers = typeLayers([
      { id: "polynomials", supertype_ids: ["rational"] },
      { id: "real", supertype_ids: [] },
      { id: "rational", supertype_ids: ["elementary", "dfinite"] },
      { id: "elementary", supertype_ids: ["real"] },
      { id: "dfinite", supertype_ids: ["real"] },
      { id: "odes", supertype_ids: [] },
    ]);
    expect(ids(layers).map((layer) => [...layer].sort())).toEqual([
      ["odes", "real"],
      ["dfinite", "elementary"],
      ["rational"],
      ["polynomials"],
    ]);
  });

  it("keeps a type next to the supertype it sits under", () => {
    const layers = typeLayers([
      { id: "a", supertype_ids: [] },
      { id: "b", supertype_ids: [] },
      { id: "under-b", supertype_ids: ["b"] },
      { id: "under-a", supertype_ids: ["a"] },
    ]);
    expect(ids(layers)).toEqual([
      ["a", "b"],
      ["under-a", "under-b"],
    ]);
  });
});

describe("typeFamilies", () => {
  it("lays out unrelated families apart, the largest first, and lone types together", () => {
    const families = typeFamilies([
      { id: "braids", supertype_ids: [] },
      { id: "odes", supertype_ids: [] },
      { id: "real", supertype_ids: [] },
      { id: "linear-odes", supertype_ids: ["odes"] },
      { id: "even", supertype_ids: ["real"] },
      { id: "odd", supertype_ids: ["real"] },
      { id: "surfaces", supertype_ids: [] },
    ]);
    expect(families.map(ids)).toEqual([
      [["real"], ["even", "odd"]],
      [["odes"], ["linear-odes"]],
      [["braids", "surfaces"]],
    ]);
  });
});
