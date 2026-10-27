import type { components } from "../client/schema";

export type ObjectOut = components["schemas"]["ObjectOut"];
export type ObjectDetailOut = components["schemas"]["ObjectDetailOut"];
export type ObjectReferenceIn = components["schemas"]["ObjectReferenceIn"];
export type ObjectReferenceOut = components["schemas"]["ObjectReferenceOut"];
export type RelationOut = components["schemas"]["RelationOut"];
export type RelationSlotOut = components["schemas"]["RelationSlotOut"];
export type SectionNode = components["schemas"]["SectionNode"];
export type OperatorDisplayOut = components["schemas"]["OperatorDisplayOut"];
export type RelationDisplayOut = components["schemas"]["RelationDisplayOut"];
export type ProvenanceOut = components["schemas"]["ProvenanceOut"];
export type CommentOut = components["schemas"]["CommentOut"];
export type ObjectRole = ObjectDetailOut["roles"][number];
export type FacetOut = components["schemas"]["FacetOut"];
export type SignatureOut = components["schemas"]["SignatureOut"];
export type EventOut = components["schemas"]["EventOut"];
export type EventKind = EventOut["kind"];
