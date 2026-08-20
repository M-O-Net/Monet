import type { QueryClient } from "@tanstack/react-query";

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
