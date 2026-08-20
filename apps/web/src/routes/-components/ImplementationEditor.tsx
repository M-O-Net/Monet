import { Popover } from "@base-ui/react/popover";
import { python } from "@codemirror/lang-python";
import { redo, undo } from "@codemirror/commands";
import CodeMirror, { type ReactCodeMirrorRef } from "@uiw/react-codemirror";
import { useRef, useState } from "react";

import { formatApiError } from "@monet/api-client";

import { Latex } from "../../components/Latex";
import { monetEditorTheme } from "../../components/editorTheme";
import { api } from "../../lib/api";
import { probe, run } from "../../sandbox/client";

interface Implementation {
  id: string;
  code: string;
  operator: { id: string; latex: string };
}

const STARTER_CODE = `def accepts(x):
    """Can this object be an input to me?"""
    return isinstance(x, MatrixBase)


def compute(a):
    """Return what this operator produces. Sympy in, sympy out."""
    return a.T
`;

export function ImplementationEditor({
  object,
  implementations,
  onChanged,
}: {
  object: { id: string; latex: string };
  implementations: Implementation[];
  onChanged: () => void;
}) {
  const createImplementation = api.useMutation("post", "/implementations");
  const mine = implementations.filter((i) => i.operator.id === object.id);

  const writeOne = () => {
    createImplementation.mutate(
      { body: { operator_id: object.id, code: STARTER_CODE } },
      { onSuccess: onChanged },
    );
  };

  return (
    <section className="mt-8">
      <h2 className="mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase">
        {mine.length > 1 ? "Implementations" : "Implementation"}
      </h2>

      {mine.length === 0 ? (
        <p className="text-sm text-ink-soft italic">
          Nothing computes this yet.{" "}
          <button
            onClick={writeOne}
            disabled={createImplementation.isPending}
            className="text-pond not-italic hover:underline disabled:opacity-50"
          >
            Write the sympy for it
          </button>
          .
        </p>
      ) : (
        <div className="space-y-4">
          {mine.map((implementation) => (
            <ImplementationForm
              key={implementation.id}
              implementation={implementation}
              onChanged={onChanged}
            />
          ))}
          <button
            onClick={writeOne}
            disabled={createImplementation.isPending}
            className="text-xs text-ink-soft hover:text-pond disabled:opacity-50"
          >
            + another implementation
          </button>
        </div>
      )}
      {createImplementation.isError && (
        <p className="mt-2 text-xs text-rust">{formatApiError(createImplementation.error)}</p>
      )}
    </section>
  );
}

const TOOL_BUTTON =
  "inline-flex h-6 w-6 items-center justify-center rounded-sm text-ink-soft transition-colors hover:bg-gold-soft/60 hover:text-ink";

const ICON = {
  width: 14,
  height: 14,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
} as const;

function UndoIcon() {
  return (
    <svg {...ICON} aria-hidden>
      <path d="M3 7v6h6" />
      <path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13" />
    </svg>
  );
}

function RedoIcon() {
  return (
    <svg {...ICON} aria-hidden>
      <path d="M21 7v6h-6" />
      <path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3L21 13" />
    </svg>
  );
}

function RevertIcon() {
  return (
    <svg {...ICON} aria-hidden>
      <path d="M3 3v6h6" />
      <path d="M3.5 13a9 9 0 1 0 2.6-6.4L3 9" />
    </svg>
  );
}

function TrashIcon() {
  return (
    <svg {...ICON} aria-hidden>
      <path d="M3 6h18" />
      <path d="M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2" />
      <path d="M19 6v14a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V6" />
      <path d="M10 11v6M14 11v6" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg {...ICON} aria-hidden>
      <path d="M20 6 9 17l-5-5" />
    </svg>
  );
}

function ConfirmPopover({
  icon,
  label,
  question,
  confirmLabel,
  onConfirm,
  disabled,
}: {
  icon: React.ReactNode;
  label: string;
  question: string;
  confirmLabel: string;
  onConfirm: () => void;
  disabled?: boolean;
}) {
  const [open, setOpen] = useState(false);
  return (
    <Popover.Root open={open} onOpenChange={setOpen}>
      <Popover.Trigger
        disabled={disabled}
        title={label}
        aria-label={label}
        className={`${TOOL_BUTTON} disabled:opacity-40 disabled:hover:bg-transparent`}
      >
        {icon}
      </Popover.Trigger>
      <Popover.Portal>
        <Popover.Positioner sideOffset={6} align="end" className="z-20 outline-none">
          <Popover.Popup className="w-60 rounded-sm border border-mist bg-paper p-3 shadow-[0_6px_20px_rgba(35,50,43,0.16)] outline-none">
            <Popover.Description className="text-xs text-ink">{question}</Popover.Description>
            <div className="mt-3 flex justify-end gap-2">
              <Popover.Close className="rounded-sm px-2 py-1 text-xs text-ink-soft transition-colors hover:bg-paper-deep hover:text-ink">
                Keep it
              </Popover.Close>
              <button
                onClick={() => {
                  setOpen(false);
                  onConfirm();
                }}
                className="rounded-sm bg-rust px-3 py-1 text-xs font-medium text-paper transition-colors hover:bg-rust/85"
              >
                {confirmLabel}
              </button>
            </div>
          </Popover.Popup>
        </Popover.Positioner>
      </Popover.Portal>
    </Popover.Root>
  );
}

function ImplementationForm({
  implementation,
  onChanged,
}: {
  implementation: Implementation;
  onChanged: () => void;
}) {
  const updateImplementation = api.useMutation("patch", "/implementations/{implementation_id}");
  const deleteImplementation = api.useMutation("delete", "/implementations/{implementation_id}");

  const editor = useRef<ReactCodeMirrorRef>(null);
  const [code, setCode] = useState(implementation.code);
  const [sample, setSample] = useState("");
  const [scratch, setScratch] = useState<{ applies: boolean; outputs: string[] } | null>(null);
  const [scratchError, setScratchError] = useState<string | null>(null);
  const [testing, setTesting] = useState(false);

  const dirty = code !== implementation.code;

  const history = (command: typeof undo) => () => {
    const view = editor.current?.view;
    if (view) {
      command(view);
      view.focus();
    }
  };

  const save = () => {
    updateImplementation.mutate(
      {
        params: { path: { implementation_id: implementation.id } },
        body: { operator_id: implementation.operator.id, code },
      },
      { onSuccess: onChanged },
    );
  };

  const test = () => {
    setTesting(true);
    setScratch(null);
    setScratchError(null);
    const inputs = sample.split("\n").filter((line) => line.trim() !== "");
    Promise.all([probe(inputs[0] ?? "", [{ id: "draft", code }]), run(code, inputs)]).then(
      ([applicable, outputs]) => {
        setTesting(false);
        setScratch({ applies: applicable.includes("draft"), outputs });
      },
      (error: unknown) => {
        setTesting(false);
        setScratchError(error instanceof Error ? error.message : String(error));
      },
    );
  };

  return (
    <div className="overflow-hidden rounded-sm border border-mist bg-white/40 shadow-[0_1px_3px_rgba(35,50,43,0.06)]">
      <div className="flex items-center gap-2 border-b border-mist bg-paper-deep/50 px-3 py-1.5">
        <div className="flex items-center gap-0.5">
          <button
            onClick={history(undo)}
            className={TOOL_BUTTON}
            title="Undo (⌘Z)"
            aria-label="Undo"
          >
            <UndoIcon />
          </button>
          <button
            onClick={history(redo)}
            className={TOOL_BUTTON}
            title="Redo (⇧⌘Z)"
            aria-label="Redo"
          >
            <RedoIcon />
          </button>
        </div>

        <span className="flex-1 text-[11px] text-ink-soft">
          {dirty ? "unsaved changes" : "saved"}
        </span>

        <ConfirmPopover
          icon={<TrashIcon />}
          label="Delete this implementation"
          question="Delete this implementation? The operator keeps its relations, but nothing will compute it."
          confirmLabel="Delete"
          onConfirm={() => {
            deleteImplementation.mutate(
              { params: { path: { implementation_id: implementation.id } } },
              { onSuccess: onChanged },
            );
          }}
        />
        <ConfirmPopover
          icon={<RevertIcon />}
          label="Discard changes"
          question="Discard your unsaved changes and go back to the saved code?"
          confirmLabel="Discard"
          disabled={!dirty}
          onConfirm={() => {
            setCode(implementation.code);
          }}
        />
        <button
          onClick={save}
          disabled={!dirty || updateImplementation.isPending}
          className="inline-flex items-center gap-1.5 rounded-sm bg-pond px-3 py-1 text-xs font-medium text-paper transition-colors hover:bg-pond-deep disabled:opacity-40 disabled:hover:bg-pond"
        >
          <CheckIcon />
          Save
        </button>
      </div>

      {updateImplementation.isError && (
        <p className="border-b border-mist px-3 py-2 text-xs text-rust">
          {formatApiError(updateImplementation.error)}
        </p>
      )}

      <CodeMirror
        ref={editor}
        value={code}
        minHeight="200px"
        theme={monetEditorTheme}
        extensions={[python()]}
        onChange={setCode}
        basicSetup={{
          foldGutter: false,
          highlightActiveLine: false,
          highlightActiveLineGutter: false,
        }}
      />

      <p className="border-t border-mist px-3 py-2 text-[11px] leading-relaxed text-ink-soft">
        Define <code className="font-mono text-ink">accepts(x)</code> and{" "}
        <code className="font-mono text-ink">compute(*inputs)</code> — both take sympy objects and{" "}
        <code className="font-mono text-ink">compute</code> returns sympy, so Monet handles the
        LaTeX at both ends. All of sympy is in scope. Take as many inputs as suit you and raise if
        they don&rsquo;t; nothing records an arity.
      </p>

      <div className="border-t border-mist px-3 py-3">
        <p className="mb-2 text-[11px] font-semibold tracking-wide text-ink-soft uppercase">
          Try it
        </p>
        <div className="flex items-start gap-2">
          <textarea
            value={sample}
            onChange={(e) => {
              setSample(e.target.value);
            }}
            rows={2}
            placeholder={"\\begin{pmatrix}2&1\\\\1&2\\end{pmatrix}   —  one input per line"}
            className="min-w-0 flex-1 rounded-sm border border-mist bg-paper px-2 py-1.5 font-mono text-xs text-ink placeholder:text-ink-soft/60 focus:border-pond focus:outline-none"
          />
          <button
            onClick={test}
            disabled={testing || sample.trim() === ""}
            className="shrink-0 rounded-sm border border-mist bg-paper px-3 py-1.5 text-xs text-ink transition-colors hover:border-pond hover:bg-gold-soft/40 disabled:opacity-50"
          >
            {testing ? "Running…" : "Run"}
          </button>
        </div>

        {scratchError && <p className="mt-2 text-xs text-rust">{scratchError}</p>}
        {scratch && (
          <div className="mt-2 space-y-1.5">
            <p className="text-[11px] text-ink-soft">
              {scratch.applies
                ? "accepts() says this applies to the first input."
                : "accepts() says it does not apply — no button would appear on that object."}
            </p>
            {scratch.outputs.map((latex, i) => (
              <div key={i} className="flex items-baseline gap-3">
                <span className="font-display text-base text-ink">
                  <Latex>{latex}</Latex>
                </span>
                <code className="font-mono text-[11px] text-ink-soft">{latex}</code>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
