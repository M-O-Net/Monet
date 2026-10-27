import { useState } from "react";

import { ObjectPicker } from "../../../components/ObjectPicker";
import { api } from "../../../lib/api";
import { textLatex } from "../../../lib/textLatex";
import type { ObjectOut } from "../../../lib/types";
import { ContributionError, Field, INPUT_CLASS, SUBMIT_CLASS } from "./fields";

const DATA_KINDS: { kind: string | null; label: string }[] = [
  { kind: "matrix", label: "matrices" },
  { kind: "poly", label: "polynomials" },
  { kind: "int", label: "integers" },
  { kind: "rational", label: "fractions" },
  { kind: "bool", label: "true or false" },
  { kind: "expr", label: "other exact expressions" },
  { kind: "knot", label: "knots" },
  { kind: null, label: "no fixed kind" },
];

export function TypeForm({
  types,
  sections,
  contributor,
  onCreated,
}: {
  types: ObjectOut[];
  sections: ObjectOut[];
  contributor: string;
  onCreated: (id: string) => void;
}) {
  const createObject = api.useMutation("post", "/objects");
  const [name, setName] = useState("");
  const [supertypeId, setSupertypeId] = useState("");
  const [dataKind, setDataKind] = useState<string | null>(null);
  const [sectionId, setSectionId] = useState("");
  const [description, setDescription] = useState("");

  const ready = name.trim() !== "" && supertypeId !== "";

  return (
    <form
      className="space-y-5"
      onSubmit={(event) => {
        event.preventDefault();
        if (!ready) return;
        createObject.mutate(
          {
            body: {
              latex: textLatex(name),
              description: description.trim() || null,
              as_type: { data_kind: dataKind, supertype_ids: [supertypeId] },
              sections: sectionId === "" ? [] : [sectionId],
              contributor,
            },
          },
          {
            onSuccess: (created) => {
              onCreated(created.id);
            },
          },
        );
      }}
    >
      <Field label="Name" hint="Plural, the way a heading reads: Upper Triangular Matrices.">
        <input
          value={name}
          onChange={(event) => {
            setName(event.target.value);
          }}
          className={INPUT_CLASS}
        />
      </Field>

      <Field
        label="A kind of"
        hint="Its supertype. Every instance of the new type is also an instance of this one; pick Mathematical Objects if nothing narrower fits."
      >
        <ObjectPicker
          objects={types}
          value={supertypeId}
          onChange={setSupertypeId}
          placeholder="choose a supertype…"
        />
      </Field>

      <Field
        label="Its instances are"
        hint="What kind of value each instance carries, so they can be read, searched and told apart."
      >
        <div className="flex flex-wrap gap-1.5">
          {DATA_KINDS.map((option) => (
            <button
              key={option.label}
              type="button"
              aria-pressed={dataKind === option.kind}
              onClick={() => {
                setDataKind(option.kind);
              }}
              className={`rounded-full px-3 py-1 text-xs ${
                dataKind === option.kind
                  ? "bg-pond text-paper"
                  : "bg-willow/15 text-ink hover:bg-willow/30"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </Field>

      <Field label="Show on the contents page under" hint="Optional.">
        <ObjectPicker
          objects={sections}
          value={sectionId}
          onChange={setSectionId}
          placeholder="no section…"
        />
      </Field>

      <Field label="Description" hint="Optional: what belongs to it.">
        <input
          value={description}
          onChange={(event) => {
            setDescription(event.target.value);
          }}
          className={INPUT_CLASS}
        />
      </Field>

      {createObject.isError && <ContributionError error={createObject.error} />}
      <button type="submit" disabled={!ready || createObject.isPending} className={SUBMIT_CLASS}>
        Add this type
      </button>
    </form>
  );
}
