export interface MathSegment {
  kind: "text" | "inline" | "display";
  value: string;
}

interface Delimiter {
  open: string;
  close: string;
  kind: "inline" | "display";
}

const DELIMITERS: Delimiter[] = [
  { open: "$$", close: "$$", kind: "display" },
  { open: "\\[", close: "\\]", kind: "display" },
  { open: "\\(", close: "\\)", kind: "inline" },
  { open: "$", close: "$", kind: "inline" },
];

const WHITESPACE = /\s/;
const DIGIT = /\d/;

function unescapedIndexOf(text: string, needle: string, from: number): number {
  let index = text.indexOf(needle, from);
  while (index > 0 && text[index - 1] === "\\") index = text.indexOf(needle, index + 1);
  return index;
}

function isSingleDollarMath(text: string, start: number, end: number): boolean {
  const first = text[start + 1] ?? "";
  const last = text[end - 1] ?? "";
  const after = text[end + 1] ?? "";
  return end > start + 1 && !WHITESPACE.test(first) && !WHITESPACE.test(last) && !DIGIT.test(after);
}

function mathAt(text: string, start: number): { segment: MathSegment; end: number } | null {
  for (const { open, close, kind } of DELIMITERS) {
    if (!text.startsWith(open, start)) continue;
    const contentStart = start + open.length;
    const closeAt = unescapedIndexOf(text, close, contentStart);
    if (closeAt === -1) continue;
    if (open === "$" && !isSingleDollarMath(text, start, closeAt)) return null;
    const value = text.slice(contentStart, closeAt).trim();
    if (!value) continue;
    return { segment: { kind, value }, end: closeAt + close.length };
  }
  return null;
}

export function splitMath(text: string): MathSegment[] {
  const segments: MathSegment[] = [];
  let plain = "";
  let index = 0;
  while (index < text.length) {
    if (text.startsWith("\\$", index)) {
      plain += "$";
      index += 2;
      continue;
    }
    const math = mathAt(text, index);
    if (math === null) {
      plain += text[index];
      index += 1;
      continue;
    }
    if (plain) segments.push({ kind: "text", value: plain });
    plain = "";
    segments.push(math.segment);
    index = math.end;
  }
  if (plain) segments.push({ kind: "text", value: plain });
  return segments;
}
