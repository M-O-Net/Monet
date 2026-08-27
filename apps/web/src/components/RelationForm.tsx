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
  selected,
  onChange,
}: {
  label: string;
  selected: ObjectSummary[];
  onChange: (objects: ObjectSummary[]) => void;
}) {
  const [pending, setPending] = useState<ObjectSummary | null>(null);

  return (
    <div>
      <p className="mb-1.5 text-xs font-semibold tracking-wide text-ink-soft uppercase">{label}</p>
      <div className="mb-1.5 flex flex-wrap gap-1.5">
        {selected.map((obj, index) => {
          return (
            <span
              key={`${obj.id}-${String(index)}`}
              className="flex items-center gap-1.5 rounded-full bg-willow/15 px-2.5 py-0.5 text-xs text-ink"
            >
              <Latex>{obj.latex}</Latex>
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
          <ObjectPicker value={pending} onChange={setPending} placeholder="Select an object…" />
        </div>
        <button
          type="button"
          disabled={!pending}
          onClick={() => {
            if (pending) onChange([...selected, pending]);
            setPending(null);
          }}
          className="rounded-sm border border-mist px-2.5 py-1 text-xs text-ink-soft hover:bg-paper-deep disabled:opacity-50"
        >
          Add
        </button>
      </div>
    </div>
  );
}

export function RelationForm({ onCreated }: { onCreated: () => void }) {
  const [operator, setOperator] = useState<ObjectSummary | null>(null);
  const [inputs, setInputs] = useState<ObjectSummary[]>([]);
  const [outputs, setOutputs] = useState<ObjectSummary[]>([]);
  const createRelation = api.useMutation("post", "/relations");

  const canSubmit = operator && inputs.length > 0 && outputs.length > 0;

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!canSubmit) return;
        createRelation.mutate(
          {
            body: {
              operator_id: operator.id,
              input_object_ids: inputs.map((obj) => obj.id),
              output_object_ids: outputs.map((obj) => obj.id),
            },
          },
          {
            onSuccess: () => {
              setOperator(null);
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
        <ObjectPicker value={operator} onChange={setOperator} placeholder="Select an operator…" />
      </div>

      <SlotPicker label="Inputs (ordered)" selected={inputs} onChange={setInputs} />
      <SlotPicker label="Outputs (ordered)" selected={outputs} onChange={setOutputs} />

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
