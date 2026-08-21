import { useQueryClient } from "@tanstack/react-query";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import { formatApiError } from "@monet/api-client";

import { ConfirmButton } from "../components/ConfirmButton";
import { Latex } from "../components/Latex";
import { RelationForm } from "../components/RelationForm";
import { api } from "../lib/api";
import { invalidateObjectGraph } from "../lib/queries";
import type { ObjectReferenceIn } from "../lib/types";
import { ConvergenceCallout } from "./-components/ConvergenceCallout";
import { LoopCallout } from "./-components/LoopCallout";
import { MemberList } from "./-components/MemberList";
import { OperatorDisplayForm } from "./-components/OperatorDisplayForm";
import { ReferenceEditor } from "./-components/ReferenceEditor";
import { ReferenceList } from "./-components/ReferenceList";
import { RelationList } from "./-components/RelationList";
import { ImplementationEditor } from "./-components/ImplementationEditor";
import { Operations } from "./-components/Operations";
import { SectionTags } from "./-components/SectionTags";

export const Route = createFileRoute("/objects/$objectId")({
  component: ObjectDetail,
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
  const allRelations = api.useQuery("get", "/relations");
  const implementations = api.useQuery("get", "/implementations");
  const updateObject = api.useMutation("patch", "/objects/{object_id}");
  const deleteObject = api.useMutation("delete", "/objects/{object_id}");
  const markTopLevel = api.useMutation("put", "/top-level-objects/{object_id}");
  const unmarkTopLevel = api.useMutation("delete", "/top-level-objects/{object_id}");

  const [editing, setEditing] = useState(false);
  const [draftLatex, setDraftLatex] = useState("");
  const [draftDescription, setDraftDescription] = useState("");
  const [draftImageUrl, setDraftImageUrl] = useState("");
  const [draftReferences, setDraftReferences] = useState<ObjectReferenceIn[]>([]);

  const invalidateAll = () => {
    invalidateObjectGraph(queryClient);
  };

  if (detail.isPending) return <p className="text-sm text-ink-soft">Loading…</p>;
  if (detail.isError) {
    return <p className="text-sm text-rust">{formatApiError(detail.error)}</p>;
  }
  const obj = detail.data;
  const edgeCount = new Set(
    [...obj.as_operator, ...obj.as_input, ...obj.as_output].map((r) => r.id),
  ).size;
  const isIsolated = edgeCount === 0 && obj.sections.length === 0 && obj.members.length === 0;
  const firstAsOperator = obj.as_operator.at(0);

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
                  body: {
                    latex: draftLatex,
                    description: draftDescription.trim() || null,
                    image_url: draftImageUrl.trim() || null,
                    references: draftReferences.filter((reference) => reference.url.trim() !== ""),
                  },
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
            <input
              value={draftImageUrl}
              onChange={(e) => {
                setDraftImageUrl(e.target.value);
              }}
              placeholder="Image URL (optional)"
              className="rounded-sm border border-mist bg-paper px-2 py-1 text-xs text-ink placeholder:text-ink-soft/60 focus:border-pond focus:outline-none"
            />
            <ReferenceEditor references={draftReferences} onChange={setDraftReferences} />
          </form>
        ) : (
          <>
            <div>
              <h1 className="font-display text-2xl text-ink">
                <Latex>{obj.latex}</Latex>
              </h1>
              {obj.description && <p className="mt-1 text-sm text-ink-soft">{obj.description}</p>}
              <SectionTags sections={obj.sections} />
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
                  setDraftImageUrl(obj.image_url ?? "");
                  setDraftReferences(
                    obj.references.map((reference) => ({
                      label: reference.label,
                      url: reference.url,
                    })),
                  );
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
                  edgeCount === 0
                    ? "It takes part in no relations, so nothing else is affected. This cannot be undone."
                    : `The ${edgeCount === 1 ? "relation" : `${String(edgeCount)} relations`} it takes part in ${edgeCount === 1 ? "goes" : "go"} with it, and will disappear from the other objects involved. This cannot be undone.`
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

      {obj.image_url !== null && obj.image_url !== "" && (
        <img
          src={obj.image_url}
          alt={obj.description ?? "Diagram of this object"}
          className="mb-7 max-h-56 w-auto max-w-full"
        />
      )}

      {isIsolated && (
        <p className="mb-7 text-sm text-ink-soft italic">
          Not yet connected to anything else in the valley.
        </p>
      )}
      <p className="mt-5 mb-6 text-sm">
        <Link
          to="/map"
          search={{ focus: objectId }}
          className="text-ink-soft underline decoration-dotted underline-offset-2 hover:text-pond"
        >
          see it on the network map →
        </Link>
      </p>

      {allRelations.data && (
        <LoopCallout relations={allRelations.data} currentObjectId={objectId} />
      )}
      <ConvergenceCallout asOutput={obj.as_output} currentObjectId={objectId} />

      <MemberList members={obj.members} />
      <RelationList
        title="Used as operator in"
        relations={obj.as_operator}
        currentObjectId={objectId}
        collapseHidden={false}
      />
      <RelationList
        title="Appears as input in"
        relations={obj.as_input}
        currentObjectId={objectId}
      />
      <RelationList
        title="Appears as output in"
        relations={obj.as_output}
        currentObjectId={objectId}
      />
      <ReferenceList references={obj.references} />

      {firstAsOperator && <OperatorDisplayForm operatorId={objectId} sample={firstAsOperator} />}

      {allObjects.data && implementations.data && (
        <Operations
          key={`${obj.id}:${obj.latex}`}
          object={{ id: obj.id, latex: obj.latex }}
          objects={allObjects.data}
          implementations={implementations.data}
          relations={allRelations.data ?? []}
          onCommitted={invalidateAll}
        />
      )}

      {implementations.data && (
        <ImplementationEditor
          object={{ id: obj.id, latex: obj.latex }}
          implementations={implementations.data}
          onChanged={invalidateAll}
        />
      )}

      <h2 className="mb-2 mt-8 text-xs font-semibold tracking-wide text-ink-soft uppercase">
        Add a relation
      </h2>
      {allObjects.data && <RelationForm objects={allObjects.data} onCreated={invalidateAll} />}
    </div>
  );
}
