import { useState } from "react";

import { ObjectPicker } from "../../../components/ObjectPicker";
import { api } from "../../../lib/api";
import { textLatex } from "../../../lib/textLatex";
import type { ObjectOut } from "../../../lib/types";
import { ContributionError, Field, INPUT_CLASS, SUBMIT_CLASS } from "./fields";

export function MapForm({
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
  const [domainId, setDomainId] = useState("");
  const [codomainId, setCodomainId] = useState("");
  const [description, setDescription] = useState("");

  const ready = name.trim() !== "" && domainId !== "" && codomainId !== "";

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
              signatures: [{ domain_id: domainId, codomain_id: codomainId }],
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
      <Field
        label="Name"
        hint="Singular, the way the operation is spoken: Trace, Generating Function."
      >
        <input
          value={name}
          onChange={(event) => {
            setName(event.target.value);
          }}
          className={INPUT_CLASS}
        />
      </Field>

      <div className="grid grid-cols-[1fr_auto_1fr] items-end gap-3">
        <Field label="From">
          <ObjectPicker
            objects={types}
            value={domainId}
            onChange={setDomainId}
            placeholder="domain…"
          />
        </Field>
        <span className="pb-1.5 text-ink-soft">→</span>
        <Field label="To">
          <ObjectPicker
            objects={types}
            value={codomainId}
            onChange={setCodomainId}
            placeholder="codomain…"
          />
        </Field>
      </div>

      <Field label="Description" hint="Optional: its definition, in words.">
        <input
          value={description}
          onChange={(event) => {
            setDescription(event.target.value);
          }}
          className={INPUT_CLASS}
        />
      </Field>

      <p className="text-xs text-ink-soft">
        Once it exists, its page lets you write the sympy that computes it.
      </p>
      {createObject.isError && <ContributionError error={createObject.error} />}
      <button type="submit" disabled={!ready || createObject.isPending} className={SUBMIT_CLASS}>
        Add this map
      </button>
    </form>
  );
}
