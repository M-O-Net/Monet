import { describe, expect, it } from "vitest";

import { cleanEditorKey } from "./editorKey";

describe("cleanEditorKey", () => {
  it("drops what a copy picks up around and inside a key", () => {
    expect(cleanEditorKey(" Ab3_-xY\n")).toBe("Ab3_-xY");
    expect(cleanEditorKey("Ab3​_-x Y ")).toBe("Ab3_-xY");
  });

  it("keeps a clean key as it is", () => {
    expect(cleanEditorKey("q8V-3k_Zp0")).toBe("q8V-3k_Zp0");
  });
});
