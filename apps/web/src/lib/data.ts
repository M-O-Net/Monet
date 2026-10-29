export type ObjectData = Record<string, unknown>;

function canonical(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(canonical);
  if (typeof value === "object" && value !== null) {
    const entries = Object.entries(value).sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0));
    return Object.fromEntries(entries.map(([key, inner]) => [key, canonical(inner)]));
  }
  return value;
}

export function sameData(
  a: ObjectData | null | undefined,
  b: ObjectData | null | undefined,
): boolean {
  if (a === null || a === undefined || b === null || b === undefined) return false;
  return JSON.stringify(canonical(a)) === JSON.stringify(canonical(b));
}

interface Faceted {
  facets: readonly { data: ObjectData | null }[];
}

export function facetData(object: Faceted): ObjectData[] {
  return object.facets.flatMap((facet) => (facet.data === null ? [] : [facet.data]));
}

export function primaryData(object: Faceted): ObjectData | null {
  return facetData(object)[0] ?? null;
}
