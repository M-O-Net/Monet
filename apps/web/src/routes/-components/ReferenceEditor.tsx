import type { ObjectReferenceIn } from "../../lib/types";

const FIELD_CLASS =
  "rounded-sm border border-mist bg-paper px-2 py-1 text-xs text-ink placeholder:text-ink-soft/60 focus:border-pond focus:outline-none";

export function ReferenceEditor({
  references,
  onChange,
}: {
  references: ObjectReferenceIn[];
  onChange: (next: ObjectReferenceIn[]) => void;
}) {
  const replace = (index: number, patch: Partial<ObjectReferenceIn>) => {
    onChange(references.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  };

  return (
    <div className="flex flex-col gap-1">
      <span className="text-[11px] tracking-wide text-ink-soft/70 uppercase">References</span>
      {references.map((reference, index) => (
        <div key={index} className="flex gap-1">
          <input
            value={reference.label}
            onChange={(e) => {
              replace(index, { label: e.target.value });
            }}
            placeholder="Label"
            className={`w-1/3 ${FIELD_CLASS}`}
          />
          <input
            value={reference.url}
            onChange={(e) => {
              replace(index, { url: e.target.value });
            }}
            placeholder="https://…"
            className={`flex-1 ${FIELD_CLASS}`}
          />
          <button
            type="button"
            onClick={() => {
              onChange(references.filter((_row, i) => i !== index));
            }}
            aria-label={`Remove reference ${String(index + 1)}`}
            className="rounded-sm border border-mist px-2 text-xs text-ink-soft hover:bg-paper-deep"
          >
            ×
          </button>
        </div>
      ))}
      <button
        type="button"
        onClick={() => {
          onChange([...references, { label: "", url: "" }]);
        }}
        className="self-start rounded-sm border border-mist px-2 py-0.5 text-xs text-ink-soft hover:bg-paper-deep"
      >
        + reference
      </button>
    </div>
  );
}
