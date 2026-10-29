import { Combobox } from "@base-ui/react/combobox";
import { keepPreviousData } from "@tanstack/react-query";
import { useState } from "react";

import { api } from "../lib/api";
import type { ObjectOut, ObjectQuery } from "../lib/types";
import { useSettled } from "../lib/useSettled";
import { Latex } from "./Latex";

const SHOWN = 20;
const TYPING_PAUSE_MS = 200;

export type PickerFilter = Omit<ObjectQuery, "q" | "offset" | "limit">;

export function ObjectPicker({
  value,
  onChange,
  placeholder,
  filter,
  exclude = [],
}: {
  value: ObjectOut | null;
  onChange: (object: ObjectOut | null) => void;
  placeholder: string;
  filter?: PickerFilter;
  exclude?: readonly string[];
}) {
  const [open, setOpen] = useState(false);
  const [typed, setTyped] = useState("");
  const q = useSettled(typed.trim(), TYPING_PAUSE_MS);
  const found = api.useQuery(
    "get",
    "/objects",
    { params: { query: { ...filter, ...(q === "" ? {} : { q }), limit: SHOWN } } },
    { enabled: open, placeholderData: keepPreviousData },
  );
  const items = (found.data?.items ?? []).filter((object) => !exclude.includes(object.id));
  const unlisted = (found.data?.total ?? 0) - (found.data?.items.length ?? 0);

  return (
    <Combobox.Root
      items={items}
      value={value}
      onValueChange={(next: ObjectOut | null) => {
        onChange(next);
      }}
      open={open}
      onOpenChange={(next) => {
        setOpen(next);
        if (next) setTyped("");
      }}
      inputValue={typed}
      onInputValueChange={setTyped}
      filter={null}
      itemToStringLabel={(object: ObjectOut) => object.latex}
      isItemEqualToValue={(a: ObjectOut, b: ObjectOut) => a.id === b.id}
    >
      <Combobox.Trigger className="flex w-full items-center justify-between gap-2 rounded-sm border border-mist bg-paper px-2 py-1.5 text-left text-xs text-ink focus:border-pond focus:outline-none">
        <Combobox.Value>
          {(selected: ObjectOut | null) =>
            selected ? (
              <Latex>{selected.latex}</Latex>
            ) : (
              <span className="text-ink-soft">{placeholder}</span>
            )
          }
        </Combobox.Value>
        <Combobox.Icon aria-hidden className="text-ink-soft">
          ▾
        </Combobox.Icon>
      </Combobox.Trigger>
      <Combobox.Portal>
        <Combobox.Positioner sideOffset={4} className="z-10 outline-none">
          <Combobox.Popup className="w-(--anchor-width) min-w-64 rounded-sm border border-mist bg-paper shadow-lg outline-none">
            <Combobox.Input
              placeholder="type to search…"
              className="w-full border-b border-mist bg-paper px-2 py-1.5 text-xs text-ink placeholder:text-ink-soft/60 focus:outline-none"
            />
            <Combobox.Status className="px-2 text-[11px] text-ink-soft empty:hidden">
              {found.isPending
                ? "Searching…"
                : unlisted > 0
                  ? `${String(unlisted)} more — keep typing to narrow`
                  : null}
            </Combobox.Status>
            <Combobox.Empty className="px-2 py-1.5 text-xs text-ink-soft italic empty:hidden">
              {found.isPending ? null : "Nothing matches."}
            </Combobox.Empty>
            <Combobox.List className="max-h-64 overflow-auto">
              {(object: ObjectOut) => (
                <Combobox.Item
                  key={object.id}
                  value={object}
                  className="block cursor-default px-2 py-1.5 text-left text-xs outline-none data-[highlighted]:bg-gold-soft/40"
                >
                  <Latex>{object.latex}</Latex>
                  {object.description && (
                    <div className="mt-0.5 text-[11px] text-ink-soft">{object.description}</div>
                  )}
                </Combobox.Item>
              )}
            </Combobox.List>
          </Combobox.Popup>
        </Combobox.Positioner>
      </Combobox.Portal>
    </Combobox.Root>
  );
}
