import { useState } from "react";

import { formatApiError } from "@monet/api-client";

import { api } from "../lib/api";
import { Latex } from "./Latex";
import { ObjectPicker } from "./ObjectPicker";

interface ObjectSummary {
  id: string;
  latex: string;
  description?: string | null;
}

function SlotPicker({
  label,
  objects,
  selected,
  onChange,
}: {
  label: string;
  objects: ObjectSummary[];
  selected: string[];
  onChange: (ids: string[]) => void;
}) {
  const [pending, setPending] = useState("");

  return (
    <div>
      <p className="mb-1.5 text-xs font-semibold tracking-wide text-ink-soft uppercase">{label}</p>
      <div className="mb-1.5 flex flex-wrap gap-1.5">
        {selected.map((id, index) => {
          const obj = objects.find((o) => o.id === id);
          return (
            <span
              key={`${id}-${String(index)}`}
              className="flex items-center gap-1.5 rounded-full bg-willow/15 px-2.5 py-0.5 text-xs text-ink"
            >
              <Latex>{obj?.latex ?? id}</Latex>
              <button
                type="button"
                onClick={() => {
                  onChange(selected.filter((_, i) => i !== index));
                }}
                className="text-ink-soft hover:text-rust"
                aria-label="Remove"
              >
                ×
              </button>
            </span>
          );
        })}
      </div>
      <div className="flex gap-2">
        <div className="flex-1">
          <ObjectPicker
            objects={objects}
            value={pending}
            onChange={setPending}
            placeholder="Select an object…"
          />
        </div>
        <button
          type="button"
          disabled={!pending}
          onClick={() => {
            onChange([...selected, pending]);
            setPending("");
          }}
          className="rounded-sm border border-mist px-2.5 py-1 text-xs text-ink-soft hover:bg-paper-deep disabled:opacity-50"
        >
          Add
        </button>
      </div>
    </div>
  );
}

export function RelationForm({
  objects,
  onCreated,
}: {
  objects: ObjectSummary[];
  onCreated: () => void;
}) {
  const [operatorId, setOperatorId] = useState("");
  const [inputs, setInputs] = useState<string[]>([]);
  const [outputs, setOutputs] = useState<string[]>([]);
  const createRelation = api.useMutation("post", "/relations");

  const canSubmit = operatorId && inputs.length > 0 && outputs.length > 0;

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!canSubmit) return;
        createRelation.mutate(
          {
            body: {
              operator_id: operatorId,
              input_object_ids: inputs,
              output_object_ids: outputs,
            },
          },
          {
            onSuccess: () => {
              setOperatorId("");
              setInputs([]);
              setOutputs([]);
              onCreated();
            },
          },
        );
      }}
      className="space-y-4 rounded-sm border border-mist bg-white/40 p-4 shadow-[0_1px_3px_rgba(35,50,43,0.06)]"
    >
      <div>
        <p className="mb-1.5 text-xs font-semibold tracking-wide text-ink-soft uppercase">
          Operator
        </p>
        <ObjectPicker
          objects={objects}
          value={operatorId}
          onChange={setOperatorId}
          placeholder="Select an operator…"
        />
      </div>

      <SlotPicker
        label="Inputs (ordered)"
        objects={objects}
        selected={inputs}
        onChange={setInputs}
      />
      <SlotPicker
        label="Outputs (ordered)"
        objects={objects}
        selected={outputs}
        onChange={setOutputs}
      />

      {createRelation.isError && (
        <p className="text-xs text-rust">{formatApiError(createRelation.error)}</p>
      )}

      <button
        type="submit"
        disabled={!canSubmit || createRelation.isPending}
        className="rounded-sm bg-pond px-3 py-1.5 text-xs font-medium text-paper hover:bg-pond-deep disabled:opacity-50"
      >
        Create relation
      </button>
    </form>
  );
}
