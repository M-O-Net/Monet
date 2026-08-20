import type { QueryClient } from "@tanstack/react-query";

/**
 * Refetch everything that can show an object, a relation or a section.
 *
 * Deliberately broad. Almost every mutation here reaches further than the page that made it: a
 * display template changes how that operator's relations read on every object's page, and
 * filing something under a section changes the contents. openapi-react-query keys are
 * ["get", path, options?], so passing only the first two elements matches every set of path
 * params for that endpoint rather than just the current one.
 */
export function invalidateObjectGraph(queryClient: QueryClient): void {
  for (const key of [
    ["get", "/objects"],
    ["get", "/objects/{object_id}"],
    ["get", "/contents"],
    ["get", "/top-level-objects"],
    ["get", "/operator-displays/{operator_id}"],
  ]) {
    void queryClient.invalidateQueries({ queryKey: key });
  }
}
