export function ContributorField({
  value,
  onChange,
}: {
  value: string;
  onChange: (name: string) => void;
}) {
  return (
    <label className="flex items-center gap-2 text-xs text-ink-soft">
      Your name
      <input
        value={value}
        onChange={(event) => {
          onChange(event.target.value);
        }}
        placeholder="optional — credited on what you add"
        className="w-64 rounded-sm border border-mist bg-paper px-2 py-1 text-xs text-ink placeholder:text-ink-soft/60 focus:border-pond focus:outline-none"
      />
    </label>
  );
}
