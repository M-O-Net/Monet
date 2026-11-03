import { Select } from "@base-ui/react/select";
import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { formatApiError } from "@monet/api-client";

import { ConfirmPopover } from "../../../components/ConfirmPopover";
import { api } from "../../../lib/api";
import { LEVELS } from "../../../lib/editorLevels";
import type { EditorCreated } from "../../../lib/types";

const HEADING = "mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase";
const FIELD_CLASS =
  "rounded-sm border border-mist bg-paper px-2 py-1 text-sm text-ink focus:border-pond focus:outline-none";

export function EditorAdmin() {
  const queryClient = useQueryClient();
  const editors = api.useQuery("get", "/editors");
  const changes = api.useQuery("get", "/changes");
  const createEditor = api.useMutation("post", "/editors");
  const deleteEditor = api.useMutation("delete", "/editors/{editor_id}");
  const [name, setName] = useState("");
  const [level, setLevel] = useState(1);
  const [created, setCreated] = useState<EditorCreated | null>(null);

  const refresh = () => {
    void queryClient.invalidateQueries({ queryKey: ["get", "/editors"] });
    void queryClient.invalidateQueries({ queryKey: ["get", "/changes"] });
  };

  if (editors.isPending) return <p className="text-sm text-ink-soft">Loading…</p>;
  if (editors.isError) {
    return <p className="text-sm text-rust">{formatApiError(editors.error)}</p>;
  }

  return (
    <div className="space-y-8">
      <section>
        <h2 className={HEADING}>Give someone a key</h2>
        <form
          className="flex flex-wrap items-center gap-2"
          onSubmit={(event) => {
            event.preventDefault();
            createEditor.mutate(
              { body: { name, level } },
              {
                onSuccess: (editor) => {
                  setCreated(editor);
                  setName("");
                  refresh();
                },
              },
            );
          }}
        >
          <input
            value={name}
            onChange={(event) => {
              setName(event.target.value);
            }}
            placeholder="Their name, as it will be credited"
            className={`${FIELD_CLASS} w-64`}
          />
          <Select.Root
            value={level}
            onValueChange={(value) => {
              if (value !== null) setLevel(value);
            }}
          >
            <Select.Trigger className={`${FIELD_CLASS} inline-flex items-center gap-2`}>
              <Select.Value>{(value: number) => `Level ${String(value)}`}</Select.Value>
              <Select.Icon>▾</Select.Icon>
            </Select.Trigger>
            <Select.Portal>
              <Select.Positioner className="z-20" sideOffset={4}>
                <Select.Popup className="rounded-sm border border-mist bg-paper p-1 shadow-[0_6px_20px_rgba(35,50,43,0.16)]">
                  {[1, 2, 3].map((option) => (
                    <Select.Item
                      key={option}
                      value={option}
                      className="cursor-pointer rounded-sm px-2 py-1 text-sm text-ink data-[highlighted]:bg-gold-soft"
                    >
                      <Select.ItemText>
                        Level {option}: {LEVELS[option]}
                      </Select.ItemText>
                    </Select.Item>
                  ))}
                </Select.Popup>
              </Select.Positioner>
            </Select.Portal>
          </Select.Root>
          <button
            type="submit"
            disabled={name.trim() === "" || createEditor.isPending}
            className="rounded-sm bg-pond px-3 py-1 text-sm font-medium text-paper hover:bg-pond-deep disabled:opacity-50"
          >
            Create key
          </button>
        </form>
        {createEditor.isError && (
          <p className="mt-2 text-xs text-rust">{formatApiError(createEditor.error)}</p>
        )}
        {created !== null && (
          <div className="mt-3 rounded-sm border border-gold/40 bg-gold-soft px-3 py-2 text-sm text-ink">
            <p>
              Key for <strong>{created.name}</strong> (level {created.level}). Send it to them now:
              it is shown only once.
            </p>
            <code className="mt-1 block break-all select-all">{created.key}</code>
          </div>
        )}
      </section>

      <section>
        <h2 className={HEADING}>Keys ({editors.data.length})</h2>
        {editors.data.length === 0 ? (
          <p className="text-sm text-ink-soft italic">No keys yet besides your own.</p>
        ) : (
          <ul className="divide-y divide-mist rounded-sm border border-mist bg-white/40">
            {editors.data.map((editor) => (
              <li
                key={editor.id ?? editor.name}
                className="flex items-center justify-between px-4 py-2 text-sm"
              >
                <span>
                  {editor.name} <span className="text-ink-soft">· level {editor.level}</span>
                </span>
                {editor.id !== null && (
                  <ConfirmPopover
                    trigger="Revoke"
                    triggerClassName="text-xs text-ink-soft hover:text-rust"
                    label={`Revoke ${editor.name}'s key`}
                    question={`Revoke ${editor.name}'s key? It stops working at once.`}
                    confirmLabel="Revoke"
                    onConfirm={() => {
                      deleteEditor.mutate(
                        { params: { path: { editor_id: editor.id ?? "" } } },
                        { onSuccess: refresh },
                      );
                    }}
                  />
                )}
              </li>
            ))}
          </ul>
        )}
        {deleteEditor.isError && (
          <p className="mt-2 text-xs text-rust">{formatApiError(deleteEditor.error)}</p>
        )}
      </section>

      <section>
        <h2 className={HEADING}>Recent changes</h2>
        {changes.isError && <p className="text-sm text-rust">{formatApiError(changes.error)}</p>}
        {changes.data?.length === 0 && (
          <p className="text-sm text-ink-soft italic">Nothing changed with a key yet.</p>
        )}
        {changes.data !== undefined && changes.data.length > 0 && (
          <table className="w-full text-left text-xs">
            <thead className="text-ink-soft">
              <tr>
                <th className="py-1 pr-3 font-normal">When</th>
                <th className="py-1 pr-3 font-normal">Who</th>
                <th className="py-1 pr-3 font-normal">What</th>
                <th className="py-1 font-normal">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-mist">
              {changes.data.map((change) => (
                <tr key={`${change.at}${change.path}${change.method}`}>
                  <td className="py-1 pr-3 whitespace-nowrap text-ink-soft">
                    {new Date(change.at).toLocaleString()}
                  </td>
                  <td className="py-1 pr-3">{change.editor}</td>
                  <td className="py-1 pr-3 font-mono break-all">
                    {change.method} {change.path}
                  </td>
                  <td className={`py-1 ${change.status < 400 ? "text-ink-soft" : "text-rust"}`}>
                    {change.status < 400 ? "done" : `refused (${String(change.status)})`}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
