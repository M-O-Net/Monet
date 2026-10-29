import { Link } from "@tanstack/react-router";

import { Latex } from "../../components/Latex";
import { findConvergence } from "../../lib/convergence";
import type { RelationGroupOut } from "../../lib/types";
import { Callout } from "./Callout";

const COUNTS = ["No", "One", "Two", "Three", "Four", "Five", "Six"];
const spell = (n: number) => COUNTS[n] ?? String(n);

export function ConvergenceCallout({ asOutput }: { asOutput: RelationGroupOut[] }) {
  const convergence = findConvergence(asOutput);
  if (convergence === null) return null;

  const many = convergence.distinctOperators >= 2;

  return (
    <Callout heading={many ? "Several routes arrive here" : "Reached more than one way"}>
      <p className="mb-3 text-sm text-ink-soft">
        {many
          ? `${spell(convergence.distinctOperators)} different operations produce this object.`
          : "The same operation produces this object from more than one starting point."}
      </p>
      <ul className="flex flex-wrap gap-1.5">
        {convergence.routes.map((route) => (
          <li key={route.operator.id}>
            <Link
              to="/objects/$objectId"
              params={{ objectId: route.operator.id }}
              className="relation-tag inline-flex items-baseline gap-1.5 rounded-sm px-2 py-0.5 text-xs"
            >
              <Latex>{route.operator.latex}</Latex>
              {route.total > 1 && <span className="text-ink-soft">×{route.total}</span>}
            </Link>
          </li>
        ))}
      </ul>
      <p className="mt-3 text-xs text-ink-soft">Each one is written out below.</p>
    </Callout>
  );
}
