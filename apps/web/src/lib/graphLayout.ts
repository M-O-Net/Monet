import type { Graph, GraphNode } from "./graphModel";

const ITERATIONS = 400;
const IDEAL_EDGE_LENGTH = 90;
const RELATION_EDGE_LENGTH = 46;
const REPULSION = 5200;
const SPRING = 0.035;
const GRAVITY = 0.012;
const MAX_STEP = 24;
const OBJECT_RADIUS = 30;
const RELATION_RADIUS = 16;

export interface Point {
  x: number;
  y: number;
}

export type Layout = Map<string, Point>;

export const nodeRadius = (node: GraphNode): number =>
  node.kind === "relation" ? RELATION_RADIUS : OBJECT_RADIUS;

function seededOrder(nodes: readonly GraphNode[]): GraphNode[] {
  return [...nodes].sort((a, b) => a.id.localeCompare(b.id));
}

export function layoutGraph(graph: Graph): Layout {
  const nodes = seededOrder(graph.nodes);
  const index = new Map(nodes.map((node, i) => [node.id, i]));
  const count = nodes.length;
  if (count === 0) return new Map();

  const xs = new Float64Array(count);
  const ys = new Float64Array(count);
  const radius = 40 + count * 7;
  for (let i = 0; i < count; i += 1) {
    const angle = (2 * Math.PI * i) / count;
    xs[i] = radius * Math.cos(angle);
    ys[i] = radius * Math.sin(angle);
  }

  const springs = graph.edges
    .map((edge) => ({ a: index.get(edge.source), b: index.get(edge.target) }))
    .filter(
      (edge): edge is { a: number; b: number } => edge.a !== undefined && edge.b !== undefined,
    );

  const restLength = nodes.map((node) =>
    node.kind === "relation" ? RELATION_EDGE_LENGTH : IDEAL_EDGE_LENGTH,
  );

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
        const push = REPULSION / distanceSquared;
        const distance = Math.sqrt(distanceSquared);
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
      const rest = Math.min(restLength[a], restLength[b]);
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
      const capped = Math.min(move, MAX_STEP) * cooling;
      if (move > 1e-9) {
        xs[i] += (fx[i] / move) * capped;
        ys[i] += (fy[i] / move) * capped;
      }
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
    const pad = nodeRadius(node);
    if (first) {
      bounds.minX = point.x - pad;
      bounds.minY = point.y - pad;
      bounds.maxX = point.x + pad;
      bounds.maxY = point.y + pad;
      first = false;
      continue;
    }
    bounds.minX = Math.min(bounds.minX, point.x - pad);
    bounds.minY = Math.min(bounds.minY, point.y - pad);
    bounds.maxX = Math.max(bounds.maxX, point.x + pad);
    bounds.maxY = Math.max(bounds.maxY, point.y + pad);
  }
  return bounds;
}
