import { Select } from "@base-ui/react/select";

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
  objects,
  value,
  onChange,
  placeholder,
}: {
  objects: ObjectSummary[];
  value: string;
  onChange: (id: string) => void;
  placeholder: string;
}) {
  return (
    <Select.Root
      items={objects.map((obj) => ({ value: obj.id, label: obj.latex }))}
      value={value || null}
      onValueChange={(id: string | null) => {
        onChange(id ?? "");
      }}
    >
      <Select.Trigger className="flex w-full items-center justify-between gap-2 rounded-sm border border-mist bg-paper px-2 py-1.5 text-left text-xs text-ink focus:border-pond focus:outline-none">
        <Select.Value>
          {() => {
            const selected = objects.find((o) => o.id === value);
            return selected ? (
              <Latex>{selected.latex}</Latex>
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
