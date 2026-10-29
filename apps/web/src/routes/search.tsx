import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";

import { QueriedMemberList } from "../components/MemberList";
import { ObjectPicker } from "../components/ObjectPicker";
import { api } from "../lib/api";
import type { ObjectData } from "../lib/data";
import { asObjectId, type PropertyFilter, toQueryParams } from "../lib/searchQuery";
import type { ObjectOut } from "../lib/types";
import { useSettled } from "../lib/useSettled";
import { PropertyFilters } from "./-components/search/PropertyFilters";
import { ValueFilter } from "./-components/search/ValueFilter";

export const Route = createFileRoute("/search")({
  component: SearchPage,
});

const LABEL_CLASS = "mb-1.5 text-xs font-semibold tracking-wide text-ink-soft uppercase";
const TYPING_PAUSE_MS = 250;
const NOTE_CLASS = "text-sm text-ink-soft italic";

function SearchPage() {
  const [type, setType] = useState<ObjectOut | null>(null);
  const [includeSubtypes, setIncludeSubtypes] = useState(true);
  const [value, setValue] = useState<ObjectData | null>(null);
  const [ignoreVariable, setIgnoreVariable] = useState(false);
  const [properties, setProperties] = useState<PropertyFilter[]>([]);
  const [text, setText] = useState("");
  const settledText = useSettled(text, TYPING_PAUSE_MS);

  const pastedId = asObjectId(text);
  const params = toQueryParams({
    typeId: type?.id ?? "",
    includeSubtypes,
    value,
    ignoreVariable,
    properties,
    description: asObjectId(settledText) === null ? settledText : "",
  });
  const notation = asObjectId(settledText) === null ? settledText.trim() : "";

  const typeDetail = api.useQuery(
    "get",
    "/objects/{object_id}",
    { params: { path: { object_id: type?.id ?? "" } } },
    { enabled: type !== null },
  );
  const kinds = new Set(typeDetail.data?.as_type?.data_kinds ?? []);

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
                value={type}
                onChange={(picked) => {
                  setType(picked);
                  setValue(null);
                  setIgnoreVariable(false);
                }}
                filter={{ role: "type" }}
                placeholder="any type…"
              />
            </div>
            {type !== null && (
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
                    setType(null);
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
            key={type?.id ?? ""}
            kinds={kinds}
            ignoreVariable={ignoreVariable}
            onIgnoreVariableChange={setIgnoreVariable}
            onValue={setValue}
          />
        </div>

        <div>
          <p className={LABEL_CLASS}>Where</p>
          <PropertyFilters filters={properties} onChange={setProperties} />
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
        {params === null ? (
          <p className={NOTE_CLASS}>Choose a filter above to search.</p>
        ) : (
          <QueriedMemberList
            key={JSON.stringify(params)}
            title={(total) => `${String(total)} ${total === 1 ? "match" : "matches"}`}
            query={params}
            pending={<p className={NOTE_CLASS}>Searching…</p>}
            empty={<p className={NOTE_CLASS}>Nothing in the network matches.</p>}
          />
        )}

        {notation !== "" && (
          <div className="mt-6 opacity-80">
            <QueriedMemberList
              key={notation}
              title={() => "Notation that looks similar"}
              query={{ q: notation }}
            />
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
