import { useEffect, useMemo, useState } from "react";

import { formatApiError } from "@monet/api-client";

import { Latex } from "../../components/Latex";
import { ObjectPicker } from "../../components/ObjectPicker";
import { api } from "../../lib/api";
import { normalizeLatex } from "../../lib/latex";
import { probe, run } from "../../sandbox/client";
import { useSandboxStatus } from "../../sandbox/useSandboxStatus";

interface ObjectSummary {
  id: string;
  latex: string;
  description?: string | null;
}

interface Implementation {
  id: string;
  code: string;
  operator: ObjectSummary;
}

interface Result {
  implementation: Implementation;
  inputIds: string[];
  outputs: string[];
}

export function Operations({
  object,
  objects,
  implementations,
  onCommitted,
}: {
  object: ObjectSummary;
  objects: ObjectSummary[];
  implementations: Implementation[];
  onCommitted: () => void;
}) {
  const assertRelation = api.useMutation("post", "/relations/assert");
  const sandboxStatus = useSandboxStatus();

  const [applicable, setApplicable] = useState<string[] | null>(null);
  const [probeError, setProbeError] = useState<string | null>(null);
  const [extraInputs, setExtraInputs] = useState<Record<string, string[]>>({});
  const [running, setRunning] = useState<string | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  const probeKey = implementations.map((i) => `${i.id}:${i.code}`).join("\u0000");
  const payload = useMemo(
    () => implementations.map((i) => ({ id: i.id, code: i.code })),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [probeKey],
  );

  useEffect(() => {
    if (payload.length === 0) return;
    let cancelled = false;
    probe(object.latex, payload).then(
      (ids) => {
        if (!cancelled) setApplicable(ids);
      },
      (error: unknown) => {
        if (!cancelled) setProbeError(error instanceof Error ? error.message : String(error));
      },
    );
    return () => {
      cancelled = true;
    };
  }, [object.latex, payload]);

  const start = (implementation: Implementation) => {
    const inputIds = [object.id, ...(extraInputs[implementation.id] ?? [])];
    setRunError(null);
    setResult(null);
    setRunning(implementation.id);
    const inputLatex = inputIds.map((id) => objects.find((o) => o.id === id)?.latex ?? "");
    run(implementation.code, inputLatex).then(
      (outputs) => {
        setRunning(null);
        setResult({ implementation, inputIds, outputs });
      },
      (error: unknown) => {
        setRunning(null);
        setRunError(error instanceof Error ? error.message : String(error));
      },
    );
  };

  const commit = () => {
    if (!result) return;
    assertRelation.mutate(
      {
        body: {
          operator_id: result.implementation.operator.id,
          input_object_ids: result.inputIds,
          output_latex: result.outputs,
        },
      },
      {
        onSuccess: () => {
          setResult(null);
          onCommitted();
        },
      },
    );
  };

  const existingFor = (latex: string) => {
    const key = normalizeLatex(latex);
    return objects.find((o) => normalizeLatex(o.latex) === key);
  };

  if (implementations.length === 0) return null;

  const shown = implementations.filter((i) => applicable?.includes(i.id));

  return (
    <section className="mt-8">
      <h2 className="mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase">
        Operations
      </h2>

      {applicable === null && !probeError && (
        <p className="text-sm text-ink-soft italic">
          {sandboxStatus === "starting"
            ? "Warming up the computer algebra sandbox…"
            : "Working out which operations apply…"}
        </p>
      )}
      {probeError && <p className="text-sm text-rust">The sandbox failed to start: {probeError}</p>}

      {applicable !== null && shown.length === 0 && (
        <p className="text-sm text-ink-soft italic">
          No implementation knows how to read this object yet.
        </p>
      )}

      <div className="space-y-2">
        {shown.map((implementation) => {
          const extra = extraInputs[implementation.id] ?? [];
          const setExtra = (ids: string[]) => {
            setExtraInputs((prev) => ({ ...prev, [implementation.id]: ids }));
          };
          return (
            <div key={implementation.id} className="flex flex-wrap items-center gap-2">
              <button
                onClick={() => {
                  start(implementation);
                }}
                disabled={running !== null}
                className="rounded-sm border border-mist bg-paper px-3 py-1.5 text-xs text-ink transition-colors hover:border-pond hover:bg-gold-soft/40 disabled:opacity-50"
              >
                {running === implementation.id ? (
                  "Computing…"
                ) : (
                  <Latex>{implementation.operator.latex}</Latex>
                )}
              </button>

              {extra.map((id, i) => (
                <span
                  key={`${id}-${String(i)}`}
                  className="inline-flex items-center gap-1 rounded-sm border border-mist bg-paper-deep px-2 py-1 text-xs"
                >
                  <Latex>{objects.find((o) => o.id === id)?.latex ?? ""}</Latex>
                  <button
                    onClick={() => {
                      setExtra(extra.filter((_, j) => j !== i));
                    }}
                    className="text-ink-soft hover:text-rust"
                    aria-label="Remove this input"
                  >
                    ×
                  </button>
                </span>
              ))}

              <span className="w-52">
                <ObjectPicker
                  objects={objects}
                  value=""
                  onChange={(id) => {
                    if (id) setExtra([...extra, id]);
                  }}
                  placeholder="+ another input…"
                />
              </span>
            </div>
          );
        })}
      </div>

      {runError && <p className="mt-3 text-sm text-rust">{runError}</p>}

      {result && (
        <div className="mt-4 rounded-sm border border-mist bg-white/40 p-4 shadow-[0_1px_3px_rgba(35,50,43,0.06)]">
          <p className="mb-3 text-xs text-ink-soft">
            <Latex>{result.implementation.operator.latex}</Latex> produced:
          </p>
          <ul className="mb-4 space-y-2">
            {result.outputs.map((latex, i) => {
              const existing = existingFor(latex);
              return (
                <li key={i} className="flex items-baseline gap-3">
                  <span className="font-display text-base text-ink">
                    <Latex>{latex}</Latex>
                  </span>
                  <span className="text-[11px] text-ink-soft">
                    {existing ? "already in the network" : "new object"}
                  </span>
                </li>
              );
            })}
          </ul>
          <div className="flex items-center gap-2">
            <button
              onClick={commit}
              disabled={assertRelation.isPending}
              className="rounded-sm bg-pond px-4 py-2 text-sm font-medium text-paper transition-colors hover:bg-pond-deep disabled:opacity-50"
            >
              Add to the network
            </button>
            <button
              onClick={() => {
                setResult(null);
              }}
              className="rounded-sm border border-mist px-3 py-2 text-sm text-ink-soft hover:bg-paper-deep"
            >
              Discard
            </button>
          </div>
          {assertRelation.isError && (
            <p className="mt-2 text-xs text-rust">{formatApiError(assertRelation.error)}</p>
          )}
        </div>
      )}
    </section>
  );
}
