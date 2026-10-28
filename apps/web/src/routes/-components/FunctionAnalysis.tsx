import { useQuery } from "@tanstack/react-query";

import type { ObjectData } from "../../lib/data";
import { formatNumber } from "../../lib/plot";
import { analyze } from "../../sandbox/client";
import { FunctionPlot } from "./FunctionPlot";
import { PolynomialRoots } from "./PolynomialRoots";

const heading = "mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase";

export function FunctionAnalysis({ latex, data }: { latex: string; data: ObjectData }) {
  const analysis = useQuery({
    queryKey: ["sandbox", "analyze", latex, JSON.stringify(data)],
    queryFn: () => analyze({ latex, data }),
    staleTime: Infinity,
    retry: false,
  });

  if (analysis.isPending) {
    return <p className="mb-7 text-sm text-ink-soft italic">Drawing its graph…</p>;
  }
  if (analysis.isError) {
    return (
      <p className="mb-7 text-xs text-rust">Could not draw its graph: {analysis.error.message}</p>
    );
  }
  const result = analysis.data;
  if (result === null) return null;
  const plottable = result.points.some(([, y]) => y !== null);

  return (
    <>
      {plottable && (
        <section className="mb-7">
          <h2 className={heading}>Graph</h2>
          <FunctionPlot analysis={result} />
          {result.complex_roots === null && result.real_roots.length > 0 && (
            <p className="mt-2 text-xs text-ink-soft">
              Crosses zero in view at {result.variable} ≈{" "}
              <span className="tabular-nums">
                {result.real_roots.map((root) => formatNumber(root.x)).join(", ")}
              </span>
            </p>
          )}
        </section>
      )}
      {result.complex_roots !== null && (
        <section className="mb-7">
          <h2 className={heading}>Roots</h2>
          <PolynomialRoots realRoots={result.real_roots} complexRoots={result.complex_roots} />
        </section>
      )}
    </>
  );
}
