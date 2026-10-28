import { useId, useMemo, useRef, useState, type KeyboardEvent, type PointerEvent } from "react";

import { curveSegments, formatNumber, ticks, yWindow } from "../../lib/plot";
import type { Analysis } from "../../sandbox/protocol";

const WIDTH = 560;
const HEIGHT = 300;
const LEFT = 44;
const RIGHT = 28;
const TOP = 12;
const BOTTOM = 26;
const PLOT_WIDTH = WIDTH - LEFT - RIGHT;
const PLOT_HEIGHT = HEIGHT - TOP - BOTTOM;
const KEY_STEP = 4;

export function FunctionPlot({ analysis }: { analysis: Analysis }) {
  const { points, variable } = analysis;
  const [x0, x1] = analysis.window;
  const yRange = useMemo(() => yWindow(points), [points]);
  const segments = useMemo(() => curveSegments(points, yRange), [points, yRange]);
  const [y0, y1] = yRange;
  const clipId = useId();
  const svg = useRef<SVGSVGElement | null>(null);
  const [hovered, setHovered] = useState<number | null>(null);

  const sx = (x: number) => LEFT + ((x - x0) / (x1 - x0)) * PLOT_WIDTH;
  const sy = (y: number) => TOP + ((y1 - y) / (y1 - y0)) * PLOT_HEIGHT;
  const path = (segment: [number, number][]) =>
    segment
      .map(([x, y], i) => `${i === 0 ? "M" : "L"}${sx(x).toFixed(2)},${sy(y).toFixed(2)}`)
      .join("");

  const xTicks = ticks([x0, x1], 6);
  const yTicks = ticks([y0, y1], 5);
  const axisVisible = y0 <= 0 && 0 <= y1;
  const visibleRoots = axisVisible ? analysis.real_roots.filter(({ x }) => x0 <= x && x <= x1) : [];

  const nearest = (x: number) => {
    let best = 0;
    for (let i = 1; i < points.length; i += 1) {
      if (Math.abs(points[i][0] - x) < Math.abs(points[best][0] - x)) best = i;
    }
    return best;
  };

  const onPointerMove = (event: PointerEvent<SVGSVGElement>) => {
    const box = svg.current?.getBoundingClientRect();
    if (box === undefined || box.width === 0) return;
    const viewX = ((event.clientX - box.left) / box.width) * WIDTH;
    setHovered(nearest(x0 + ((viewX - LEFT) / PLOT_WIDTH) * (x1 - x0)));
  };

  const onKeyDown = (event: KeyboardEvent<SVGSVGElement>) => {
    const direction = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
    if (direction === 0) return;
    event.preventDefault();
    setHovered((current) => {
      const start = current ?? Math.floor(points.length / 2);
      return Math.min(points.length - 1, Math.max(0, start + direction * KEY_STEP));
    });
  };

  const hover = hovered === null ? undefined : points.at(hovered);
  const hoverY = hover?.[1] ?? null;
  const hoverOnLeft = hover !== undefined && sx(hover[0]) > LEFT + PLOT_WIDTH / 2;

  return (
    <svg
      ref={svg}
      viewBox={`0 0 ${String(WIDTH)} ${String(HEIGHT)}`}
      className="block h-auto w-full max-w-xl touch-none outline-none focus-visible:ring-1 focus-visible:ring-pond"
      role="img"
      aria-label={`Graph of y = f(${variable}) for ${variable} from ${formatNumber(x0)} to ${formatNumber(x1)}`}
      tabIndex={0}
      onPointerMove={onPointerMove}
      onPointerLeave={() => {
        setHovered(null);
      }}
      onKeyDown={onKeyDown}
      onBlur={() => {
        setHovered(null);
      }}
    >
      <defs>
        <clipPath id={clipId}>
          <rect x={LEFT} y={TOP} width={PLOT_WIDTH} height={PLOT_HEIGHT} />
        </clipPath>
      </defs>

      <g className="stroke-mist" strokeWidth={1}>
        {xTicks.map((t) => (
          <line key={`x${String(t)}`} x1={sx(t)} x2={sx(t)} y1={TOP} y2={TOP + PLOT_HEIGHT} />
        ))}
        {yTicks.map((t) => (
          <line key={`y${String(t)}`} x1={LEFT} x2={LEFT + PLOT_WIDTH} y1={sy(t)} y2={sy(t)} />
        ))}
      </g>

      <g className="stroke-ink-soft" strokeWidth={1} opacity={0.7}>
        {axisVisible && <line x1={LEFT} x2={LEFT + PLOT_WIDTH} y1={sy(0)} y2={sy(0)} />}
        {x0 <= 0 && 0 <= x1 && <line x1={sx(0)} x2={sx(0)} y1={TOP} y2={TOP + PLOT_HEIGHT} />}
      </g>

      <g className="fill-ink-soft text-[10px] tabular-nums">
        {xTicks.map((t) => (
          <text key={`x${String(t)}`} x={sx(t)} y={HEIGHT - 8} textAnchor="middle">
            {formatNumber(t)}
          </text>
        ))}
        {yTicks.map((t) => (
          <text key={`y${String(t)}`} x={LEFT - 6} y={sy(t) + 3} textAnchor="end">
            {formatNumber(t)}
          </text>
        ))}
        <text x={WIDTH - 2} y={HEIGHT - 8} textAnchor="end" className="italic">
          {variable}
        </text>
      </g>

      <g clipPath={`url(#${clipId})`}>
        {segments.map((segment) => (
          <path
            key={segment[0][0]}
            d={path(segment)}
            fill="none"
            className="stroke-curve"
            strokeWidth={2}
            strokeLinejoin="round"
            strokeLinecap="round"
          />
        ))}
      </g>

      {visibleRoots.map((root) => (
        <g key={root.x}>
          <circle
            cx={sx(root.x)}
            cy={sy(0)}
            r={4.5}
            className="fill-root stroke-paper"
            strokeWidth={2}
          />
          {root.multiplicity > 1 && (
            <text
              x={sx(root.x)}
              y={sy(0) - 9}
              textAnchor="middle"
              className="fill-ink-soft text-[10px]"
            >
              ×{root.multiplicity}
            </text>
          )}
        </g>
      ))}

      {hover !== undefined && (
        <g pointerEvents="none">
          <line
            x1={sx(hover[0])}
            x2={sx(hover[0])}
            y1={TOP}
            y2={TOP + PLOT_HEIGHT}
            className="stroke-ink-soft"
            strokeWidth={1}
            opacity={0.5}
          />
          {hoverY !== null && y0 <= hoverY && hoverY <= y1 && (
            <circle
              cx={sx(hover[0])}
              cy={sy(hoverY)}
              r={4}
              className="fill-curve stroke-paper"
              strokeWidth={2}
            />
          )}
          <g
            transform={`translate(${String(hoverOnLeft ? LEFT + 8 : LEFT + PLOT_WIDTH - 128)}, ${String(TOP + 6)})`}
          >
            <rect width={120} height={36} rx={2} className="fill-paper stroke-mist" />
            <text x={8} y={15} className="fill-ink text-[11px] font-semibold tabular-nums">
              y = {hoverY === null ? "undefined" : formatNumber(hoverY)}
            </text>
            <text x={8} y={29} className="fill-ink-soft text-[10px] tabular-nums">
              {variable} = {formatNumber(hover[0])}
            </text>
          </g>
        </g>
      )}
    </svg>
  );
}
