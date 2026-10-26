import { Link } from "@tanstack/react-router";
import type { ReactNode } from "react";

import { formatApiError } from "@monet/api-client";

export const INPUT_CLASS =
  "w-full rounded-sm border border-mist bg-paper px-3 py-1.5 text-sm text-ink placeholder:text-ink-soft/60 focus:border-pond focus:outline-none";
export const SUBMIT_CLASS =
  "rounded-sm bg-pond px-4 py-2 text-sm font-medium text-paper transition-colors hover:bg-pond-deep disabled:opacity-50";

export function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <div>
      <p className="mb-1.5 text-xs font-semibold tracking-wide text-ink-soft uppercase">{label}</p>
      {children}
      {hint && <p className="mt-1 text-xs text-ink-soft">{hint}</p>}
    </div>
  );
}

const HELD_BY = /object ([0-9a-f-]{36}) already holds this data/;

export function ContributionError({ error }: { error: unknown }) {
  const message = formatApiError(error);
  const existing = HELD_BY.exec(message)?.[1];
  if (existing !== undefined) {
    return (
      <p className="text-sm text-rust">
        This is already in the network.{" "}
        <Link
          to="/objects/$objectId"
          params={{ objectId: existing }}
          className="underline underline-offset-2"
        >
          Open it →
        </Link>
      </p>
    );
  }
  return <p className="text-sm text-rust">{message}</p>;
}
