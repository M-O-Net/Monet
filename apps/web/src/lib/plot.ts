export type Sample = readonly [number, number | null];
export type Range = readonly [number, number];
export type Segment = [number, number][];

const TAIL_QUANTILE = 0.05;
const TAIL_ALLOWANCE = 0.5;
const ZERO_REACH = 1;
const Y_PADDING = 0.06;
const OFFSCREEN_SPANS = 10;
const COMPLEX_PADDING = 1.25;
const NOISE = 1e-12;

const quantile = (sorted: readonly number[], q: number): number =>
  sorted[Math.round(q * (sorted.length - 1))];

export function yWindow(points: readonly Sample[]): Range {
  const ys = points
    .map(([, y]) => y)
    .filter((y): y is number => y !== null && Number.isFinite(y))
    .sort((a, b) => a - b);
  if (ys.length === 0) return [-1, 1];

  const low = quantile(ys, TAIL_QUANTILE);
  const high = quantile(ys, 1 - TAIL_QUANTILE);
  const allowance = (high - low) * TAIL_ALLOWANCE;
  let min = Math.max(ys[0], low - allowance);
  let max = Math.min(ys[ys.length - 1], high + allowance);

  if (min > 0 && min <= (max - min) * ZERO_REACH) min = 0;
  if (max < 0 && -max <= (max - min) * ZERO_REACH) max = 0;
  if (max - min < 1e-9) {
    min -= 1;
    max += 1;
  }
  const pad = (max - min) * Y_PADDING;
  return [min - pad, max + pad];
}

export function curveSegments(points: readonly Sample[], [min, max]: Range): Segment[] {
  const span = max - min;
  const clamp = (y: number) =>
    Math.min(max + OFFSCREEN_SPANS * span, Math.max(min - OFFSCREEN_SPANS * span, y));
  const segments: Segment[] = [];
  let current: Segment = [];
  let previous: number | null = null;

  for (const [x, y] of points) {
    const jumped =
      y !== null &&
      previous !== null &&
      ((previous > max && y < min) || (previous < min && y > max));
    if (y === null || !Number.isFinite(y) || jumped) {
      if (current.length > 1) segments.push(current);
      current = [];
    }
    if (y !== null && Number.isFinite(y)) current.push([x, clamp(y)]);
    previous = y !== null && Number.isFinite(y) ? y : null;
  }
  if (current.length > 1) segments.push(current);
  return segments;
}

export function niceStep(span: number, count: number): number {
  const raw = span / Math.max(1, count);
  const magnitude = 10 ** Math.floor(Math.log10(raw));
  const fraction = raw / magnitude;
  const nice = fraction < 1.5 ? 1 : fraction < 3 ? 2 : fraction < 7 ? 5 : 10;
  return nice * magnitude;
}

export function ticks([min, max]: Range, count = 5): number[] {
  if (!(max > min)) return [];
  const step = niceStep(max - min, count);
  const found: number[] = [];
  for (let k = Math.ceil(min / step); k * step <= max + step * 1e-9; k += 1) {
    found.push(Number((k * step).toPrecision(12)) || 0);
  }
  return found;
}

export function formatNumber(value: number, digits = 4): string {
  if (value === 0) return "0";
  const magnitude = Math.abs(value);
  if (magnitude >= 1e5 || magnitude < 1e-3) return value.toExponential(2).replace("e+", "e");
  return String(Number(value.toPrecision(digits)));
}

export function complexExtent(roots: readonly { re: number; im: number }[]): number {
  const reach = Math.max(1, ...roots.flatMap(({ re, im }) => [Math.abs(re), Math.abs(im)]));
  const step = niceStep(reach * COMPLEX_PADDING, 2);
  return Math.ceil((reach * COMPLEX_PADDING) / step) * step;
}

export function formatComplex(rawRe: number, rawIm: number): string {
  const size = Math.hypot(rawRe, rawIm);
  const re = Math.abs(rawRe) < NOISE * size ? 0 : rawRe;
  const im = Math.abs(rawIm) < NOISE * size ? 0 : rawIm;
  if (im === 0) return formatNumber(re);
  const imaginary = Math.abs(im) === 1 ? "i" : `${formatNumber(Math.abs(im))}i`;
  if (re === 0) return im < 0 ? `-${imaginary}` : imaginary;
  return `${formatNumber(re)} ${im < 0 ? "-" : "+"} ${imaginary}`;
}
