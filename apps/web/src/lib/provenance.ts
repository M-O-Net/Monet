import type { ProvenanceOut } from "./types";

export function describeSource(source: string | null): string {
  if (source === "manual") return "entered by hand";
  if (source === "runner") return "found by the runner";
  if (source?.startsWith("implementation:") === true) return "computed by an implementation";
  if (source === "computed") return "computed";
  return "added";
}

export function describeProvenance(provenance: ProvenanceOut): string {
  const day = new Date(provenance.at).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
  const who = provenance.contributor === null ? "" : ` by ${provenance.contributor}`;
  return `${describeSource(provenance.source)}${who} · ${day}`;
}
