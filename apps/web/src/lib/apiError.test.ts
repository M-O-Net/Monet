import { describe, expect, it } from "vitest";

import { ApiError, formatApiError } from "@monet/api-client";

describe("formatApiError", () => {
  it("passes on what the server said", () => {
    expect(formatApiError(new ApiError(400, "a type needs a name"))).toBe("a type needs a name");
  });

  it("names the error code when the server said nothing readable", () => {
    expect(formatApiError(new ApiError(502, null))).toBe(
      "The Monet server had a problem (error 502). Try again in a minute.",
    );
    expect(formatApiError(new ApiError(404, null))).toBe(
      "The Monet server refused this (error 404).",
    );
  });

  it("says when the server could not be reached at all", () => {
    expect(formatApiError(new TypeError("Load failed"))).toBe(
      "Could not reach the Monet server (Load failed). Check your connection, or try again in a minute.",
    );
  });

  it("keeps the reason of any other failure", () => {
    expect(formatApiError(new SyntaxError("Unexpected token <"))).toBe(
      "Something went wrong: Unexpected token <",
    );
    expect(formatApiError({ detail: "from a plain body" })).toBe("from a plain body");
    expect(formatApiError(null)).toBe("Something went wrong.");
  });
});
