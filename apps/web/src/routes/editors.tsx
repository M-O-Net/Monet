import { createFileRoute, Link } from "@tanstack/react-router";

import { useEditor } from "../lib/useEditor";
import { EditorAdmin } from "./-components/editors/EditorAdmin";

export const Route = createFileRoute("/editors")({
  component: EditorsPage,
});

function EditorsPage() {
  const { level, checking } = useEditor();
  return (
    <div>
      <h1 className="mb-5 font-display text-xl font-medium text-ink">Editors</h1>
      {checking && <p className="text-sm text-ink-soft">Checking your key…</p>}
      {!checking && level < 3 && (
        <p className="text-sm text-ink-soft">
          This page needs a level-3{" "}
          <Link to="/key" className="text-pond hover:underline">
            editor key
          </Link>
          .
        </p>
      )}
      {level >= 3 && <EditorAdmin />}
    </div>
  );
}
