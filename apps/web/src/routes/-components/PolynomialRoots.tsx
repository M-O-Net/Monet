import { useState } from "react";

import { Latex } from "../../components/Latex";
import { complexExtent, formatComplex, ticks } from "../../lib/plot";
import type { ComplexRoot, RealRoot } from "../../sandbox/protocol";

const SIZE = 220;
const MARGIN = 18;
const PLANE = SIZE - MARGIN * 2;

const sameText = (a: string, b: string) => a.replace(/\s/g, "") === b.replace(/\s/g, "");

export function PolynomialRoots({
  realRoots,
  complexRoots,
}: {
  realRoots: RealRoot[];
  complexRoots: ComplexRoot[];
}) {
  const roots: ComplexRoot[] = [
    ...realRoots.map(({ x, latex, multiplicity }) => ({ re: x, im: 0, latex, multiplicity })),
    ...[...complexRoots].sort((a, b) => a.re - b.re || a.im - b.im),
  ];
  const [hovered, setHovered] = useState<number | null>(null);
  const extent = complexExtent(roots);
  const gridTicks = ticks([-extent, extent], 4);
  const s = (value: number) => MARGIN + ((value + extent) / (2 * extent)) * PLANE;
  const flip = (value: number) => SIZE - s(value);
  const degree = roots.reduce((total, root) => total + root.multiplicity, 0);
  const realCount = realRoots.reduce((total, root) => total + root.multiplicity, 0);

  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
      <svg
        viewBox={`0 0 ${String(SIZE)} ${String(SIZE)}`}
        className="block w-56 shrink-0"
        role="img"
        aria-label="The roots plotted in the complex plane"
      >
        <g className="stroke-mist" strokeWidth={1}>
          {gridTicks.map((t) => (
            <g key={t}>
              <line x1={s(t)} x2={s(t)} y1={MARGIN} y2={SIZE - MARGIN} />
              <line x1={MARGIN} x2={SIZE - MARGIN} y1={flip(t)} y2={flip(t)} />
            </g>
          ))}
        </g>
        <g className="stroke-ink-soft" strokeWidth={1} opacity={0.7}>
          <line x1={MARGIN} x2={SIZE - MARGIN} y1={flip(0)} y2={flip(0)} />
          <line x1={s(0)} x2={s(0)} y1={MARGIN} y2={SIZE - MARGIN} />
        </g>
        <g className="fill-ink-soft text-[9px] tabular-nums">
          <text x={SIZE - MARGIN} y={flip(0) - 4} textAnchor="end" className="italic">
            Re
          </text>
          <text x={s(0) + 4} y={MARGIN + 8} className="italic">
            Im
          </text>
          <text x={SIZE - MARGIN} y={flip(0) + 11} textAnchor="end">
            {extent}
          </text>
          <text x={s(0) - 4} y={MARGIN + 8} textAnchor="end">
            {extent}i
          </text>
        </g>
        {roots.map((root, index) => (
          <g
            key={`${String(root.re)}:${String(root.im)}`}
            onPointerEnter={() => {
              setHovered(index);
            }}
            onPointerLeave={() => {
              setHovered(null);
            }}
          >
            <title>{formatComplex(root.re, root.im)}</title>
            <circle cx={s(root.re)} cy={flip(root.im)} r={12} fill="transparent" />
            <circle
              cx={s(root.re)}
              cy={flip(root.im)}
              r={hovered === index ? 6 : 4.5}
              className="fill-root stroke-paper"
              strokeWidth={2}
            />
            {root.multiplicity > 1 && (
              <text x={s(root.re) + 8} y={flip(root.im) - 6} className="fill-ink-soft text-[10px]">
                ×{root.multiplicity}
              </text>
            )}
          </g>
        ))}
      </svg>

      <div className="min-w-0 flex-1">
        <p className="mb-2 text-xs text-ink-soft">
          {degree} {degree === 1 ? "root" : "roots"} counted with multiplicity
          {" · "}
          {realCount === 0 ? "none" : realCount} real
        </p>
        <ul className="space-y-1">
          {roots.map((root, index) => (
            <li
              key={`${String(root.re)}:${String(root.im)}`}
              onPointerEnter={() => {
                setHovered(index);
              }}
              onPointerLeave={() => {
                setHovered(null);
              }}
              className={[
                "flex items-baseline gap-2 rounded-sm px-1.5 py-0.5 text-sm",
                hovered === index ? "bg-gold-soft/60" : "",
              ].join(" ")}
            >
              <span className="inline-block size-2 shrink-0 rounded-full bg-root" />
              <span className="min-w-0 overflow-x-auto text-ink">
                <Latex>{root.latex ?? `\\approx ${formatComplex(root.re, root.im)}`}</Latex>
              </span>
              {root.latex !== null && !sameText(root.latex, formatComplex(root.re, root.im)) && (
                <span className="text-xs text-ink-soft tabular-nums">
                  ≈ {formatComplex(root.re, root.im)}
                </span>
              )}
              {root.multiplicity > 1 && (
                <span className="text-xs text-ink-soft">multiplicity {root.multiplicity}</span>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
