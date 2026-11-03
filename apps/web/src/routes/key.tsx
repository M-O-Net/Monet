import { createFileRoute } from "@tanstack/react-router";

import { EditorKeyForm } from "./-components/editors/EditorKeyForm";

export const Route = createFileRoute("/key")({
  component: KeyPage,
});

function KeyPage() {
  return (
    <div>
      <h1 className="mb-1 font-display text-xl font-medium text-ink">Editor key</h1>
      <p className="mb-5 text-sm text-ink-soft">
        Anyone can read, comment and suggest. Adding to the network needs an editor key.
      </p>
      <EditorKeyForm />
    </div>
  );
}
