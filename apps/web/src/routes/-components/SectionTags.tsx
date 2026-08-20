import { Link } from "@tanstack/react-router";

import { Latex } from "../../components/Latex";
import type { ObjectOut } from "../../lib/types";

const MAX_TAGS = 12;

/**
 * The sections this object is filed under.
 *
 * Rendered as soft chips rather than the operator badge's gold square on purpose: a membership
 * is what the object *is*, not a relation it takes part in, and reusing the badge would put the
 * Element Of rows straight back on the page in a different shape.
 */
export function SectionTags({ sections }: { sections: ObjectOut[] }) {
  if (sections.length === 0) return null;
  return (
    <ul className="mt-2 flex flex-wrap items-center gap-1.5">
      <li className="text-[11px] tracking-wide text-ink-soft/70 uppercase">in</li>
      {sections.slice(0, MAX_TAGS).map((section) => (
        <li key={section.id}>
          <Link
            to="/objects/$objectId"
            params={{ objectId: section.id }}
            className="inline-flex rounded-full bg-willow/15 px-2.5 py-0.5 text-xs text-ink transition-colors hover:bg-willow/30"
          >
            <Latex>{section.latex}</Latex>
          </Link>
        </li>
      ))}
      {sections.length > MAX_TAGS && (
        <li className="text-xs text-ink-soft">+{sections.length - MAX_TAGS}</li>
      )}
    </ul>
  );
}
