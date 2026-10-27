import type { ObjectRole } from "../../lib/types";

export function RoleBadges({ roles }: { roles: ObjectRole[] }) {
  if (roles.length === 0) return null;
  return (
    <div className="mb-1.5 flex gap-1.5">
      {roles.map((role) => (
        <span
          key={role}
          className="inline-block rounded-sm border border-mist px-1.5 py-0.5 text-[10px] tracking-widest text-ink-soft uppercase"
        >
          {role}
        </span>
      ))}
    </div>
  );
}
