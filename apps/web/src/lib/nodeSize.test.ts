import { describe, expect, it } from "vitest";

import { estimateNodeSize } from "./nodeSize";

describe("estimateNodeSize", () => {
  it("grows a matrix by its columns, not by how long its source is", () => {
    const small = estimateNodeSize("\\begin{pmatrix}2&1\\\\1&2\\end{pmatrix}");
    const wide = estimateNodeSize(
      "\\begin{pmatrix}-1&1&0&0\\\\0&-1&1&0\\\\0&0&-1&1\\\\0&0&0&-1\\end{pmatrix}",
    );
    expect(wide.width).toBeGreaterThan(small.width);
    expect(wide.height).toBeGreaterThan(small.height);
  });

  it("does not let a macro-heavy label claim width its rendering will not use", () => {
    const spelled = estimateNodeSize("\\text{Inverse}");
    const plain = estimateNodeSize("Inverse");
    expect(spelled.width).toBe(plain.width);
  });

  it("grows a plain label with its visible length", () => {
    expect(estimateNodeSize("\\text{Characteristic Polynomial}").width).toBeGreaterThan(
      estimateNodeSize("\\text{Degree}").width,
    );
  });

  it("keeps a one-character label wide enough to be clickable", () => {
    expect(estimateNodeSize("6").width).toBeGreaterThanOrEqual(34);
  });

  it("caps a very long label", () => {
    const long = estimateNodeSize(`\\text{${"a".repeat(400)}}`);
    expect(long.width).toBeLessThanOrEqual(190);
  });

  it("shrinks everything by the scale it is given", () => {
    expect(estimateNodeSize("\\text{Degree}", 0.5).width).toBe(
      estimateNodeSize("\\text{Degree}").width / 2,
    );
  });
});
