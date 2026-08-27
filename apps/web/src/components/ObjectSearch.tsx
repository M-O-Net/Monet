import { Dialog } from "@base-ui/react/dialog";
import { useNavigate } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";

import { api } from "../lib/api";
import { searchObjects } from "../lib/search";
import { Latex } from "./Latex";

const RESULT_LIMIT = 10;

export function ObjectSearch() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [cursor, setCursor] = useState(0);
  const navigate = useNavigate();
  const objects = api.useQuery("get", "/objects", {}, { enabled: open });

  const results = useMemo(
    () => searchObjects(objects.data ?? [], query, RESULT_LIMIT),
    [objects.data, query],
  );

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const typingElsewhere =
        document.activeElement instanceof HTMLInputElement ||
        document.activeElement instanceof HTMLTextAreaElement ||
        (document.activeElement as HTMLElement | null)?.isContentEditable === true;
      if ((event.metaKey || event.ctrlKey) && event.key === "k") {
        event.preventDefault();
        setOpen(true);
        return;
      }
      if (event.key === "/" && !typingElsewhere && !event.metaKey && !event.ctrlKey) {
        event.preventDefault();
        setOpen(true);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
    };
  }, []);

  const go = (objectId: string) => {
    setOpen(false);
    setQuery("");
    setCursor(0);
    void navigate({ to: "/objects/$objectId", params: { objectId } });
  };

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger className="text-xs text-ink-soft underline decoration-dotted underline-offset-2 hover:text-pond">
        search
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Backdrop className="fixed inset-0 z-30 bg-ink/20" />
        <Dialog.Popup className="fixed top-[15vh] left-1/2 z-40 w-[min(34rem,92vw)] -translate-x-1/2 rounded-sm border border-mist bg-paper shadow-[0_12px_40px_rgba(35,50,43,0.22)] outline-none">
          <Dialog.Title className="sr-only">Search the network</Dialog.Title>
          <input
            autoFocus
            value={query}
            placeholder="Search by name, notation or description…"
            onChange={(event) => {
              setQuery(event.target.value);
              setCursor(0);
            }}
            onKeyDown={(event) => {
              if (event.key === "ArrowDown") {
                event.preventDefault();
                setCursor((c) => Math.min(c + 1, results.length - 1));
              } else if (event.key === "ArrowUp") {
                event.preventDefault();
                setCursor((c) => Math.max(c - 1, 0));
              } else if (event.key === "Enter") {
                const chosen = results.at(cursor);
                if (chosen !== undefined) go(chosen.id);
              }
            }}
            className="w-full border-b border-mist bg-transparent px-4 py-3 text-sm text-ink outline-none placeholder:text-ink-soft/70"
          />
          {objects.isPending && (
            <p className="px-4 py-3 text-sm text-ink-soft italic">Fetching the catalogue…</p>
          )}
          {objects.data && results.length === 0 && (
            <p className="px-4 py-3 text-sm text-ink-soft italic">Nothing matches that.</p>
          )}
          <ul className="max-h-[50vh] overflow-y-auto">
            {results.map((object, index) => (
              <li key={object.id}>
                <button
                  onMouseEnter={() => {
                    setCursor(index);
                  }}
                  onClick={() => {
                    go(object.id);
                  }}
                  className={`flex w-full items-baseline gap-3 px-4 py-2 text-left ${
                    index === cursor ? "bg-gold-soft/50" : ""
                  }`}
                >
                  <span className="text-sm text-ink">
                    <Latex>{object.latex}</Latex>
                  </span>
                  {object.description && (
                    <span className="truncate text-xs text-ink-soft">{object.description}</span>
                  )}
                </button>
              </li>
            ))}
          </ul>
        </Dialog.Popup>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
