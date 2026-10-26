import { useState } from "react";

import { ObjectPicker } from "../../../components/ObjectPicker";
import { api } from "../../../lib/api";
import { textLatex } from "../../../lib/textLatex";
import type { ObjectOut } from "../../../lib/types";
import { ContributionError, Field, INPUT_CLASS, SUBMIT_CLASS } from "./fields";

export function TypeForm({
  types,
  contributor,
  onCreated,
}: {
  types: ObjectOut[];
  contributor: string;
  onCreated: (id: string) => void;
}) {
  const createObject = api.useMutation("post", "/objects");
  const [name, setName] = useState("");
  const [supertypeId, setSupertypeId] = useState("");
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
              subtype_of: [supertypeId],
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
