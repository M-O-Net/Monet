import { Link } from "@tanstack/react-router";
import { useMemo } from "react";

import { Latex } from "../../components/Latex";
import { api } from "../../lib/api";
import { layoutBounds, layoutGraph, nodeLabel } from "../../lib/graphLayout";
import { buildGraph } from "../../lib/graphModel";
import { hiddenByOperator } from "../../lib/neighborhood";
import type { RelationOut } from "../../lib/types";

const BOX_WIDTH = 288;
const BOX_HEIGHT = 208;
const PADDING = 12;
const PER_MAP = 3;

export function NeighborhoodMap({ objectId }: { objectId: string }) {
  const neighborhood = api.useQuery("get", "/objects/{object_id}/neighborhood", {
    params: { path: { object_id: objectId }, query: { per_map: PER_MAP } },
  });

  if (!neighborhood.data || neighborhood.data.relations.length === 0) return null;
  const notes = hiddenByOperator(neighborhood.data.hidden);

  return (
    <figure className="mt-2 w-72 shrink-0">
      <MiniMap relations={neighborhood.data.relations} focusId={objectId} />
      <figcaption className="mt-1.5 space-y-0.5 text-[0.7rem] text-ink-soft">
        {notes.map(({ operator, count }) => (
          <p key={operator.id}>
            +{count} more via{" "}
            <Link
              to="/objects/$objectId"
              params={{ objectId: operator.id }}
              className="hover:text-pond"
            >
              <Latex>{operator.latex}</Latex>
            </Link>
          </p>
        ))}
        <p>
          <Link
            to="/map"
            search={{ focus: objectId }}
            className="underline decoration-dotted underline-offset-2 hover:text-pond"
          >
            see it on the network map →
          </Link>
        </p>
      </figcaption>
    </figure>
  );
}

function MiniMap({ relations, focusId }: { relations: RelationOut[]; focusId: string }) {
  const graph = useMemo(() => buildGraph(relations), [relations]);
  const layout = useMemo(() => layoutGraph(graph), [graph]);
  const bounds = useMemo(() => layoutBounds(graph, layout), [graph, layout]);

  const width = bounds.maxX - bounds.minX + PADDING * 2;
  const height = bounds.maxY - bounds.minY + PADDING * 2;
  const scale = Math.min(1, BOX_WIDTH / width, BOX_HEIGHT / height);
  const offsetX = (BOX_WIDTH - width * scale) / 2;
  const offsetY = (BOX_HEIGHT - height * scale) / 2;
  const place = (point: { x: number; y: number }) => ({
    x: offsetX + (point.x + PADDING - bounds.minX) * scale,
    y: offsetY + (point.y + PADDING - bounds.minY) * scale,
  });

  return (
    <div
      className="relative overflow-hidden rounded-sm border border-mist bg-white/30"
      style={{ width: BOX_WIDTH, height: BOX_HEIGHT }}
    >
      <svg
        className="pointer-events-none absolute top-0 left-0 text-pond"
        width={BOX_WIDTH}
        height={BOX_HEIGHT}
        aria-hidden="true"
      >
        {graph.edges.map((edge) => {
          const source = layout.get(edge.source);
          const target = layout.get(edge.target);
          if (source === undefined || target === undefined) return null;
          const from = place(source);
          const to = place(target);
          return (
            <line
              key={edge.id}
              x1={from.x}
              y1={from.y}
              x2={to.x}
              y2={to.y}
              stroke="currentColor"
              strokeWidth={1}
              opacity={0.5}
            />
          );
        })}
      </svg>
      <div className="absolute inset-0">
        {graph.nodes.map((node) => {
          const point = layout.get(node.id);
          if (point === undefined) return null;
          const { x, y } = place(point);
          const isRelation = node.kind === "relation";
          const objectId = isRelation ? node.relation.operator.id : node.object.id;
          return (
            <Link
              key={node.id}
              to="/objects/$objectId"
              params={{ objectId }}
              className={[
                "absolute flex items-center justify-center rounded-sm border whitespace-nowrap",
                isRelation
                  ? "border-gold/40 bg-gold-soft px-1.5 py-0.5 text-[0.6rem] text-ink-soft"
                  : "border-mist bg-paper px-2 py-1 text-xs text-ink",
                node.id === focusId ? "border-pond! text-pond" : "hover:border-pond",
              ].join(" ")}
              style={{
                left: x,
                top: y,
                transform: `translate(-50%, -50%) scale(${String(scale)})`,
              }}
            >
              <Latex>{nodeLabel(node)}</Latex>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
