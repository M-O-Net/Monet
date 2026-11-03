const FIELD =
  "w-56 rounded-sm border border-mist bg-paper px-2 py-1 text-xs text-ink placeholder:text-ink-soft/60 focus:border-pond focus:outline-none";

export function ContributorField({
  name,
  email,
  onNameChange,
  onEmailChange,
}: {
  name: string;
  email: string;
  onNameChange: (name: string) => void;
  onEmailChange: (email: string) => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-ink-soft">
      <label className="flex items-center gap-2">
        Your name
        <input
          value={name}
          onChange={(event) => {
            onNameChange(event.target.value);
          }}
          placeholder="optional"
          className={FIELD}
        />
      </label>
      <label className="flex items-center gap-2">
        Email
        <input
          type="email"
          value={email}
          onChange={(event) => {
            onEmailChange(event.target.value);
          }}
          placeholder="optional, shown publicly"
          className={FIELD}
        />
      </label>
    </div>
  );
}
