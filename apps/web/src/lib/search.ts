import type { ObjectOut } from "./types";

const MACRO = /\\[a-zA-Z]+/g;
const GROUPING = /[{}$]/g;
const NOISE = /[\s,&\\]+/g;

export function searchKey(latex: string): string {
  return latex.replace(MACRO, " ").replace(GROUPING, "").replace(NOISE, " ").trim().toLowerCase();
}

const PREFIX = 0;
const WORD = 1;
const SUBSTRING = 2;
const SUBSEQUENCE = 3;
const NO_MATCH = 4;

function rank(haystack: string, needle: string): number {
  if (needle === "" || haystack.startsWith(needle)) return PREFIX;
  const at = haystack.indexOf(needle);
  if (at > 0 && haystack[at - 1] === " ") return WORD;
  if (at > 0) return SUBSTRING;
  let cursor = 0;
  for (const character of needle) {
    cursor = haystack.indexOf(character, cursor) + 1;
    if (cursor === 0) return NO_MATCH;
  }
  return SUBSEQUENCE;
}

export function searchObjects(
  objects: readonly ObjectOut[],
  query: string,
  limit = 12,
): ObjectOut[] {
  const needle = searchKey(query);
  if (needle === "") return objects.slice(0, limit);

  const scored: { object: ObjectOut; rank: number; length: number }[] = [];
  for (const object of objects) {
    const latexKey = searchKey(object.latex);
    const descriptionKey = searchKey(object.description ?? "");
    const best = Math.min(rank(latexKey, needle), rank(descriptionKey, needle));
    if (best === NO_MATCH) continue;
    scored.push({ object, rank: best, length: latexKey.length });
  }

  scored.sort(
    (a, b) =>
      a.rank - b.rank || a.length - b.length || a.object.latex.localeCompare(b.object.latex),
  );
  return scored.slice(0, limit).map((entry) => entry.object);
}
