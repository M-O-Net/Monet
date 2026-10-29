import { describe, expect, it } from "vitest";

import { creditsHeading, describeCredits } from "./credits";

const knotinfo = { label: "KnotInfo", url: "https://knotinfo.math.indiana.edu/" };
const atlas = { label: "Knot Atlas", url: "https://katlas.org/wiki/3_1" };

describe("describeCredits", () => {
  it("names every source once and says nothing when there is none", () => {
    expect(describeCredits([])).toBeUndefined();
    expect(describeCredits([knotinfo])).toBe("Source: KnotInfo");
    expect(describeCredits([knotinfo, atlas, { ...knotinfo, url: "https://other" }])).toBe(
      "Sources: KnotInfo, Knot Atlas",
    );
  });

  it("agrees in number with what it credits", () => {
    expect(creditsHeading([atlas])).toBe("Source");
    expect(creditsHeading([atlas, knotinfo])).toBe("Sources");
    expect(creditsHeading([knotinfo, { ...knotinfo, url: "https://other" }])).toBe("Source");
  });
});
