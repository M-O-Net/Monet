export type ObjectData = Record<string, unknown>;

interface Faceted {
  facets: readonly { data: ObjectData | null }[];
}

export function facetData(object: Faceted): ObjectData[] {
  return object.facets.flatMap((facet) => (facet.data === null ? [] : [facet.data]));
}

export function primaryData(object: Faceted): ObjectData | null {
  return facetData(object)[0] ?? null;
}
