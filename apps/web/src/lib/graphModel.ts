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

export function buildGraph(relations: readonly RelationOut[]): Graph {
  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];
  const known = new Set<string>();

  const remember = (object: ObjectOut) => {
    if (known.has(object.id)) return;
    known.add(object.id);
    nodes.push({ kind: "object", id: object.id, object });
  };

  for (const relation of relations) {
    if (isMembership(relation)) continue;
    nodes.push({ kind: "relation", id: relation.id, relation });
    for (const input of relation.inputs) {
      remember(input.object);
      edges.push({
        id: `${relation.id}:in:${String(input.position)}`,
        source: input.object.id,
        target: relation.id,
      });
    }
    for (const output of relation.outputs) {
      remember(output.object);
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
