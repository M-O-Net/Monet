import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";

import { formatApiError } from "@monet/api-client";

import { ObjectPicker } from "../components/ObjectPicker";
import { api } from "../lib/api";
import type { ObjectData } from "../lib/data";
import { searchObjects } from "../lib/search";
import { asObjectId, dataKinds, type PropertyFilter, toQueryParams } from "../lib/searchQuery";
import { MemberList } from "./-components/MemberList";
import { PropertyFilters } from "./-components/search/PropertyFilters";
import { ValueFilter } from "./-components/search/ValueFilter";

export const Route = createFileRoute("/search")({
  component: SearchPage,
});

const LABEL_CLASS = "mb-1.5 text-xs font-semibold tracking-wide text-ink-soft uppercase";
const NOTATION_MATCH_LIMIT = 8;

function SearchPage() {
  const types = api.useQuery("get", "/types");
  const allObjects = api.useQuery("get", "/objects");

  const [typeId, setTypeId] = useState("");
  const [includeSubtypes, setIncludeSubtypes] = useState(true);
  const [value, setValue] = useState<ObjectData | null>(null);
  const [ignoreVariable, setIgnoreVariable] = useState(false);
  const [properties, setProperties] = useState<PropertyFilter[]>([]);
  const [text, setText] = useState("");

  const pastedId = asObjectId(text);
  const params = toQueryParams({
    typeId,
    includeSubtypes,
    value,
    ignoreVariable,
    properties,
    description: pastedId === null ? text : "",
  });

  const instances = api.useQuery(
    "get",
    "/objects/query",
    { params: { query: { member_of: typeId } } },
    { enabled: typeId !== "" },
  );
  const results = api.useQuery(
    "get",
    "/objects/query",
    { params: { query: params ?? {} } },
    { enabled: params !== null },
  );

  const kinds = useMemo(
    () => dataKinds((instances.data ?? []).map((instance) => instance.data)),
    [instances.data],
  );
  const notationMatches = useMemo(
    () =>
      text.trim() === "" || pastedId !== null
        ? []
        : searchObjects(allObjects.data ?? [], text, NOTATION_MATCH_LIMIT),
    [allObjects.data, text, pastedId],
  );

  return (
    <div>
      <h1 className="font-display text-2xl text-ink">Search</h1>
      <p className="mt-1 mb-6 text-sm text-ink-soft">
        Narrow down by what an object is and what is known about it. Each filter is optional; they
        combine.
      </p>

      <div className="space-y-5 rounded-sm border border-mist bg-white/40 p-4 shadow-[0_1px_3px_rgba(35,50,43,0.06)]">
        <div>
          <p className={LABEL_CLASS}>Of type</p>
          <div className="flex items-center gap-3">
            <div className="flex-1">
              <ObjectPicker
                objects={types.data ?? []}
                value={typeId}
                onChange={(id) => {
                  setTypeId(id);
                  setValue(null);
                  setIgnoreVariable(false);
                }}
                placeholder="any type…"
              />
            </div>
            {typeId !== "" && (
              <>
                <label className="flex items-center gap-1.5 text-xs text-ink-soft">
                  <input
                    type="checkbox"
                    checked={includeSubtypes}
                    onChange={(event) => {
                      setIncludeSubtypes(event.target.checked);
                    }}
                  />
                  and its subtypes
                </label>
                <button
                  type="button"
                  onClick={() => {
                    setTypeId("");
                    setValue(null);
                  }}
                  className="text-xs text-ink-soft hover:text-rust"
                >
                  clear
                </button>
              </>
            )}
          </div>
        </div>

        <div>
          <p className={LABEL_CLASS}>Equal to</p>
          <ValueFilter
            key={typeId}
            kinds={kinds}
            ignoreVariable={ignoreVariable}
            onIgnoreVariableChange={setIgnoreVariable}
            onValue={setValue}
          />
        </div>

        <div>
          <p className={LABEL_CLASS}>Where</p>
          <PropertyFilters
            filters={properties}
            objects={allObjects.data ?? []}
            onChange={setProperties}
          />
        </div>

        <div>
          <p className={LABEL_CLASS}>Description mentions</p>
          <input
            value={text}
            onChange={(event) => {
              setText(event.target.value);
            }}
            placeholder="words from its description, or paste an object id"
            className="w-full rounded-sm border border-mist bg-paper px-3 py-1.5 text-sm text-ink placeholder:text-ink-soft/60 focus:border-pond focus:outline-none"
          />
          {pastedId !== null && (
            <p className="mt-2 text-sm">
              <Link
                to="/objects/$objectId"
                params={{ objectId: pastedId }}
                className="text-pond underline underline-offset-2"
              >
                Open object {pastedId} →
              </Link>
            </p>
          )}
        </div>
      </div>

      <div className="mt-8">
        {params === null && (
          <p className="text-sm text-ink-soft italic">Choose a filter above to search.</p>
        )}
        {results.isError && <p className="text-sm text-rust">{formatApiError(results.error)}</p>}
        {params !== null && results.isPending && (
          <p className="text-sm text-ink-soft italic">Searching…</p>
        )}
        {params !== null && results.data?.length === 0 && (
          <p className="text-sm text-ink-soft italic">Nothing in the network matches.</p>
        )}
        {params !== null && results.data && (
          <MemberList
            title={`${String(results.data.length)} ${results.data.length === 1 ? "match" : "matches"}`}
            members={results.data}
          />
        )}

        {notationMatches.length > 0 && (
          <div className="mt-6 opacity-80">
            <MemberList title="Notation that looks similar" members={notationMatches} />
            <p className="-mt-5 text-xs text-ink-soft">
              A last resort: this compares how objects are written, not what they are, so it can
              miss an object written another way and show one that only looks alike.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
