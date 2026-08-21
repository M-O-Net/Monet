import { isMembership } from "./cycles";
import type { ObjectOut, RelationOut } from "./types";

export interface ObjectNode {
  kind: "object";
  id: string;
  object: ObjectOut;
}

export interface RelationNode {
  kind: "relation";
  id: string;
  relation: RelationOut;
}

export type GraphNode = ObjectNode | RelationNode;

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
}

export interface Graph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export function buildGraph(
  relations: readonly RelationOut[],
  objects: readonly ObjectOut[],
): Graph {
  const computational = relations.filter((relation) => !isMembership(relation));

  const nodes: GraphNode[] = objects.map((object) => ({ kind: "object", id: object.id, object }));
  const known = new Set(objects.map((object) => object.id));
  const edges: GraphEdge[] = [];

  for (const relation of computational) {
    nodes.push({ kind: "relation", id: relation.id, relation });
    for (const slot of [...relation.inputs, ...relation.outputs]) {
      if (known.has(slot.object.id)) continue;
      known.add(slot.object.id);
      nodes.push({ kind: "object", id: slot.object.id, object: slot.object });
    }
    for (const input of relation.inputs) {
      edges.push({
        id: `${relation.id}:in:${String(input.position)}`,
        source: input.object.id,
        target: relation.id,
      });
    }
    for (const output of relation.outputs) {
      edges.push({
        id: `${relation.id}:out:${String(output.position)}`,
        source: relation.id,
        target: output.object.id,
      });
    }
  }

  return { nodes, edges };
}

export function neighbourhood(graph: Graph, nodeId: string): Set<string> {
  const touching = new Set<string>([nodeId]);
  for (const edge of graph.edges) {
    if (edge.source === nodeId) touching.add(edge.target);
    if (edge.target === nodeId) touching.add(edge.source);
  }
  return touching;
}
