import { useEffect, useMemo, useState } from "react";

import { formatApiError } from "@monet/api-client";

import { Link } from "@tanstack/react-router";

import { Latex } from "../../components/Latex";
import { ObjectPicker } from "../../components/ObjectPicker";
import { api } from "../../lib/api";
import { findCyclesThrough } from "../../lib/cycles";
import type { Cycle } from "../../lib/cycles";
import { buildRelationHtml } from "../../lib/relationTemplate";
import type { RelationOut } from "../../lib/types";
import { probe, run } from "../../sandbox/client";
import { useSandboxStatus } from "../../sandbox/useSandboxStatus";
import { Callout } from "./Callout";
import { CycleChain } from "./CycleChain";
import { RelationExpression } from "./RelationExpression";

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

interface Receipt {
  relation: RelationOut;
  createdRelation: boolean;
  createdObjects: ObjectSummary[];
  closedLoops: Cycle[];
}

function OutputStatus({ latex }: { latex: string }) {
  const found = api.useQuery("get", "/objects", { params: { query: { latex } } });
  if (found.isPending) return <span className="text-[11px] text-ink-soft">checking…</span>;
  return (
    <span className="text-[11px] text-ink-soft">
      {found.data?.length ? "already in the network" : "new object"}
    </span>
  );
}

export function Operations({
  object,
  implementations,
  relations,
  onCommitted,
}: {
  object: ObjectSummary;
  implementations: Implementation[];
  relations: RelationOut[];
  onCommitted: () => void;
}) {
  const assertRelation = api.useMutation("post", "/relations/assert");
  const sandboxStatus = useSandboxStatus();

  const [applicable, setApplicable] = useState<string[] | null>(null);
  const [skipped, setSkipped] = useState(0);
  const [probeError, setProbeError] = useState<string | null>(null);
  const [extraInputs, setExtraInputs] = useState<Record<string, ObjectSummary[]>>({});
  const [running, setRunning] = useState<string | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const [receipt, setReceipt] = useState<Receipt | null>(null);
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
      (probed) => {
        if (cancelled) return;
        setApplicable(probed.applicable);
        setSkipped(probed.skipped);
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
    const extra = extraInputs[implementation.id] ?? [];
    const inputIds = [object.id, ...extra.map((obj) => obj.id)];
    const inputLatex = [object.latex, ...extra.map((obj) => obj.latex)];
    setRunError(null);
    setResult(null);
    setReceipt(null);
    setRunning(implementation.id);
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
        onSuccess: (assertion) => {
          const known = new Map<string, ObjectSummary>();
          for (const slot of [...assertion.relation.inputs, ...assertion.relation.outputs]) {
            known.set(slot.object.id, slot.object);
          }
          setReceipt({
            relation: assertion.relation,
            createdRelation: assertion.created_relation,
            createdObjects: assertion.created_object_ids.flatMap((id) => {
              const found = known.get(id);
              return found === undefined ? [] : [found];
            }),
            closedLoops: findCyclesThrough(
              [...relations.filter((r) => r.id !== assertion.relation.id), assertion.relation],
              object.id,
            ).filter((cycle) => cycle.some((step) => step.relation.id === assertion.relation.id)),
          });
          setResult(null);
          onCommitted();
        },
      },
    );
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

      {applicable !== null && shown.length === 0 && skipped === 0 && (
        <p className="text-sm text-ink-soft italic">
          No implementation knows how to read this object yet.
        </p>
      )}

      {skipped > 0 && (
        <p className="text-sm text-ink-soft italic">
          Checking took too long, so {skipped} of {implementations.length} implementations were not
          tried on this object.
        </p>
      )}

      <div className="space-y-2">
        {shown.map((implementation) => {
          const extra = extraInputs[implementation.id] ?? [];
          const setExtra = (chosen: ObjectSummary[]) => {
            setExtraInputs((prev) => ({ ...prev, [implementation.id]: chosen }));
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

              {extra.map((chosen, i) => (
                <span
                  key={`${chosen.id}-${String(i)}`}
                  className="inline-flex items-center gap-1 rounded-sm border border-mist bg-paper-deep px-2 py-1 text-xs"
                >
                  <Latex>{chosen.latex}</Latex>
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
                  value={null}
                  onChange={(chosen) => {
                    if (chosen) setExtra([...extra, chosen]);
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
            {result.outputs.map((latex, i) => (
              <li key={i} className="flex items-baseline gap-3">
                <span className="font-display text-base text-ink">
                  <Latex>{latex}</Latex>
                </span>
                <OutputStatus latex={latex} />
              </li>
            ))}
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

      {receipt && (
        <Callout heading={receipt.createdRelation ? "New to the network" : "Already recorded"}>
          <button
            onClick={() => {
              setReceipt(null);
            }}
            className="float-right -mt-7 text-ink-soft hover:text-rust"
            aria-label="Dismiss"
          >
            ×
          </button>

          <p className="mb-3 text-sm">
            <RelationExpression
              html={buildRelationHtml(
                receipt.relation,
                receipt.relation.display?.template ?? null,
                object.id,
              )}
            />
          </p>

          <p className="text-sm text-ink-soft">
            {!receipt.createdRelation
              ? "Someone entered this by hand before anything could compute it. The computation agrees with them."
              : receipt.createdObjects.length === 0
                ? "Every object it involves was already catalogued — this joined two things that were both already here."
                : "Catalogued alongside it:"}
          </p>

          {receipt.createdObjects.length > 0 && (
            <ul className="mt-2 flex flex-wrap gap-2">
              {receipt.createdObjects.map((created) => (
                <li key={created.id}>
                  <Link
                    to="/objects/$objectId"
                    params={{ objectId: created.id }}
                    className="relation-tag inline-block rounded-sm px-2 py-0.5 text-xs"
                  >
                    <Latex>{created.latex}</Latex>
                  </Link>
                </li>
              ))}
            </ul>
          )}

          {receipt.closedLoops.length > 0 && (
            <div className="mt-4 border-t border-mist pt-3">
              <p className="mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase">
                {receipt.createdRelation
                  ? receipt.closedLoops.length === 1
                    ? "It closed a loop"
                    : "It closed loops"
                  : receipt.closedLoops.length === 1
                    ? "It sits on a loop"
                    : "It sits on loops"}
              </p>
              <ul className="space-y-2">
                {receipt.closedLoops.map((cycle) => (
                  <li key={cycle.map((step) => step.relation.id).join(">")}>
                    <CycleChain cycle={cycle} currentObjectId={object.id} />
                  </li>
                ))}
              </ul>
            </div>
          )}
        </Callout>
      )}
    </section>
  );
}
