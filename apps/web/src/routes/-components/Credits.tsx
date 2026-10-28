import { Fragment } from "react";

import { creditsHeading } from "../../lib/credits";
import type { ReferenceOut } from "../../lib/types";

export function Credits({ references }: { references: ReferenceOut[] }) {
  if (references.length === 0) return null;
  return (
    <p className="mt-1 text-[11px] text-ink-soft/80">
      {creditsHeading(references)}:{" "}
      {references.map((reference, index) => (
        <Fragment key={reference.url}>
          {index > 0 && ", "}
          <a
            href={reference.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-pond hover:text-pond-deep hover:underline"
          >
            {reference.label}
          </a>
        </Fragment>
      ))}
    </p>
  );
}
