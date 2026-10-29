import { useState } from "react";

import type { components } from "../../../client/schema";

type StorageStatsOut = components["schemas"]["StorageStatsOut"];
type StorageCategoryOut = components["schemas"]["StorageCategoryOut"];
type StorageCategory = StorageCategoryOut["category"];

const LOOK: Record<StorageCategory, { label: string; swatch: string; about: string }> = {
  instances: {
    label: "Instances",
    swatch: "bg-series-1",
    about: "objects, what each one is, references, contents page",
  },
  edges: { label: "Edges", swatch: "bg-series-2", about: "relations, their slots and credits" },
  maps: { label: "Maps", swatch: "bg-series-3", about: "implementations, signatures, displays" },
  types: { label: "Types", swatch: "bg-series-4", about: "types and subtypes" },
  activity: { label: "Comments & activity", swatch: "bg-series-5", about: "comments, the feed" },
  other: {
    label: "Other tables",
    swatch: "bg-series-6",
    about: "tables outside the categories above, such as migration history",
  },
  overhead: {
    label: "Postgres overhead",
    swatch: "bg-series-rest",
    about: "the database engine's own bookkeeping; roughly constant",
  },
};

const UNITS = ["B", "KB", "MB", "GB", "TB"];

function formatBytes(bytes: number): string {
  let value = bytes;
  let unit = 0;
  while (value >= 1024 && unit < UNITS.length - 1) {
    value /= 1024;
    unit += 1;
  }
  const digits = unit === 0 || value >= 100 ? 0 : 1;
  return `${value.toFixed(digits)} ${UNITS[unit] ?? ""}`;
}

function formatShare(share: number): string {
  if (share > 0 && share < 0.001) return "<0.1%";
  return `${(share * 100).toFixed(1)}%`;
}

export function StorageBreakdown({ stats }: { stats: StorageStatsOut }) {
  const [hovered, setHovered] = useState<StorageCategory | null>(null);
  const total = stats.database_bytes;
  const share = (category: StorageCategoryOut) => (total > 0 ? category.size_bytes / total : 0);
  const activeIndex = stats.categories.findIndex((c) => c.category === hovered);
  const active = activeIndex >= 0 ? stats.categories[activeIndex] : undefined;
  const activeStart = stats.categories
    .slice(0, Math.max(activeIndex, 0))
    .reduce((sum, c) => sum + share(c), 0);

  return (
    <div>
      <p className="text-5xl font-semibold text-ink">{formatBytes(total)}</p>
      <p className="mt-1 text-sm text-ink-soft">
        in all, measured at {new Date(stats.measured_at).toLocaleTimeString()} — re-measured at most
        once a minute.
      </p>

      <div className="relative mt-8">
        <div
          className="flex h-6 gap-0.5"
          role="img"
          aria-label={stats.categories
            .map((c) => `${LOOK[c.category].label} ${formatShare(share(c))}`)
            .join(", ")}
        >
          {stats.categories.map((category) => (
            <div
              key={category.category}
              className={`min-w-0.5 first:rounded-l last:rounded-r ${LOOK[category.category].swatch} ${
                hovered !== null && hovered !== category.category ? "opacity-50" : ""
              }`}
              style={{ flexGrow: category.size_bytes, flexBasis: 0 }}
              tabIndex={0}
              onPointerEnter={() => {
                setHovered(category.category);
              }}
              onPointerLeave={() => {
                setHovered(null);
              }}
              onFocus={() => {
                setHovered(category.category);
              }}
              onBlur={() => {
                setHovered(null);
              }}
            />
          ))}
        </div>
        {active && (
          <div
            className="pointer-events-none absolute bottom-8 rounded-sm border border-mist bg-paper px-3 py-2 text-sm whitespace-nowrap shadow-[0_1px_3px_rgba(35,50,43,0.12)]"
            style={{ left: `min(${(activeStart * 100).toFixed(2)}%, calc(100% - 16rem))` }}
          >
            <span className="font-semibold text-ink">{formatBytes(active.size_bytes)}</span>{" "}
            <span className="text-ink-soft">
              · {formatShare(share(active))} · {LOOK[active.category].label}
            </span>
          </div>
        )}
      </div>

      <ul className="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-xs text-ink-soft">
        {stats.categories.map((category) => (
          <li key={category.category} className="flex items-center gap-1.5">
            <span
              className={`inline-block size-2.5 rounded-sm ${LOOK[category.category].swatch}`}
            />
            {LOOK[category.category].label}
          </li>
        ))}
      </ul>

      <table className="mt-10 w-full text-sm">
        <thead>
          <tr className="border-b border-mist text-left text-xs text-ink-soft">
            <th className="py-2 font-medium">Category</th>
            <th className="py-2 text-right font-medium">Size</th>
            <th className="py-2 text-right font-medium">Share</th>
            <th className="py-2 text-right font-medium">Rows</th>
          </tr>
        </thead>
        <tbody className="tabular-nums">
          {stats.categories.map((category) => (
            <tr key={category.category} className="border-b border-mist/60 align-top">
              <td className="py-2">
                <span className="flex items-center gap-2 text-ink">
                  <span
                    className={`inline-block size-2.5 rounded-sm ${LOOK[category.category].swatch}`}
                  />
                  {LOOK[category.category].label}
                </span>
                <span className="block pl-4.5 text-xs text-ink-soft">
                  {LOOK[category.category].about}
                </span>
              </td>
              <td className="py-2 text-right text-ink">{formatBytes(category.size_bytes)}</td>
              <td className="py-2 text-right text-ink-soft">{formatShare(share(category))}</td>
              <td className="py-2 text-right text-ink-soft">
                {category.category === "overhead" ? "—" : `≈${category.rows.toLocaleString()}`}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <p className="mt-6 text-xs leading-relaxed text-ink-soft">
        Images are not stored in the database: an object keeps only a link to an image hosted
        elsewhere. About {stats.image_links.toLocaleString()} objects have one, and their links take
        about {formatBytes(stats.image_link_bytes)}, counted under Instances. Row counts are
        Postgres&apos;s own running estimates, not exact counts.
      </p>
    </div>
  );
}
