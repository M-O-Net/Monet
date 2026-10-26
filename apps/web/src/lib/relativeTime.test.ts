import { describe, expect, it } from "vitest";

import { relativeTime } from "./relativeTime";

const now = new Date("2026-10-26T12:00:00Z");
const before = (seconds: number) => new Date(now.getTime() - seconds * 1000).toISOString();

describe("relativeTime", () => {
  it("speaks in the largest whole unit that fits", () => {
    expect(relativeTime(before(20), now)).toBe("just now");
    expect(relativeTime(before(5 * 60), now)).toBe("5 minutes ago");
    expect(relativeTime(before(3 * 3600 + 59 * 60), now)).toBe("3 hours ago");
    expect(relativeTime(before(26 * 3600), now)).toBe("yesterday");
    expect(relativeTime(before(9 * 86400), now)).toBe("9 days ago");
  });

  it("falls back to the date once it is more than a month old", () => {
    expect(relativeTime("2026-01-02T12:00:00Z", now)).toMatch(/2026/);
  });
});
