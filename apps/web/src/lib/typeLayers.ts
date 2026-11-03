export interface Node {
  id: string;
  supertype_ids: string[];
}

const SWEEPS = 4;

function mean(values: number[]): number | null {
  return values.length === 0 ? null : values.reduce((sum, value) => sum + value, 0) / values.length;
}

export function typeLayers<T extends Node>(nodes: T[]): T[][] {
  const byId = new Map(nodes.map((node) => [node.id, node]));
  const depth = new Map<string, number>();
  const depthOf = (node: T, visiting: ReadonlySet<string>): number => {
    const known = depth.get(node.id);
    if (known !== undefined) return known;
    const above = node.supertype_ids
      .map((id) => byId.get(id))
      .filter((parent): parent is T => parent !== undefined && !visiting.has(parent.id));
    const nextVisiting = new Set(visiting).add(node.id);
    const found = Math.max(-1, ...above.map((parent) => depthOf(parent, nextVisiting))) + 1;
    depth.set(node.id, found);
    return found;
  };
  for (const node of nodes) depthOf(node, new Set());

  const layers: T[][] = [];
  for (const node of nodes) {
    const index = depth.get(node.id) ?? 0;
    (layers[index] ??= []).push(node);
  }

  const below = new Map<string, string[]>();
  for (const node of nodes) {
    for (const parent of node.supertype_ids) {
      below.set(parent, [...(below.get(parent) ?? []), node.id]);
    }
  }
  const position = new Map<string, number>();
  const record = (layer: T[]) => {
    layer.forEach((node, index) => position.set(node.id, index / Math.max(1, layer.length - 1)));
  };
  const reorder = (layer: T[], neighbours: (node: T) => string[]) => {
    const key = new Map(
      layer.map((node, index) => [
        node.id,
        mean(neighbours(node).flatMap((id) => position.get(id) ?? [])) ??
          index / Math.max(1, layer.length - 1),
      ]),
    );
    layer.sort((a, b) => (key.get(a.id) ?? 0) - (key.get(b.id) ?? 0));
    record(layer);
  };

  layers.forEach(record);
  for (let sweep = 0; sweep < SWEEPS; sweep++) {
    for (const layer of layers.slice(1)) reorder(layer, (node) => node.supertype_ids);
    for (const layer of layers.slice(0, -1).reverse()) {
      reorder(layer, (node) => below.get(node.id) ?? []);
    }
  }
  return layers;
}

export function typeFamilies<T extends Node>(nodes: T[]): T[][][] {
  const ids = new Set(nodes.map((node) => node.id));
  const family = new Map(nodes.map((node) => [node.id, node.id]));
  const root = (id: string): string => {
    const parent = family.get(id) ?? id;
    return parent === id ? id : root(parent);
  };
  for (const node of nodes) {
    for (const parent of node.supertype_ids) {
      if (ids.has(parent)) family.set(root(node.id), root(parent));
    }
  }
  const members = new Map<string, T[]>();
  for (const node of nodes) {
    const key = root(node.id);
    members.set(key, [...(members.get(key) ?? []), node]);
  }
  const families = [...members.values()].sort((a, b) => b.length - a.length);
  const related = families.filter((found) => found.length > 1).map(typeLayers);
  const alone = families.filter((found) => found.length === 1).flat();
  return alone.length > 0 ? [...related, [alone]] : related;
}
