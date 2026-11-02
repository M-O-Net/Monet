import { describe, expect, it } from "vitest";

import { splitMath } from "./mathText";

describe("splitMath", () => {
  it("leaves text without math as one text segment", () => {
    expect(splitMath("Real functions.")).toEqual([{ kind: "text", value: "Real functions." }]);
  });

  it("finds inline math between single dollars", () => {
    expect(splitMath("Functions with $f(-x) = f(x)$.")).toEqual([
      { kind: "text", value: "Functions with " },
      { kind: "inline", value: "f(-x) = f(x)" },
      { kind: "text", value: "." },
    ]);
  });

  it("finds display math and the backslash delimiters", () => {
    expect(splitMath("See $$x^2$$ and \\(y\\) and \\[z\\]")).toEqual([
      { kind: "text", value: "See " },
      { kind: "display", value: "x^2" },
      { kind: "text", value: " and " },
      { kind: "inline", value: "y" },
      { kind: "text", value: " and " },
      { kind: "display", value: "z" },
    ]);
  });

  it("does not mistake prices or a lone dollar for math", () => {
    expect(splitMath("costs $5 and $10")).toEqual([{ kind: "text", value: "costs $5 and $10" }]);
    expect(splitMath("one $ sign")).toEqual([{ kind: "text", value: "one $ sign" }]);
    expect(splitMath("$ x $")).toEqual([{ kind: "text", value: "$ x $" }]);
  });

  it("keeps an escaped dollar as a literal dollar", () => {
    expect(splitMath("\\$5 and $a$")).toEqual([
      { kind: "text", value: "$5 and " },
      { kind: "inline", value: "a" },
    ]);
  });

  it("leaves an unclosed delimiter as text", () => {
    expect(splitMath("half $x + 1")).toEqual([{ kind: "text", value: "half $x + 1" }]);
  });
});
