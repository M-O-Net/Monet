import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { formatApiError } from "@monet/api-client";

import { ConfirmButton } from "../../components/ConfirmButton";
import { ContributorField } from "../../components/ContributorField";
import { api } from "../../lib/api";
import { useContributor } from "../../lib/contributor";
import type { CommentOut } from "../../lib/types";

function Comment({ comment, onDeleted }: { comment: CommentOut; onDeleted: () => void }) {
  const deleteComment = api.useMutation("delete", "/comments/{comment_id}");
  const day = new Date(comment.at).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  return (
    <li className="rounded-sm border border-mist bg-white/40 px-3 py-2">
      <p className="text-sm whitespace-pre-wrap text-ink">{comment.body}</p>
      <div className="mt-1 flex items-center justify-between text-[11px] text-ink-soft/80">
        <span>
          {comment.contributor ?? "anonymous"} · {day}
        </span>
        <ConfirmButton
          label="Delete"
          title="Delete this comment?"
          description="It disappears for everyone. This cannot be undone."
          confirmLabel="Delete"
          tone="danger"
          pending={deleteComment.isPending}
          className="text-ink-soft hover:text-rust"
          onConfirm={() => {
            deleteComment.mutate(
              { params: { path: { comment_id: comment.id } } },
              { onSuccess: onDeleted },
            );
          }}
        />
      </div>
    </li>
  );
}

export function Comments({ objectId }: { objectId: string }) {
  const queryClient = useQueryClient();
  const comments = api.useQuery("get", "/objects/{object_id}/comments", {
    params: { path: { object_id: objectId } },
  });
  const createComment = api.useMutation("post", "/objects/{object_id}/comments");
  const [contributor, setContributor] = useContributor();
  const [body, setBody] = useState("");

  const refresh = () => {
    void queryClient.invalidateQueries({ queryKey: ["get", "/objects/{object_id}/comments"] });
    void queryClient.invalidateQueries({ queryKey: ["get", "/events"] });
  };

  return (
    <section className="mt-8 mb-7">
      <h2 className="mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase">Comments</h2>
      {comments.isError && <p className="text-xs text-rust">{formatApiError(comments.error)}</p>}
      {comments.data?.length === 0 && (
        <p className="mb-3 text-sm text-ink-soft italic">
          No comments yet — ideas, perspective, a partial result or an interesting mistake all
          belong here.
        </p>
      )}
      {comments.data && comments.data.length > 0 && (
        <ul className="mb-3 space-y-2">
          {comments.data.map((comment) => (
            <Comment key={comment.id} comment={comment} onDeleted={refresh} />
          ))}
        </ul>
      )}
      <form
        className="space-y-2"
        onSubmit={(event) => {
          event.preventDefault();
          if (body.trim() === "") return;
          createComment.mutate(
            {
              params: { path: { object_id: objectId } },
              body: { body, contributor },
            },
            {
              onSuccess: () => {
                setBody("");
                refresh();
              },
            },
          );
        }}
      >
        <textarea
          value={body}
          onChange={(event) => {
            setBody(event.target.value);
          }}
          rows={3}
          placeholder="Add a comment…"
          className="w-full rounded-sm border border-mist bg-paper px-3 py-2 text-sm text-ink placeholder:text-ink-soft/60 focus:border-pond focus:outline-none"
        />
        <div className="flex flex-wrap items-center justify-between gap-2">
          <ContributorField value={contributor} onChange={setContributor} />
          <button
            type="submit"
            disabled={createComment.isPending || body.trim() === ""}
            className="rounded-sm bg-pond px-3 py-1.5 text-xs font-medium text-paper hover:bg-pond-deep disabled:opacity-50"
          >
            Comment
          </button>
        </div>
        {createComment.isError && (
          <p className="text-xs text-rust">{formatApiError(createComment.error)}</p>
        )}
      </form>
    </section>
  );
}
