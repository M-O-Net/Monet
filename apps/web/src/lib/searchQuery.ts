import type { ObjectData } from "./data";

export interface PropertyFilter {
  operatorId: string;
  valueId: string;
}

export interface SearchCriteria {
  typeId: string;
  includeSubtypes: boolean;
  value: ObjectData | null;
  ignoreVariable: boolean;
  properties: PropertyFilter[];
  description: string;
}

export interface QueryParams {
  member_of?: string;
  transitive?: boolean;
  data_equals?: string;
  data_contains?: string;
  description_contains?: string;
  where?: string[];
}

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
  const where = criteria.properties
    .filter((property) => property.operatorId !== "" && property.valueId !== "")
    .map((property) => `${property.operatorId}:${property.valueId}`);
  if (where.length > 0) params.where = where;
  const description = criteria.description.trim();
  if (description !== "") params.description_contains = description;
  return Object.keys(params).length === 0 ? null : params;
}

export function dataKinds(data: readonly (ObjectData | null)[]): Set<string> {
  const kinds = new Set<string>();
  for (const entry of data) {
    if (entry === null) continue;
    for (const key of Object.keys(entry)) kinds.add(key);
  }
  return kinds;
}

const OBJECT_ID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function asObjectId(text: string): string | null {
  const trimmed = text.trim();
  return OBJECT_ID.test(trimmed) ? trimmed.toLowerCase() : null;
}
