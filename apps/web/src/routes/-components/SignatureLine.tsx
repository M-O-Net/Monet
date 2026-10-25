import { Link } from "@tanstack/react-router";

import { Latex } from "../../components/Latex";
import type { ObjectDetailOut, ObjectOut } from "../../lib/types";

function TypeLink({ type }: { type: ObjectOut }) {
  return (
    <Link
      to="/objects/$objectId"
      params={{ objectId: type.id }}
      className="rounded-full bg-willow/15 px-2.5 py-0.5 text-xs text-ink transition-colors hover:bg-willow/30"
    >
      <Latex>{type.latex}</Latex>
    </Link>
  );
}

export function SignatureLine({ signature }: { signature: ObjectDetailOut["signature"] }) {
  if (signature === null) return null;
  return (
    <p className="mt-2 flex flex-wrap items-center gap-2 text-sm text-ink-soft">
      <TypeLink type={signature.domain} />
      <span aria-label="to">→</span>
      <TypeLink type={signature.codomain} />
    </p>
  );
}
