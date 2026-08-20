// Aliases for the generated OpenAPI schema, so components name a type instead of
// re-declaring its shape. Root AGENTS.md: "No hand-written duplicate types" — the generated
// contract is the single source of truth, and a hand-copy silently drifts the moment the API
// gains a field.
import type { components } from "../client/schema";

export type ObjectOut = components["schemas"]["ObjectOut"];
export type ObjectDetailOut = components["schemas"]["ObjectDetailOut"];
export type RelationOut = components["schemas"]["RelationOut"];
export type RelationSlotOut = components["schemas"]["RelationSlotOut"];
export type SectionNode = components["schemas"]["SectionNode"];
export type OperatorDisplayOut = components["schemas"]["OperatorDisplayOut"];
export type RelationDisplayOut = components["schemas"]["RelationDisplayOut"];
