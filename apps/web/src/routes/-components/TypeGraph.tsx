import { Link } from "@tanstack/react-router";
import { useLayoutEffect, useRef, useState } from "react";

import { Latex } from "../../components/Latex";
import type { SectionTypeOut } from "../../lib/types";
import { typeFamilies } from "../../lib/typeLayers";

interface Edge {
  from: string;
  to: string;
  path: string;
}

function edgePath(container: DOMRect, above: DOMRect, below: DOMRect): string {
  const x1 = above.left + above.width / 2 - container.left;
  const y1 = above.bottom - container.top;
  const x2 = below.left + below.width / 2 - container.left;
  const y2 = below.top - container.top;
  const bend = (y2 - y1) / 2;
  return `M ${String(x1)} ${String(y1)} C ${String(x1)} ${String(y1 + bend)}, ${String(x2)} ${String(y2 - bend)}, ${String(x2)} ${String(y2)}`;
}

function TypeNode({
  type,
  highlighted,
  onHover,
  register,
}: {
  type: SectionTypeOut;
  highlighted: boolean;
  onHover: (id: string | null) => void;
  register: (id: string, element: HTMLElement | null) => void;
}) {
  return (
    <li
      ref={(element) => {
        register(type.id, element);
      }}
      onMouseEnter={() => {
        onHover(type.id);
      }}
      onMouseLeave={() => {
        onHover(null);
      }}
      className={`relative shrink-0 rounded-sm border bg-paper px-2.5 py-1.5 text-center shadow-[0_1px_3px_rgba(35,50,43,0.06)] transition-colors ${highlighted ? "border-pond" : "border-mist"}`}
    >
      <Link
        to="/objects/$objectId"
        params={{ objectId: type.id }}
        className="block text-[13px] whitespace-nowrap text-ink hover:text-pond"
      >
        <Latex>{type.latex}</Latex>
      </Link>
      <p className="mt-0.5 text-[11px] text-ink-soft tabular-nums">
        {type.instance_count} {type.instance_count === 1 ? "instance" : "instances"}
      </p>
      {type.elsewhere.length > 0 && (
        <p className="mt-1 text-[11px] text-ink-soft">
          also a kind of{" "}
          {type.elsewhere.map((supertype, index) => (
            <span key={supertype.id}>
              {index > 0 && ", "}
              <Link
                to="/objects/$objectId"
                params={{ objectId: supertype.id }}
                className="text-pond hover:text-pond-deep"
              >
                <Latex>{supertype.latex}</Latex>
              </Link>
            </span>
          ))}
        </p>
      )}
    </li>
  );
}

export function TypeGraph({ types }: { types: SectionTypeOut[] }) {
  const scroller = useRef<HTMLDivElement>(null);
  const container = useRef<HTMLDivElement>(null);
  const elements = useRef(new Map<string, HTMLElement>());
  const [edges, setEdges] = useState<Edge[]>([]);
  const [hovered, setHovered] = useState<string | null>(null);
  const families = typeFamilies(types);

  useLayoutEffect(() => {
    const frame = container.current;
    if (frame === null) return;
    const measure = () => {
      const box = frame.getBoundingClientRect();
      setEdges(
        types.flatMap((type) =>
          type.supertype_ids.flatMap((supertypeId) => {
            const above = elements.current.get(supertypeId);
            const below = elements.current.get(type.id);
            if (above === undefined || below === undefined) return [];
            return [
              {
                from: supertypeId,
                to: type.id,
                path: edgePath(box, above.getBoundingClientRect(), below.getBoundingClientRect()),
              },
            ];
          }),
        ),
      );
    };
    measure();
    const view = scroller.current;
    if (view !== null) view.scrollLeft = (view.scrollWidth - view.clientWidth) / 2;
    const observer = new ResizeObserver(measure);
    observer.observe(frame);
    for (const element of elements.current.values()) observer.observe(element);
    return () => {
      observer.disconnect();
    };
  }, [types]);

  const touching = (edge: Edge) =>
    hovered !== null && (edge.from === hovered || edge.to === hovered);
  const neighbours = new Set(edges.filter(touching).flatMap((edge) => [edge.from, edge.to]));

  return (
    <div
      ref={scroller}
      className="overflow-x-auto rounded-sm border border-mist bg-white/40 px-3 py-5"
    >
      <div ref={container} className="relative mx-auto w-max min-w-full">
        <svg
          className="pointer-events-none absolute inset-0 h-full w-full overflow-visible"
          aria-hidden
        >
          {[...edges]
            .sort((a, b) => Number(touching(a)) - Number(touching(b)))
            .map((edge) => (
              <path
                key={`${edge.from}:${edge.to}`}
                d={edge.path}
                fill="none"
                strokeWidth={touching(edge) ? 1.75 : 1.25}
                className={touching(edge) ? "stroke-pond" : "stroke-ink-soft/35"}
              />
            ))}
        </svg>
        <div className="relative flex flex-col gap-12">
          {families.map((layers, familyIndex) => (
            <div key={familyIndex} className="flex flex-col gap-8">
              {layers.map((layer, index) => (
                <ul key={index} className="flex items-start justify-center gap-x-3">
                  {layer.map((type) => (
                    <TypeNode
                      key={type.id}
                      type={type}
                      highlighted={type.id === hovered || neighbours.has(type.id)}
                      onHover={setHovered}
                      register={(id, element) => {
                        if (element === null) elements.current.delete(id);
                        else elements.current.set(id, element);
                      }}
                    />
                  ))}
                </ul>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
