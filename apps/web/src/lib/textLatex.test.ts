import { describe, expect, it } from "vitest";

import { textLatex } from "./textLatex";

describe("textLatex", () => {
  it("wraps a plain name in text mode", () => {
    expect(textLatex("  Upper Triangular Matrices ")).toBe("\\text{Upper Triangular Matrices}");
  });

  it("escapes the characters text mode would otherwise read as commands", () => {
    expect(textLatex("50% of {x_1} & #2")).toBe("\\text{50\\% of \\{x\\_1\\} \\& \\#2}");
  });
});
