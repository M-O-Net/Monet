import { useQueryClient } from "@tanstack/react-query";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import { formatApiError } from "@monet/api-client";

import { Latex } from "../components/Latex";
import { RelationForm } from "../components/RelationForm";
import { api } from "../lib/api";
import { RelationList } from "./-components/RelationList";
import { ImplementationEditor } from "./-components/ImplementationEditor";
import { Operations } from "./-components/Operations";

export const Route = createFileRoute("/objects/$objectId")({
  component: ObjectDetail,
});

function ObjectDetail() {
  const { objectId } = Route.useParams();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const detail = api.useQuery("get", "/objects/{object_id}", {
    params: { path: { object_id: objectId } },
  });
  const allObjects = api.useQuery("get", "/objects");
  const implementations = api.useQuery("get", "/implementations");
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
    void queryClient.invalidateQueries({ queryKey: ["get", "/implementations"] });
  };

  if (detail.isPending) return <p className="text-sm text-ink-soft">Loading…</p>;
  if (detail.isError) {
    return <p className="text-sm text-rust">{formatApiError(detail.error)}</p>;
  }
  const obj = detail.data;
  const hasNoRelations =
    obj.as_operator.length === 0 && obj.as_input.length === 0 && obj.as_output.length === 0;

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
              <button
                onClick={() => {
                  const mutation = obj.is_top_level ? unmarkTopLevel : markTopLevel;
                  mutation.mutate(
                    { params: { path: { object_id: objectId } } },
                    { onSuccess: invalidateAll },
                  );
                }}
                className={
                  obj.is_top_level
                    ? "rounded-sm border border-gold/40 bg-gold-soft px-2 py-1 text-xs text-ink hover:bg-gold-soft/70"
                    : "rounded-sm border border-mist px-2 py-1 text-xs text-ink-soft hover:bg-paper-deep"
                }
                title="Whether this object appears on the contents page"
              >
                {obj.is_top_level ? "On contents page" : "Add to contents page"}
              </button>
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
              <button
                onClick={() => {
                  deleteObject.mutate(
                    { params: { path: { object_id: objectId } } },
                    { onSuccess: () => void navigate({ to: "/" }) },
                  );
                }}
                className="rounded-sm border border-rust/30 px-2 py-1 text-xs text-rust hover:bg-rust/10"
              >
                Delete
              </button>
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

      {allObjects.data && (
        <Operations
          object={{ id: obj.id, latex: obj.latex }}
          objects={allObjects.data}
          implementations={implementations.data ?? []}
          onCommitted={invalidateAll}
        />
      )}

      <ImplementationEditor
        object={{ id: obj.id, latex: obj.latex }}
        implementations={implementations.data ?? []}
        onChanged={invalidateAll}
      />

      <h2 className="mb-2 mt-8 text-xs font-semibold tracking-wide text-ink-soft uppercase">
        Add a relation
      </h2>
      {allObjects.data && <RelationForm objects={allObjects.data} onCreated={invalidateAll} />}
    </div>
  );
}
