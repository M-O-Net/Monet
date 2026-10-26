import { useState } from "react";

import { Latex } from "../../../components/Latex";
import type { ObjectData } from "../../../lib/data";
import { describe } from "../../../sandbox/client";
import type { SandboxValue } from "../../../sandbox/protocol";

const EXAMPLES: Partial<Record<string, string>> = {
  poly: "x^2 - x + 1",
  matrix: "Matrix([[2, 1], [1, 2]])",
  int: "17",
  rational: "3/4",
  bool: "True",
};

function placeholderFor(kinds: ReadonlySet<string>): string {
  const examples = [...kinds].flatMap((kind) => {
    const example = EXAMPLES[kind];
    return example === undefined ? [] : [example];
  });
  return examples.length > 0
    ? `e.g. ${examples.join(", or ")}`
    : "a polynomial, Matrix([[1, 2], [3, 4]]), a number…";
}

export function ValueFilter({
  kinds,
  ignoreVariable,
  onIgnoreVariableChange,
  onValue,
}: {
  kinds: ReadonlySet<string>;
  ignoreVariable: boolean;
  onIgnoreVariableChange: (ignore: boolean) => void;
  onValue: (value: ObjectData | null) => void;
}) {
  const [text, setText] = useState("");
  const [knot, setKnot] = useState("");
  const [read, setRead] = useState<SandboxValue | null>(null);
  const [reading, setReading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const readValue = () => {
    const typed = text.trim();
    setError(null);
    if (typed === "") {
      setRead(null);
      onValue(null);
      return;
    }
    setReading(true);
    describe(typed).then(
      (value) => {
        setReading(false);
        setRead(value);
        onValue(value.data);
      },
      (failure: unknown) => {
        setReading(false);
        setRead(null);
        onValue(null);
        setError(failure instanceof Error ? failure.message : String(failure));
      },
    );
  };

  return (
    <div className="space-y-2">
      {kinds.has("knot") ? (
        <input
          value={knot}
          onChange={(event) => {
            setKnot(event.target.value);
            const name = event.target.value.trim();
            onValue(name === "" ? null : { knot: name });
          }}
          placeholder="a knot by its Rolfsen name, e.g. 3_1"
          className="w-full rounded-sm border border-mist bg-paper px-3 py-1.5 text-sm text-ink placeholder:text-ink-soft/60 focus:border-pond focus:outline-none"
        />
      ) : (
        <form
          className="flex gap-2"
          onSubmit={(event) => {
            event.preventDefault();
            readValue();
          }}
        >
          <input
            value={text}
            onChange={(event) => {
              setText(event.target.value);
            }}
            placeholder={placeholderFor(kinds)}
            className="flex-1 rounded-sm border border-mist bg-paper px-3 py-1.5 text-sm text-ink placeholder:text-ink-soft/60 focus:border-pond focus:outline-none"
          />
          <button
            type="submit"
            disabled={reading}
            className="rounded-sm border border-mist px-3 py-1.5 text-xs text-ink-soft hover:bg-paper-deep disabled:opacity-50"
          >
            {reading ? "Reading…" : "Match"}
          </button>
        </form>
      )}
      {read && (
        <p className="text-xs text-ink-soft">
          Looking for <Latex>{read.latex}</Latex>
          {read.data === null && " — which the sandbox could not turn into data to match"}
        </p>
      )}
      {read?.data?.poly !== undefined && (
        <label className="flex items-center gap-2 text-xs text-ink-soft">
          <input
            type="checkbox"
            checked={ignoreVariable}
            onChange={(event) => {
              onIgnoreVariableChange(event.target.checked);
            }}
          />
          any variable name (so <Latex>{"z^{2}+1"}</Latex> also matches <Latex>{"x^{2}+1"}</Latex>)
        </label>
      )}
      {error && <p className="text-xs text-rust">Could not read that: {error}</p>}
    </div>
  );
}
