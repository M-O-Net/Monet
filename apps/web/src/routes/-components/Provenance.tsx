import { describeProvenance } from "../../lib/provenance";
import type { ProvenanceOut } from "../../lib/types";

export function Provenance({ provenance }: { provenance: ProvenanceOut | null }) {
  if (provenance === null) return null;
  return <p className="mt-1 text-[11px] text-ink-soft/80">{describeProvenance(provenance)}</p>;
}
