import { describe, expect, it } from "vitest";

import {
  complexExtent,
  curveSegments,
  formatComplex,
  formatNumber,
  ticks,
  yWindow,
  type Sample,
} from "./plot";

const sample = (f: (x: number) => number, lo: number, hi: number, n = 401): Sample[] =>
  Array.from({ length: n }, (_, i) => {
    const x = lo + ((hi - lo) * i) / (n - 1);
    const y = f(x);
    return [x, Number.isFinite(y) ? y : null] as const;
  });

describe("yWindow", () => {
  it("shows the whole of a tame curve", () => {
    const [min, max] = yWindow(sample((x) => x * x - 4 * x + 3, -0.2, 4.2));
    expect(min).toBeLessThan(-1);
    expect(max).toBeGreaterThan(3.84);
    expect(max).toBeLessThan(4.5);
  });

  it("reaches down to the x-axis when the curve stays near it", () => {
    const [min] = yWindow(sample((x) => x * x - x + 1, -1.7, 2.7));
    expect(min).toBeLessThanOrEqual(0);
  });

  it("leaves out the axis when the curve is far above it", () => {
    const [min] = yWindow(sample((x) => x * x + 100, -2, 2));
    expect(min).toBeGreaterThan(90);
  });

  it("clamps a pole instead of flattening everything else", () => {
    const [min, max] = yWindow(sample((x) => 1 / x, -5, 5, 400));
    expect(max).toBeLessThan(10);
    expect(min).toBeGreaterThan(-10);
  });

  it("gives a constant curve some height", () => {
    const [min, max] = yWindow(sample(() => 2, -1, 1));
    expect(min).toBeLessThan(2);
    expect(max).toBeGreaterThan(2);
  });

  it("falls back when nothing could be evaluated", () => {
    expect(yWindow([[0, null]])).toEqual([-1, 1]);
  });
});

describe("curveSegments", () => {
  it("breaks where the function is undefined", () => {
    const segments = curveSegments(
      [
        [0, 1],
        [1, 2],
        [2, null],
        [3, 2],
        [4, 1],
      ],
      [0, 3],
    );
    expect(segments).toEqual([
      [
        [0, 1],
        [1, 2],
      ],
      [
        [3, 2],
        [4, 1],
      ],
    ]);
  });

  it("breaks across a pole rather than drawing a vertical streak", () => {
    const segments = curveSegments(
      sample((x) => 1 / x, -5, 5, 400),
      [-4, 4],
    );
    expect(segments).toHaveLength(2);
    expect(segments[0].every(([x]) => x < 0)).toBe(true);
    expect(segments[1].every(([x]) => x > 0)).toBe(true);
  });

  it("keeps far-off points finite and near the window", () => {
    const segments = curveSegments(
      [
        [0, 0],
        [1, 1e12],
      ],
      [0, 1],
    );
    expect(segments[0][1][1]).toBe(11);
  });
});

describe("ticks", () => {
  it("lands on round numbers inside the range", () => {
    expect(ticks([-0.2, 4.2])).toEqual([0, 1, 2, 3, 4]);
    expect(ticks([-10, 10])).toEqual([-10, -5, 0, 5, 10]);
    expect(ticks([0.1, 0.35], 5)).toEqual([0.1, 0.15, 0.2, 0.25, 0.3, 0.35]);
  });

  it("is empty for an empty range", () => {
    expect(ticks([1, 1])).toEqual([]);
  });
});

describe("complexExtent", () => {
  it("frames the unit circle with room to spare", () => {
    expect(complexExtent([{ re: 0.5, im: 0.866 }])).toBeGreaterThan(1);
    expect(complexExtent([{ re: 0.5, im: 0.866 }])).toBeLessThanOrEqual(2);
  });

  it("grows to the farthest root", () => {
    expect(complexExtent([{ re: -30, im: 2 }])).toBeGreaterThanOrEqual(30 * 1.25);
  });
});

describe("formatting", () => {
  it("trims numbers to a few significant figures", () => {
    expect(formatNumber(1.1673039782614187)).toBe("1.167");
    expect(formatNumber(-3)).toBe("-3");
    expect(formatNumber(123456)).toBe("1.23e5");
  });

  it("writes complex numbers and drops floating-point noise", () => {
    expect(formatComplex(0.5, -0.8660254)).toBe("0.5 - 0.866i");
    expect(formatComplex(1e-17, 1)).toBe("i");
    expect(formatComplex(0, -2)).toBe("-2i");
    expect(formatComplex(2, 1e-15)).toBe("2");
  });
});
