import type { ObjectRole } from "../../lib/types";

const LABEL: Record<ObjectRole, string> = {
  type: "type",
  map: "map",
  section: "section",
  instance: "instance",
};

export function RoleBadge({ role }: { role: ObjectRole }) {
  return (
    <span className="mb-1.5 inline-block rounded-sm border border-mist px-1.5 py-0.5 text-[10px] tracking-widest text-ink-soft uppercase">
      {LABEL[role]}
    </span>
  );
}
