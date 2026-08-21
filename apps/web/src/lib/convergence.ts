import type { ObjectOut, RelationOut } from "./types";

export interface Route {
  operator: ObjectOut;
  relations: RelationOut[];
}

export interface Convergence {
  routes: Route[];
  distinctOperators: number;
}

const inputKey = (relation: RelationOut): string =>
  relation.inputs.map((slot) => slot.object.id).join(",");

export function findConvergence(asOutput: readonly RelationOut[]): Convergence | null {
  const byOperator = new Map<string, Route>();
  for (const relation of asOutput) {
    const route = byOperator.get(relation.operator.id) ?? {
      operator: relation.operator,
      relations: [],
    };
    route.relations.push(relation);
    byOperator.set(relation.operator.id, route);
  }

  const routes = [...byOperator.values()];
  if (routes.length >= 2) return { routes, distinctOperators: routes.length };

  const only = routes.at(0);
  if (only === undefined) return null;
  const distinctInputs = new Set(only.relations.map(inputKey));
  if (distinctInputs.size < 2) return null;
  return { routes, distinctOperators: 1 };
}
