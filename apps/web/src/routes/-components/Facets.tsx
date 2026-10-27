import { Link } from "@tanstack/react-router";
import { useState } from "react";

import { formatApiError } from "@monet/api-client";

import { Latex } from "../../components/Latex";
import { ObjectPicker } from "../../components/ObjectPicker";
import { api } from "../../lib/api";
import { primaryData } from "../../lib/data";
import type { ObjectDetailOut, ObjectOut } from "../../lib/types";

type Facet = ObjectDetailOut["facets"][number];

function kindOf(facet: Facet): string {
  return facet.data === null ? "no data" : (Object.keys(facet.data).at(0) ?? "no data");
}

export function Facets({
  objectId,
  facets,
  types,
  onChanged,
}: {
  objectId: string;
  facets: Facet[];
  types: ObjectOut[];
  onChanged: () => void;
}) {
  const setFacet = api.useMutation("put", "/objects/{object_id}/facets/{type_id}");
  const removeFacet = api.useMutation("delete", "/objects/{object_id}/facets/{type_id}");
  const [typeId, setTypeId] = useState("");
  const data = primaryData({ facets });
  const held = new Set(facets.map((facet) => facet.type.id));

  return (
    <section className="mb-7">
      <h2 className="mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase">
        An instance of
      </h2>
      {facets.length > 0 && (
        <ul className="mb-3 divide-y divide-mist rounded-sm border border-mist bg-white/40">
          {facets.map((facet) => (
            <li key={facet.type.id} className="px-4 py-2.5">
              <div className="flex items-baseline justify-between gap-3">
                <Link
                  to="/objects/$objectId"
                  params={{ objectId: facet.type.id }}
                  className="text-sm text-ink hover:text-pond"
                >
                  <Latex>{facet.type.latex}</Latex>
                </Link>
                <span className="flex items-baseline gap-3 text-[11px] text-ink-soft">
                  {kindOf(facet)}
                  <button
                    type="button"
                    onClick={() => {
                      removeFacet.mutate(
                        { params: { path: { object_id: objectId, type_id: facet.type.id } } },
                        { onSuccess: onChanged },
                      );
                    }}
                    className="hover:text-rust"
                    aria-label="Remove this type"
                  >
                    ×
                  </button>
                </span>
              </div>
              {facet.data !== null && (
                <details className="mt-1">
                  <summary className="cursor-pointer text-[11px] text-ink-soft">its data</summary>
                  <pre className="mt-1 overflow-x-auto text-[11px] text-ink-soft">
                    {JSON.stringify(facet.data)}
                  </pre>
                </details>
              )}
            </li>
          ))}
        </ul>
      )}
      <form
        className="flex flex-wrap items-center gap-2"
        onSubmit={(event) => {
          event.preventDefault();
          if (typeId === "") return;
          setFacet.mutate(
            { params: { path: { object_id: objectId, type_id: typeId } }, body: { data } },
            {
              onSuccess: () => {
                setTypeId("");
                onChanged();
              },
            },
          );
        }}
      >
        <div className="w-64">
          <ObjectPicker
            objects={types.filter((type) => !held.has(type.id))}
            value={typeId}
            onChange={setTypeId}
            placeholder="also an instance of…"
          />
        </div>
        <button
          type="submit"
          disabled={typeId === "" || setFacet.isPending}
          className="rounded-sm border border-mist px-2.5 py-1 text-xs text-ink-soft hover:bg-paper-deep disabled:opacity-50"
        >
          Add
        </button>
        {data !== null && (
          <span className="text-[11px] text-ink-soft">with the same data, read as that type</span>
        )}
      </form>
      {setFacet.isError && (
        <p className="mt-2 text-xs text-rust">{formatApiError(setFacet.error)}</p>
      )}
    </section>
  );
}
