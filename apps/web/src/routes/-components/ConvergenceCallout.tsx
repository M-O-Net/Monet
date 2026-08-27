import { Link } from "@tanstack/react-router";

import { Latex } from "../../components/Latex";
import { findConvergence } from "../../lib/convergence";
import { buildRelationHtml } from "../../lib/relationTemplate";
import type { RelationOut } from "../../lib/types";
import { Callout } from "./Callout";
import { RelationExpression } from "./RelationExpression";

const COUNTS = ["No", "One", "Two", "Three", "Four", "Five", "Six"];
const spell = (n: number) => COUNTS[n] ?? String(n);

export function ConvergenceCallout({
  asOutput,
  currentObjectId,
}: {
  asOutput: RelationOut[];
  currentObjectId: string;
}) {
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
      <ul className="space-y-3">
        {convergence.routes.map((route) => (
          <li key={route.operator.id}>
            <Link
              to="/objects/$objectId"
              params={{ objectId: route.operator.id }}
              className="relation-tag mb-1 inline-block rounded-sm px-2 py-0.5 text-xs"
            >
              <Latex>{route.operator.latex}</Latex>
            </Link>
            <ul className="space-y-1">
              {route.relations.map((relation) => (
                <li key={relation.id} className="text-sm">
                  <RelationExpression
                    html={buildRelationHtml(
                      relation,
                      relation.display?.template ?? null,
                      currentObjectId,
                    )}
                  />
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </Callout>
  );
}
