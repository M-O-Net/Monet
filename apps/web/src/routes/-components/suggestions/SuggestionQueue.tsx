import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";

import { formatApiError } from "@monet/api-client";

import { ConfirmPopover } from "../../../components/ConfirmPopover";
import { api, apiBaseUrl } from "../../../lib/api";
import { relativeTime } from "../../../lib/relativeTime";
import type { SuggestionOut } from "../../../lib/types";
import { readAsDataUrl } from "../../../lib/screenshots";

const STORAGE_KEY = "monet.reviewKey";

function rememberedKey(): string {
  try {
    return localStorage.getItem(STORAGE_KEY) ?? "";
  } catch {
    return "";
  }
}

function rememberKey(key: string): void {
  try {
    localStorage.setItem(STORAGE_KEY, key);
  } catch {
    return;
  }
}

export function SuggestionQueue({ linkKey }: { linkKey: string | undefined }) {
  const navigate = useNavigate();
  const [key, setKey] = useState(() => linkKey ?? rememberedKey());

  useEffect(() => {
    if (linkKey === undefined) return;
    rememberKey(linkKey);
    void navigate({ to: "/suggestions", search: {}, replace: true });
  }, [linkKey, navigate]);

  const chooseKey = (next: string) => {
    rememberKey(next);
    setKey(next);
  };

  if (!key) return <KeyForm onSubmit={chooseKey} />;
  return (
    <Queue
      reviewKey={key}
      onForget={() => {
        chooseKey("");
      }}
    />
  );
}

function KeyForm({ onSubmit }: { onSubmit: (key: string) => void }) {
  const [value, setValue] = useState("");
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        if (value.trim()) onSubmit(value.trim());
      }}
      className="flex max-w-md gap-2"
    >
      <input
        value={value}
        onChange={(event) => {
          setValue(event.target.value);
        }}
        type="password"
        placeholder="Review key"
        className="flex-1 rounded-sm border border-mist bg-paper px-3 py-2 text-sm text-ink placeholder:text-ink-soft/60 focus:border-pond focus:outline-none"
      />
      <button
        type="submit"
        className="rounded-sm bg-pond px-4 py-2 text-sm font-medium text-paper transition-colors hover:bg-pond-deep"
      >
        Open
      </button>
    </form>
  );
}

function Queue({ reviewKey, onForget }: { reviewKey: string; onForget: () => void }) {
  const suggestions = api.useQuery("get", "/suggestions", {
    params: { header: { "x-review-key": reviewKey } },
  });

  if (suggestions.isPending) return <p className="text-sm text-ink-soft">Gathering suggestions…</p>;
  if (suggestions.isError) {
    return (
      <div className="space-y-2 text-sm">
        <p className="text-rust">{formatApiError(suggestions.error)}</p>
        <button type="button" onClick={onForget} className="text-pond hover:underline">
          Enter a different key
        </button>
      </div>
    );
  }
  if (suggestions.data.length === 0) {
    return <p className="text-sm text-ink-soft">No suggestions waiting.</p>;
  }
  return (
    <ul className="divide-y divide-mist rounded-sm border border-mist bg-white/40 shadow-[0_1px_3px_rgba(35,50,43,0.06)]">
      {suggestions.data.map((suggestion) => (
        <SuggestionItem key={suggestion.id} suggestion={suggestion} reviewKey={reviewKey} />
      ))}
    </ul>
  );
}

function SuggestionItem({
  suggestion,
  reviewKey,
}: {
  suggestion: SuggestionOut;
  reviewKey: string;
}) {
  const queryClient = useQueryClient();
  const dismiss = api.useMutation("delete", "/suggestions/{suggestion_id}");

  return (
    <li className="space-y-2 px-4 py-3">
      <div className="flex items-baseline justify-between gap-3 text-xs text-ink-soft">
        <span>
          {suggestion.contributor ?? "Anonymous"} · {relativeTime(suggestion.at)} · on{" "}
          <a href={suggestion.page_path} className="text-pond hover:underline">
            {suggestion.page_path}
          </a>
        </span>
        <ConfirmPopover
          trigger="Dismiss"
          triggerClassName="text-xs text-ink-soft hover:text-rust"
          label="Dismiss this suggestion"
          question="Dismiss this suggestion and its screenshots? This cannot be undone."
          confirmLabel="Dismiss"
          disabled={dismiss.isPending}
          onConfirm={() => {
            dismiss.mutate(
              {
                params: {
                  path: { suggestion_id: suggestion.id },
                  header: { "x-review-key": reviewKey },
                },
              },
              {
                onSuccess: () => {
                  void queryClient.invalidateQueries({ queryKey: ["get", "/suggestions"] });
                },
              },
            );
          }}
        />
      </div>
      <p className="text-sm whitespace-pre-wrap text-ink">{suggestion.body}</p>
      {suggestion.screenshots.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {suggestion.screenshots.map((shot) => (
            <Screenshot
              key={shot.id}
              suggestionId={suggestion.id}
              screenshotId={shot.id}
              reviewKey={reviewKey}
            />
          ))}
        </div>
      )}
      {dismiss.isError && <p className="text-xs text-rust">{formatApiError(dismiss.error)}</p>}
    </li>
  );
}

function Screenshot({
  suggestionId,
  screenshotId,
  reviewKey,
}: {
  suggestionId: string;
  screenshotId: string;
  reviewKey: string;
}) {
  const [expanded, setExpanded] = useState(false);
  const image = useQuery({
    queryKey: ["suggestion-screenshot", suggestionId, screenshotId],
    staleTime: Infinity,
    queryFn: async () => {
      const response = await fetch(
        `${apiBaseUrl}/suggestions/${suggestionId}/screenshots/${screenshotId}`,
        { headers: { "X-Review-Key": reviewKey } },
      );
      if (!response.ok) throw new Error(`screenshot failed to load (${String(response.status)})`);
      return readAsDataUrl(await response.blob());
    },
  });

  if (image.isPending) return <span className="text-xs text-ink-soft">loading screenshot…</span>;
  if (image.isError) return <span className="text-xs text-rust">{image.error.message}</span>;
  return (
    <button
      type="button"
      onClick={() => {
        setExpanded(!expanded);
      }}
      className={expanded ? "w-full" : ""}
      aria-label={expanded ? "Shrink screenshot" : "Enlarge screenshot"}
    >
      <img
        src={image.data}
        alt="Screenshot sent with the suggestion"
        className={
          expanded
            ? "w-full rounded-sm border border-mist"
            : "h-24 rounded-sm border border-mist object-cover"
        }
      />
    </button>
  );
}
