import type { SVGProps } from "react";

interface Point {
  x: number;
  y: number;
}

export function ArrowMarker({ id }: { id: string }) {
  return (
    <defs>
      <marker
        id={id}
        viewBox="0 0 8 8"
        refX="4"
        refY="4"
        markerWidth="7"
        markerHeight="7"
        orient="auto"
      >
        <path d="M 0 1 L 8 4 L 0 7 z" fill="currentColor" />
      </marker>
    </defs>
  );
}

export function DirectedEdge({
  tail,
  head,
  markerId,
  ...line
}: { tail: Point; head: Point; markerId: string } & SVGProps<SVGPolylineElement>) {
  const middle = { x: (tail.x + head.x) / 2, y: (tail.y + head.y) / 2 };
  const points = [tail, middle, head].map(({ x, y }) => `${String(x)},${String(y)}`).join(" ");
  return <polyline points={points} fill="none" markerMid={`url(#${markerId})`} {...line} />;
}
