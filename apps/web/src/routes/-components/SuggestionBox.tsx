import { Popover } from "@base-ui/react/popover";
import { useRouterState } from "@tanstack/react-router";
import { useState } from "react";

import { formatApiError } from "@monet/api-client";

import { api } from "../../lib/api";
import { useContributor } from "../../lib/contributor";
import { type EncodedScreenshot, shrinkScreenshot } from "../../lib/screenshots";

const MAX_SCREENSHOTS = 3;
const FIELD_CLASS =
  "w-full rounded-sm border border-mist bg-paper px-2 py-1.5 text-xs text-ink placeholder:text-ink-soft/60 focus:border-pond focus:outline-none";

export function SuggestionBox() {
  const pagePath = useRouterState({ select: (state) => state.location.href });
  const [contributor, setContributor] = useContributor();
  const [text, setText] = useState("");
  const [screenshots, setScreenshots] = useState<EncodedScreenshot[]>([]);
  const [screenshotError, setScreenshotError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);
  const send = api.useMutation("post", "/suggestions");

  const addImages = async (files: File[]) => {
    setScreenshotError(null);
    const images = files.filter((file) => file.type.startsWith("image/"));
    const room = MAX_SCREENSHOTS - screenshots.length;
    if (images.length > room) setScreenshotError(`Up to ${String(MAX_SCREENSHOTS)} screenshots.`);
    try {
      const shrunk = await Promise.all(images.slice(0, room).map(shrinkScreenshot));
      setScreenshots((current) => [...current, ...shrunk].slice(0, MAX_SCREENSHOTS));
    } catch (error) {
      setScreenshotError(error instanceof Error ? error.message : "Could not read the image.");
    }
  };

  const submit = (event: React.SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!text.trim()) return;
    send.mutate(
      {
        body: {
          body: text,
          page_path: pagePath,
          contributor,
          screenshots: screenshots.map(({ media_type, data }) => ({ media_type, data })),
        },
      },
      {
        onSuccess: () => {
          setText("");
          setScreenshots([]);
          setSent(true);
        },
      },
    );
  };

  return (
    <Popover.Root
      onOpenChange={(open) => {
        if (open) setSent(false);
      }}
    >
      <Popover.Trigger className="fixed right-4 bottom-4 z-30 rounded-full border border-mist bg-paper px-3 py-1.5 text-xs text-ink-soft opacity-40 shadow-[0_1px_3px_rgba(35,50,43,0.12)] transition-opacity hover:text-ink hover:opacity-100 focus-visible:opacity-100 data-[popup-open]:opacity-100">
        Suggest
      </Popover.Trigger>
      <Popover.Portal>
        <Popover.Positioner side="top" align="end" sideOffset={8} className="z-30 outline-none">
          <Popover.Popup className="w-80 max-w-[calc(100vw-2rem)] rounded-sm border border-mist bg-paper p-4 shadow-[0_6px_20px_rgba(35,50,43,0.16)] outline-none">
            <Popover.Title className="font-display text-sm text-ink">
              Suggest a change
            </Popover.Title>
            {sent ? (
              <div className="mt-2 space-y-3 text-xs text-ink-soft">
                <p>Thanks, your suggestion is in the review queue.</p>
                <button
                  type="button"
                  onClick={() => {
                    setSent(false);
                  }}
                  className="text-pond hover:underline"
                >
                  Suggest something else
                </button>
              </div>
            ) : (
              <form onSubmit={submit} className="mt-2 space-y-2.5">
                <textarea
                  value={text}
                  onChange={(event) => {
                    setText(event.target.value);
                  }}
                  onPaste={(event) => {
                    const files = Array.from(event.clipboardData.files);
                    if (files.length > 0) {
                      event.preventDefault();
                      void addImages(files);
                    }
                  }}
                  rows={4}
                  placeholder="A database, type or map to add, or something to correct"
                  className={FIELD_CLASS}
                />
                <div>
                  {screenshots.length > 0 && (
                    <ul className="mb-1.5 flex gap-2">
                      {screenshots.map((shot, index) => (
                        <li key={shot.preview} className="relative">
                          <img
                            src={shot.preview}
                            alt={`Screenshot ${String(index + 1)}`}
                            className="h-14 w-20 rounded-sm border border-mist object-cover"
                          />
                          <button
                            type="button"
                            aria-label={`Remove screenshot ${String(index + 1)}`}
                            onClick={() => {
                              setScreenshots((current) => current.filter((s) => s !== shot));
                            }}
                            className="absolute -top-1.5 -right-1.5 h-4 w-4 rounded-full bg-ink text-[10px] leading-4 text-paper"
                          >
                            ×
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                  {screenshots.length < MAX_SCREENSHOTS && (
                    <label className="cursor-pointer text-xs text-pond hover:underline">
                      Add screenshots
                      <input
                        type="file"
                        accept="image/*"
                        multiple
                        className="sr-only"
                        onChange={(event) => {
                          void addImages(Array.from(event.target.files ?? []));
                          event.target.value = "";
                        }}
                      />
                    </label>
                  )}
                  <span className="text-xs text-ink-soft"> or paste one into the box</span>
                  {screenshotError !== null && (
                    <p className="mt-1 text-xs text-rust">{screenshotError}</p>
                  )}
                </div>
                <input
                  value={contributor}
                  onChange={(event) => {
                    setContributor(event.target.value);
                  }}
                  placeholder="Your name (optional)"
                  className={FIELD_CLASS}
                />
                <div className="flex items-center justify-between gap-3 pt-1">
                  <span className="text-[11px] text-ink-soft">Sent with a link to this page.</span>
                  <button
                    type="submit"
                    disabled={send.isPending || !text.trim()}
                    className="rounded-sm bg-pond px-3 py-1.5 text-xs font-medium text-paper transition-colors hover:bg-pond-deep disabled:opacity-50"
                  >
                    Send
                  </button>
                </div>
                {send.isError && <p className="text-xs text-rust">{formatApiError(send.error)}</p>}
              </form>
            )}
          </Popover.Popup>
        </Popover.Positioner>
      </Popover.Portal>
    </Popover.Root>
  );
}
