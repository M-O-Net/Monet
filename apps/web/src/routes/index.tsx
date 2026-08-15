import { useQueryClient } from "@tanstack/react-query";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import { formatApiError } from "@monet/api-client";

import { Latex } from "../components/Latex";
import { api } from "../lib/api";

export const Route = createFileRoute("/")({
  component: TopLevelObjectList,
});

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

function TopLevelObjectList() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const sections = api.useQuery("get", "/top-level-objects");
  const createObject = api.useMutation("post", "/objects");
  const [latex, setLatex] = useState("");
  const [description, setDescription] = useState("");

  const handleSubmit = (event: React.SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!latex.trim()) return;
    createObject.mutate(
      { body: { latex, description: description.trim() || null } },
      {
        onSuccess: (created) => {
          setLatex("");
          setDescription("");
          void queryClient.invalidateQueries({ queryKey: ["get", "/top-level-objects"] });
          void navigate({ to: "/objects/$objectId", params: { objectId: created.id } });
        },
      },
    );
  };

  return (
    <div>
      <h1 className="mb-1 font-display text-xl font-medium text-ink">Contents</h1>
      <p className="mb-5 text-sm text-ink-soft">
        Every specimen and operation catalogued so far, filed under one of the sections below.
      </p>

      <form onSubmit={handleSubmit} className="mb-8 space-y-2">
        <div className="flex gap-2">
          <input
            value={latex}
            onChange={(e) => {
              setLatex(e.target.value);
            }}
            placeholder="Describe a new specimen in LaTeX, e.g. x^2 - 4x + 3"
            className="flex-1 rounded-sm border border-mist bg-paper px-3 py-2 text-sm text-ink placeholder:text-ink-soft/60 focus:border-pond focus:outline-none"
          />
          <button
            type="submit"
            disabled={createObject.isPending}
            className="rounded-sm bg-pond px-4 py-2 text-sm font-medium text-paper transition-colors hover:bg-pond-deep disabled:opacity-50"
          >
            Add
          </button>
        </div>
        <input
          value={description}
          onChange={(e) => {
            setDescription(e.target.value);
          }}
          placeholder="Description (optional)"
          className="w-full rounded-sm border border-mist bg-paper px-3 py-1.5 text-xs text-ink placeholder:text-ink-soft/60 focus:border-pond focus:outline-none"
        />
      </form>
      {createObject.isError && (
        <p className="mb-4 text-sm text-rust">{formatApiError(createObject.error)}</p>
      )}

      {sections.isPending && <p className="text-sm text-ink-soft">Gathering sections…</p>}
      {sections.isError && <p className="text-sm text-rust">{formatApiError(sections.error)}</p>}

      <ul className="divide-y divide-mist rounded-sm border border-mist bg-white/40 shadow-[0_1px_3px_rgba(35,50,43,0.06)]">
        {sections.data?.map((obj, i) => (
          <li key={obj.id}>
            <Link
              to="/objects/$objectId"
              params={{ objectId: obj.id }}
              className="group flex items-baseline gap-4 border-l-2 border-l-transparent px-4 py-4 transition-colors hover:border-l-gold hover:bg-gold-soft/40"
            >
              <span className="font-display text-xs text-ink-soft/70 tabular-nums group-hover:text-gold">
                {toRoman(i + 1)}
              </span>
              <span className="min-w-0 flex-1">
                <span className="font-display text-base text-ink">
                  <Latex>{obj.latex}</Latex>
                </span>
                {obj.description && (
                  <p className="mt-0.5 text-xs text-ink-soft">{obj.description}</p>
                )}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
