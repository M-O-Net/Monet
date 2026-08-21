import type { Graph, GraphNode } from "./graphModel";
import { estimateNodeSize, sizeRadius } from "./nodeSize";

const ITERATIONS = 600;
const EDGE_GAP = 26;
const REPULSION = 1.6;
const SPRING = 0.06;
const GRAVITY = 0.006;
const MAX_STEP = 30;
const RELATION_SCALE = 0.7;

export interface Point {
  x: number;
  y: number;
}

export type Layout = Map<string, Point>;

export const nodeLabel = (node: GraphNode): string =>
  node.kind === "object" ? node.object.latex : node.relation.operator.latex;

export const nodeSize = (node: GraphNode) =>
  estimateNodeSize(nodeLabel(node), node.kind === "relation" ? RELATION_SCALE : 1);

export const nodeRadius = (node: GraphNode): number => sizeRadius(nodeSize(node));

export function layoutGraph(graph: Graph): Layout {
  const nodes = [...graph.nodes].sort((a, b) => a.id.localeCompare(b.id));
  const index = new Map(nodes.map((node, i) => [node.id, i]));
  const count = nodes.length;
  if (count === 0) return new Map();

  const radii = nodes.map(nodeRadius);
  const xs = new Float64Array(count);
  const ys = new Float64Array(count);
  const spread = 60 + count * 9;
  for (let i = 0; i < count; i += 1) {
    const angle = (2 * Math.PI * i) / count;
    xs[i] = spread * Math.cos(angle);
    ys[i] = spread * Math.sin(angle);
  }

  const springs = graph.edges
    .map((edge) => ({ a: index.get(edge.source), b: index.get(edge.target) }))
    .filter((e): e is { a: number; b: number } => e.a !== undefined && e.b !== undefined);

  const fx = new Float64Array(count);
  const fy = new Float64Array(count);

  for (let step = 0; step < ITERATIONS; step += 1) {
    fx.fill(0);
    fy.fill(0);

    for (let i = 0; i < count; i += 1) {
      for (let j = i + 1; j < count; j += 1) {
        let dx = xs[i] - xs[j];
        let dy = ys[i] - ys[j];
        let distanceSquared = dx * dx + dy * dy;
        if (distanceSquared < 1e-6) {
          dx = ((i % 7) - 3) * 0.5 + 0.1;
          dy = ((j % 5) - 2) * 0.5 + 0.1;
          distanceSquared = dx * dx + dy * dy;
        }
        const distance = Math.sqrt(distanceSquared);
        const wanted = radii[i] + radii[j] + EDGE_GAP;
        const push = (REPULSION * wanted * wanted) / distanceSquared;
        const ux = dx / distance;
        const uy = dy / distance;
        fx[i] += ux * push;
        fy[i] += uy * push;
        fx[j] -= ux * push;
        fy[j] -= uy * push;
      }
    }

    for (const { a, b } of springs) {
      const dx = xs[b] - xs[a];
      const dy = ys[b] - ys[a];
      const distance = Math.hypot(dx, dy) || 1e-3;
      const rest = radii[a] + radii[b] + EDGE_GAP;
      const pull = (distance - rest) * SPRING;
      const ux = (dx / distance) * pull;
      const uy = (dy / distance) * pull;
      fx[a] += ux;
      fy[a] += uy;
      fx[b] -= ux;
      fy[b] -= uy;
    }

    const cooling = 1 - step / ITERATIONS;
    for (let i = 0; i < count; i += 1) {
      fx[i] -= xs[i] * GRAVITY;
      fy[i] -= ys[i] * GRAVITY;
      const move = Math.hypot(fx[i], fy[i]);
      if (move < 1e-9) continue;
      const capped = Math.min(move, MAX_STEP) * cooling;
      xs[i] += (fx[i] / move) * capped;
      ys[i] += (fy[i] / move) * capped;
    }
  }

  const layout: Layout = new Map();
  for (let i = 0; i < count; i += 1) layout.set(nodes[i].id, { x: xs[i], y: ys[i] });
  return layout;
}

export interface Bounds {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
}

export function layoutBounds(graph: Graph, layout: Layout): Bounds {
  const bounds: Bounds = { minX: 0, minY: 0, maxX: 0, maxY: 0 };
  let first = true;
  for (const node of graph.nodes) {
    const point = layout.get(node.id);
    if (point === undefined) continue;
    const { width, height } = nodeSize(node);
    const left = point.x - width / 2;
    const top = point.y - height / 2;
    if (first) {
      bounds.minX = left;
      bounds.minY = top;
      bounds.maxX = left + width;
      bounds.maxY = top + height;
      first = false;
      continue;
    }
    bounds.minX = Math.min(bounds.minX, left);
    bounds.minY = Math.min(bounds.minY, top);
    bounds.maxX = Math.max(bounds.maxX, left + width);
    bounds.maxY = Math.max(bounds.maxY, top + height);
  }
  return bounds;
}
