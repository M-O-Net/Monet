import { ObjectPicker } from "../../../components/ObjectPicker";
import type { PropertyFilter } from "../../../lib/searchQuery";
import type { ObjectOut } from "../../../lib/types";

export function PropertyFilters({
  filters,
  objects,
  onChange,
}: {
  filters: PropertyFilter[];
  objects: ObjectOut[];
  onChange: (filters: PropertyFilter[]) => void;
}) {
  const update = (index: number, change: Partial<PropertyFilter>) => {
    onChange(filters.map((filter, i) => (i === index ? { ...filter, ...change } : filter)));
  };

  return (
    <div className="space-y-2">
      {filters.map((filter, index) => (
        <div key={index} className="flex items-center gap-2">
          <div className="flex-1">
            <ObjectPicker
              objects={objects}
              value={filter.operatorId}
              onChange={(operatorId) => {
                update(index, { operatorId });
              }}
              placeholder="an operation, e.g. Determinant…"
            />
          </div>
          <span className="text-sm text-ink-soft">=</span>
          <div className="flex-1">
            <ObjectPicker
              objects={objects}
              value={filter.valueId}
              onChange={(valueId) => {
                update(index, { valueId });
              }}
              placeholder="its value, e.g. 3…"
            />
          </div>
          <button
            type="button"
            onClick={() => {
              onChange(filters.filter((_, i) => i !== index));
            }}
            className="text-ink-soft hover:text-rust"
            aria-label="Remove this filter"
          >
            ×
          </button>
        </div>
      ))}
      <button
        type="button"
        onClick={() => {
          onChange([...filters, { operatorId: "", valueId: "" }]);
        }}
        className="text-xs text-ink-soft underline decoration-dotted underline-offset-2 hover:text-pond"
      >
        + where an operation gives a value
      </button>
    </div>
  );
}
