import { Select } from "@base-ui/react/select";
import { useState } from "react";

import { api } from "../lib/api";
import { Latex } from "./Latex";

interface ObjectSummary {
  id: string;
  latex: string;
  description?: string | null;
}

// Built on Base UI's Select (keyboard nav, typeahead, positioning) rather than a native
// <select><option>, which can only render plain text and so couldn't show a LaTeX-typeset
// object (or its description) inside an option.
export function ObjectPicker({
  value,
  onChange,
  placeholder,
}: {
  value: ObjectSummary | null;
  onChange: (object: ObjectSummary | null) => void;
  placeholder: string;
}) {
  const [open, setOpen] = useState(false);
  const query = api.useQuery("get", "/objects", {}, { enabled: open });
  const objects: ObjectSummary[] = query.data ?? (value ? [value] : []);

  return (
    <Select.Root
      open={open}
      onOpenChange={setOpen}
      items={objects.map((obj) => ({ value: obj.id, label: obj.latex }))}
      value={value?.id ?? null}
      onValueChange={(id: string | null) => {
        onChange(objects.find((obj) => obj.id === id) ?? null);
      }}
    >
      <Select.Trigger className="flex w-full items-center justify-between gap-2 rounded-sm border border-mist bg-paper px-2 py-1.5 text-left text-xs text-ink focus:border-pond focus:outline-none">
        <Select.Value>
          {() => {
            return value ? (
              <Latex>{value.latex}</Latex>
            ) : (
              <span className="text-ink-soft">{placeholder}</span>
            );
          }}
        </Select.Value>
        <Select.Icon aria-hidden className="text-ink-soft">
          ▾
        </Select.Icon>
      </Select.Trigger>
      <Select.Portal>
        <Select.Positioner sideOffset={4} className="z-10 outline-none">
          <Select.Popup className="max-h-64 w-(--anchor-width) overflow-auto rounded-sm border border-mist bg-paper shadow-lg outline-none">
            <Select.List>
              {query.isPending && open && (
                <p className="px-2 py-1.5 text-xs text-ink-soft italic">Loading objects…</p>
              )}
              {objects.map((obj) => (
                <Select.Item
                  key={obj.id}
                  value={obj.id}
                  className="block cursor-default px-2 py-1.5 text-left text-xs outline-none data-[highlighted]:bg-gold-soft/40"
                >
                  <Select.ItemText>
                    <Latex>{obj.latex}</Latex>
                  </Select.ItemText>
                  {obj.description && (
                    <div className="mt-0.5 text-[11px] text-ink-soft">{obj.description}</div>
                  )}
                </Select.Item>
              ))}
            </Select.List>
          </Select.Popup>
        </Select.Positioner>
      </Select.Portal>
    </Select.Root>
  );
}
