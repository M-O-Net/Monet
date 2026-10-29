import type { ReferenceOut } from "./types";

export function creditsHeading(references: readonly ReferenceOut[]): string {
  return new Set(references.map((reference) => reference.label)).size === 1 ? "Source" : "Sources";
}

export function describeCredits(references: readonly ReferenceOut[]): string | undefined {
  if (references.length === 0) return undefined;
  const names = [...new Set(references.map((reference) => reference.label))];
  return `${creditsHeading(references)}: ${names.join(", ")}`;
}
