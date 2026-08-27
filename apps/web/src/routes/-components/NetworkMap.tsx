import { Link } from "@tanstack/react-router";
import { useEffect, useMemo, useRef, useState } from "react";

import { Latex } from "../../components/Latex";
import { layoutBounds, layoutGraph, nodeLabel } from "../../lib/graphLayout";
import { buildGraph, neighbourhood } from "../../lib/graphModel";
import type { RelationOut } from "../../lib/types";

const PADDING = 48;
const MIN_SCALE = 0.2;
const MAX_SCALE = 3;
const WHEEL_SENSITIVITY = 0.0015;

interface View {
  x: number;
  y: number;
  scale: number;
}

export function NetworkMap({
  relations,
  focusId,
}: {
  relations: RelationOut[];
  focusId: string | null;
}) {
  const graph = useMemo(() => buildGraph(relations), [relations]);
  const layout = useMemo(() => layoutGraph(graph), [graph]);
  const bounds = useMemo(() => layoutBounds(graph, layout), [graph, layout]);

  const width = bounds.maxX - bounds.minX + PADDING * 2;
  const height = bounds.maxY - bounds.minY + PADDING * 2;
  const originX = PADDING - bounds.minX;
  const originY = PADDING - bounds.minY;

  const frame = useRef<HTMLDivElement | null>(null);
  const [view, setView] = useState<View | null>(null);
  const [hovered, setHovered] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const dragging = useRef<{ x: number; y: number; view: View } | null>(null);

  const fit = useMemo(() => {
    return (box: DOMRect): View => {
      const scale = Math.max(MIN_SCALE, Math.min(1, box.width / width, box.height / height));
      const target = focusId === null ? undefined : layout.get(focusId);
      const centreX = target === undefined ? width / 2 : target.x + originX;
      const centreY = target === undefined ? height / 2 : target.y + originY;
      return {
        scale,
        x: box.width / 2 - centreX * scale,
        y: box.height / 2 - centreY * scale,
      };
    };
  }, [width, height, originX, originY, focusId, layout]);

  useEffect(() => {
    const element = frame.current;
    if (element === null) return;
    setView(fit(element.getBoundingClientRect()));
  }, [fit]);

  const highlighted = useMemo(() => {
    const anchor = hovered ?? selected ?? focusId;
    return anchor === null ? null : neighbourhood(graph, anchor);
  }, [graph, hovered, selected, focusId]);

  const dim = (id: string) => highlighted !== null && !highlighted.has(id);
  const transform =
    view === null
      ? undefined
      : `translate(${String(view.x)}px, ${String(view.y)}px) scale(${String(view.scale)})`;

  return (
    <div
      ref={frame}
      className="relative h-[70vh] cursor-grab touch-none overflow-hidden rounded-sm border border-mist bg-white/30 active:cursor-grabbing"
      onWheel={(event) => {
        setView((current) => {
          if (current === null) return current;
          const next = current.scale * Math.exp(-event.deltaY * WHEEL_SENSITIVITY);
          const scale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, next));
          const box = frame.current?.getBoundingClientRect();
          if (box === undefined) return { ...current, scale };
          const pointerX = event.clientX - box.left;
          const pointerY = event.clientY - box.top;
          const ratio = scale / current.scale;
          return {
            scale,
            x: pointerX - (pointerX - current.x) * ratio,
            y: pointerY - (pointerY - current.y) * ratio,
          };
        });
      }}
      onPointerDown={(event) => {
        if (event.button !== 0 || view === null) return;
        if ((event.target as HTMLElement).closest("a") !== null) return;
        dragging.current = { x: event.clientX, y: event.clientY, view };
        event.currentTarget.setPointerCapture(event.pointerId);
      }}
      onPointerMove={(event) => {
        const start = dragging.current;
        if (start === null) return;
        setView({
          ...start.view,
          x: start.view.x + (event.clientX - start.x),
          y: start.view.y + (event.clientY - start.y),
        });
      }}
      onPointerUp={() => {
        dragging.current = null;
      }}
    >
      <svg
        className="pointer-events-none absolute top-0 left-0 text-pond"
        style={{ transform, transformOrigin: "0 0" }}
        width={width}
        height={height}
      >
        <defs>
          <marker
            id="map-arrow"
            viewBox="0 0 8 8"
            refX="7"
            refY="4"
            markerWidth="5"
            markerHeight="5"
            orient="auto-start-reverse"
          >
            <path d="M 0 1 L 7 4 L 0 7 z" fill="currentColor" />
          </marker>
        </defs>
        {graph.edges.map((edge) => {
          const from = layout.get(edge.source);
          const to = layout.get(edge.target);
          if (from === undefined || to === undefined) return null;
          const faded = dim(edge.source) && dim(edge.target);
          return (
            <line
              key={edge.id}
              x1={from.x + originX}
              y1={from.y + originY}
              x2={to.x + originX}
              y2={to.y + originY}
              stroke="currentColor"
              strokeWidth={1}
              markerEnd="url(#map-arrow)"
              opacity={faded ? 0.2 : 0.6}
            />
          );
        })}
      </svg>

      <div
        className="absolute top-0 left-0"
        style={{ transform, transformOrigin: "0 0", width, height }}
      >
        {graph.nodes.map((node) => {
          const point = layout.get(node.id);
          if (point === undefined) return null;
          const isRelation = node.kind === "relation";
          const objectId = isRelation ? node.relation.operator.id : node.object.id;
          const isSelected = node.id === selected;
          return (
            <div
              key={node.id}
              className="absolute -translate-x-1/2 -translate-y-1/2"
              style={{ left: point.x + originX, top: point.y + originY, zIndex: isSelected ? 2 : 1 }}
            >
              <button
                type="button"
                onMouseEnter={() => {
                  setHovered(node.id);
                }}
                onMouseLeave={() => {
                  setHovered(null);
                }}
                onClick={(event) => {
                  event.stopPropagation();
                  setSelected(isSelected ? null : node.id);
                }}
                className={[
                  "flex items-center justify-center rounded-sm border whitespace-nowrap transition-all",
                  isRelation
                    ? "border-gold/40 bg-gold-soft text-ink-soft"
                    : "border-mist bg-paper text-ink shadow-[0_1px_3px_rgba(35,50,43,0.08)]",
                  isSelected
                    ? "border-pond px-3 py-1.5 text-sm shadow-[0_2px_8px_rgba(35,50,43,0.18)]"
                    : isRelation
                      ? "px-1.5 py-0.5 text-[0.6rem]"
                      : "px-2 py-1 text-xs",
                  node.id === focusId ? "is-current border-pond" : "",
                  dim(node.id) && !isSelected ? "opacity-30" : "",
                ].join(" ")}
              >
                <Latex>{nodeLabel(node)}</Latex>
              </button>
              {isSelected && (
                <div className="absolute top-full left-1/2 mt-1.5 flex -translate-x-1/2 gap-1 whitespace-nowrap">
                  <Link
                    to="/map"
                    search={{ focus: objectId }}
                    className="rounded-sm border border-mist bg-paper px-2 py-0.5 text-[0.65rem] text-ink-soft shadow-sm hover:bg-gold-soft/60"
                  >
                    centre here
                  </Link>
                  <Link
                    to="/objects/$objectId"
                    params={{ objectId }}
                    className="rounded-sm border border-pond bg-pond px-2 py-0.5 text-[0.65rem] text-paper shadow-sm hover:bg-pond-deep"
                  >
                    open →
                  </Link>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <button
        onClick={() => {
          const box = frame.current?.getBoundingClientRect();
          if (box !== undefined) setView(fit(box));
        }}
        className="absolute right-3 bottom-3 rounded-sm border border-mist bg-paper px-2 py-1 text-xs text-ink-soft hover:bg-gold-soft/40"
      >
        Reset view
      </button>
    </div>
  );
}
