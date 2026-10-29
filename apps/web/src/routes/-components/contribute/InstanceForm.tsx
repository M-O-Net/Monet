import { useState } from "react";

import { Latex } from "../../../components/Latex";
import { ObjectPicker } from "../../../components/ObjectPicker";
import { api } from "../../../lib/api";
import type { ObjectOut } from "../../../lib/types";
import { describe } from "../../../sandbox/client";
import type { SandboxValue } from "../../../sandbox/protocol";
import { ContributionError, Field, INPUT_CLASS, SUBMIT_CLASS } from "./fields";

export function InstanceForm({
  contributor,
  onCreated,
}: {
  contributor: string;
  onCreated: (id: string) => void;
}) {
  const createObject = api.useMutation("post", "/objects");
  const [type, setType] = useState<ObjectOut | null>(null);
  const [text, setText] = useState("");
  const [notationOnly, setNotationOnly] = useState(false);
  const [read, setRead] = useState<SandboxValue | null>(null);
  const [reading, setReading] = useState(false);
  const [readError, setReadError] = useState<string | null>(null);
  const [description, setDescription] = useState("");

  const readValue = () => {
    setReadError(null);
    setReading(true);
    describe(text.trim()).then(
      (value) => {
        setReading(false);
        setRead(value);
      },
      (failure: unknown) => {
        setReading(false);
        setRead(null);
        setReadError(failure instanceof Error ? failure.message : String(failure));
      },
    );
  };

  const ready = type !== null && (notationOnly ? text.trim() !== "" : read !== null);

  return (
    <form
      className="space-y-5"
      onSubmit={(event) => {
        event.preventDefault();
        if (type === null || !ready) return;
        createObject.mutate(
          {
            body: {
              latex: notationOnly || read === null ? text.trim() : read.latex,
              description: description.trim() || null,
              facets: [
                { type_id: type.id, data: notationOnly || read === null ? null : read.data },
              ],
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
      <Field label="Type" hint="What kind of object this is.">
        <ObjectPicker
          value={type}
          onChange={setType}
          filter={{ role: "type" }}
          placeholder="choose a type…"
        />
      </Field>

      <Field
        label="The object"
        hint={
          notationOnly
            ? "Recorded exactly as typed, in LaTeX. Without data it can't be matched or computed with."
            : "Type it the way you would in a calculator — x^2 - x + 1, Matrix([[2, 1], [1, 2]]), 17 — then read it."
        }
      >
        <div className="flex gap-2">
          <input
            value={text}
            onChange={(event) => {
              setText(event.target.value);
              setRead(null);
            }}
            className={INPUT_CLASS}
          />
          {!notationOnly && (
            <button
              type="button"
              disabled={reading || text.trim() === ""}
              onClick={readValue}
              className="rounded-sm border border-mist px-3 py-1.5 text-xs text-ink-soft hover:bg-paper-deep disabled:opacity-50"
            >
              {reading ? "Reading…" : "Read it"}
            </button>
          )}
        </div>
        <label className="mt-2 flex items-center gap-2 text-xs text-ink-soft">
          <input
            type="checkbox"
            checked={notationOnly}
            onChange={(event) => {
              setNotationOnly(event.target.checked);
              setRead(null);
            }}
          />
          the sandbox can't read this kind of object (a knot, say) — record its notation only
        </label>
        {read && (
          <p className="mt-2 text-sm text-ink">
            Read as <Latex>{read.latex}</Latex>
          </p>
        )}
        {readError && <p className="mt-2 text-xs text-rust">Could not read that: {readError}</p>}
      </Field>

      <Field label="Description" hint="Optional: why it is interesting, where it comes from.">
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
        Add this object
      </button>
    </form>
  );
}
