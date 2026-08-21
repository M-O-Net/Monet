import { describe, expect, it } from "vitest";

import { buildGraph, neighbourhood } from "./graphModel";
import type { ObjectOut, RelationOut } from "./types";

const id = (n: number) => `${String(n).padStart(8, "0")}-0000-4000-8000-000000000000`;
const object = (n: number, latex: string): ObjectOut => ({ id: id(n), latex, description: null });

const A = object(1, "A");
const B = object(2, "B");
const E = object(3, "E");
const ADD = object(4, "\\text{Add}");
const ELEMENT_OF = object(5, "\\text{Element Of}");
const MATRICES = object(6, "\\text{Matrices}");
const LONE = object(7, "\\text{Lonely}");

let next = 100;
const relation = (
  operator: ObjectOut,
  inputs: ObjectOut[],
  outputs: ObjectOut[],
  membership = false,
): RelationOut => ({
  id: id((next += 1)),
  operator,
  inputs: inputs.map((object, position) => ({ position, object })),
  outputs: outputs.map((object, position) => ({ position, object })),
  display: { template: null, hidden_by_default: false, is_membership: membership },
});

describe("buildGraph", () => {
  it("gives a binary relation its own node with an edge from each input", () => {
    const add = relation(ADD, [A, B], [E]);
    const graph = buildGraph([add], [A, B, E]);
    expect(graph.nodes.filter((node) => node.kind === "relation")).toHaveLength(1);
    expect(graph.edges.filter((edge) => edge.target === add.id).map((edge) => edge.source)).toEqual(
      [A.id, B.id],
    );
    expect(graph.edges.filter((edge) => edge.source === add.id).map((edge) => edge.target)).toEqual(
      [E.id],
    );
  });

  it("leaves membership relations out entirely", () => {
    const graph = buildGraph([relation(ELEMENT_OF, [A], [MATRICES], true)], [A, MATRICES]);
    expect(graph.nodes.filter((node) => node.kind === "relation")).toEqual([]);
    expect(graph.edges).toEqual([]);
  });

  it("keeps an object that takes part in nothing", () => {
    const graph = buildGraph([], [LONE]);
    expect(graph.nodes.map((node) => node.id)).toEqual([LONE.id]);
  });

  it("does not list an object twice when it is both catalogued and used", () => {
    const graph = buildGraph([relation(ADD, [A, B], [E])], [A, B, E]);
    const ids = graph.nodes.filter((node) => node.kind === "object").map((node) => node.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("carries an object reached only through a relation", () => {
    const graph = buildGraph([relation(ADD, [A, B], [E])], [A, B]);
    expect(graph.nodes.some((node) => node.id === E.id)).toBe(true);
  });

  it("reports what a node touches, in both directions", () => {
    const add = relation(ADD, [A, B], [E]);
    const graph = buildGraph([add], [A, B, E]);
    expect(neighbourhood(graph, add.id)).toEqual(new Set([add.id, A.id, B.id, E.id]));
    expect(neighbourhood(graph, A.id)).toEqual(new Set([A.id, add.id]));
  });
});
