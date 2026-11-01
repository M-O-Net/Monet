import { createFileRoute } from "@tanstack/react-router";

import { SuggestionQueue } from "./-components/suggestions/SuggestionQueue";

export const Route = createFileRoute("/suggestions")({
  validateSearch: (search: Record<string, unknown>): { key?: string } =>
    typeof search.key === "string" ? { key: search.key } : {},
  component: SuggestionsPage,
});

function SuggestionsPage() {
  const { key } = Route.useSearch();
  return (
    <div>
      <h1 className="mb-1 font-display text-xl font-medium text-ink">Suggestions</h1>
      <p className="mb-5 text-sm text-ink-soft">What visitors suggested, newest first.</p>
      <SuggestionQueue linkKey={key} />
    </div>
  );
}
