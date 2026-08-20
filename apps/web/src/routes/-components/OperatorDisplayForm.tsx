import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { formatApiError } from "@monet/api-client";

import { api } from "../../lib/api";
import { invalidateObjectGraph } from "../../lib/queries";
import { buildTemplateHtml } from "../../lib/relationTemplate";
import type { RelationOut } from "../../lib/types";
import { RelationExpression } from "./RelationExpression";

function placeholdersFor(relation: RelationOut): string[] {
  return [
    ...relation.inputs.map((_slot, i) => `{in${String(i)}}`),
    ...relation.outputs.map((_slot, i) => `{out${String(i)}}`),
    // Wraps whatever notation stands for this operator, making it a link to the operator the
    // same way the operands link to theirs.
    "\\op{}",
  ];
}

function Editor({ operatorId, sample }: { operatorId: string; sample: RelationOut }) {
  const queryClient = useQueryClient();
  const display = api.useQuery("get", "/operator-displays/{operator_id}", {
    params: { path: { operator_id: operatorId } },
  });
  const save = api.useMutation("put", "/operator-displays/{operator_id}");

  const [draft, setDraft] = useState<string | null>(null);
  const [hiddenDraft, setHiddenDraft] = useState<boolean | null>(null);

  if (display.isPending) return <p className="text-xs text-ink-soft">Loading…</p>;
  if (display.isError) return <p className="text-xs text-rust">{formatApiError(display.error)}</p>;

  const template = draft ?? display.data.template ?? "";
  const hidden = hiddenDraft ?? display.data.hidden_by_default;
  // The preview runs the very function the relation rows run, so it cannot promise something
  // the page will not deliver.
  const renders = template.trim() === "" || buildTemplateHtml(template, sample) !== null;

  return (
    <form
      className="space-y-3 rounded-sm border border-mist bg-white/40 p-4 shadow-[0_1px_3px_rgba(35,50,43,0.06)]"
      onSubmit={(event) => {
        event.preventDefault();
        save.mutate(
          {
            params: { path: { operator_id: operatorId } },
            body: {
              template: template.trim() === "" ? null : template,
              hidden_by_default: hidden,
              is_membership: display.data.is_membership,
            },
          },
          {
            onSuccess: () => {
              setDraft(null);
              setHiddenDraft(null);
              invalidateObjectGraph(queryClient);
            },
          },
        );
      }}
    >
      <div>
        <p className="mb-1.5 text-xs font-semibold tracking-wide text-ink-soft uppercase">
          Template
        </p>
        <input
          value={template}
          onChange={(event) => {
            setDraft(event.target.value);
          }}
          placeholder="Leave empty for the plain arrow row"
          className="w-full rounded-sm border border-mist bg-paper px-2 py-1.5 font-mono text-xs text-ink placeholder:text-ink-soft/60 focus:border-pond focus:outline-none"
        />
        <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
          <span className="text-[11px] text-ink-soft/70">insert</span>
          {placeholdersFor(sample).map((placeholder) => (
            <button
              key={placeholder}
              type="button"
              onClick={() => {
                setDraft(template + placeholder);
              }}
              className="rounded-sm border border-mist px-1.5 py-0.5 font-mono text-[11px] text-ink-soft hover:bg-paper-deep"
            >
              {placeholder}
            </button>
          ))}
        </div>
      </div>

      <div>
        <p className="mb-1.5 text-xs font-semibold tracking-wide text-ink-soft uppercase">
          Preview
        </p>
        {template.trim() === "" ? (
          <p className="text-xs text-ink-soft italic">No template — rows keep the plain layout.</p>
        ) : renders ? (
          <div className="text-sm">
            <RelationExpression relation={sample} template={template} />
          </div>
        ) : (
          <p className="text-xs text-rust">
            Doesn&apos;t render against this relation. Every input and output has to appear at least
            once, and the LaTeX has to parse.
          </p>
        )}
      </div>

      <label className="flex items-center gap-2 text-xs text-ink-soft">
        <input
          type="checkbox"
          checked={hidden}
          onChange={(event) => {
            setHiddenDraft(event.target.checked);
          }}
        />
        Collapse these rows behind a “show more” disclosure on other objects&apos; pages
      </label>

      {save.isError && <p className="text-xs text-rust">{formatApiError(save.error)}</p>}

      <button
        type="submit"
        disabled={!renders || save.isPending}
        className="rounded-sm bg-pond px-3 py-1.5 text-xs font-medium text-paper hover:bg-pond-deep disabled:opacity-50"
      >
        Save display
      </button>
    </form>
  );
}

/**
 * Editor for how this operator's relations render. Only shown for objects actually used as an
 * operator — there is nothing to configure otherwise, and no real relation to preview against.
 * Mounted only once opened, so the extra request is not paid on every object page.
 */
export function OperatorDisplayForm({
  operatorId,
  sample,
}: {
  operatorId: string;
  sample: RelationOut;
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="mt-8">
      <button
        type="button"
        onClick={() => {
          setOpen(!open);
        }}
        className="mb-2 flex items-center gap-1.5 text-xs font-semibold tracking-wide text-ink-soft uppercase hover:text-pond"
      >
        <span aria-hidden>{open ? "−" : "+"}</span>
        Display as operator
      </button>
      {open && <Editor operatorId={operatorId} sample={sample} />}
    </div>
  );
}
