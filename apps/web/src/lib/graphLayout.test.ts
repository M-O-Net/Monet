import { describe, expect, it } from "vitest";

import { layoutBounds, layoutGraph } from "./graphLayout";
import { buildGraph } from "./graphModel";
import type { ObjectOut, RelationOut } from "./types";

const id = (n: number) => `${String(n).padStart(8, "0")}-0000-4000-8000-000000000000`;
const object = (n: number, latex: string): ObjectOut => ({ id: id(n), latex, description: null });

const OPERATOR = object(99, "\\text{Add}");

let next = 100;
const relation = (inputs: ObjectOut[], outputs: ObjectOut[]): RelationOut => ({
  id: id((next += 1)),
  operator: OPERATOR,
  inputs: inputs.map((object, position) => ({ position, object })),
  outputs: outputs.map((object, position) => ({ position, object })),
  display: null,
});

const objects = Array.from({ length: 8 }, (_unused, i) => object(i, `x_{${String(i)}}`));
const joined = buildGraph(
  [relation([objects[0]], [objects[1]]), relation([objects[1]], [objects[2]])],
  objects,
);

function at(layout: Map<string, { x: number; y: number }>, nodeId: string) {
  const point = layout.get(nodeId);
  if (point === undefined) throw new Error(`no position for ${nodeId}`);
  return point;
}

const distance = (a: { x: number; y: number }, b: { x: number; y: number }) =>
  Math.hypot(a.x - b.x, a.y - b.y);

describe("layoutGraph", () => {
  it("places every node", () => {
    const layout = layoutGraph(joined);
    expect(layout.size).toBe(joined.nodes.length);
  });

  it("produces finite coordinates", () => {
    for (const point of layoutGraph(joined).values()) {
      expect(Number.isFinite(point.x)).toBe(true);
      expect(Number.isFinite(point.y)).toBe(true);
    }
  });

  it("gives the same picture every time, so the map does not shuffle on reload", () => {
    const first = layoutGraph(joined);
    const second = layoutGraph(joined);
    for (const [nodeId, point] of first) {
      expect(second.get(nodeId)?.x).toBe(point.x);
      expect(second.get(nodeId)?.y).toBe(point.y);
    }
  });

  it("does not depend on the order the nodes arrive in", () => {
    const shuffled = { ...joined, nodes: [...joined.nodes].reverse() };
    const first = layoutGraph(joined);
    const second = layoutGraph(shuffled);
    for (const [nodeId, point] of first) {
      expect(second.get(nodeId)?.x).toBeCloseTo(point.x, 6);
    }
  });

  it("pulls the ends of an edge closer than two nodes with no edge between them", () => {
    const layout = layoutGraph(joined);
    const along = (edge: { source: string; target: string }) =>
      distance(at(layout, edge.source), at(layout, edge.target));
    const unconnected = distance(at(layout, objects[5].id), at(layout, objects[6].id));
    for (const edge of joined.edges) expect(along(edge)).toBeLessThan(unconnected);
  });

  it("handles an empty graph", () => {
    expect(layoutGraph({ nodes: [], edges: [] }).size).toBe(0);
  });

  it("bounds every node it laid out", () => {
    const layout = layoutGraph(joined);
    const bounds = layoutBounds(joined, layout);
    for (const point of layout.values()) {
      expect(point.x).toBeGreaterThanOrEqual(bounds.minX);
      expect(point.x).toBeLessThanOrEqual(bounds.maxX);
      expect(point.y).toBeGreaterThanOrEqual(bounds.minY);
      expect(point.y).toBeLessThanOrEqual(bounds.maxY);
    }
  });
});
