import { describe, expect, it } from "vitest";

import { layoutBounds, layoutGraph, nodeSize } from "./graphLayout";
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
const joined = buildGraph([
  relation([objects[0]], [objects[1]]),
  relation([objects[1]], [objects[2]]),
  relation([objects[5]], [objects[7]]),
  relation([objects[6]], [objects[4]]),
]);

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

describe("layoutGraph on a network the size Monet actually serves", () => {
  const wide = "\\begin{pmatrix}-1&1&0&0\\\\0&-1&1&0\\\\0&0&-1&1\\\\0&0&0&-1\\end{pmatrix}";
  const many = Array.from({ length: 24 }, (_unused, i) =>
    object(200 + i, i % 3 === 0 ? wide : `\\text{Characteristic Polynomial ${String(i)}}`),
  );
  const dense = buildGraph(many.slice(0, -1).map((from, i) => relation([from], [many[i + 1]])));

  it("draws every node clear of every other", () => {
    const layout = layoutGraph(dense);
    let overlaps = 0;
    for (let i = 0; i < dense.nodes.length; i += 1) {
      for (let j = i + 1; j < dense.nodes.length; j += 1) {
        const a = at(layout, dense.nodes[i].id);
        const b = at(layout, dense.nodes[j].id);
        const sa = nodeSize(dense.nodes[i]);
        const sb = nodeSize(dense.nodes[j]);
        const clearX = Math.abs(a.x - b.x) >= (sa.width + sb.width) / 2;
        const clearY = Math.abs(a.y - b.y) >= (sa.height + sb.height) / 2;
        if (!clearX && !clearY) overlaps += 1;
      }
    }
    expect(overlaps).toBe(0);
  });

  it("never leaves two nodes sitting on the same point", () => {
    const layout = layoutGraph(dense);
    const nearest = (nodeId: string) =>
      Math.min(
        ...dense.nodes
          .filter((other) => other.id !== nodeId)
          .map((other) => distance(at(layout, nodeId), at(layout, other.id))),
      );
    for (const node of dense.nodes) expect(nearest(node.id)).toBeGreaterThan(0);
  });
});
