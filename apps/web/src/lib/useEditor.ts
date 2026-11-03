import { api } from "./api";
import { useEditorKey } from "./editorKey";
import type { EditorOut } from "./types";

export function useEditor(): { editor: EditorOut | null; level: number; checking: boolean } {
  const key = useEditorKey();
  const me = api.useQuery(
    "get",
    "/editors/me",
    { params: { header: { "x-editor-key": key } } },
    { enabled: key !== "", retry: false },
  );
  const editor = key === "" ? null : (me.data ?? null);
  return { editor, level: editor?.level ?? 0, checking: key !== "" && me.isPending };
}
