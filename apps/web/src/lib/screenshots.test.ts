import { describe, expect, it } from "vitest";

import { fitWithin } from "./screenshots";

describe("fitWithin", () => {
  it("leaves an image that already fits alone", () => {
    expect(fitWithin(800, 600, 1920)).toEqual({ width: 800, height: 600 });
  });

  it("scales the longer side down to the limit, keeping the shape", () => {
    expect(fitWithin(3840, 2160, 1920)).toEqual({ width: 1920, height: 1080 });
    expect(fitWithin(1000, 4000, 1920)).toEqual({ width: 480, height: 1920 });
  });

  it("never shrinks a side to nothing", () => {
    expect(fitWithin(10000, 1, 1920)).toEqual({ width: 1920, height: 1 });
  });
});
