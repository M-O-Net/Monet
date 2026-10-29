import type { ObjectData } from "./data";
import type { ObjectOut, ObjectQuery } from "./types";

export interface PropertyFilter {
  operator: ObjectOut | null;
  value: ObjectOut | null;
}

export interface SearchCriteria {
  typeId: string;
  includeSubtypes: boolean;
  value: ObjectData | null;
  ignoreVariable: boolean;
  properties: PropertyFilter[];
  description: string;
}

export type QueryParams = Pick<
  ObjectQuery,
  "member_of" | "transitive" | "data_equals" | "data_contains" | "description_contains" | "where"
>;

export function withoutVariable(data: ObjectData): ObjectData | null {
  const poly = data.poly;
  if (typeof poly !== "object" || poly === null) return null;
  const rest = Object.fromEntries(Object.entries(poly).filter(([key]) => key !== "var"));
  return { poly: rest };
}

export function toQueryParams(criteria: SearchCriteria): QueryParams | null {
  const params: QueryParams = {};
  if (criteria.typeId !== "") {
    params.member_of = criteria.typeId;
    params.transitive = criteria.includeSubtypes;
  }
  if (criteria.value !== null) {
    const loosened = criteria.ignoreVariable ? withoutVariable(criteria.value) : null;
    if (loosened === null) params.data_equals = JSON.stringify(criteria.value);
    else params.data_contains = JSON.stringify(loosened);
  }
  const where = criteria.properties.flatMap(({ operator, value }) =>
    operator === null || value === null ? [] : [`${operator.id}:${value.id}`],
  );
  if (where.length > 0) params.where = where;
  const description = criteria.description.trim();
  if (description !== "") params.description_contains = description;
  return Object.keys(params).length === 0 ? null : params;
}

const OBJECT_ID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function asObjectId(text: string): string | null {
  const trimmed = text.trim();
  return OBJECT_ID.test(trimmed) ? trimmed.toLowerCase() : null;
}
