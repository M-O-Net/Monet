import { Link } from "@tanstack/react-router";

import { Latex } from "../../components/Latex";
import type { SectionNode } from "../../lib/types";

const ROMAN_NUMERALS: [number, string][] = [
  [10, "X"],
  [9, "IX"],
  [5, "V"],
  [4, "IV"],
  [1, "I"],
];

function toRoman(n: number): string {
  let remaining = n;
  let result = "";
  for (const [value, numeral] of ROMAN_NUMERALS) {
    while (remaining >= value) {
      result += numeral;
      remaining -= value;
    }
  }
  return result;
}

// Standard outline notation: I, II, III / A, B, C / i, ii, iii. Roman numerals stay at the top
// level so the contents still reads as a journal's, and the lower two levels are subordinate
// without needing any extra chrome to say so. Three levels is a table of contents; more is a
// tree explorer, which is not what this page is for.
const MARKERS: ((index: number) => string)[] = [
  (index) => toRoman(index + 1),
  (index) => String.fromCharCode(65 + (index % 26)),
  (index) => toRoman(index + 1).toLowerCase(),
];

function TreeNode({
  node,
  index,
  depth,
  seen,
}: {
  node: SectionNode;
  index: number;
  depth: number;
  seen: ReadonlySet<string>;
}) {
  // The API already guards its walk, but membership relations are ordinary data and a cycle is
  // two clicks away in the relation form — a hung tab is not worth the five tokens saved.
  if (seen.has(node.id)) return null;
  const nextSeen = new Set(seen).add(node.id);
  const marker = MARKERS[depth] ?? MARKERS[0];
  const children = depth + 1 < MARKERS.length ? node.children : [];
  const hiddenInside = node.member_count - children.length;

  return (
    <li>
      {/* The row link and the child list are siblings, not nested: an anchor cannot contain
          another anchor, so the children cannot live inside the row's own <Link>. */}
      <Link
        to="/objects/$objectId"
        params={{ objectId: node.id }}
        className="group flex items-baseline gap-4 border-l-2 border-l-transparent pr-4 transition-colors hover:border-l-gold hover:bg-gold-soft/40"
        style={{ paddingLeft: `${String(1 + depth * 1.25)}rem` }}
      >
        <span className="font-display text-xs text-ink-soft/70 tabular-nums group-hover:text-gold">
          {marker(index)}
        </span>
        <span className="min-w-0 flex-1 py-3">
          <span
            className={
              depth === 0 ? "font-display text-base text-ink" : "font-display text-sm text-ink"
            }
          >
            <Latex>{node.latex}</Latex>
          </span>
          {node.description !== null && (
            <p className="mt-0.5 text-xs text-ink-soft">{node.description}</p>
          )}
          {hiddenInside > 0 && (
            <p className="mt-0.5 text-xs text-ink-soft/70">
              {hiddenInside} {hiddenInside === 1 ? "entry" : "entries"} inside
            </p>
          )}
        </span>
      </Link>
      {children.length > 0 && (
        <ul className="ml-6 border-l border-mist/70">
          {children.map((child, childIndex) => (
            <TreeNode
              key={child.id}
              node={child}
              index={childIndex}
              depth={depth + 1}
              seen={nextSeen}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

export function ContentsTree({ sections }: { sections: SectionNode[] }) {
  return (
    <ul className="divide-y divide-mist rounded-sm border border-mist bg-white/40 shadow-[0_1px_3px_rgba(35,50,43,0.06)]">
      {sections.map((section, index) => (
        <TreeNode key={section.id} node={section} index={index} depth={0} seen={new Set()} />
      ))}
    </ul>
  );
}
