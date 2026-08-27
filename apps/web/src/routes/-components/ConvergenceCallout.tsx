import { Link } from "@tanstack/react-router";

import { Latex } from "../../components/Latex";
import { findConvergence } from "../../lib/convergence";
import type { RelationOut } from "../../lib/types";
import { Callout } from "./Callout";

const COUNTS = ["No", "One", "Two", "Three", "Four", "Five", "Six"];
const spell = (n: number) => COUNTS[n] ?? String(n);

export function ConvergenceCallout({
  asOutput,
  total,
}: {
  asOutput: RelationOut[];
  total: number;
}) {
  const convergence = findConvergence(asOutput);
  if (convergence === null) return null;

  const many = convergence.distinctOperators >= 2;
  const partial = total > asOutput.length;
  const count = partial
    ? `at least ${String(convergence.distinctOperators)}`
    : spell(convergence.distinctOperators).toLowerCase();

  return (
    <Callout heading={many ? "Several routes arrive here" : "Reached more than one way"}>
      <p className="mb-3 text-sm text-ink-soft">
        {many
          ? `${count[0].toUpperCase()}${count.slice(1)} different operations produce this object.`
          : "The same operation produces this object from more than one starting point."}
      </p>
      {partial && (
        <p className="mb-3 text-xs text-ink-soft">
          Showing {asOutput.length} of {total} relations that produce this object.
        </p>
      )}
      <ul className="flex flex-wrap gap-1.5">
        {convergence.routes.map((route) => (
          <li key={route.operator.id}>
            <Link
              to="/objects/$objectId"
              params={{ objectId: route.operator.id }}
              className="relation-tag inline-block rounded-sm px-2 py-0.5 text-xs"
            >
              <Latex>{route.operator.latex}</Latex>
            </Link>
          </li>
        ))}
      </ul>
      <p className="mt-3 text-xs text-ink-soft">Each one is written out below.</p>
    </Callout>
  );
}
