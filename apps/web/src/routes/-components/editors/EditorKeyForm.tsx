import { useQueryClient } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { useState } from "react";

import { useEditorKey, writeEditorKey } from "../../../lib/editorKey";
import { LEVELS } from "../../../lib/editorLevels";
import { useEditor } from "../../../lib/useEditor";

const FIELD_CLASS =
  "w-full rounded-sm border border-mist bg-paper px-2 py-1.5 text-sm text-ink focus:border-pond focus:outline-none";

export function EditorKeyForm() {
  const queryClient = useQueryClient();
  const key = useEditorKey();
  const { editor, checking } = useEditor();
  const [draft, setDraft] = useState("");

  const use = (next: string) => {
    writeEditorKey(next);
    void queryClient.invalidateQueries();
  };

  if (editor !== null) {
    return (
      <div className="space-y-3 text-sm text-ink">
        <p>
          You are editing as <strong>{editor.name}</strong>, level {editor.level}: you can{" "}
          {LEVELS[editor.level]}.
        </p>
        {editor.level >= 3 && (
          <p>
            <Link to="/editors" className="text-pond hover:underline">
              Manage editor keys and see recent changes →
            </Link>
          </p>
        )}
        <button
          type="button"
          onClick={() => {
            use("");
          }}
          className="rounded-sm border border-mist px-3 py-1 text-xs text-ink-soft hover:bg-paper-deep"
        >
          Forget this key on this browser
        </button>
      </div>
    );
  }

  return (
    <form
      className="max-w-md space-y-2"
      onSubmit={(event) => {
        event.preventDefault();
        use(draft.trim());
        setDraft("");
      }}
    >
      <label className="block text-xs text-ink-soft" htmlFor="editor-key">
        Paste the editor key you were given. This browser remembers it.
      </label>
      <input
        id="editor-key"
        type="password"
        autoComplete="off"
        value={draft}
        onChange={(event) => {
          setDraft(event.target.value);
        }}
        className={FIELD_CLASS}
      />
      <button
        type="submit"
        disabled={draft.trim() === ""}
        className="rounded-sm bg-pond px-3 py-1 text-sm font-medium text-paper hover:bg-pond-deep disabled:opacity-50"
      >
        Use this key
      </button>
      {key !== "" && !checking && (
        <p className="text-xs text-rust">That key isn&apos;t valid. Check it and try again.</p>
      )}
    </form>
  );
}
