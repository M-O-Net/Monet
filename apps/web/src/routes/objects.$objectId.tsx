import { useQueryClient } from "@tanstack/react-query";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import { formatApiError } from "@monet/api-client";

import { ConfirmButton } from "../components/ConfirmButton";
import { Latex } from "../components/Latex";
import { RelationForm } from "../components/RelationForm";
import { api } from "../lib/api";
import { RelationList } from "./-components/RelationList";

export const Route = createFileRoute("/objects/$objectId")({
  component: ObjectDetail,
  // Navigating between two objects only changes the param, and TanStack Router reuses the
  // component for that — so without this, per-object local state (the edit draft below)
  // leaks across the navigation: open Edit on A, click through to B, and B shows A's draft.
  remountDeps: ({ params }) => params.objectId,
});

function ObjectDetail() {
  const { objectId } = Route.useParams();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const detail = api.useQuery("get", "/objects/{object_id}", {
    params: { path: { object_id: objectId } },
  });
  const allObjects = api.useQuery("get", "/objects");
  const updateObject = api.useMutation("patch", "/objects/{object_id}");
  const deleteObject = api.useMutation("delete", "/objects/{object_id}");
  const markTopLevel = api.useMutation("put", "/top-level-objects/{object_id}");
  const unmarkTopLevel = api.useMutation("delete", "/top-level-objects/{object_id}");

  const [editing, setEditing] = useState(false);
  const [draftLatex, setDraftLatex] = useState("");
  const [draftDescription, setDraftDescription] = useState("");

  const invalidateAll = () => {
    void queryClient.invalidateQueries({ queryKey: ["get", "/objects"] });
    void queryClient.invalidateQueries({ queryKey: ["get", "/top-level-objects"] });
    void queryClient.invalidateQueries({
      queryKey: ["get", "/objects/{object_id}", { params: { path: { object_id: objectId } } }],
    });
  };

  if (detail.isPending) return <p className="text-sm text-ink-soft">Loading…</p>;
  if (detail.isError) {
    return <p className="text-sm text-rust">{formatApiError(detail.error)}</p>;
  }
  const obj = detail.data;
  const relationCount = obj.as_operator.length + obj.as_input.length + obj.as_output.length;
  const hasNoRelations = relationCount === 0;

  return (
    <div>
      <Link
        to="/"
        className="mb-5 inline-flex items-center gap-1 text-sm text-ink-soft hover:text-pond"
      >
        ← contents
      </Link>

      <div className="mb-7 flex items-start justify-between gap-4 border-b border-mist pb-5">
        {editing ? (
          <form
            className="flex flex-1 flex-col gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              updateObject.mutate(
                {
                  params: { path: { object_id: objectId } },
                  body: { latex: draftLatex, description: draftDescription.trim() || null },
                },
                {
                  onSuccess: () => {
                    setEditing(false);
                    invalidateAll();
                  },
                },
              );
            }}
          >
            <div className="flex gap-2">
              <input
                value={draftLatex}
                onChange={(e) => {
                  setDraftLatex(e.target.value);
                }}
                className="flex-1 rounded-sm border border-mist bg-paper px-2 py-1 text-lg text-ink focus:border-pond focus:outline-none"
                autoFocus
              />
              <button
                type="submit"
                className="rounded-sm bg-pond px-3 py-1 text-sm font-medium text-paper hover:bg-pond-deep"
              >
                Save
              </button>
              <button
                type="button"
                onClick={() => {
                  setEditing(false);
                }}
                className="rounded-sm border border-mist px-3 py-1 text-sm text-ink-soft hover:bg-paper-deep"
              >
                Cancel
              </button>
            </div>
            <input
              value={draftDescription}
              onChange={(e) => {
                setDraftDescription(e.target.value);
              }}
              placeholder="Description (optional)"
              className="rounded-sm border border-mist bg-paper px-2 py-1 text-xs text-ink placeholder:text-ink-soft/60 focus:border-pond focus:outline-none"
            />
          </form>
        ) : (
          <>
            <div>
              <h1 className="font-display text-2xl text-ink">
                <Latex>{obj.latex}</Latex>
              </h1>
              {obj.description && <p className="mt-1 text-sm text-ink-soft">{obj.description}</p>}
            </div>
            <div className="flex shrink-0 gap-2">
              {obj.is_top_level ? (
                <ConfirmButton
                  label="On contents page"
                  title="Remove from the contents page?"
                  description="It will stop being listed as a section on the contents page. Nothing else changes — its relations and everything filed under it stay exactly as they are."
                  confirmLabel="Remove"
                  tone="danger"
                  pending={unmarkTopLevel.isPending}
                  className="rounded-sm border border-gold/40 bg-gold-soft px-2 py-1 text-xs text-ink hover:bg-gold-soft/70"
                  onConfirm={() => {
                    unmarkTopLevel.mutate(
                      { params: { path: { object_id: objectId } } },
                      { onSuccess: invalidateAll },
                    );
                  }}
                />
              ) : (
                <ConfirmButton
                  label="Add to contents page"
                  title="Add to the contents page?"
                  description="It will be listed as a top-level section on the contents page."
                  confirmLabel="Add"
                  pending={markTopLevel.isPending}
                  className="rounded-sm border border-mist px-2 py-1 text-xs text-ink-soft hover:bg-paper-deep"
                  onConfirm={() => {
                    markTopLevel.mutate(
                      { params: { path: { object_id: objectId } } },
                      { onSuccess: invalidateAll },
                    );
                  }}
                />
              )}
              <button
                onClick={() => {
                  setDraftLatex(obj.latex);
                  setDraftDescription(obj.description ?? "");
                  setEditing(true);
                }}
                className="rounded-sm border border-mist px-2 py-1 text-xs text-ink-soft hover:bg-paper-deep"
              >
                Edit
              </button>
              <ConfirmButton
                label="Delete"
                title="Delete this object?"
                description={
                  relationCount === 0
                    ? "It takes part in no relations, so nothing else is affected. This cannot be undone."
                    : `It takes part in ${String(relationCount)} relation${relationCount === 1 ? "" : "s"}. Deleting is blocked while any of them still reference it — remove those first. This cannot be undone.`
                }
                confirmLabel="Delete"
                tone="danger"
                pending={deleteObject.isPending}
                className="rounded-sm border border-rust/30 px-2 py-1 text-xs text-rust hover:bg-rust/10"
                onConfirm={() => {
                  deleteObject.mutate(
                    { params: { path: { object_id: objectId } } },
                    { onSuccess: () => void navigate({ to: "/" }) },
                  );
                }}
              />
            </div>
          </>
        )}
      </div>
      {deleteObject.isError && (
        <p className="mb-4 text-xs text-rust">{formatApiError(deleteObject.error)}</p>
      )}

      {hasNoRelations && (
        <p className="mb-7 text-sm text-ink-soft italic">
          Not yet connected to anything else in the valley.
        </p>
      )}
      <RelationList title="Used as operator in" relations={obj.as_operator} />
      <RelationList title="Appears as input in" relations={obj.as_input} />
      <RelationList title="Appears as output in" relations={obj.as_output} />

      <h2 className="mb-2 mt-8 text-xs font-semibold tracking-wide text-ink-soft uppercase">
        Add a relation
      </h2>
      {allObjects.data && <RelationForm objects={allObjects.data} onCreated={invalidateAll} />}
    </div>
  );
}
