import { describe, expect, it } from "vitest";

import { describeProvenance } from "./provenance";

const at = "2026-10-26T12:00:00Z";

describe("describeProvenance", () => {
  it("says how a fact arrived and who brought it", () => {
    expect(
      describeProvenance({ at, contributor: "Noether", email: null, source: "manual" }),
    ).toMatch(/^entered by hand by Noether · /);
    expect(
      describeProvenance({ at, contributor: "Noether", email: "n@example.org", source: "manual" }),
    ).toMatch(/^entered by hand by Noether \(n@example\.org\) · /);
    expect(
      describeProvenance({ at, contributor: null, email: null, source: "implementation:1234" }),
    ).toMatch(/^computed by an implementation · /);
  });
});
