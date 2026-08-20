import { Link } from "@tanstack/react-router";

import { Latex } from "../../components/Latex";
import type { ObjectOut } from "../../lib/types";

const MAX_MEMBERS = 50;

/** What is filed under this object — the main event on a section's page. */
export function MemberList({ members }: { members: ObjectOut[] }) {
  if (members.length === 0) return null;
  const shown = members.slice(0, MAX_MEMBERS);

  return (
    <div className="mb-7">
      <h2 className="mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase">
        Filed under this section
      </h2>
      <ul className="divide-y divide-mist rounded-sm border border-mist bg-white/40 shadow-[0_1px_3px_rgba(35,50,43,0.06)]">
        {shown.map((member) => (
          <li key={member.id}>
            <Link
              to="/objects/$objectId"
              params={{ objectId: member.id }}
              className="flex items-baseline gap-3 border-l-2 border-l-transparent px-4 py-2.5 transition-colors hover:border-l-gold hover:bg-gold-soft/40"
            >
              <span className="min-w-0 flex-1 text-sm text-ink">
                <Latex>{member.latex}</Latex>
              </span>
            </Link>
          </li>
        ))}
      </ul>
      {members.length > shown.length && (
        <p className="mt-1.5 text-xs text-ink-soft">
          showing {shown.length} of {members.length}
        </p>
      )}
    </div>
  );
}
